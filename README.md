# Data Quality Copilot

An AI-assisted SaaS-style platform for monitoring ETL data batches. It validates records, tracks quality metrics, identifies rule violations, and can generate remediation guidance.



This represents a real data-engineering product: teams submit ETL output, receive data-quality and observability metrics, then use an AI copilot to understand an incident and prioritise a fix.

## Architecture

```
ETL output → FastAPI ingestion → quality rules → SQLite observability store → AI remediation explanation
```

## Features

- Batch-level profiling: row count, null rate, valid and rejected rows.
- Configurable required-field and non-negative-value checks.
- Rejection log with exact reasons and record indexes.
- Persistent scan history in SQLite.
- Optional AI incident explanation through the OpenAI Responses API.
- Interactive API documentation at `/docs`.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`. Use `POST /scans` to validate a data batch. Set `OPENAI_API_KEY` only to enable `POST /ai/explain`.

## Production roadmap

Add user authentication, multi-tenancy, PostgreSQL, Airflow/Prefect orchestration, alerting, and cloud deployment.

## Skills demonstrated

`Python` · `FastAPI` · `ETL` · `Data Quality` · `Observability` · `SQLite` · `OpenAI API` · `Docker` · `SaaS Architecture`
