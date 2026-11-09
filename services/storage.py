import json
import sqlite3
import uuid
from datetime import datetime, timezone

from flask import g

from config import DATABASE


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("""CREATE TABLE IF NOT EXISTS analyses (
            id TEXT PRIMARY KEY, client_id TEXT NOT NULL, doc_type TEXT NOT NULL,
            overall_risk INTEGER NOT NULL, summary TEXT NOT NULL,
            clauses TEXT NOT NULL, created_at TEXT NOT NULL
        )""")
        g.db.commit()
    return g.db


def close_db(_error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def save_analysis(result, owner):
    analysis_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    get_db().execute(
        "INSERT INTO analyses VALUES (?, ?, ?, ?, ?, ?, ?)",
        (analysis_id, owner, result["doc_type"], result["overall_risk"],
         json.dumps(result["summary"], ensure_ascii=False),
         json.dumps(result["clauses"], ensure_ascii=False), created_at),
    )
    get_db().commit()
    return analysis_id, created_at


def list_analyses(owner):
    return get_db().execute(
        "SELECT id, doc_type, overall_risk, created_at FROM analyses "
        "WHERE client_id = ? ORDER BY created_at DESC LIMIT 20", (owner,)
    ).fetchall()


def get_analysis(analysis_id, owner):
    return get_db().execute(
        "SELECT id, doc_type, overall_risk, summary, clauses, created_at FROM analyses "
        "WHERE id = ? AND client_id = ?", (analysis_id, owner)
    ).fetchone()
