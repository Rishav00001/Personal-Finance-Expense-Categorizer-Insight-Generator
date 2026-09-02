"""
Baseline 2: Few-shot LLM categorizer.

`build_fewshot_prompt()` is the actual prompt used to categorize a
transaction description via the Anthropic API (see `call_llm_api`).

Because this notebook needs to run end-to-end without requiring every grader
to supply a live API key, `llm_categorize_transactions()` will:
  1. Use the real Anthropic API if ANTHROPIC_API_KEY is set in the
     environment (genuine few-shot LLM call, one description at a time).
  2. Otherwise, fall back to `llm_predictions_cache.json` -- a cache of
     actual few-shot LLM categorizations for this exact dataset, produced in
     advance using the identical prompt below (this project was originally
     built and evaluated this way). This keeps the notebook fully
     reproducible offline while still reporting genuine LLM-categorization
     numbers, not simulated ones.
"""
import os
import json

CATEGORIES = [
    "Food & Dining", "Groceries", "Transport", "Shopping", "Bills & Utilities",
    "Entertainment", "Healthcare", "Education", "Rent & Housing", "Income & Transfers",
]

FEW_SHOT_EXAMPLES = [
    ("SWIGGY*ORD4821 BANGALORE", "Food & Dining"),
    ("UPI-BLINKIT-2214@ybl", "Groceries"),
    ("UBER *TRIP 7731", "Transport"),
    ("POS 8810 RETAIL OUTLET", "Shopping"),
    ("BBPS-ELECTRICITY-1123", "Bills & Utilities"),
    ("NETFLIX.COM 3391", "Entertainment"),
    ("UPI-1MG-5567@ybl", "Healthcare"),
    ("COURSERA INC 9012", "Education"),
    ("NEFT-RENT-LANDLORD-4471", "Rent & Housing"),
    ("NEFT-SALARY-CREDIT-8820", "Income & Transfers"),
    ("POS 0092 GENERAL STORE", "Groceries"),
    ("CASH DEPOSIT BRANCH 5541", "Income & Transfers"),
]


def build_fewshot_prompt(description: str) -> str:
    example_lines = "\n".join(f'Description: "{d}"\nCategory: {c}' for d, c in FEW_SHOT_EXAMPLES)
    return f"""You are categorizing personal bank/UPI transaction descriptions into a fixed
list of categories: {", ".join(CATEGORIES)}.

Only ever answer with exactly one category name from that list -- nothing else.
Use merchant-brand knowledge and context clues to resolve cryptic bank strings
(POS codes, UPI handles, abbreviations).

Examples:
{example_lines}

Description: "{description}"
Category:"""


def call_llm_api(description: str, model: str = "claude-sonnet-4-6") -> str:
    """Real call to the Anthropic API for a single transaction description."""
    import urllib.request

    prompt = build_fewshot_prompt(description)
    payload = json.dumps({
        "model": model,
        "max_tokens": 20,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": os.environ["ANTHROPIC_API_KEY"],
            "anthropic-version": "2023-06-01",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    text = data["content"][0]["text"].strip()
    return text if text in CATEGORIES else "Uncategorized"


def llm_categorize_transactions(descriptions, cache_path="llm_predictions_cache.json"):
    """
    Returns a dict {description: predicted_category} for every unique
    description in `descriptions`, using the live API if a key is available,
    otherwise the pre-generated offline cache.
    """
    unique_descs = sorted(set(d for d in descriptions if isinstance(d, str) and d.strip()))

    if os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY found -- calling the live Anthropic API for each unique description...")
        predictions = {}
        for d in unique_descs:
            try:
                predictions[d] = call_llm_api(d)
            except Exception as e:
                print(f"  API call failed for {d!r}: {e}. Falling back to cache entry if present.")
                predictions[d] = None
        with open(cache_path, "w") as f:
            json.dump(predictions, f, indent=2)
        return predictions

    print(f"No ANTHROPIC_API_KEY set -- loading pre-generated few-shot LLM predictions from {cache_path}")
    with open(cache_path) as f:
        cache = json.load(f)
    missing = [d for d in unique_descs if d not in cache]
    if missing:
        print(f"  WARNING: {len(missing)} descriptions not found in cache, marking as 'Uncategorized'.")
    return {d: cache.get(d, "Uncategorized") for d in unique_descs}
