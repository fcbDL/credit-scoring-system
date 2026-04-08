"""SQLite database module for evaluation history."""

import sqlite3
import json
from datetime import datetime
from typing import Optional
from pathlib import Path
import os


# Get project root (parent of mini_agent)
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "evaluation_history.db"


def get_db_connection(db_path: Optional[Path] = None):
    """Get database connection."""
    conn = sqlite3.connect(str(db_path or DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[Path] = None):
    """Initialize database and create tables."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            user_input TEXT,
            numeric_data TEXT,
            text_data TEXT,
            final_decision TEXT,
            decision_reason TEXT,
            numeric_result TEXT,
            semantic_risk TEXT,
            credit_score REAL,
            risk_level TEXT,
            conflict_detected INTEGER,
            trace TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print(f"[DB] Database initialized at {db_path or DB_PATH}")


def save_evaluation(
    user_id: Optional[str],
    user_input: str,
    numeric_data: dict,
    text_data: dict,
    final_decision: str,
    decision_reason: str,
    numeric_result: dict,
    semantic_risk: dict,
    credit_score: float,
    risk_level: str,
    conflict_detected: bool,
    trace: list,
    db_path: Optional[Path] = None,
) -> int:
    """Save evaluation record and return ID."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO evaluations (
            user_id, user_input, numeric_data, text_data,
            final_decision, decision_reason, numeric_result, semantic_risk,
            credit_score, risk_level, conflict_detected, trace
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        user_input,
        json.dumps(numeric_data, ensure_ascii=False),
        json.dumps(text_data, ensure_ascii=False),
        final_decision,
        decision_reason,
        json.dumps(numeric_result, ensure_ascii=False),
        json.dumps(semantic_risk, ensure_ascii=False),
        credit_score,
        risk_level,
        1 if conflict_detected else 0,
        json.dumps(trace, ensure_ascii=False),
    ))

    eval_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return eval_id


def get_evaluations(
    limit: int = 50,
    offset: int = 0,
    user_id: Optional[str] = None,
    db_path: Optional[Path] = None,
) -> list[dict]:
    """Get evaluation records."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    if user_id:
        cursor.execute("""
            SELECT * FROM evaluations
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (user_id, limit, offset))
    else:
        cursor.execute("""
            SELECT * FROM evaluations
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))

    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        results.append({
            "id": row["id"],
            "user_id": row["user_id"],
            "final_decision": row["final_decision"],
            "credit_score": row["credit_score"],
            "risk_level": row["risk_level"],
            "created_at": row["created_at"],
        })

    return results


def get_evaluation_by_id(
    eval_id: int,
    db_path: Optional[Path] = None,
) -> Optional[dict]:
    """Get evaluation record by ID."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM evaluations WHERE id = ?", (eval_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "user_input": row["user_input"],
        "numeric_data": json.loads(row["numeric_data"]),
        "text_data": json.loads(row["text_data"]),
        "final_decision": row["final_decision"],
        "decision_reason": row["decision_reason"],
        "numeric_result": json.loads(row["numeric_result"]),
        "semantic_risk": json.loads(row["semantic_risk"]),
        "credit_score": row["credit_score"],
        "risk_level": row["risk_level"],
        "conflict_detected": bool(row["conflict_detected"]),
        "trace": json.loads(row["trace"]),
        "created_at": row["created_at"],
    }


def get_statistics(db_path: Optional[Path] = None) -> dict:
    """Get evaluation statistics."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # Total count
    cursor.execute("SELECT COUNT(*) as total FROM evaluations")
    total = cursor.fetchone()["total"]

    # By decision
    cursor.execute("""
        SELECT final_decision, COUNT(*) as count
        FROM evaluations
        GROUP BY final_decision
    """)
    decision_counts = {row["final_decision"]: row["count"] for row in cursor.fetchall()}

    # Average credit score
    cursor.execute("SELECT AVG(credit_score) as avg FROM evaluations")
    avg_score = cursor.fetchone()["avg"] or 0

    # Risk level distribution
    cursor.execute("""
        SELECT risk_level, COUNT(*) as count
        FROM evaluations
        GROUP BY risk_level
    """)
    risk_distribution = {row["risk_level"]: row["count"] for row in cursor.fetchall()}

    conn.close()

    return {
        "total": total,
        "decisions": decision_counts,
        "average_credit_score": round(avg_score, 2),
        "risk_distribution": risk_distribution,
    }


# Initialize on import
init_db()
