# cleaner/matcher.py
from db.session import get_session
from models.merchant import Merchant
from models.transaction import Transaction
from config import MATCH_BY

def match_transaction(transaction: Transaction) -> bool:
    """
    Try to match a cleaned transaction description to a merchant.
    Updates the transaction's account fields in place.
    Returns True if a match was found, False if not.
    """
    if not transaction.clean_description:
        return False

    session = next(get_session())

    merchant = _find_match(session, transaction.clean_description)

    if merchant:
        if MATCH_BY == "number":
            transaction.account = merchant.account_number
        else:
            transaction.account = merchant.account_name
        transaction.is_matched = True
        session.close()
        return True

    transaction.is_matched = False
    session.close()
    return False


def _find_match(session, clean_description: str):
    """
    Try to find a merchant match using two strategies:
    1. Exact match — the clean description matches raw_name exactly
    2. Partial match — a merchant's raw_name appears anywhere in the description
    """
    clean_upper = clean_description.upper()

    # Strategy 1 — exact match
    merchant = session.query(Merchant).filter(
        Merchant.raw_name.ilike(clean_description)
    ).first()

    if merchant:
        return merchant

    # Strategy 2 — partial match
    # Loop through all merchants and check if their raw_name
    # appears anywhere in the cleaned description
    all_merchants = session.query(Merchant).all()
    for merchant in all_merchants:
        if merchant.raw_name.upper() in clean_upper:
            return merchant

    return None