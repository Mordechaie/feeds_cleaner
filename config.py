from pathlib import Path

# Root of the project (the feeds_cleaner/ directory)
BASE_DIR = Path(__file__).resolve().parent

# Data folder — where Excel files and the SQLite DB live
DATA_DIR = BASE_DIR / "data"

# SQLite database URL — SQLAlchemy needs it in this format
DATABASE_URL = f"sqlite:///{DATA_DIR / 'transactions.db'}"

# Seed data files
NAMES_ACCOUNTS_FILE = DATA_DIR / "names_accounts.xlsx"
QB_RULES_FILE = DATA_DIR / "qb_rules.xlsx"