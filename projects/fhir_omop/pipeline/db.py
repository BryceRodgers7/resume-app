"""DB helpers for the FHIR-OMOP demo.

Thin wrappers around the existing `database.db_manager.DatabaseManager` — we
reuse its `get_connection()` context manager and don't introduce a new
connection layer. Every function takes the manager as a parameter; the
Streamlit page is responsible for caching the single instance.
"""
import json
import logging
import time
from typing import Dict, Iterable, List, Optional, Tuple

import pandas as pd
import psycopg2.extras

from database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


# Listed in the order safe for TRUNCATE without explicit CASCADE chasing
# (children before parents). CASCADE is still used in the SQL because of the
# FK chain through ingestion_run + person.
FHIR_DEMO_TABLES_IN_RESET_ORDER: List[str] = [
    "fhir_demo_code_mapping_report",
    "fhir_demo_drug_exposure",
    "fhir_demo_measurement",
    "fhir_demo_condition_occurrence",
    "fhir_demo_visit_occurrence",
    "fhir_demo_person",
    "fhir_demo_raw_fhir_resource",
    "fhir_demo_ingestion_run",
]


# ---------------------------------------------------------------------------
# Reset / ingestion run lifecycle
# ---------------------------------------------------------------------------
def reset_demo_data(db: DatabaseManager) -> None:
    """Truncate every fhir_demo_* table and restart their SERIAL sequences."""
    sql = (
        "TRUNCATE TABLE "
        + ", ".join(FHIR_DEMO_TABLES_IN_RESET_ORDER)
        + " RESTART IDENTITY CASCADE;"
    )
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
    logger.info("fhir_demo_* tables truncated")


def start_ingestion_run(db: DatabaseManager, notes: Optional[str] = None) -> int:
    """Open a new ingestion_run row and return its id."""
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO fhir_demo_ingestion_run (status, notes) "
                "VALUES (%s, %s) RETURNING ingestion_run_id",
                ("in_progress", notes),
            )
            run_id = cur.fetchone()[0]
        conn.commit()
    return run_id


def complete_ingestion_run(
    db: DatabaseManager,
    run_id: int,
    status: str,
    notes: Optional[str] = None,
) -> None:
    """Stamp `completed_at` + final status onto an ingestion run."""
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE fhir_demo_ingestion_run
                SET completed_at = CURRENT_TIMESTAMP,
                    status       = %s,
                    notes        = COALESCE(%s, notes)
                WHERE ingestion_run_id = %s
                """,
                (status, notes, run_id),
            )
        conn.commit()


# ---------------------------------------------------------------------------
# Raw landing zone
# ---------------------------------------------------------------------------
def insert_raw_resources(
    db: DatabaseManager,
    ingestion_run_id: int,
    resources: Iterable[dict],
) -> int:
    """Drop each FHIR resource into fhir_demo_raw_fhir_resource as JSONB."""
    rows = [
        (ingestion_run_id, r.get("resourceType", "Unknown"), json.dumps(r))
        for r in resources
    ]
    if not rows:
        return 0
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            psycopg2.extras.execute_values(
                cur,
                "INSERT INTO fhir_demo_raw_fhir_resource "
                "(ingestion_run_id, resource_type, resource_json) VALUES %s",
                rows,
            )
        conn.commit()
    return len(rows)


def bulk_ingest_resources(
    db: DatabaseManager,
    source_label: str,
    resources: List[dict],
) -> Tuple[int, int]:
    """Land FHIR resources in fhir_demo_raw_fhir_resource — single transaction.

    Combines start_ingestion_run + insert_raw_resources + complete_ingestion_run
    into ONE connection + ONE transaction. This collapses three round-trips
    to Postgres into one, which is the actual perf win — Supabase connection
    setup is the bottleneck, not the inserts.

    Returns:
        (ingestion_run_id, inserted_row_count)
    """
    t_open = time.perf_counter()
    rows = [
        (None, r.get("resourceType", "Unknown"), json.dumps(r))
        for r in resources
    ]
    n = len(rows)
    logger.info(
        "bulk_ingest_resources: %d resource(s) prepared (source=%r) — opening DB connection",
        n, source_label,
    )

    with db.get_connection() as conn:
        t_conn = time.perf_counter()
        logger.info("bulk_ingest_resources: DB connection open (%.3fs)", t_conn - t_open)
        with conn.cursor() as cur:
            # Open the ingestion run row
            cur.execute(
                "INSERT INTO fhir_demo_ingestion_run (status, notes) "
                "VALUES (%s, %s) RETURNING ingestion_run_id",
                ("in_progress", source_label),
            )
            run_id = cur.fetchone()[0]
            logger.info("bulk_ingest_resources: opened ingestion run #%d", run_id)

            # Insert raw resources, retroactively tagged with the new run_id
            if n:
                tagged = [(run_id, rt, body) for (_, rt, body) in rows]
                psycopg2.extras.execute_values(
                    cur,
                    "INSERT INTO fhir_demo_raw_fhir_resource "
                    "(ingestion_run_id, resource_type, resource_json) VALUES %s",
                    tagged,
                )
                logger.info("bulk_ingest_resources: inserted %d raw resource(s) under run #%d", n, run_id)

            # Close the ingestion run row
            cur.execute(
                """
                UPDATE fhir_demo_ingestion_run
                SET completed_at = CURRENT_TIMESTAMP,
                    status       = %s,
                    notes        = %s
                WHERE ingestion_run_id = %s
                """,
                ("loaded", f"{source_label} — {n} raw resources", run_id),
            )
        conn.commit()
        t_done = time.perf_counter()
        logger.info(
            "bulk_ingest_resources: committed run #%d (%d row(s), %.3fs end-to-end)",
            run_id, n, t_done - t_open,
        )
    return run_id, n


def fetch_raw_resources_by_type(db: DatabaseManager) -> Dict[str, List[dict]]:
    """Read every raw resource back out of the DB, grouped by resource_type."""
    grouped: Dict[str, List[dict]] = {}
    with db.get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT resource_type, resource_json "
                "FROM fhir_demo_raw_fhir_resource ORDER BY resource_id"
            )
            for row in cur.fetchall():
                grouped.setdefault(row["resource_type"], []).append(row["resource_json"])
    return grouped


# ---------------------------------------------------------------------------
# OMOP-inspired inserts
# ---------------------------------------------------------------------------
def insert_persons(db: DatabaseManager, persons: List[dict]) -> Dict[str, int]:
    """Upsert persons by source_patient_id; return {source_patient_id: person_id}."""
    mapping: Dict[str, int] = {}
    if not persons:
        return mapping
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            for p in persons:
                cur.execute(
                    """
                    INSERT INTO fhir_demo_person (source_patient_id, gender, birth_date)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (source_patient_id) DO UPDATE
                        SET gender = EXCLUDED.gender,
                            birth_date = EXCLUDED.birth_date
                    RETURNING person_id, source_patient_id
                    """,
                    (p["source_patient_id"], p["gender"], p["birth_date"]),
                )
                person_id, source_id = cur.fetchone()
                mapping[source_id] = person_id
        conn.commit()
    return mapping


def _bulk_insert(db: DatabaseManager, sql: str, values: list) -> int:
    if not values:
        return 0
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            psycopg2.extras.execute_values(cur, sql, values)
        conn.commit()
    return len(values)


def insert_visits(db: DatabaseManager, rows: List[dict]) -> int:
    values = [
        (r["person_id"], r["encounter_id"], r["visit_start_date"],
         r["visit_end_date"], r["visit_type"])
        for r in rows
    ]
    return _bulk_insert(
        db,
        "INSERT INTO fhir_demo_visit_occurrence "
        "(person_id, encounter_id, visit_start_date, visit_end_date, visit_type) VALUES %s",
        values,
    )


def insert_conditions(db: DatabaseManager, rows: List[dict]) -> int:
    values = [
        (r["person_id"], r["condition_code"], r["condition_display"],
         r["coding_system"], r["condition_start_date"])
        for r in rows
    ]
    return _bulk_insert(
        db,
        "INSERT INTO fhir_demo_condition_occurrence "
        "(person_id, condition_code, condition_display, coding_system, condition_start_date) VALUES %s",
        values,
    )


def insert_measurements(db: DatabaseManager, rows: List[dict]) -> int:
    values = [
        (r["person_id"], r["measurement_code"], r["measurement_display"],
         r["value_numeric"], r["unit"], r["measurement_date"])
        for r in rows
    ]
    return _bulk_insert(
        db,
        "INSERT INTO fhir_demo_measurement "
        "(person_id, measurement_code, measurement_display, value_numeric, unit, measurement_date) VALUES %s",
        values,
    )


def insert_drug_exposures(db: DatabaseManager, rows: List[dict]) -> int:
    values = [
        (r["person_id"], r["drug_code"], r["drug_display"],
         r["coding_system"], r["start_date"])
        for r in rows
    ]
    return _bulk_insert(
        db,
        "INSERT INTO fhir_demo_drug_exposure "
        "(person_id, drug_code, drug_display, coding_system, start_date) VALUES %s",
        values,
    )


def insert_mapping_reports(db: DatabaseManager, rows: List[dict]) -> int:
    values = [
        (r["resource_type"], r["source_code"], r["coding_system"],
         r["mapped_successfully"], r["notes"])
        for r in rows
    ]
    return _bulk_insert(
        db,
        "INSERT INTO fhir_demo_code_mapping_report "
        "(resource_type, source_code, coding_system, mapped_successfully, notes) VALUES %s",
        values,
    )


# ---------------------------------------------------------------------------
# Read helpers for the UI
# ---------------------------------------------------------------------------
def query_dataframe(db: DatabaseManager, sql: str, params: Optional[tuple] = None) -> pd.DataFrame:
    """Run a SELECT and return a pandas DataFrame.

    Built on the existing connection manager + a RealDictCursor — avoids the
    SQLAlchemy dependency that `pd.read_sql_query` would otherwise demand.
    """
    with db.get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params or ())
            return pd.DataFrame(cur.fetchall())


def fetch_table_dataframe(db: DatabaseManager, table_name: str) -> pd.DataFrame:
    """SELECT * FROM <fhir_demo_*> table, guarded by a prefix whitelist."""
    if not table_name.startswith("fhir_demo_"):
        raise ValueError(f"Refusing to query non-demo table: {table_name}")
    return query_dataframe(db, f"SELECT * FROM {table_name} ORDER BY 1")
