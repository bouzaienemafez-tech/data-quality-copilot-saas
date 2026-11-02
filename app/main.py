"""Data Quality Copilot: a minimal SaaS-style ETL observability API."""
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "data/observability.db"
app = FastAPI(title="Data Quality Copilot", version="1.0.0")


class ScanRequest(BaseModel):
    batch_name: str = Field(examples=["orders_2026_11_02"])
    records: list[dict[str, Any]]
    required_fields: list[str] = ["order_id", "customer_id"]
    non_negative_fields: list[str] = ["amount"]


def scan_records(request: ScanRequest):
    rejected, valid, nulls, cells = [], 0, 0, 0
    for index, record in enumerate(request.records):
        reasons = []
        for value in record.values():
            cells += 1
            nulls += value in (None, "")
        for field in request.required_fields:
            if record.get(field) in (None, ""):
                reasons.append(f"missing required field: {field}")
        for field in request.non_negative_fields:
            if record.get(field) is not None:
                try:
                    if float(record[field]) < 0:
                        reasons.append(f"negative value: {field}")
                except (TypeError, ValueError):
                    reasons.append(f"non-numeric value: {field}")
        if reasons:
            rejected.append({"record_index": index, "reasons": reasons})
        else:
            valid += 1
    total = len(request.records)
    return {"total_rows": total, "valid_rows": valid, "rejected_rows": len(rejected), "null_rate": round(nulls / cells, 4) if cells else 0, "quality_score": round(100 * valid / total, 1) if total else 0, "rejections": rejected}


def connection():
    DATABASE.parent.mkdir(exist_ok=True)
    db = sqlite3.connect(DATABASE)
    db.execute("CREATE TABLE IF NOT EXISTS scans (id INTEGER PRIMARY KEY, batch_name TEXT, scanned_at TEXT, result_json TEXT)")
    return db


@app.get("/health")
def health():
    return {"status": "ready"}


@app.post("/scans")
def create_scan(request: ScanRequest):
    result = scan_records(request)
    db = connection()
    cursor = db.execute("INSERT INTO scans(batch_name, scanned_at, result_json) VALUES (?, ?, ?)", (request.batch_name, datetime.now(timezone.utc).isoformat(), json.dumps(result)))
    db.commit()
    db.close()
    return {"scan_id": cursor.lastrowid, "batch_name": request.batch_name, **result}


@app.get("/scans")
def scan_history():
    db = connection()
    rows = db.execute("SELECT id, batch_name, scanned_at, result_json FROM scans ORDER BY id DESC").fetchall()
    db.close()
    return [{"scan_id": row[0], "batch_name": row[1], "scanned_at": row[2], **json.loads(row[3])} for row in rows]


@app.post("/ai/explain")
def explain_findings(result: dict[str, Any]):
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=503, detail="Set OPENAI_API_KEY to enable AI explanations.")
    from openai import OpenAI
    prompt = "You are a data reliability engineer. Summarize this ETL quality scan, assess severity, and give three prioritized remediation steps. Do not invent facts.\n\n" + json.dumps(result)
    response = OpenAI().responses.create(model="gpt-6-astra", input=prompt)
    return {"explanation": response.output_text}
