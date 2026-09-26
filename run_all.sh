#!/usr/bin/env bash
set -euo pipefail
python scripts/audit_data.py
pytest -q
python scripts/evaluate.py
python scripts/train_final.py
python scripts/make_predictions.py
pytest -q
echo 'Done. Start service with: uvicorn app:app --reload'
