"""FHIR-to-OMOP clinical data pipeline demo page.

A simplified healthcare interoperability demo. Loads synthetic FHIR R4
bundles, lands them in a raw JSONB table, transforms them into a small
OMOP-inspired schema, and renders the result as metrics, tables, and charts.

This is a portfolio familiarity project — not a production OMOP ETL.
"""
import json
import logging
import time
from pathlib import Path
from typing import List

import streamlit as st

import nav
from app import home_page
from database.db_manager import DatabaseManager
from projects.fhir_omop.pipeline import analytics, fhir_loader, transformers
from projects.fhir_omop.pipeline import db as demo_db

logger = logging.getLogger(__name__)

SAMPLE_DATA_DIR = (
    Path(__file__).resolve().parent.parent
    / "projects" / "fhir_omop" / "sample_data"
)

st.set_page_config(
    page_title="FHIR → OMOP Demo",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

nav.config_navigation(home_page)


@st.cache_resource
def get_db() -> DatabaseManager:
    return DatabaseManager()


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("🧬 FHIR-to-OMOP Clinical Data Pipeline Demo")

st.markdown(
    """
    ### Simplified Healthcare Interoperability Demo

    This page loads **synthetic FHIR R4** patient bundles, transforms them into
    a **simplified, OMOP-inspired relational schema**, and surfaces the result
    as analytics and tables.

    It is intended to demonstrate familiarity with healthcare interoperability
    concepts — **not** production clinical compliance or certified OMOP CDM use.
    """
)

with st.expander("🎯 What this demonstrates", expanded=False):
    st.markdown(
        """
        - **FHIR R4 ingestion** — reading Bundle JSON resembling Synthea output
        - **Standard terminology awareness** — SNOMED CT, LOINC, RxNorm, ICD-10
        - **OMOP-inspired modeling** — person / visit_occurrence /
          condition_occurrence / measurement / drug_exposure flattened into a
          portfolio-friendly form
        - **ETL pipeline shape** — raw landing zone (JSONB) → transform step →
          analytics queries, each stage observable in the UI
        - **Code-mapping reporting** — happy-path "mapped vs. unmapped" check
          to illustrate where real concept-id resolution would live
        """
    )

with st.expander("🔧 Setup & demo workflow", expanded=False):
    st.markdown(
        """
        **One-time DB setup** — run `database/fhir_omop_sql/001_create_tables.sql`
        against the Supabase/Postgres database used by this app.

        **Demo workflow:**
        1. **Reset Demo Data** — truncate every `fhir_demo_*` table.
        2. **Load Sample FHIR Bundles** — read JSON from
           `projects/fhir_omop/sample_data/`, open an ingestion run, and
           persist every resource as JSONB in `fhir_demo_raw_fhir_resource`.
        3. **Run Transformation Pipeline** — read the raw resources back out,
           transform them into the OMOP-inspired tables, and generate the
           code-mapping report.

        Each step is independent and idempotent within a fresh reset.
        """
    )

# ---------------------------------------------------------------------------
# DB handle
# ---------------------------------------------------------------------------
try:
    db = get_db()
except Exception as e:
    st.error(f"Database not available: {e}")
    st.stop()

# ---------------------------------------------------------------------------
# Action buttons
# ---------------------------------------------------------------------------
col_a, col_b, col_c = st.columns(3)
with col_a:
    reset_clicked = st.button("🧹 Reset Demo Data", width="stretch")
with col_b:
    load_clicked = st.button(
        "📥 Load Sample FHIR Bundles", type="primary", width="stretch"
    )
with col_c:
    transform_clicked = st.button(
        "⚙️ Run Transformation Pipeline", width="stretch"
    )

status_placeholder = st.empty()


def _run_reset() -> None:
    logger.info("reset: user clicked Reset Demo Data")
    t0 = time.perf_counter()
    with st.status("Truncating `fhir_demo_*` tables...", expanded=False) as s:
        demo_db.reset_demo_data(db)
        s.update(label=f"All `fhir_demo_*` tables truncated ({time.perf_counter() - t0:.2f}s)",
                 state="complete")
    logger.info("reset: complete (%.3fs)", time.perf_counter() - t0)
    status_placeholder.success("All `fhir_demo_*` tables truncated.")


def _ingest_bundles(bundles: List[dict], source_label: str, status_ui) -> None:
    """Land already-parsed FHIR Bundles into fhir_demo_raw_fhir_resource.

    Shared by the sample-data path and the upload path so both produce the
    same audit trail (one ingestion_run row per click) and the same logging
    surface. All DB writes happen inside a SINGLE transaction
    (`demo_db.bulk_ingest_resources`) so the click triggers exactly one
    Supabase round-trip end-to-end — the previous 3-round-trip flow was the
    cause of the "white screen while it hangs" symptom.
    """
    status_ui.update(label=f"{source_label}: grouping resources by type...")
    t_group = time.perf_counter()
    grouped = fhir_loader.group_bundles_by_resource_type(bundles)
    all_resources = [r for rs in grouped.values() for r in rs]
    logger.info(
        "ingest: %s — %d bundle(s), %d resource(s) total, grouped in %.3fs",
        source_label, len(bundles), len(all_resources), time.perf_counter() - t_group,
    )
    status_ui.write(f"Grouped **{len(all_resources)}** resource(s) from **{len(bundles)}** bundle(s).")

    if not all_resources:
        status_ui.update(label=f"{source_label}: no FHIR resources found.", state="error")
        status_placeholder.warning(f"{source_label}: no FHIR resources found.")
        return

    status_ui.update(label=f"{source_label}: writing to Supabase (1 transaction)...")
    t_db = time.perf_counter()
    run_id, inserted = demo_db.bulk_ingest_resources(db, source_label, all_resources)
    elapsed = time.perf_counter() - t_db
    logger.info(
        "ingest: %s — wrote run #%d, %d row(s) to fhir_demo_raw_fhir_resource in %.3fs",
        source_label, run_id, inserted, elapsed,
    )
    status_ui.write(f"Inserted **{inserted}** raw resource(s) under run **#{run_id}** ({elapsed:.2f}s).")
    status_ui.update(label=f"{source_label} — run #{run_id} complete.", state="complete")
    status_placeholder.success(
        f"{source_label} — {len(bundles)} bundle(s), "
        f"{inserted} raw resources inserted (run #{run_id})."
    )


def _run_sample_load() -> None:
    logger.info("sample_load: user clicked Load Sample FHIR Bundles")
    t0 = time.perf_counter()
    with st.status("Loading sample FHIR bundles...", expanded=True) as s:
        s.update(label=f"Scanning {SAMPLE_DATA_DIR.name}/ for bundle files...")
        bundle_paths = fhir_loader.discover_bundle_files(SAMPLE_DATA_DIR)
        s.write(f"Found **{len(bundle_paths)}** bundle file(s).")
        if not bundle_paths:
            logger.warning("sample_load: no bundle files under %s", SAMPLE_DATA_DIR)
            s.update(label="No bundle files found.", state="error")
            status_placeholder.warning(f"No bundle files found in {SAMPLE_DATA_DIR}")
            return
        s.update(label=f"Parsing {len(bundle_paths)} bundle file(s)...")
        bundles = [fhir_loader.load_bundle(p) for p in bundle_paths]
        _ingest_bundles(bundles, source_label="Loaded sample bundles", status_ui=s)
    logger.info("sample_load: end-to-end %.3fs", time.perf_counter() - t0)


def _run_uploaded_load(uploaded_files) -> None:
    logger.info(
        "upload_load: user clicked Load Uploaded Bundles — %d file(s) selected",
        len(uploaded_files) if uploaded_files else 0,
    )
    if not uploaded_files:
        status_placeholder.warning("No files selected.")
        return
    t0 = time.perf_counter()
    with st.status(f"Parsing {len(uploaded_files)} uploaded file(s)...", expanded=True) as s:
        bundles: List[dict] = []
        bad: List[str] = []
        for uf in uploaded_files:
            try:
                payload = uf.getvalue()
                bundle = json.loads(payload.decode("utf-8"))
                bundles.append(bundle)
                logger.info(
                    "upload_load: parsed %s (%d bytes, %d entries)",
                    uf.name, len(payload), len(bundle.get("entry", []) or []),
                )
                s.write(f"Parsed `{uf.name}` — {len(payload):,} bytes, "
                        f"{len(bundle.get('entry', []) or [])} entries")
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.warning("upload_load: failed to parse %s — %s", uf.name, e)
                bad.append(f"{uf.name}: {e}")
        if bad:
            s.update(label="Some uploads could not be parsed as JSON.", state="error")
            status_placeholder.error(
                "Some uploads could not be parsed as JSON:\n- " + "\n- ".join(bad)
            )
            return
        _ingest_bundles(bundles, source_label="Loaded uploaded bundles", status_ui=s)
    logger.info("upload_load: end-to-end %.3fs", time.perf_counter() - t0)


def _run_transform() -> None:
    logger.info("transform: user clicked Run Transformation Pipeline")
    t0 = time.perf_counter()
    with st.status("Running transformation pipeline...", expanded=True) as s:
        s.update(label="Reading raw resources from Supabase...")
        t = time.perf_counter()
        grouped = demo_db.fetch_raw_resources_by_type(db)
        logger.info(
            "transform: fetched raw resources in %.3fs — %s",
            time.perf_counter() - t,
            {k: len(v) for k, v in grouped.items()},
        )
        if not grouped:
            logger.warning("transform: no raw resources to transform")
            s.update(label="No raw resources found.", state="error")
            status_placeholder.warning(
                "No raw resources found. Click **Load Sample FHIR Bundles** first."
            )
            return

        s.write(f"Read {sum(len(v) for v in grouped.values())} raw resource(s) "
                f"across {len(grouped)} resource type(s).")

        # Persons first so downstream resources can resolve person_id
        s.update(label="Inserting persons...")
        t = time.perf_counter()
        person_rows = [transformers.transform_patient(p) for p in grouped.get("Patient", [])]
        person_lookup = demo_db.insert_persons(db, person_rows)
        logger.info(
            "transform: inserted %d person(s) in %.3fs",
            len(person_lookup), time.perf_counter() - t,
        )
        s.write(f"Inserted **{len(person_lookup)}** person(s).")

        def _transform_many(resources, fn):
            return [row for row in (fn(r, person_lookup) for r in resources) if row is not None]

        s.update(label="Transforming clinical events...")
        visits     = _transform_many(grouped.get("Encounter", []),         transformers.transform_encounter)
        conditions = _transform_many(grouped.get("Condition", []),         transformers.transform_condition)
        measures   = _transform_many(grouped.get("Observation", []),       transformers.transform_observation)
        drugs      = _transform_many(grouped.get("MedicationRequest", []), transformers.transform_medication_request)
        logger.info(
            "transform: built rows — visits=%d, conditions=%d, measures=%d, drugs=%d",
            len(visits), len(conditions), len(measures), len(drugs),
        )

        s.update(label="Writing clinical events to Supabase...")
        t = time.perf_counter()
        n_v = demo_db.insert_visits(db, visits)
        n_c = demo_db.insert_conditions(db, conditions)
        n_m = demo_db.insert_measurements(db, measures)
        n_d = demo_db.insert_drug_exposures(db, drugs)
        logger.info(
            "transform: inserted v=%d c=%d m=%d d=%d in %.3fs",
            n_v, n_c, n_m, n_d, time.perf_counter() - t,
        )
        s.write(f"Inserted **{n_v}** visits, **{n_c}** conditions, "
                f"**{n_m}** measurements, **{n_d}** drug exposures.")

        s.update(label="Writing code mapping report...")
        t = time.perf_counter()
        mapping_rows = transformers.build_mapping_report_rows(grouped)
        demo_db.insert_mapping_reports(db, mapping_rows)
        logger.info(
            "transform: inserted %d mapping report row(s) in %.3fs",
            len(mapping_rows), time.perf_counter() - t,
        )
        s.write(f"Inserted **{len(mapping_rows)}** mapping report row(s).")

        elapsed = time.perf_counter() - t0
        s.update(label=f"Transformation complete ({elapsed:.2f}s).", state="complete")
        logger.info("transform: end-to-end %.3fs", elapsed)
        status_placeholder.success(
            f"Transformation complete — {len(person_lookup)} persons, "
            f"{n_v} visits, {n_c} conditions, {n_m} measurements, "
            f"{n_d} drug exposures, {len(mapping_rows)} mapping rows."
        )


if reset_clicked:
    try:
        _run_reset()
    except Exception as e:
        logger.exception("Reset failed")
        status_placeholder.error(f"Reset failed: {e}")

if load_clicked:
    try:
        _run_sample_load()
    except Exception as e:
        logger.exception("Load failed")
        status_placeholder.error(f"Load failed: {e}")

if transform_clicked:
    try:
        _run_transform()
    except Exception as e:
        logger.exception("Transform failed")
        status_placeholder.error(f"Transform failed: {e}")

# ---------------------------------------------------------------------------
# Upload-your-own bundles (alternative to the sample data above).
# ---------------------------------------------------------------------------
with st.expander("📤 Or upload your own FHIR Bundle JSON files", expanded=False):
    st.caption(
        "Each file must be a FHIR R4 Bundle (JSON) with an `entry` array. "
        "Resources of types Patient, Encounter, Condition, Observation, and "
        "MedicationRequest are picked up by the transformer; everything else "
        "is still landed in the raw table but ignored downstream."
    )
    uploaded_files = st.file_uploader(
        "Drop one or more FHIR Bundle JSON files here",
        type=["json"],
        accept_multiple_files=True,
        key="fhir_upload",
    )
    if st.button("📥 Load Uploaded Bundles", width="content", disabled=not uploaded_files):
        try:
            _run_uploaded_load(uploaded_files)
        except Exception as e:
            logger.exception("Upload load failed")
            status_placeholder.error(f"Upload load failed: {e}")

st.divider()

# ---------------------------------------------------------------------------
# Metric cards
# ---------------------------------------------------------------------------
try:
    counts = analytics.get_summary_counts(db)
    mapping_rate = analytics.get_mapping_success_rate(db)
except Exception as e:
    counts = {"raw_resources": 0, "patients": 0, "encounters": 0,
              "conditions": 0, "measurements": 0, "drug_exposures": 0}
    mapping_rate = None
    st.warning(
        f"Could not load metrics from the database — "
        f"have you run `database/fhir_omop_sql/001_create_tables.sql`? ({e})"
    )

# Pipeline-stage banner: keeps the row of metric cards from looking like a
# bug when raw data is loaded but the transformation hasn't run yet.
omop_total = (
    counts["patients"] + counts["encounters"] + counts["conditions"]
    + counts["measurements"] + counts["drug_exposures"]
)
if counts["raw_resources"] > 0 and omop_total == 0:
    st.info(
        f"📥 **{counts['raw_resources']} raw FHIR resource(s) loaded** — "
        f"click **Run Transformation Pipeline** above to populate the "
        f"OMOP-inspired tables and the metrics below."
    )
elif counts["raw_resources"] > 0:
    st.caption(f"🗂️ {counts['raw_resources']} raw FHIR resource(s) currently in the landing zone.")

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Patients",              counts["patients"])
m2.metric("Encounters",            counts["encounters"])
m3.metric("Conditions",            counts["conditions"])
m4.metric("Measurements",          counts["measurements"])
m5.metric("Drug Exposures",        counts["drug_exposures"])
m6.metric("Mapping Success Rate",  f"{mapping_rate}%" if mapping_rate is not None else "—")

st.divider()

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab_raw, tab_omop, tab_mapping, tab_analytics, tab_arch = st.tabs([
    "📄 Raw FHIR Resources",
    "🗄️ OMOP-Inspired Tables",
    "🔗 Code Mapping Report",
    "📊 Analytics Dashboard",
    "🏗️ Architecture Notes",
])

# ----- Raw FHIR Resources --------------------------------------------------
with tab_raw:
    st.markdown("#### Raw FHIR resources (as stored in `fhir_demo_raw_fhir_resource`)")
    try:
        raw = demo_db.fetch_raw_resources_by_type(db)
    except Exception as e:
        raw = {}
        st.error(f"Could not read raw resources: {e}")
    if not raw:
        st.info("No raw resources loaded yet. Click **Load Sample FHIR Bundles** above.")
    else:
        for rtype in sorted(raw.keys()):
            with st.expander(f"{rtype} — {len(raw[rtype])} resource(s)", expanded=False):
                for i, resource in enumerate(raw[rtype], start=1):
                    st.caption(f"{rtype} #{i} — id: {resource.get('id', '(no id)')}")
                    st.json(resource, expanded=False)

# ----- OMOP-Inspired Tables ------------------------------------------------
with tab_omop:
    st.markdown("#### OMOP-inspired tables (Supabase / Postgres)")
    st.caption(
        "These tables are intentionally a simplified slice of the real OMOP CDM. "
        "Concept-id resolution, vocabulary tables, and a great deal of nuance have been omitted."
    )
    for table in [
        "fhir_demo_person",
        "fhir_demo_visit_occurrence",
        "fhir_demo_condition_occurrence",
        "fhir_demo_measurement",
        "fhir_demo_drug_exposure",
    ]:
        st.markdown(f"**`{table}`**")
        try:
            df = demo_db.fetch_table_dataframe(db, table)
            if df.empty:
                st.info("(empty)")
            else:
                st.dataframe(df, width="stretch", hide_index=True)
        except Exception as e:
            st.error(f"Could not load {table}: {e}")

# ----- Code Mapping Report -------------------------------------------------
with tab_mapping:
    st.markdown("#### Terminology mapping report")
    st.markdown(
        """
        Real OMOP ETL maps every source code to a canonical *concept_id* using
        the OHDSI vocabulary tables (SNOMED CT, LOINC, RxNorm, ICD-10-CM, …).
        For this demo we run a much simpler check: **is the FHIR resource
        using one of the recognized standard coding systems?**

        | Standard | System URI |
        | --- | --- |
        | SNOMED CT          | `http://snomed.info/sct` |
        | LOINC              | `http://loinc.org` |
        | RxNorm             | `http://www.nlm.nih.gov/research/umls/rxnorm` |
        | ICD-10 / ICD-10-CM | `http://hl7.org/fhir/sid/icd-10[-cm]` |

        Resources with no coding system, or with a non-standard system, are
        flagged so they can be reviewed downstream.
        """
    )
    try:
        report = analytics.get_mapping_report(db)
        if report.empty:
            st.info("Run the transformation pipeline to generate a mapping report.")
        else:
            st.dataframe(report, width="stretch", hide_index=True)
    except Exception as e:
        st.error(f"Could not load mapping report: {e}")

# ----- Analytics Dashboard -------------------------------------------------
with tab_analytics:
    st.markdown("#### Analytics dashboard")
    a_col1, a_col2 = st.columns(2)

    with a_col1:
        st.markdown("**Conditions by frequency**")
        try:
            df = analytics.get_conditions_by_frequency(db)
            if df.empty:
                st.info("No conditions yet.")
            else:
                st.bar_chart(df.set_index("condition")["occurrences"])
        except Exception as e:
            st.error(str(e))

        st.markdown("**Encounters by visit type**")
        try:
            df = analytics.get_encounter_counts_by_type(db)
            if df.empty:
                st.info("No encounters yet.")
            else:
                st.bar_chart(df.set_index("visit_type")["encounters"])
        except Exception as e:
            st.error(str(e))

    with a_col2:
        st.markdown("**Measurements over time**")
        try:
            df = analytics.get_measurements_over_time(db)
            if df.empty:
                st.info("No measurements yet.")
            else:
                st.line_chart(df.set_index("date")["measurements"])
        except Exception as e:
            st.error(str(e))

        st.markdown("**Drug exposures by display name**")
        try:
            df = analytics.get_drug_counts(db)
            if df.empty:
                st.info("No drug exposures yet.")
            else:
                st.bar_chart(df.set_index("drug")["prescriptions"])
        except Exception as e:
            st.error(str(e))

# ----- Architecture Notes --------------------------------------------------
with tab_arch:
    st.markdown("#### Architecture notes")
    st.markdown(
        """
        **FHIR (Fast Healthcare Interoperability Resources).**
        HL7's modern web-friendly standard for exchanging clinical data. Each
        clinical fact — a patient, an encounter, a diagnosis, a lab result —
        is a typed JSON *resource* that references other resources by id.
        R4 is the current widely-adopted release.

        **OMOP CDM (Common Data Model).**
        OHDSI's columnar relational model designed for population-level
        analytics across institutions. Source codes from any vocabulary get
        normalized to a standard `concept_id`, and clinical events live in a
        small set of canonical tables (`person`, `visit_occurrence`,
        `condition_occurrence`, `measurement`, `drug_exposure`, …). This demo
        mirrors that *shape* with `fhir_demo_*` tables — without the
        concept-id resolution that real OMOP ETL performs.

        **ETL pipeline used here.**
        1. *Extract.* Read FHIR Bundle JSON from `projects/fhir_omop/sample_data/`.
        2. *Land.* Persist every resource as JSONB in
           `fhir_demo_raw_fhir_resource`, tagged to a row in
           `fhir_demo_ingestion_run`. This is the typical "schema-on-read"
           landing zone in healthcare ETL.
        3. *Transform.* Map FHIR fields → simplified OMOP-style columns.
           Patient ids are reconciled to internal `person_id`s; FHIR
           references are resolved client-side.
        4. *Report.* For every coded resource, emit a row into
           `fhir_demo_code_mapping_report` indicating whether the source
           coding system was a recognized standard vocabulary.

        **Terminology mapping.**
        SNOMED CT covers diagnoses and clinical findings; LOINC covers
        observations and lab tests; RxNorm covers medications; ICD-10-CM is
        used for billing. Real OMOP ETL invests heavily in resolving these
        to `concept_id`s — this demo only flags presence vs. absence.

        **Why synthetic data.**
        All bundles are hand-authored to resemble Synthea output. No real
        patient data is involved. The intent is to demonstrate familiarity
        with the *shape* of FHIR R4 and OMOP-style workflows.

        **Why this project exists.**
        It's a portfolio familiarity demo — to show that the patterns of
        healthcare interoperability (resource-oriented JSON, terminology
        mapping, OMOP-style flattening, raw-then-curated ETL) are well
        understood, and deployable on the existing Streamlit + Supabase +
        Fly.io stack with no extra services or backends.
        """
    )
