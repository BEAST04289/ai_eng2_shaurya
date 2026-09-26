from __future__ import annotations

from pathlib import Path
import pandas as pd

REQUIRED_TRAIN = {
    "order_id", "order_placed_at", "customer_id", "sku", "sales_channel",
    "payment_mode", "discount_pct", "qty", "order_value_inr",
    "promised_delivery_days", "delivery_pincode", "is_gift",
    "customer_prior_orders", "customer_prior_returns", "delivery_note",
    "last_service_event_type", "pickup_scheduled_at", "source", "returned",
}
REQUIRED_TEST = REQUIRED_TRAIN - {"returned"}


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    return pd.read_csv(path)


def parse_order_dates(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["order_placed_at"] = pd.to_datetime(out["order_placed_at"], errors="raise")
    out["pickup_scheduled_at"] = pd.to_datetime(out["pickup_scheduled_at"], errors="coerce")
    return out


def validate_schema(df: pd.DataFrame, train: bool) -> None:
    required = REQUIRED_TRAIN if train else REQUIRED_TEST
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def canonicalize_train(df: pd.DataFrame) -> pd.DataFrame:
    """One row per order_id. Prefer crm when partner re-import duplicates exist.

    Duplicate groups are allowed only when all columns except `source` agree.
    This turns a silent data-quality assumption into a testable invariant.
    """
    validate_schema(df, train=True)
    work = parse_order_dates(df)

    dup = work[work.duplicated("order_id", keep=False)].copy()
    if not dup.empty:
        compare_cols = [c for c in work.columns if c != "source"]
        bad_ids = []
        for order_id, g in dup.groupby("order_id", sort=False):
            if any(g[c].nunique(dropna=False) > 1 for c in compare_cols):
                bad_ids.append(order_id)
        if bad_ids:
            raise ValueError(
                "Conflicting duplicate order rows; refusing to guess. "
                f"Examples: {bad_ids[:10]}"
            )

    priority = work["source"].map({"crm": 0, "partner_feed": 1}).fillna(9)
    work = (
        work.assign(_source_priority=priority)
        .sort_values(["order_id", "_source_priority"])
        .drop_duplicates("order_id", keep="first")
        .drop(columns="_source_priority")
        .sort_values("order_placed_at")
        .reset_index(drop=True)
    )
    return work


def canonicalize_test(df: pd.DataFrame) -> pd.DataFrame:
    validate_schema(df, train=False)
    out = parse_order_dates(df).copy()
    if out["order_id"].duplicated().any():
        dupes = out.loc[out["order_id"].duplicated(keep=False), "order_id"].unique()[:10]
        raise ValueError(f"Test order_id must be unique. Examples: {dupes.tolist()}")
    return out.reset_index(drop=True)


def load_reference(customers_path: Path, products_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    customers = read_csv(customers_path)
    products = read_csv(products_path)
    customers = customers.copy()
    products = products.copy()
    customers["signup_date"] = pd.to_datetime(customers["signup_date"], errors="coerce")
    products["launch_date"] = pd.to_datetime(products["launch_date"], errors="coerce")
    if customers["customer_id"].duplicated().any():
        raise ValueError("customers.csv must have one row per customer_id")
    if products["sku"].duplicated().any():
        raise ValueError("products.csv must have one row per sku")
    return customers, products
