# main.py
import csv
from io import StringIO
from datetime import datetime
import pandas as pd

from db.init_db import init_db
from db.session import SessionLocal
from models.transaction import Transaction
from models.merchant import Merchant
from importers.names_accounts import import_names
from cleaner.normalizer import normalize
from cleaner.matcher import match_transaction
from config import MATCH_BY
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment


def load_transactions(filepath: str):
    """Read a Chase CSV and insert raw transactions into the database."""
    print(f"\nReading {filepath}...")

    with open(filepath, encoding='latin-1') as f:
        content = f.read().replace('\x00', '')

    reader = csv.DictReader(StringIO(content))
    rows = list(reader)
    print(f"DEBUG: CSV has {len(rows)} rows")

    session = SessionLocal()
    imported = 0
    skipped = 0

    for row in rows:
        description = str(row.get("Description", "")).strip()
        amount = row.get("Amount", "").strip()
        date_raw = str(row.get("Posting Date", "")).strip()
        transaction_type = str(row.get("Type", "")).strip()

        if not description:
            skipped += 1
            continue

        try:
            amount = float(amount)
        except (ValueError, TypeError):
            skipped += 1
            continue

        try:
            date = datetime.strptime(date_raw, "%m/%d/%Y").date()
        except ValueError:
            skipped += 1
            continue

        transaction = Transaction(
            date=date,
            raw_description=description,
            amount=amount,
            source="Chase",
            transaction_type=transaction_type,
        )
        session.add(transaction)
        imported += 1

    session.commit()
    session.close()
    print(f"Done. {imported} imported, {skipped} skipped.")


def clean_transactions():
    """Normalize and match all uncleaned transactions."""
    session = SessionLocal()
    unclean = session.query(Transaction).filter_by(is_cleaned=False).all()

    if not unclean:
        print("\nNo uncleaned transactions found.")
        session.close()
        return

    print(f"\nCleaning {len(unclean)} transactions...")
    matched = 0
    unmatched = 0

    for transaction in unclean:
        transaction.clean_description = normalize(
            transaction.raw_description,
            transaction.transaction_type
        )
        transaction.is_cleaned = True

        found = match_transaction(transaction)
        if found:
            matched += 1
        else:
            unmatched += 1

    session.commit()
    session.close()
    print(f"Done. {matched} matched, {unmatched} unmatched.")


def review_unmatched():
    """Print all transactions that could not be matched to a merchant."""
    session = SessionLocal()
    unmatched = session.query(Transaction).filter_by(is_matched=False).all()

    if not unmatched:
        print("\nNo unmatched transactions.")
        session.close()
        return

    print(f"\n{'Date':<12} {'Amount':>10}  {'Clean Description':<40} {'Raw Description'}")
    print("-" * 100)
    for t in unmatched:
        print(f"{str(t.date):<12} {t.amount:>10.2f}  {str(t.clean_description):<40} {t.raw_description}")

    session.close()


def export_to_excel():
    """Export cleaned transactions to an Excel file."""
    session = SessionLocal()
    transactions = session.query(Transaction).filter_by(is_cleaned=True).all()
    session.close()

    if not transactions:
        print("\nNo cleaned transactions to export.")
        return

    wb = Workbook()
    ws = wb.active
    ws.title = "Cleaned Transactions"

    headers = ["Date", "Raw Description", "Clean Description", "Account Number", "Account Name", "Amount"]
    ws.append(headers)

    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF", name="Arial")
        cell.fill = PatternFill("solid", start_color="2F4F8F")
        cell.alignment = Alignment(horizontal="center")

    for t in transactions:
        ws.append([
            str(t.date),
            t.raw_description,
            t.clean_description,
            t.account if MATCH_BY == "number" else "",
            t.account if MATCH_BY == "name" else "",
            t.amount,
        ])

    ws.column_dimensions["A"].width = 14
    ws.column_dimensions["B"].width = 45
    ws.column_dimensions["C"].width = 35
    ws.column_dimensions["D"].width = 18
    ws.column_dimensions["E"].width = 28
    ws.column_dimensions["F"].width = 12

    for row in ws.iter_rows(min_row=2, min_col=6, max_col=6):
        for cell in row:
            cell.number_format = '#,##0.00;(#,##0.00)'

    output_path = "data/cleaned_transactions.xlsx"
    wb.save(output_path)
    print(f"\nExported {len(transactions)} transactions to {output_path}")


def show_menu():
    print("\n" + "=" * 40)
    print("       FEEDS CLEANER")
    print("=" * 40)
    print("1. Initialize database")
    print("2. Import merchant names")
    print("3. Load transactions from CSV")
    print("4. Clean and match transactions")
    print("5. Review unmatched transactions")
    print("6. Export to Excel")
    print("7. Exit")
    print("=" * 40)


def main():
    while True:
        show_menu()
        choice = input("Select an option: ").strip()

        if choice == "1":
            init_db()
        elif choice == "2":
            import_names()
        elif choice == "3":
            filepath = input("Enter path to CSV file: ").strip()
            load_transactions(filepath)
        elif choice == "4":
            clean_transactions()
        elif choice == "5":
            review_unmatched()
        elif choice == "6":
            export_to_excel()
        elif choice == "7":
            print("\nGoodbye.\n")
            break
        else:
            print("\nInvalid option. Please choose 1-7.")


if __name__ == "__main__":
    main()