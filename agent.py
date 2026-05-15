import sys
import pandas as pd
from openai import OpenAI

# =====================================================
# HERMES FINANCIAL AGENT - REAL ESTATE COMPANY
# =====================================================
# Uses RAG (Retrieval Augmented Generation) to answer
# CFO questions about cash flow and liquidity.
#
# Anti-Hallucination Strategy:
# 1. All numbers come directly from the CSV file (pandas)
# 2. The model is used ONLY to phrase the answer
# 3. temperature=0.1 reduces random invented responses
# 4. The prompt forbids the model from using outside data
# 5. YES/NO decisions are made by Python code, not the model
# 6. The model never sees raw CSV - only pre-calculated numbers
# 7. Summary is printed directly from CSV - no model involved
# =====================================================

# Connect to Ollama locally - free, no internet needed
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

# =====================================================
# LOAD CSV AS KNOWLEDGE BASE
# =====================================================
# The CSV file is the single source of truth.
# dtype=str prevents encoding errors during file read.
# Numeric columns are converted explicitly after loading.
# The agent must never answer from model memory or assumptions.
# =====================================================
df = pd.read_csv("cashflow_statement.csv", dtype=str)
df["amount"] = pd.to_numeric(df["amount"])
df["cash_balance"] = pd.to_numeric(df["cash_balance"])

# =====================================================
# SYSTEM PROMPT - STRICT ANTI-HALLUCINATION RULES
# =====================================================
# This prompt is the first line of defense against hallucination.
# It explicitly forbids the model from inventing any numbers.
# The model is only allowed to use the data passed in the prompt.
# =====================================================
SYSTEM_PROMPT = """You are Hermes, a professional real estate financial advisor.

STRICT ANTI-HALLUCINATION RULES:
1. Answer ONLY based on the provided knowledge base data
2. NEVER invent, estimate, or assume any numbers
3. If data is missing, say: Insufficient data in knowledge base
4. Be data-driven: always base answers on retrieved numbers
5. Give YES/NO answers with detailed numerical justification showing all figures
6. Be professional, directed at the CFO
7. Plain text only, no markdown, no asterisks, no bold"""

# =====================================================
# RAG STEP 1 - RETRIEVE: GET DATA FROM KNOWLEDGE BASE
# =====================================================
def get_data(month):
    # Filter knowledge base by month using pandas
    # This is pure data retrieval - no AI involved at this stage
    data = df[df["month"] == month]

    # If month not found, return None - agent will say: Insufficient data
    if data.empty:
        return None

    # -----------------------------------------------
    # ANTI-HALLUCINATION: All numbers are calculated
    # by Python from the CSV - NOT by the AI model.
    # The model receives only pre-verified numbers.
    # -----------------------------------------------
    balance  = data["cash_balance"].iloc[0]           # Cash balance from CSV
    salaries = data[data["type"] == "salary"]["amount"].sum()   # Salaries from CSV
    income   = data[data["type"] == "income"]["amount"].sum()   # Income from CSV
    expenses = data[data["type"] == "expense"]["amount"].sum()  # Expenses from CSV

    # -----------------------------------------------
    # ANTI-HALLUCINATION: YES/NO decision is made by
    # Python code here - NOT by the AI model.
    # This prevents the model from guessing the answer.
    # -----------------------------------------------
    covers = balance >= salaries  # True if liquidity covers salaries

    # Build the knowledge context to pass to the model
    # The model is only allowed to use these numbers
    return (
        "Data for " + month + " from cashflow_statement.csv:\n"
        "- Cash Balance            : " + "{:,.0f}".format(balance) + " SAR\n"
        "- Total Income            : " + "{:,.0f}".format(income) + " SAR\n"
        "- Total Salaries          : " + "{:,.0f}".format(salaries) + " SAR\n"
        "- Other Expenses          : " + "{:,.0f}".format(expenses) + " SAR\n"
        "- Total Outflow           : " + "{:,.0f}".format(salaries + expenses) + " SAR\n"
        "- Net Cash Position       : " + "{:,.0f}".format(balance - salaries - expenses) + " SAR\n"
        "- Covers Salaries         : " + ("YES" if covers else "NO") + "\n"
        "- Remaining After Salaries: " + "{:,.0f}".format(balance - salaries) + " SAR"
    )

def get_summary():
    # -----------------------------------------------
    # ANTI-HALLUCINATION: Summary is printed directly
    # from the CSV without calling the AI model at all.
    # This guarantees zero hallucination for summary queries.
    # -----------------------------------------------
    lines = [
        "CASHFLOW SUMMARY - ALL MONTHS",
        "Source: cashflow_statement.csv",
        ""
    ]
    # Loop through all months in the knowledge base
    for month in df["month"].unique():
        data     = df[df["month"] == month]
        balance  = data["cash_balance"].iloc[0]
        salaries = data[data["type"] == "salary"]["amount"].sum()
        income   = data[data["type"] == "income"]["amount"].sum()
        expenses = data[data["type"] == "expense"]["amount"].sum()
        lines.append(
            month + " | Balance=" + "{:,.0f}".format(balance) +
            " | Income=" + "{:,.0f}".format(income) +
            " | Salaries=" + "{:,.0f}".format(salaries) +
            " | Expenses=" + "{:,.0f}".format(expenses)
        )
    return "\n".join(lines)

def detect_month(question):
    # Exact matching against CSV month values only
    # No fuzzy matching or guessing - prevents wrong month retrieval
    for month in df["month"].unique():
        if month.lower() in question.lower():
            return month
    return None  # No month found - will default to latest month

# =====================================================
# RAG STEP 2+3 - AUGMENT + GENERATE
# =====================================================
def ask_hermes(question):
    """
    Full RAG Pipeline - 3 steps:

    Step 1 - RETRIEVE:
    Search the CSV knowledge base using pandas.
    Numbers are calculated by Python - not by the model.

    Step 2 - AUGMENT:
    Inject the pre-verified numbers into the prompt.
    The model is forbidden from using any other data.

    Step 3 - GENERATE:
    The model phrases a professional answer for the CFO.
    It only explains the numbers - it does not calculate them.
    """

    # Step 1: Retrieve - get verified data from knowledge base
    month = detect_month(question)
    if month:
        context = get_data(month)
        if not context:
            return "No data available in knowledge base for this month."
    else:
        # Default to latest month if no month detected in question
        context = "Latest month data:\n" + get_data(df["month"].iloc[-1])

    # Step 2: Augment - inject pre-verified numbers into prompt
    # The model is forbidden from using any other data source
    # All numbers in context come from the CSV - not from model memory
    prompt = (
        "Knowledge Base Retrieved:\n" + context +
        "\n\nCFO Question: " + question +
        "\n\nAnswer based ONLY on the knowledge base above." +
        "\nDo not invent any number." +
        "\nUse plain text only, no markdown or asterisks."
    )

    # Step 3: Generate - Hermes writes the professional answer
    # temperature=0.1 = low randomness = less hallucination risk
    # The model only phrases the answer - numbers are pre-verified
    response = client.chat.completions.create(
        model="qwen3:4b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},  # Anti-hallucination rules
            {"role": "user",   "content": prompt}           # Question + verified data
        ],
        temperature=0.1  # Low temperature = less random = less hallucination
    )
    return response.choices[0].message.content

# =====================================================
# MAIN LOOP
# =====================================================
print("=" * 55)
print("   Hermes Financial Agent - Real Estate Company")
print("   Knowledge Base: cashflow_statement.csv")
print("=" * 55)
print("Type 'exit' to quit")
print("Type 'summary' for all months")
print("")

while True:
    try:
        question = input("CFO: ")
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")
        sys.exit(0)

    # Exit the agent
    if question.strip().lower() == "exit":
        print("Goodbye!")
        sys.exit(0)

    # Summary: prints knowledge base directly - NO model call
    # Guarantees zero hallucination for summary queries
    if question.strip().lower() == "summary":
        print(get_summary())
        continue

    # Skip empty input
    if not question.strip():
        continue

    # Send to Hermes RAG pipeline
    try:
        answer = ask_hermes(question)
        print("\nHermes: " + answer + "\n")
    except Exception as e:
        print("\nError: " + str(e) + "\n")
    print("-" * 55)
