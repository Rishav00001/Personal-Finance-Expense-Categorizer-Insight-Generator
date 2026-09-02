# Personal Finance Expense Categorizer & Insight Generator

## Problem Statement
A budgeting app ingests raw bank-transaction descriptions (often cryptic
merchant strings) and needs to categorize each one, then explain a user's
spending pattern in plain language — not just show a pie chart.

## Business Objective
Build and compare a rule-based categorizer against few-shot LLM
categorization, plus an LLM-generated natural-language insight layer, and
recommend a pipeline for a budgeting app's transaction feed.

## Dataset
A synthetic, 6-month (Jan–Jun 2025), self-exported-style bank/UPI statement
containing **384 transactions**, generated to realistically mimic a
Kaggle-style personal finance transaction export: cryptic POS/UPI merchant
strings, debit/credit sign conventions, inconsistent currency formatting
(`Rs. 1,234.56` vs `1234.56`), a handful of duplicate rows, missing values,
and obvious test transactions — with a hidden `true_category` ground-truth
column (used only for evaluation, never shown to either categorizer).

- **File:** `Dataset/bank_transactions.csv`
- **Columns:** `txn_id`, `date`, `description`, `amount`, `true_category`
- A real Kaggle export (e.g. [bukolafatunde/personal-finance](https://www.kaggle.com/datasets/bukolafatunde/personal-finance))
  or an anonymized self-exported bank/UPI statement could be substituted here
  with no change to the pipeline below.

## Approaches Built
1. **Baseline 1 — Rule-based / keyword categorizer** (`Notebook/rule_based.py`):
   a curated 74-entry keyword dictionary matched against the uppercased
   description.
2. **Baseline 2 — Few-shot LLM categorizer** (`Notebook/llm_categorizer.py`):
   a 12-example few-shot prompt (including 2 deliberately ambiguous
   examples) against the same fixed 10-category taxonomy. Calls the live
   Anthropic API if `ANTHROPIC_API_KEY` is set; otherwise loads
   `llm_predictions_cache.json`, a cache of actual few-shot LLM outputs for
   this dataset (produced with the identical prompt), so the notebook is
   fully reproducible offline.
3. **Insight generator**: takes a pre-computed monthly aggregate table
   (never raw transaction rows) and produces a 3–4 sentence natural-language
   spending summary per month, with an explicit "only state numbers present
   in the data" instruction to reduce hallucination.

## Model / Approach Comparison

| Approach | Metric | Score | Notes |
|---|---|---|---|
| Rule-based keyword categorizer | Categorization accuracy (n=120 manually labeled) | **92.5%** | Fails almost exclusively on generic, no-brand-token strings (returns `Uncategorized`); free, deterministic, fully offline. |
| Few-shot LLM categorizer | Categorization accuracy (n=120 manually labeled) | **95.8%** | Resolves most generic/ambiguous strings via brand/world knowledge; costs an API call per unique description; non-deterministic. |
| LLM insight generator | Numeric factual-accuracy rate | **96.2%** (25/26 claims) | 1 hallucinated figure found (a single-digit transcription error in the March summary) — caught by manual fact-checking against the aggregate table. |

Rule-based vs. LLM category-assignment agreement across the full cleaned
dataset: **94.4%** (21 disagreements out of ~376 transactions).

## Recommendation
**Hybrid pipeline:** run the rule-based keyword categorizer first (fast,
free, deterministic) for transactions with a clear brand token, and route
only the `Uncategorized` remainder to the few-shot LLM categorizer — this
captures most of the LLM's accuracy edge while minimizing API cost/latency.
For insights, keep the LLM generator strictly grounded in a pre-computed
aggregate table with an explicit no-invented-numbers instruction, **and**
keep an automated fact-check step in the loop before any summary reaches a
user — the one hallucination found in this project occurred *even with*
aggregate-table grounding, so prompt design alone was not sufficient.

Two additional insight features recommended for a production budgeting app:
- **Month-over-month category comparison** (computable directly from the
  aggregate table, no extra LLM calls).
- **Budget-limit warnings** when a user-set category cap is exceeded.

## Repository Structure
```
AIML-Project4-RollNo-XXXXX/
├── Dataset/
│   └── bank_transactions.csv
├── Notebook/
│   ├── expense_categorizer_insights.ipynb   (main notebook, all cells executed)
│   ├── rule_based.py                        (keyword categorizer module)
│   ├── llm_categorizer.py                   (few-shot LLM categorizer + prompt)
│   ├── llm_predictions_cache.json           (offline cache of LLM categorizations)
│   ├── insight_summaries_cache.json         (offline cache of generated insights)
│   └── monthly_aggregate_table.json         (structured aggregate fed to the insight prompt)
├── Images/
│   ├── eda_01_monthly_spend.png
│   ├── eda_02_amount_distribution.png
│   ├── eda_03_debit_credit_counts.png
│   └── eda_04_day_of_week_spend.png
└── README.md
```

## How to Reproduce
```bash
cd Notebook
# Optional: export ANTHROPIC_API_KEY to run live LLM calls instead of the cache
jupyter nbconvert --to notebook --execute --inplace expense_categorizer_insights.ipynb
```

## Screenshots
See `Images/eda_01_monthly_spend.png` (total spend by month) and
`Images/eda_02_amount_distribution.png` (transaction amount distribution)
for sample visualizations referenced in the notebook.

## Notes on Data Privacy
This dataset is fully synthetic — no real account numbers, names, or
transaction data are included. If this pipeline is ever pointed at a real
exported bank/UPI statement, account numbers and real personal names
embedded in transfer descriptions should be redacted/hashed before the file
is committed to version control or included in any README screenshot.
