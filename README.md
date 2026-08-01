# Hermes Financial Agent — Real Estate

A local AI financial agent designed for real estate cash-flow analysis. It retrieves verified financial data from a structured CSV knowledge base and generates grounded responses to CFO liquidity questions using a local language model.

---

## Project Overview

| Field | Details |
|---|---|
| Agent | Hermes |
| Industry | Real Estate |
| Task | Financial Intelligence and Liquidity Analysis |
| Knowledge Base | `cashflow_statement.csv` |

---

## Features

- Runs entirely on a local machine.
- Retrieves financial data directly from a CSV file.
- Answers liquidity and cash-flow questions using verified data.
- Uses grounded generation to reduce hallucination risk.
- Performs deterministic financial calculations in Python.
- Keeps sensitive financial information on the local device.

---

## How It Works

1. The CFO asks a liquidity or cash-flow question.
2. Python identifies the requested month and required financial fields.
3. `pandas` retrieves the corresponding records from the CSV knowledge base.
4. Deterministic calculations, such as YES/NO decisions, are performed in Python.
5. Only the retrieved and Python-calculated financial context is sent to the local language model.
6. Hermes generates a professional response based exclusively on the provided financial context.

---

## Grounding Strategy

- Financial values are retrieved directly from the CSV file.
- Numerical calculations are performed by Python.
- The language model is instructed to answer only from the retrieved information.
- A low temperature setting reduces response variability.

---

## Tech Stack

- Python
- pandas
- Ollama
- Local LLM
- OpenAI Python SDK

---

## Project Structure

```text
hermes-financial-agent/
├── README.md
├── agent.py
├── cashflow_statement.csv
└── requirements.txt
```

---

## Installation

### 1. Install Ollama

Download and install Ollama from:

https://ollama.com/download

### 2. Pull the Local Language Model

```bash
ollama pull qwen3:4b
```

The project is currently configured to use `qwen3:4b`. To use another Ollama model, update the model name in `agent.py`.

### 3. Start the Ollama Server

```bash
ollama serve
```

### 4. Install Python Dependencies

Using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

Alternatively, install the required packages directly:

```bash
pip install pandas openai
```

### 5. Run the Agent

```bash
python3 agent.py
```

---

## Example 1

### Question

```text
Does the 2.1M liquidity cover May salaries?
```

### Response

```text
YES. Available liquidity is 2,100,000 SAR, while May salaries are
400,000 SAR. The available liquidity is sufficient to cover May salaries.
```

---

## Example 2

### Question

```text
What is the net cash position after salaries in April, and does it
indicate financial health?
```

### Response

```text
The remaining cash after salaries in April is 2,650,000 SAR according
to the knowledge base. However, the available data is insufficient to
determine the company's overall financial health.
```

---

## Knowledge Base

The CSV file contains sample financial data for five months, including:

- Rental income
- Employee salaries
- Bonuses
- Maintenance expenses
- Utility expenses
- Insurance expenses
- Monthly cash balance
- Remaining cash after salaries

---

## Limitations

- Hermes answers only from the available knowledge base.
- It does not provide financial forecasts or investment advice.
- Generated wording may vary depending on the local language model.
- The current knowledge base contains only five months of sample financial data.

---

## Disclaimer

Hermes is intended for educational and demonstration purposes only. It should not be used as a substitute for professional financial, accounting, or investment advice.

All financial data included in this repository is fictional sample data.
