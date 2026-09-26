$ErrorActionPreference = "Stop"
python scripts/audit_data.py
pytest -q
python scripts/evaluate.py
python scripts/train_final.py
python scripts/make_predictions.py
pytest -q
Write-Host "Done. Start service with: uvicorn app:app --reload"
