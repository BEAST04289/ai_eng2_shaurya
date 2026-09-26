from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
ARTIFACTS = ROOT / "artifacts"

TRAIN_FILE = RAW / "train.csv"
TEST_FILE = RAW / "test_unlabelled.csv"
CUSTOMERS_FILE = RAW / "customers.csv"
PRODUCTS_FILE = RAW / "products.csv"
SAMPLE_FILE = RAW / "sample_submission.csv"
MODEL_FILE = ARTIFACTS / "model.cbm"
LOGISTIC_FILE = ARTIFACTS / "logistic.joblib"
METADATA_FILE = ARTIFACTS / "model_metadata.json"
EVAL_FILE = ARTIFACTS / "evaluation.json"
PREDICTIONS_FILE = ROOT / "predictions.csv"
