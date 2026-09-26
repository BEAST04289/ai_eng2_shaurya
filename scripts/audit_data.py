from __future__ import annotations

import sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import TRAIN_FILE, TEST_FILE, CUSTOMERS_FILE, PRODUCTS_FILE, SAMPLE_FILE
from src.data import read_csv, canonicalize_train, canonicalize_test, load_reference


def main() -> None:
    train_raw = read_csv(TRAIN_FILE)
    test_raw = read_csv(TEST_FILE)
    sample = read_csv(SAMPLE_FILE)
    customers, products = load_reference(CUSTOMERS_FILE, PRODUCTS_FILE)
    train = canonicalize_train(train_raw)
    test = canonicalize_test(test_raw)

    print("=== CORE ===")
    print(f"train_raw_rows={len(train_raw)}")
    print(f"train_unique_order_ids={train_raw.order_id.nunique()}")
    print(f"duplicate_order_id_groups={(train_raw.order_id.value_counts() > 1).sum()}")
    print(f"canonical_train_rows={len(train)}")
    print(f"returns={int(train.returned.sum())}")
    print(f"return_rate={train.returned.mean():.4f}")
    print(f"majority_accuracy={max(train.returned.mean(), 1-train.returned.mean()):.4f}")
    print(f"train_range={train.order_placed_at.min()} -> {train.order_placed_at.max()}")
    print(f"test_rows={len(test)}")
    print(f"test_range={test.order_placed_at.min()} -> {test.order_placed_at.max()}")

    print("\n=== DUPLICATES ===")
    dup = train_raw[train_raw.order_id.duplicated(keep=False)]
    print(dup.groupby("order_id")["source"].apply(lambda s: tuple(sorted(s))).value_counts().to_string())

    print("\n=== LEAKAGE CHECK ===")
    print("train last_service_event_type x returned")
    print(pd.crosstab(train_raw.last_service_event_type, train_raw.returned).to_string())
    print(f"train pickup_nonnull={train_raw.pickup_scheduled_at.notna().sum()}")
    print(f"test pickup_nonnull={test_raw.pickup_scheduled_at.notna().sum()}")
    print("test service events")
    print(test_raw.last_service_event_type.value_counts(dropna=False).to_string())

    print("\n=== JOIN COVERAGE ===")
    print(f"train_customer_coverage={train.customer_id.isin(customers.customer_id).mean():.4f}")
    print(f"test_customer_coverage={test.customer_id.isin(customers.customer_id).mean():.4f}")
    print(f"train_product_coverage={train.sku.isin(products.sku).mean():.4f}")
    print(f"test_product_coverage={test.sku.isin(products.sku).mean():.4f}")

    print("\n=== PAYMENT-GATEWAY VALUE SCALE ===")
    joined = train_raw.merge(products[["sku", "list_price_inr"]], on="sku", how="left")
    dt = pd.to_datetime(joined.order_placed_at)
    expected = joined.list_price_inr * joined.qty * (1 - joined.discount_pct / 100.0)
    ratio = joined.order_value_inr / expected
    october = dt.dt.to_period("M").astype(str).eq("2025-10")
    print(f"october_raw_rows={int(october.sum())}")
    print(f"october_ratio_unique={sorted(np.round(ratio[october].dropna().unique(), 6).tolist())[:10]}")
    print(f"non_october_ratio_gt_10={int(((~october) & (ratio > 10)).sum())}")

    print("\n=== SAMPLE SUBMISSION ===")
    print(f"sample_shape={sample.shape}")
    print(f"sample_columns={sample.columns.tolist()}")
    print(f"sample_order_matches_test={sample.order_id.tolist() == test_raw.order_id.tolist()}")


if __name__ == "__main__":
    main()
