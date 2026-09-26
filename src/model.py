from __future__ import annotations

from catboost import CatBoostClassifier
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .features import CAT_FEATURES, NUM_FEATURES, FEATURES

CATBOOST_PARAMS = {
    "iterations": 100,
    "depth": 6,
    "learning_rate": 0.05,
    "loss_function": "Logloss",
    "l2_leaf_reg": 5,
    "random_seed": 42,
    "verbose": False,
    "allow_writing_files": False,
}

ENSEMBLE_CATBOOST_WEIGHT = 0.50


def ensure_feature_order(X: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in FEATURES if c not in X.columns]
    if missing:
        raise ValueError(f"Missing model features: {missing}")
    out = X[FEATURES].copy()
    for c in CAT_FEATURES:
        out[c] = out[c].fillna("MISSING").astype(str)
    return out


def make_logistic_pipeline() -> Pipeline:
    pre = ColumnTransformer(
        [
            ("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=2), CAT_FEATURES),
            (
                "num",
                Pipeline(
                    [
                        ("impute", SimpleImputer(strategy="median")),
                        ("scale", StandardScaler()),
                    ]
                ),
                NUM_FEATURES,
            ),
        ]
    )
    return Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=2000, C=1.0))])


def fit_catboost(X_train: pd.DataFrame, y_train) -> CatBoostClassifier:
    model = CatBoostClassifier(**CATBOOST_PARAMS)
    model.fit(ensure_feature_order(X_train), y_train, cat_features=CAT_FEATURES)
    return model


def fit_logistic(X_train: pd.DataFrame, y_train) -> Pipeline:
    model = make_logistic_pipeline()
    model.fit(ensure_feature_order(X_train), y_train)
    return model


def predict_catboost(model: CatBoostClassifier, X: pd.DataFrame):
    return model.predict_proba(ensure_feature_order(X))[:, 1]


def predict_logistic(model: Pipeline, X: pd.DataFrame):
    return model.predict_proba(ensure_feature_order(X))[:, 1]


def predict_ensemble(catboost_model, logistic_model, X: pd.DataFrame, catboost_weight: float = ENSEMBLE_CATBOOST_WEIGHT):
    pc = predict_catboost(catboost_model, X)
    pl = predict_logistic(logistic_model, X)
    return catboost_weight * pc + (1.0 - catboost_weight) * pl
