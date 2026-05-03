from pathlib import Path

# Root of the project (the feeds_cleaner/ directory)
BASE_DIR = Path(__file__).resolve().parent

# Data folder — where Excel files and the SQLite DB live
DATA_DIR = BASE_DIR / "data"

# SQLite database URL — SQLAlchemy needs it in this format
DATABASE_URL = f"sqlite:///{DATA_DIR / 'transactions.db'}"

# Seed data file
NAMES_FILE = DATA_DIR / "Names.xlsx"

# Matching mode — "number" matches by account number (e.g. 6005)
#                 "name" matches by account name (e.g. "Wages")
MATCH_BY = "number"  # Change to "name" for clients without account numbers