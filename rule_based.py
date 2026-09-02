"""
Baseline 1: Rule-based / keyword categorizer.
A curated keyword -> category dictionary, matched against the (uppercased)
transaction description. First matching keyword wins. Deliberately built the
way a first-pass keyword dictionary realistically would be -- it covers the
common/obvious brand tokens well but has NO entry for generic/ambiguous
strings (e.g. "POS 0092 GENERAL STORE", "SERVICES PVT LTD"), which is exactly
where it is expected to fail relative to the LLM approach.
"""

KEYWORD_DICT = {
    # Food & Dining
    "SWIGGY": "Food & Dining", "ZOMATO": "Food & Dining", "DOMINOS": "Food & Dining",
    "CHAIPOINT": "Food & Dining", "STARBUCKS": "Food & Dining", "BARBEQUE NATION": "Food & Dining",
    "MC DONALDS": "Food & Dining", "BURGERKING": "Food & Dining", "CCD": "Food & Dining",
    "MEESHOFOOD": "Food & Dining",
    # Groceries
    "BIGBASKET": "Groceries", "DMART": "Groceries", "RELIANCE FRESH": "Groceries",
    "BLINKIT": "Groceries", "MORE SUPERMARKET": "Groceries", "ZEPTO": "Groceries",
    "NATURE BASKET": "Groceries", "SPENCERS": "Groceries",
    # Transport
    "UBER": "Transport", "OLACABS": "Transport", "IRCTC": "Transport",
    "INDIAN OIL": "Transport", "RAPIDO": "Transport", "METRO RECHARGE": "Transport",
    "HPCLPETROL": "Transport", "PARKPLUS": "Transport",
    # Shopping
    "AMAZON": "Shopping", "FLIPKART": "Shopping", "MYNTRA": "Shopping",
    "AJIO": "Shopping", "LIFESTYLE STORE": "Shopping", "NYKAA": "Shopping",
    "DECATHLON": "Shopping", "CROMA": "Shopping",
    # Bills & Utilities
    "ELECTRICITY": "Bills & Utilities", "JIOPREPAID": "Bills & Utilities",
    "AIRTEL PAYMENTS": "Bills & Utilities", "BROADBAND": "Bills & Utilities",
    "GASBILLPAY": "Bills & Utilities", "BSNL": "Bills & Utilities",
    "WATERBOARD": "Bills & Utilities", "DTHRECHARGE": "Bills & Utilities",
    # Entertainment
    "NETFLIX": "Entertainment", "BOOKMYSHOW": "Entertainment", "SPOTIFY": "Entertainment",
    "PVR": "Entertainment", "HOTSTAR": "Entertainment", "STEAM": "Entertainment",
    "GAMEZONE": "Entertainment",
    # Healthcare
    "APOLLO PHARMACY": "Healthcare", "PRACTO": "Healthcare", "MEDPLUS": "Healthcare",
    "1MG": "Healthcare", "FORTIS": "Healthcare", "NETMEDS": "Healthcare",
    "DIAGNOSTICLAB": "Healthcare",
    # Education
    "BYJUS": "Education", "COURSERA": "Education", "UDEMY": "Education",
    "TUITIONFEE": "Education", "UNIVERSITY EXAM": "Education", "UNACADEMY": "Education",
    # Rent & Housing
    "RENT-LANDLORD": "Rent & Housing", "HOUSERENT": "Rent & Housing",
    "MAINTENANCE-SOC": "Rent & Housing", "BROKERFEE": "Rent & Housing",
    # Income & Transfers
    "SALARY-CREDIT": "Income & Transfers", "FROM-RAHUL": "Income & Transfers",
    "REFUND-AMAZON": "Income & Transfers", "ATM WDL": "Income & Transfers",
    "SPLITWISE": "Income & Transfers", "FREELANCE-PAYMENT": "Income & Transfers",
    "TO-MOM": "Income & Transfers", "CASH DEPOSIT": "Income & Transfers",
}


def rule_based_categorize(description: str) -> str:
    """Return best-matching category, or 'Uncategorized' if no keyword hits."""
    if not isinstance(description, str) or not description.strip():
        return "Uncategorized"
    desc_upper = description.upper()
    for keyword, category in KEYWORD_DICT.items():
        if keyword in desc_upper:
            return category
    return "Uncategorized"
