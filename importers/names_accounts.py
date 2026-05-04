# importers/names_accounts.py
from db.session import SessionLocal
from models.merchant import Merchant
from utils.excel import read_excel
from config import NAMES_FILE

def import_names():
    """Read Names.xlsx and seed the merchants table."""
    print(f"Reading {NAMES_FILE}...")
    rows = read_excel(NAMES_FILE)

    session = SessionLocal()

    imported = 0
    skipped = 0

    for row in rows:
        raw_name = row.get("Name")
        account_number = str(row.get("Num", "")).strip()
        account_name = row.get("account_name")

        if not raw_name or not account_number or not account_name:
            skipped += 1
            continue

        exists = session.query(Merchant).filter_by(raw_name=raw_name).first()
        if exists:
            skipped += 1
            continue

        merchant = Merchant(
            raw_name=raw_name,
            account_number=account_number,
            account_name=account_name.strip(),
        )
        session.add(merchant)
        imported += 1

    session.commit()
    session.close()

    print(f"Done. {imported} imported, {skipped} skipped.")

if __name__ == "__main__":
    import_names()
    