# Olist AI Analytics

An AI-powered analytics platform for querying Brazilian e-commerce data using natural language. Ask questions about sales, products, customers, and delivery performance — and get SQL-generated results with interactive visualizations and AI-written summaries.

---

## Overview

This full-stack application lets you explore the [Olist Brazilian E-Commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) without writing a single line of SQL. Type a question, and the system:

1. Generates valid PostgreSQL from your question using the Cohere LLM
2. Executes the query safely against the database
3. Translates Portuguese product categories to English
4. Auto-selects the best chart type (Bar, Pie, Line)
5. Returns a 3-bullet AI summary of the findings

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, Tailwind CSS, Chart.js |
| Backend | FastAPI, Python, Uvicorn |
| Database | PostgreSQL |
| AI / LLM | Cohere API (`command-r-08-2024`) |
| Vector Search | FAISS (schema embeddings) |
| HTTP Client | Axios |

---

## Project Structure

```
olist-ai-analytics/
├── backend/
│   ├── main.py                  # FastAPI app (port 8000)
│   ├── question_processor.py    # Request orchestrator
│   ├── sql_generator.py         # LLM-based SQL generation
│   ├── query_executor.py        # Safe PostgreSQL execution
│   ├── chart_generator.py       # Auto chart type selection
│   ├── category_translator.py   # Portuguese → English translation
│   ├── analytics_queries.py     # Pre-built KPI queries
│   ├── retriever.py             # FAISS schema search
│   ├── schema_embeddings.py     # Schema embedding generation
│   ├── schema_extractor.py      # Live schema extraction
│   ├── requirements.txt
│   └── .env                     # API keys and DB URL (not committed)
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── ChatWindow.jsx
│   │   │   ├── ChatInput.jsx
│   │   │   ├── MessageBubble.jsx
│   │   │   ├── ChartRenderer.jsx
│   │   │   ├── DataTable.jsx
│   │   │   ├── SqlViewer.jsx
│   │   │   ├── SummaryBlock.jsx
│   │   │   └── NeuralBackground.jsx
│   │   └── services/api.js
│   ├── package.json
│   └── vite.config.js
├── sql/
│   ├── schema.sql               # PostgreSQL schema DDL
│   └── views.sql                # Materialized views and indexes
└── data/                        # Olist CSV datasets
```

---

## Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+ running locally
- [Cohere API key](https://cohere.com/)

---

## Setup

### 1. Database

```bash
# Create the database
createdb olist_dev

# Load schema and views
psql -U postgres -d olist_dev -f sql/schema.sql
psql -U postgres -d olist_dev -f sql/views.sql

# Load data from CSVs
psql -U postgres -d olist_dev -c "\COPY olist.customers FROM 'data/olist_customers_dataset.csv' WITH (FORMAT csv, HEADER true);"
psql -U postgres -d olist_dev -c "\COPY olist.sellers FROM 'data/olist_sellers_dataset.csv' WITH (FORMAT csv, HEADER true);"
psql -U postgres -d olist_dev -c "\COPY olist.products FROM 'data/olist_products_dataset.csv' WITH (FORMAT csv, HEADER true);"
psql -U postgres -d olist_dev -c "\COPY olist.orders FROM 'data/olist_orders_dataset.csv' WITH (FORMAT csv, HEADER true);"
psql -U postgres -d olist_dev -c "\COPY olist.order_items FROM 'data/olist_order_items_dataset.csv' WITH (FORMAT csv, HEADER true);"
psql -U postgres -d olist_dev -c "\COPY olist.payments FROM 'data/olist_order_payments_dataset.csv' WITH (FORMAT csv, HEADER true);"
psql -U postgres -d olist_dev -c "\COPY olist.reviews FROM 'data/olist_order_reviews_dataset.csv' WITH (FORMAT csv, HEADER true);"
psql -U postgres -d olist_dev -c "\COPY olist.geolocation FROM 'data/olist_geolocation_dataset.csv' WITH (FORMAT csv, HEADER true);"
psql -U postgres -d olist_dev -c "\COPY olist.product_category_name_translation FROM 'data/product_category_name_translation.csv' WITH (FORMAT csv, HEADER true);"
```

### 2. Backend

```bash
cd backend

python -m venv venv
source venv/Scripts/activate      # Windows
# source venv/bin/activate         # macOS / Linux

pip install -r requirements.txt
```

Create a `.env` file inside `backend/`:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/olist_dev
COHERE_API_KEY=YOUR_COHERE_API_KEY
```

Start the backend:

```bash
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

API is available at `http://localhost:8000`.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

App is available at `http://localhost:5173`.

---

## Usage

Open `http://localhost:5173` in your browser and type a question in the chat input. Examples:

- *"What are the top 10 product categories by total revenue?"*
- *"Show me average delivery delay by state."*
- *"How many orders were placed each month in 2018?"*
- *"What percentage of orders were delivered late?"*
- *"Which sellers have the highest average review score?"*

Each response includes:
- An AI-generated 3-bullet summary
- An interactive chart (bar, pie, or line)
- A collapsible data table
- The generated SQL query

---

## API Reference

### `POST /ask`

**Request**
```json
{ "question": "Top 5 states by number of orders?" }
```

**Response**
```json
{
  "question": "Top 5 states by number of orders?",
  "sql": "SELECT customer_state, COUNT(*) AS order_count FROM ...",
  "explanation": "...",
  "data": {
    "columns": ["customer_state", "order_count"],
    "rows": [...],
    "row_count": 5
  },
  "chart_spec": {
    "type": "bar",
    "data": { "labels": [...], "datasets": [...] }
  },
  "summary": "• SP leads with 41k orders\n• ...\n• ...",
  "meta": {
    "execution_time_ms": 312,
    "source": "llm",
    "chart_available": true
  }
}
```

### `GET /`

Health check. Returns `{"status": "API running"}`.

---

## Database Schema

The `olist` PostgreSQL schema contains:

| Table | Description |
|-------|-------------|
| `customers` | Customer ID, city, state |
| `sellers` | Seller ID and location |
| `products` | Product catalog with dimensions and weight |
| `orders` | Order header with status and timestamps |
| `order_items` | Line items linking orders to products |
| `payments` | Payment method, installments, value |
| `reviews` | Customer review scores and comments |
| `geolocation` | Zip code latitude/longitude coordinates |
| `product_category_name_translation` | Portuguese to English category mapping |

**Materialized views:**
- `order_revenue` — pre-computed total revenue per order
- `order_delivery_metrics` — delivery delay in days per order

---

## Utility Scripts

```bash
cd backend
source venv/Scripts/activate

python check_models.py          # List available Cohere models
python test_execution.py        # Run pre-built KPI queries
python schema_embeddings.py     # Regenerate FAISS schema index
python -m retriever             # Test semantic schema search
```

---

## Safety & Limits

- Only `SELECT` statements are allowed — no destructive SQL operations
- Query execution timeout: **15 seconds**
- Result row limit: **200 rows**
- Chart data capped at **20 data points**

---

## Production Considerations

- Replace the hardcoded CORS origin (`localhost:5173`) in `main.py` with your production domain
- Store `COHERE_API_KEY` and `DATABASE_URL` in a secrets manager (not `.env`)
- Serve the frontend build (`npm run build`) via a CDN or static host
- Use a managed PostgreSQL instance (e.g., AWS RDS, Supabase)
- Wrap Uvicorn with Gunicorn for multi-worker production deployments

---

## License

This project uses the [Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) made available under CC BY-NC-SA 4.0.
