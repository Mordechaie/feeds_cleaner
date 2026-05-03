# importers/names_accounts.py
from db.session import get_session
from models.merchant import Merchant
from utils.excel import read_excel
from config import NAMES_ACCOUNTS_FILE

def import_names_accounts():
    """Read names_accounts.xlsx and seed the merchants table."""
    print(f"Reading {NAMES_ACCOUNTS_FILE}...")
    rows = read_excel(NAMES_ACCOUNTS_FILE)

    session = next(get_session())

    imported = 0
    skipped = 0

    for row in rows:
        raw_name = row.get("merchant")
        account_number = str(row.get("Num", "")).strip()
        account_name = row.get("account_name")

        # Skip rows missing essential data
        if not raw_name or not account:
            skipped += 1
            continue

        # Avoid duplicates
        exists = session.query(Merchant).filter_by(raw_name=raw_name).first()
        if exists:
            skipped += 1
            continue

        merchant = Merchant(
            raw_name=raw_name,
            account=account,
        )
        session.add(merchant)
        imported += 1

    session.commit()
    session.close()

    print(f"Done. {imported} imported, {skipped} skipped.")

if __name__ == "__main__":
    import_names_accounts()