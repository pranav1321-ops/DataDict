# backend/sql_generator.py

import os
import re
import requests
from dotenv import load_dotenv
from schema_extractor import extract_schema

load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
COHERE_URL = "https://api.cohere.com/v2/chat"

HEADERS = {
    "Authorization": f"Bearer {COHERE_API_KEY}",
    "Content-Type": "application/json"
}


# ==========================================
# ROBUST SQL EXTRACTION
# ==========================================

def extract_sql(raw_output: str) -> str:
    if not raw_output:
        return ""

    raw = raw_output.strip()

    blocks = re.findall(r'```(?:sql|postgresql)?\s*(.*?)\s*```', raw, re.DOTALL | re.IGNORECASE)
    if blocks:
        return max(blocks, key=len).strip()

    match = re.search(r'(WITH|SELECT)[\s\S]*', raw, re.IGNORECASE)
    if match:
        return match.group(0).strip()

    return raw


# ==========================================
# BULLETPROOF CLEANER
# ==========================================

def clean_sql_output(raw_sql: str) -> str:
    if not raw_sql:
        return ""

    sql = raw_sql.strip()

    if "```" in sql:
        match = re.search(r'```(?:sql|postgresql)?\s*(.*?)\s*```', sql, re.DOTALL | re.IGNORECASE)
        if match:
            sql = match.group(1).strip()

    sql = sql.rstrip(';').strip()

    # Remove any existing LIMIT
    sql = re.sub(r'(?is)\s+LIMIT\s+\d+(?:\s+OFFSET\s+\d+)?', '', sql)

    sql = sql.strip() + "\nLIMIT 200"
    return sql


# ==========================================
# SQL SAFETY VALIDATION
# ==========================================

def validate_sql(sql: str):
    if not sql:
        raise ValueError("Empty SQL generated.")

    lowered = sql.strip().lower()

    if not (lowered.startswith("select") or lowered.startswith("with")):
        raise ValueError("Only safe SELECT queries are allowed.")

    forbidden = ["insert ", "update ", "delete ", "drop ", "alter ", "truncate ", "create "]
    if any(word in lowered for word in forbidden):
        raise ValueError("Destructive queries are not allowed.")

    if sql.strip().count(';') > 1:
        raise ValueError("Multiple SQL statements are not allowed.")

    return True


# ==========================================
# MAIN SQL GENERATOR - STRONG CATEGORY FIX
# ==========================================

def generate_sql(user_query: str, chat_history=None):
    if chat_history is None:
        chat_history = []

    schema_context = extract_schema()

    system_prompt = f"""You are a senior PostgreSQL analyst for Olist Brazilian e-commerce.

STRICT RULES — VIOLATE = INVALID:
- Return ONLY raw SQL. No explanations, no markdown, no ```, no comments.
- ALWAYS start with SELECT or WITH.
- ALWAYS use fully qualified names: olist.orders, olist.products, olist.order_items etc.
- ALWAYS alias tables (o, p, oi, c...).
- ALWAYS qualify joins (oi.product_id = p.product_id).

CRITICAL FOR PRODUCT CATEGORIES:
- There is NO table called product_category_name_translation in the database.
- NEVER join or mention any translation table.
- Product category names (in Portuguese) are in olist.products.product_category_name.
- To get categories by sales you MUST join like this:
  FROM olist.order_items oi
  JOIN olist.products p ON oi.product_id = p.product_id
- Use p.product_category_name in SELECT and GROUP BY.
- Translation to English happens in Python AFTER the query.

Database Schema:
{schema_context}

Examples:

User: top 5 product categories by sales
Assistant:
SELECT p.product_category_name,
       SUM(oi.price) AS total_sales
FROM olist.order_items oi
JOIN olist.products p ON oi.product_id = p.product_id
GROUP BY p.product_category_name
ORDER BY total_sales DESC

User: highest selling product in 2018
Assistant:
SELECT p.product_category_name, 
       SUM(oi.price) AS total_sales
FROM olist.order_items oi
JOIN olist.products p ON oi.product_id = p.product_id
JOIN olist.orders o ON oi.order_id = o.order_id
WHERE o.order_purchase_timestamp BETWEEN '2018-01-01' AND '2018-12-31'
GROUP BY p.product_category_name
ORDER BY total_sales DESC

Now generate SQL for the user question below. Return ONLY the SQL."""

    messages = [{"role": "system", "content": system_prompt}]

    for turn in chat_history[-4:]:
        messages.append({"role": "user", "content": turn["query"]})
        messages.append({"role": "assistant", "content": turn["sql"]})

    messages.append({"role": "user", "content": user_query})

    payload = {
        "model": "command-r-08-2024",
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": 800
    }

    try:
        print(f"\n[SQL Generator] Processing query: {user_query[:150]}...")

        response = requests.post(COHERE_URL, headers=HEADERS, json=payload, timeout=35)

        if response.status_code >= 400:
            raise RuntimeError(f"Cohere API error {response.status_code}: {response.text[:400]}")

        data = response.json()
        blocks = data.get("message", {}).get("content", [])
        raw_output = next((b.get("text") for b in blocks if b.get("type") == "text"), "")

        if not raw_output:
            raise RuntimeError("Model returned empty response")

        print(f"[SQL Generator] RAW OUTPUT FROM MODEL:\n{raw_output}\n{'─' * 90}")

        extracted = extract_sql(raw_output)
        final_sql = clean_sql_output(extracted)

        print(f"[SQL Generator] FINAL CLEAN SQL:\n{final_sql}\n{'─' * 90}")

        validate_sql(final_sql)
        return final_sql

    except Exception as e:
        print(f"[SQL Generator ERROR] {str(e)}")
        raise RuntimeError(f"SQL generation failed: {str(e)}")