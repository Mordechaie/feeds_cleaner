# cleaner/normalizer.py
import re

def normalize(description: str, transaction_type: str = "") -> str:
    """
    Clean a raw bank transaction description.
    Returns a normalized string for matching against the merchants table.
    """
    if not description:
        return ""

    # Route to the right cleaner based on transaction type
    if transaction_type in ("ACH_DEBIT", "ACH_CREDIT"):
        return _clean_ach(description)
    elif "ZELLE" in description.upper():
        return _clean_zelle(description)
    else:
        return _clean_debit_card(description)


def _clean_debit_card(description: str) -> str:
    """
    Clean debit card descriptions.
    Example: 'SHELL SERVICE STATION INWOOD NY 04/30' -> 'SHELL SERVICE STATION'
    """
    # Remove trailing date patterns like 04/30 or 04/30/26
    description = re.sub(r'\d{2}/\d{2}(/\d{2,4})?$', '', description)

    # Remove state abbreviations and city noise at the end
    description = re.sub(r'\s+[A-Z]{2}\s*$', '', description)

    # Remove reference numbers and transaction IDs
    description = re.sub(r'[#*]\w+', '', description)

    return description.strip()


def _clean_ach(description: str) -> str:
    """
    Extract the vendor name from ACH descriptions.
    Example: 'ORIG CO NAME:ADP PAYROLL FEES ...' -> 'ADP PAYROLL FEES'
    """
    # Try to extract ORIG CO NAME first — most reliable field
    match = re.search(r'ORIG CO NAME[:\s]+([^0-9\n]+?)(?:\s{2,}|$)', description, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Fallback — return first meaningful chunk before whitespace runs
    parts = re.split(r'\s{2,}', description.strip())
    return parts[0].strip() if parts else description.strip()


def _clean_zelle(description: str) -> str:
    """
    Extract the recipient name from Zelle descriptions.
    Example: 'Zelle payment to Cristie JPM99cf4p5yi' -> 'Cristie'
    """
    # Match 'Zelle payment to <Name> <reference>'
    match = re.search(r'zelle payment to ([a-zA-Z\s]+?)(?:\s+[A-Z]{3}\w+)?$', description, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    return description.strip()