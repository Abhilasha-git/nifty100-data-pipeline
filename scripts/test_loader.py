# scripts/test_loader.py

from src.etl.loader import load_core_files

datasets = load_core_files()

print(datasets["cashflow"].columns.tolist())