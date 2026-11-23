from pathlib import Path

RULE_VERSION = 'roast-ledger-1.0'
PORT = 18474
SAMPLES = Path(__file__).resolve().parents[1] / 'sample_data'
FILE_LIMIT = 300_000
