# cleaner/matcher.py
from rapidfuzz import fuzz
from db.session import SessionLocal
from models.merchant import Merchant
from models.rule import Rule
from models.transaction import Transaction

# Minimum score for a fuzzy match to be accepted (0-100)
FUZZY_THRESHOLD = 80

def match_transaction(transaction: Transaction) -> bool:
    """
    Try to match a cleaned transaction description to a rule or merchant.
    Rules are checked first, merchants as fallback.
    Returns True if a match was found, False if not.
    """
    if not transaction.clean_description:
        return False

    session = SessionLocal()
    clean = transaction.clean_description.upper()

    # Step 1 — check rules first
    rule = _match_rules(session, clean)
    if rule:
        transaction.clean_description = rule.clean_name
        transaction.account_number = rule.account_number
        transaction.account_name = rule.account_name
        transaction.is_matched = True
        session.close()
        return True

    # Step 2 — fall back to merchant lookup
    merchant = _match_merchants(session, clean)
    if merchant:
        transaction.account_number = merchant.account_number
        transaction.account_name = merchant.account_name
        transaction.is_matched = True
        session.close()
        return True

    transaction.is_matched = False
    session.close()
    return False


def _match_rules(session, clean: str):
    """
    Check active rules using exact then fuzzy matching.
    """
    rules = session.query(Rule).filter_by(is_active=True).all()

    # Exact / partial match first
    for rule in rules:
        if rule.pattern.upper() in clean:
            return rule

    # Fuzzy match second
    best_score = 0
    best_rule = None
    for rule in rules:
        score = fuzz.partial_ratio(rule.pattern.upper(), clean)
        if score > best_score:
            best_score = score
            best_rule = rule

    if best_score >= FUZZY_THRESHOLD:
        return best_rule

    return None


def _match_merchants(session, clean: str):
    """
    Check merchants using exact then fuzzy matching.
    """
    merchants = session.query(Merchant).all()

    # Exact / partial match first
    for merchant in merchants:
        if merchant.raw_name.upper() in clean:
            return merchant

    # Fuzzy match second
    best_score = 0
    best_match = None
    for merchant in merchants:
        score = fuzz.partial_ratio(merchant.raw_name.upper(), clean)
        if score > best_score:
            best_score = score
            best_match = merchant

    if best_score >= FUZZY_THRESHOLD:
        return best_match

    return None