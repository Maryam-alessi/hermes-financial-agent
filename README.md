Hermes Financial Agent - Real Estate
A local AI financial agent that uses RAG (Retrieval Augmented Generation) to analyze cash flow data and answer CFO liquidity questions without hallucination.
Project Overview

Company: Real Estate
Agent: Hermes
Task: Financial Intelligence and Liquidity Analysis
Knowledge Base: cashflow_statement.csv (income, expenses, cash balance)

How It Works

CFO asks a question about liquidity
Agent retrieves relevant data from CSV using pandas (filtered by month)
Agent passes the verified numbers to the local LLM
Hermes generates a professional answer based ONLY on the retrieved data

Anti-Hallucination Strategy

All numbers come directly from the CSV file
YES/NO decisions are made by Python code, not the AI model
temperature=0.1 reduces random invented responses
The model is forbidden from using outside data
Summary is printed directly from CSV with no model involved

Tech Stack

Hermes Agent v0.13.0
Ollama (local LLM server)
Local AI model
Python + pandas
WSL (Windows Subsystem for Linux)
RAG (Retrieval Augmented Generation)

How to Run

Install Ollama: https://ollama.com/download
Pull Ollama model
Install dependencies: pip install pandas openai
Run the agent: python3 agent.py

Example
CFO: Does the 2.1M liquidity cover May salaries?
Hermes: YES. Liquidity available: 2,100,000 SAR. May salaries: 400,000 SAR. Since 2,100,000 > 400,000, the liquidity covers May salaries.
Knowledge Base
The CSV file contains 5 months of financial data:

Income (rental income)
Salaries (employee salaries and bonuses)
Expenses (maintenance, utilities, insurance)
Cash balance per month

Note: Data is sample data used for training purposes.
