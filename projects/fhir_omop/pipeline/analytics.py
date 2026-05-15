"""SQL-backed analytics for the FHIR-OMOP dashboard.

Every function returns either a small dict/scalar (for metric cards) or a
pandas DataFrame ready to hand to `st.bar_chart` / `st.line_chart` /
`st.dataframe`. All queries hit the same Supabase/Postgres database used by
the rest of the app — there is no caching layer; Streamlit reruns are fast
because the demo data set is tiny.
"""
import logging
from typing import Dict, Optional

import pandas as pd

from database.db_manager import DatabaseManager
from projects.fhir_omop.pipeline.db import query_dataframe

logger = logging.getLogger(__name__)


def get_summary_counts(db: DatabaseManager) -> Dict[str, int]:
    """Counts for the metric cards (patients, encounters, conditions, ...).

    Includes `raw_resources` from the landing zone so the page can detect the
    'loaded but not transformed' state and surface a hint.
    """
    counts: Dict[str, int] = {}
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            for label, table in [
                ("raw_resources",  "fhir_demo_raw_fhir_resource"),
                ("patients",       "fhir_demo_person"),
                ("encounters",     "fhir_demo_visit_occurrence"),
                ("conditions",     "fhir_demo_condition_occurrence"),
                ("measurements",   "fhir_demo_measurement"),
                ("drug_exposures", "fhir_demo_drug_exposure"),
            ]:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                counts[label] = cur.fetchone()[0]
    return counts


def get_mapping_success_rate(db: DatabaseManager) -> Optional[float]:
    """Percentage of mapping_report rows where mapped_successfully = TRUE.

    Returns None when no mapping rows exist yet, so the UI can render '—'
    instead of a misleading '0.0%'.
    """
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    SUM(CASE WHEN mapped_successfully THEN 1 ELSE 0 END)::float AS mapped,
                    COUNT(*)::float AS total
                FROM fhir_demo_code_mapping_report
                """
            )
            mapped, total = cur.fetchone()
    if not total:
        return None
    return round((mapped / total) * 100.0, 1)


def get_conditions_by_frequency(db: DatabaseManager) -> pd.DataFrame:
    return query_dataframe(
        db,
        """
        SELECT condition_display AS condition, COUNT(*) AS occurrences
        FROM fhir_demo_condition_occurrence
        WHERE condition_display IS NOT NULL
        GROUP BY condition_display
        ORDER BY occurrences DESC
        """,
    )


def get_measurements_over_time(db: DatabaseManager) -> pd.DataFrame:
    return query_dataframe(
        db,
        """
        SELECT measurement_date AS date, COUNT(*) AS measurements
        FROM fhir_demo_measurement
        WHERE measurement_date IS NOT NULL
        GROUP BY measurement_date
        ORDER BY measurement_date
        """,
    )


def get_encounter_counts_by_type(db: DatabaseManager) -> pd.DataFrame:
    return query_dataframe(
        db,
        """
        SELECT COALESCE(visit_type, 'unspecified') AS visit_type, COUNT(*) AS encounters
        FROM fhir_demo_visit_occurrence
        GROUP BY visit_type
        ORDER BY encounters DESC
        """,
    )


def get_drug_counts(db: DatabaseManager) -> pd.DataFrame:
    return query_dataframe(
        db,
        """
        SELECT drug_display AS drug, COUNT(*) AS prescriptions
        FROM fhir_demo_drug_exposure
        WHERE drug_display IS NOT NULL
        GROUP BY drug_display
        ORDER BY prescriptions DESC
        """,
    )


def get_mapping_report(db: DatabaseManager) -> pd.DataFrame:
    return query_dataframe(
        db,
        """
        SELECT resource_type, source_code, coding_system, mapped_successfully, notes
        FROM fhir_demo_code_mapping_report
        ORDER BY mapped_successfully ASC, resource_type, source_code
        """,
    )
