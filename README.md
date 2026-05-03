# feeds_cleaner

A console-based Python tool that reads bank and credit card transactions from Excel,
cleans merchant names, and matches them to a chart of accounts using a local SQLite database.

---

## What This Tool Does

Banks and credit cards export transactions with messy, inconsistent merchant descriptions
like `AMZN MKTP US*1A2B3C` or `SQ *STARBUCKS #1234`. This tool:

1. Reads those raw transactions from Excel
2. Cleans and normalizes the merchant descriptions
3. Matches them to a chart of accounts (e.g. "Office Supplies", "Travel", "Meals")
4. Stores everything in a local SQLite database for review and export

---

## Data Flow

```
Excel files (bank/CC exports)
        ↓
  raw transactions imported into SQLite
        ↓
  normalizer.py strips noise from descriptions
        ↓
  matcher.py looks up cleaned name in merchants/rules tables
        ↓
  account assigned to transaction
        ↓
  clean, categorized transactions ready for review
```

---

## Project Structure

```
feeds_cleaner/
│
├── main.py                  # Entry point — CLI menu and app loop
├── config.py                # DB path, file paths, app-wide settings
├── requirements.txt         # Third-party dependencies
├── README.md                # This file
│
├── data/                    # Input Excel files and the SQLite database
│   ├── names_accounts.xlsx  # Merchant name → account mappings (seed data)
│   ├── qb_rules.xlsx        # QuickBooks cleaning rules (seed data)
│   └── transactions.db      # SQLite database (auto-created on first run)
│
├── models/                  # SQLAlchemy ORM models (define database tables)
│   ├── __init__.py
│   ├── base.py              # Shared Base class all models inherit from
│   ├── merchant.py          # Merchants table — name to account mappings
│   ├── rule.py              # Rules table — QB cleaning rules
│   └── transaction.py       # Transactions table — imported and cleaned records
│
├── db/                      # Database setup and session management
│   ├── __init__.py
│   ├── session.py           # Creates engine, SessionLocal, and get_session()
│   └── init_db.py           # Run once to create all tables in the database
│
├── importers/               # One-time scripts to seed the database from Excel
│   ├── __init__.py
│   ├── names_accounts.py    # Reads names_accounts.xlsx → merchants table
│   └── qb_rules.py          # Reads qb_rules.xlsx → rules table
│
├── cleaner/                 # Core transaction cleaning logic
│   ├── __init__.py
│   ├── normalizer.py        # Strips noise from raw merchant strings
│   └── matcher.py           # Matches cleaned names to chart of accounts
│
└── utils/                   # Shared helpers used across the project
    ├── __init__.py
    └── excel.py             # Reads Excel files and returns rows as dictionaries
```

---

## How It Was Built — Step by Step

Understanding the order things were built explains why each piece exists.

### Step 1 — config.py
The first file. Defines all file paths and the database URL in one place so nothing
else in the project hardcodes them. Every other file imports from here.

### Step 2 — models/base.py
Creates the single shared `Base` object that all ORM models inherit from.
SQLAlchemy uses this to keep track of all models and build the database schema.
It lives in its own file to avoid circular imports.

### Step 3 — models/merchant.py, rule.py, transaction.py
The three database tables:
- `merchants` — stores merchant names and the account they map to
- `rules` — stores QuickBooks cleaning rules (patterns and what to do with them)
- `transactions` — stores raw and cleaned transaction records

Each model inherits from `Base`, which is how SQLAlchemy knows about them.

### Step 4 — db/session.py
Uses `DATABASE_URL` from config to create the database engine and a session factory.
Exposes `get_session()` — a context manager that opens a session, commits on success,
rolls back on error, and always closes cleanly. Every file that touches the database
uses this.

### Step 5 — db/init_db.py
A one-time script that calls `Base.metadata.create_all()` to create all tables
in the SQLite file. Must import all models before calling it so SQLAlchemy knows
what to create. Safe to run multiple times — won't overwrite existing tables.

### Step 6 — utils/excel.py
A shared helper that reads any Excel file and returns a list of dictionaries —
one dict per row, with column headers as keys. Both importers use this so the
Excel-reading logic only lives in one place.

### Step 7 — importers/names_accounts.py and qb_rules.py
One-time seed scripts that read the Excel files and insert rows into the database.
They use `utils/excel.py` to read the file, check for duplicates before inserting,
and report how many rows were imported or skipped.

### Step 8 — cleaner/normalizer.py (TODO)
Will strip noise from raw bank descriptions — lowercase, remove special characters,
trim trailing numbers and IDs that banks append to merchant names.

### Step 9 — cleaner/matcher.py (TODO)
Will look up the normalized description against the merchants and rules tables
and assign an account to each transaction.

### Step 10 — main.py (TODO)
The CLI entry point. Will present a menu to import transactions, run the cleaner,
review unmatched transactions, and export results.

---

## Setup

### 1. Install dependencies

```powershell
pip install -r requirements.txt
```

### 2. Add your Excel seed files to the data/ folder

- `data/names_accounts.xlsx`
- `data/qb_rules.xlsx`

### 3. Initialize the database

```powershell
python db/init_db.py
```

This creates `data/transactions.db` with all tables.

### 4. Import seed data

```powershell
python importers/names_accounts.py
python importers/qb_rules.py
```

### 5. Run the tool

```powershell
python main.py
```

---

## Dependencies

| Package | Purpose |
|---|---|
| sqlalchemy | ORM — models, sessions, and database schema |
| pandas | Reading Excel files |
| openpyxl | Required by pandas to open .xlsx files |

---

## Notes

- The SQLite database is local and lives in the `data/` folder. No server needed.
- Importers are safe to re-run — duplicates are detected and skipped.
- `raw_description` on transactions is never overwritten — the original bank text is always preserved.
- Column names in the importers must match your actual Excel headers exactly.
  Run the importers once and check the output if rows are being skipped unexpectedly.