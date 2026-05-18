"""FHIR-to-OMOP clinical data pipeline demo page.

A simplified healthcare interoperability demo. The page is a thin HTTP
client over the FHIR-OMOP backend service. All database I/O — ingestion,
transformation, analytics queries — happens in the backend. This page
renders the result and provides the three action buttons (reset, load,
transform).

Why a backend
-------------
The previous version did DB work in-process. Holding a Supabase connection
inside the Streamlit websocket made the page hang to a blank white screen
whenever a handshake stalled. Moving the work behind an HTTP boundary lets
the backend bound those failures (connect_timeout + retry) and surface
them as actionable errors instead of a dead page.
"""
import json
import logging
import time
from typing import Dict, List

import pandas as pd
import streamlit as st

import nav
from app import home_page
from projects.fhir_omop.pipeline import terminology
from projects.fhir_omop.pipeline.api_client import (
    ApiError,
    ApiNotConfiguredError,
    FhirOmopApiClient,
)

logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="FHIR → OMOP Demo",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

nav.config_navigation(home_page)


# Friendly category labels used wherever the page would otherwise expose
# internal storage names. Keeps the UI vendor-neutral and avoids leaking the
# physical schema.
_TABLE_LABELS: Dict[str, str] = {
    "fhir_demo_person":              "Patients",
    "fhir_demo_visit_occurrence":    "Visits",
    "fhir_demo_condition_occurrence": "Conditions",
    "fhir_demo_measurement":         "Measurements",
    "fhir_demo_drug_exposure":       "Drug Exposures",
    "fhir_demo_code_mapping_report": "Code Mapping Report",
    "fhir_demo_raw_fhir_resource":   "Raw FHIR Landing Zone",
}


def _label_for(table_name: str) -> str:
    return _TABLE_LABELS.get(table_name, table_name)


@st.cache_resource
def get_client() -> FhirOmopApiClient:
    return FhirOmopApiClient()


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("🧬 FHIR-to-OMOP Clinical Data Pipeline")

st.markdown(
    """
    ### Healthcare Interoperability: Raw FHIR → Curated Analytics Schema

    A healthcare data pipeline that ingests synthetic **FHIR R4** patient
    bundles, transforms them into an **OMOP-inspired analytics schema**, and
    surfaces the result as interactive tables and charts. This page
    demonstrates familiarity with healthcare interoperability concepts —
    not production clinical compliance or certified OMOP CDM use.
    """
)

with st.expander("🎯 What This Demonstrates", expanded=False):
    st.markdown(
        """
        - **FHIR R4 ingestion** — reading Bundle JSON resembling Synthea output
        - **Standard terminology awareness** — SNOMED CT, LOINC, RxNorm, ICD-10
        - **OMOP-inspired modeling** — Patients, Visits, Conditions,
          Measurements, and Drug Exposures flattened from FHIR resources
        - **ETL pipeline shape** — raw landing zone → transform step →
          analytics queries, each stage observable in the UI
        - **Service-oriented architecture** — a thin front-end calling a
          dedicated backend service, with idempotent writes and bounded
          failure modes
        - **Code-mapping reporting** — a "mapped vs. unmapped" check that
          illustrates where real concept-id resolution would live in a
          production pipeline
        """
    )

with st.expander("🔧 Pipeline Architecture", expanded=False):
    st.markdown(
        """
        **Stages:**
        1. Synthetic FHIR R4 Bundle JSON (hand-authored, resembling Synthea output)
        2. Raw landing zone — every resource persisted as JSONB
        3. Transformation — FHIR resources flattened into OMOP-style columns
        4. Code mapping report — classifies each coded resource against
           recognized standard vocabularies
        5. Analytics — frequency and time-series queries powering the charts

        **Implementation notes:**
        - PostgreSQL holds both the raw landing zone and the curated schema
        - A dedicated backend service owns all database I/O
        - Writes happen in a single transaction per pipeline step
        - Idempotency keys de-duplicate retried calls so transient network
          blips don't corrupt the ingestion run
        """
    )

with st.expander("💡 Try It Out", expanded=False):
    st.markdown(
        """
        **Three buttons, in order:**
        1. 🧹 **Reset Demo Data** — clears the previous run's results
        2. 📥 **Load Sample FHIR Bundles** — ingests three hand-authored
           patient bundles into the raw landing zone
        3. ⚙️ **Run Transformation Pipeline** — flattens raw FHIR resources
           into the analytics tables and generates the code-mapping report

        **Then explore the tabs below:**
        - **Raw FHIR Resources** — every JSON resource as it was received
        - **Clinical Terminology Explorer** — every coded concept, its source
          vocabulary, and how it maps into the analytics schema
        - **OMOP-Inspired Tables** — the flattened relational view used for
          analytics
        - **Code Mapping Report** — which codings were recognized vs. flagged
        - **Analytics Dashboard** — frequency and time-series views over the
          curated data

        Or use the **upload** expander further down to drop your own FHIR
        Bundle JSON files into the same pipeline.
        """
    )

# ---------------------------------------------------------------------------
# Client init (with config banner on failure)
# ---------------------------------------------------------------------------
try:
    client = get_client()
except ApiNotConfiguredError:
    st.error(
        "⚙️ This page is currently unavailable — the data pipeline behind it "
        "is not reachable. Please check back later, or contact the site "
        "maintainer."
    )
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


def _retry_notice(status_ui, op_label: str):
    """Return an on_retry callback that surfaces the retry in st.status."""
    def on_retry(err: Exception) -> None:
        status_ui.write(f"⚠️ {op_label} failed ({err}). Retrying in 2s...")
        status_ui.update(label=f"{op_label} — retrying after transient error")
    return on_retry


def _run_reset() -> None:
    logger.info("reset: user clicked Reset Demo Data")
    t0 = time.perf_counter()
    with st.status("Resetting demo data...", expanded=False) as s:
        client.reset(on_retry=_retry_notice(s, "Reset"))
        s.update(
            label=f"Demo data cleared ({time.perf_counter() - t0:.2f}s)",
            state="complete",
        )
    logger.info("reset: complete (%.3fs)", time.perf_counter() - t0)
    status_placeholder.success("Demo data cleared.")


def _run_sample_load() -> None:
    logger.info("sample_load: user clicked Load Sample FHIR Bundles")
    t0 = time.perf_counter()
    idem = client.new_idempotency_key()
    with st.status("Loading sample FHIR bundles...", expanded=True) as s:
        s.update(label="Ingesting sample bundles into the raw landing zone...")
        result = client.ingest_sample(idem_key=idem, on_retry=_retry_notice(s, "Sample load"))
        raw_count = result.get("raw_count", 0)
        bundle_count = result.get("bundle_count", 0)
        run_id = result.get("run_id")
        server_elapsed = result.get("elapsed_ms", 0) / 1000.0
        s.write(
            f"Ingested **{raw_count}** resource(s) from **{bundle_count}** "
            f"bundle(s) under run **#{run_id}** ({server_elapsed:.2f}s)."
        )
        s.update(
            label=f"Sample load complete ({time.perf_counter() - t0:.2f}s).",
            state="complete",
        )
    logger.info("sample_load: end-to-end %.3fs", time.perf_counter() - t0)
    status_placeholder.success(
        f"Loaded {raw_count} resource(s) from {bundle_count} bundle(s) — run #{run_id}."
    )


def _run_uploaded_load(uploaded_files) -> None:
    if not uploaded_files:
        status_placeholder.warning("No files selected.")
        return
    logger.info(
        "upload_load: user clicked Load Uploaded Bundles — %d file(s) selected",
        len(uploaded_files),
    )
    t0 = time.perf_counter()
    with st.status(f"Parsing {len(uploaded_files)} uploaded file(s)...", expanded=True) as s:
        bundles: List[dict] = []
        bad: List[str] = []
        for uf in uploaded_files:
            try:
                payload = uf.getvalue()
                bundle = json.loads(payload.decode("utf-8"))
                bundles.append(bundle)
                s.write(
                    f"Parsed `{uf.name}` — {len(payload):,} bytes, "
                    f"{len(bundle.get('entry', []) or [])} entries"
                )
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                bad.append(f"{uf.name}: {e}")
        if bad:
            s.update(label="Some uploads could not be parsed as JSON.", state="error")
            status_placeholder.error(
                "Some uploads could not be parsed as JSON:\n- " + "\n- ".join(bad)
            )
            return

        idem = client.new_idempotency_key()
        s.update(label=f"Ingesting {len(bundles)} bundle(s) into the raw landing zone...")
        result = client.ingest(
            bundles=bundles,
            source_label="Loaded uploaded bundles",
            idem_key=idem,
            on_retry=_retry_notice(s, "Upload"),
        )
        raw_count = result.get("raw_count", 0)
        run_id = result.get("run_id")
        s.write(
            f"Ingested **{raw_count}** raw resource(s) under run **#{run_id}**."
        )
        s.update(
            label=f"Upload load complete ({time.perf_counter() - t0:.2f}s).",
            state="complete",
        )
    logger.info("upload_load: end-to-end %.3fs", time.perf_counter() - t0)
    status_placeholder.success(
        f"Uploaded — {len(bundles)} bundle(s), {raw_count} raw resources (run #{run_id})."
    )


def _run_transform() -> None:
    logger.info("transform: user clicked Run Transformation Pipeline")
    t0 = time.perf_counter()
    idem = client.new_idempotency_key()
    with st.status("Running transformation pipeline...", expanded=True) as s:
        s.update(label="Flattening FHIR resources into the analytics schema...")
        result = client.transform(idem_key=idem, on_retry=_retry_notice(s, "Transform"))
        counts = result.get("counts", {})
        server_elapsed = result.get("elapsed_ms", 0) / 1000.0
        s.write(
            f"Inserted **{counts.get('persons', 0)}** patients, "
            f"**{counts.get('visits', 0)}** visits, "
            f"**{counts.get('conditions', 0)}** conditions, "
            f"**{counts.get('measurements', 0)}** measurements, "
            f"**{counts.get('drug_exposures', 0)}** drug exposures, "
            f"**{counts.get('mapping_report', 0)}** mapping report row(s) "
            f"({server_elapsed:.2f}s)."
        )
        s.update(
            label=f"Transformation complete ({time.perf_counter() - t0:.2f}s).",
            state="complete",
        )
    logger.info("transform: end-to-end %.3fs", time.perf_counter() - t0)
    status_placeholder.success(
        f"Transformation complete — {counts.get('persons', 0)} patients, "
        f"{counts.get('visits', 0)} visits, {counts.get('conditions', 0)} conditions, "
        f"{counts.get('measurements', 0)} measurements, "
        f"{counts.get('drug_exposures', 0)} drug exposures, "
        f"{counts.get('mapping_report', 0)} mapping rows."
    )


if reset_clicked:
    try:
        _run_reset()
    except ApiError as e:
        logger.exception("Reset failed")
        status_placeholder.error(f"Reset failed: {e}")

if load_clicked:
    try:
        _run_sample_load()
    except ApiError as e:
        logger.exception("Sample load failed")
        status_placeholder.error(f"Sample load failed: {e}")

if transform_clicked:
    try:
        _run_transform()
    except ApiError as e:
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
        except ApiError as e:
            logger.exception("Upload load failed")
            status_placeholder.error(f"Upload load failed: {e}")

st.divider()

# ---------------------------------------------------------------------------
# Dashboard fetch — ONE call to /dashboard renders everything below.
# ---------------------------------------------------------------------------
# Collapsing the previous ~17 separate DB connections (per page rerun) into
# a single HTTP request is the actual win of moving to a backend. If this
# call fails after the client's internal retry, the page renders an error
# banner and stops; individual tabs don't make their own backend calls.
with st.spinner("Loading dashboard..."):
    try:
        dashboard = client.dashboard()
    except ApiError:
        st.error(
            "Could not load dashboard data. The pipeline may be temporarily "
            "unavailable — please try again in a moment."
        )
        st.stop()

# ---------------------------------------------------------------------------
# Metric cards
# ---------------------------------------------------------------------------
counts: Dict[str, int] = dashboard.get("summary", {}) or {}
mapping_rate = dashboard.get("mapping_success_rate")

omop_total = sum(
    counts.get(k, 0)
    for k in ("patients", "encounters", "conditions", "measurements", "drug_exposures")
)
if counts.get("raw_resources", 0) > 0 and omop_total == 0:
    st.info(
        f"📥 **{counts.get('raw_resources', 0)} raw FHIR resource(s) loaded** — "
        f"click **Run Transformation Pipeline** above to populate the "
        f"OMOP-inspired tables and the metrics below."
    )
elif counts.get("raw_resources", 0) > 0:
    st.caption(
        f"🗂️ {counts.get('raw_resources', 0)} raw FHIR resource(s) currently "
        f"in the landing zone."
    )

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Patients",              counts.get("patients", 0))
m2.metric("Encounters",            counts.get("encounters", 0))
m3.metric("Conditions",            counts.get("conditions", 0))
m4.metric("Measurements",          counts.get("measurements", 0))
m5.metric("Drug Exposures",        counts.get("drug_exposures", 0))
m6.metric("Mapping Success Rate",  f"{mapping_rate}%" if mapping_rate is not None else "—")

st.divider()

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab_raw, tab_term, tab_omop, tab_mapping, tab_analytics, tab_arch = st.tabs([
    "📄 Raw FHIR Resources",
    "🧠 Clinical Terminology Explorer",
    "🗄️ OMOP-Inspired Tables",
    "🔗 Code Mapping Report",
    "📊 Analytics Dashboard",
    "🏗️ Architecture Notes",
])

# ----- Raw FHIR Resources --------------------------------------------------
with tab_raw:
    st.markdown("#### Raw FHIR resources (as received from the source)")
    raw: Dict[str, List[dict]] = dashboard.get("raw_resources_by_type", {}) or {}
    if not raw:
        st.info("No raw resources loaded yet. Click **Load Sample FHIR Bundles** above.")
    else:
        for rtype in sorted(raw.keys()):
            with st.expander(f"{rtype} — {len(raw[rtype])} resource(s)", expanded=False):
                for i, resource in enumerate(raw[rtype], start=1):
                    st.caption(f"{rtype} #{i} — id: {resource.get('id', '(no id)')}")
                    st.json(resource, expanded=False)

# ----- Clinical Terminology Explorer ---------------------------------------
with tab_term:
    st.markdown("#### Clinical Terminology Explorer")
    st.markdown(
        """
        FHIR defines the **structure** of exchanged healthcare data; clinical
        terminologies define the **meaning** of the coded concepts inside it.
        This view extracts every coding from the raw FHIR resources currently
        loaded and shows how common standards — LOINC, SNOMED CT, ICD-10 /
        ICD-10-CM, and RxNorm — map into the OMOP-inspired target tables.
        """
    )

    raw_grouped: Dict[str, List[dict]] = dashboard.get("raw_resources_by_type", {}) or {}
    all_raw = [r for rs in raw_grouped.values() for r in rs]
    term_rows = terminology.build_terminology_rows(all_raw)

    if not term_rows:
        st.info(
            "No coded resources loaded yet. Click **Load Sample FHIR Bundles** "
            "(or upload your own bundles) above to populate this view."
        )
    else:
        summary = terminology.summarize_terminology_rows(term_rows)
        t1, t2, t3, t4, t5 = st.columns(5)
        t1.metric("Total coded concepts",      summary["total_codings"])
        t2.metric("Known terminology systems", summary["known_systems"])
        t3.metric("Mapped demo codes",         summary["mapped"])
        t4.metric("Unsupported systems",       summary["unsupported"])
        t5.metric("Missing / unknown codes",   summary["missing_or_unknown"])

        df = pd.DataFrame(term_rows)
        all_systems   = sorted(df["terminology_name"].dropna().unique().tolist())
        all_resources = sorted(df["resource_type"].dropna().unique().tolist())

        f1, f2, f3, f4 = st.columns([1.2, 1.2, 1.2, 2])
        with f1:
            sel_systems = st.multiselect(
                "Terminology system", all_systems, default=all_systems,
                key="term_sys_filter",
            )
        with f2:
            sel_resources = st.multiselect(
                "Resource type", all_resources, default=all_resources,
                key="term_res_filter",
            )
        with f3:
            sel_status = st.selectbox(
                "Mapping status",
                ["All", "Mapped only", "Unmapped only"],
                key="term_status_filter",
            )
        with f4:
            text_q = st.text_input(
                "Search code or display", "",
                placeholder="e.g. 4548-4 or hypertension",
                key="term_search",
            )

        filtered = df[
            df["terminology_name"].isin(sel_systems)
            & df["resource_type"].isin(sel_resources)
        ]
        if sel_status == "Mapped only":
            filtered = filtered[filtered["mapped_successfully"] == True]  # noqa: E712
        elif sel_status == "Unmapped only":
            filtered = filtered[filtered["mapped_successfully"] == False]  # noqa: E712
        if text_q:
            q = text_q.strip().lower()
            filtered = filtered[
                filtered["code"].astype(str).str.lower().str.contains(q, na=False)
                | filtered["display"].astype(str).str.lower().str.contains(q, na=False)
            ]

        st.caption(f"Showing **{len(filtered)}** of {len(df)} coding(s).")

        display_df = filtered.copy()
        display_df["target_table"] = display_df["target_table"].map(_label_for)
        display_df = display_df.rename(columns={
            "resource_type":       "Resource Type",
            "terminology_name":    "System",
            "code":                "Code",
            "display":             "Display",
            "terminology_category": "Category",
            "target_table":        "Maps To",
            "mapped_successfully": "Mapped?",
            "analytics_use":       "Analytics Use",
        })[
            ["Resource Type", "System", "Code", "Display",
             "Category", "Maps To", "Mapped?", "Analytics Use"]
        ]
        st.dataframe(display_df, width="stretch", hide_index=True)

        st.markdown("##### Selected code details")
        if filtered.empty:
            st.info("No codings match the current filters.")
        else:
            options = [
                f"{r['resource_type']} · {r['terminology_name']} · {r['code']} "
                f"— {r['display'] or '(no display)'}"
                for _, r in filtered.iterrows()
            ]
            picked = st.selectbox("Pick a coding to explain", options, key="term_pick")
            picked_row = filtered.iloc[options.index(picked)]
            st.markdown(
                f"""
**FHIR {picked_row['resource_type']}** *(id: `{picked_row.get('resource_id') or '—'}`)*
&nbsp;&nbsp;↓
**{picked_row['terminology_name']}** `{picked_row['code']}` — {picked_row['display'] or '(no display)'}
&nbsp;&nbsp;↓
Maps to **{_label_for(picked_row['target_table'])}**
&nbsp;&nbsp;↓
Used for *{picked_row['analytics_use'].lower()}*

> {picked_row['explanation']}
                """
            )

    st.divider()

    st.markdown("##### Terminology reference cards")
    st.caption(
        "Quick orientation to the standards this demo recognizes. Real ETL "
        "would resolve every coding through these vocabularies' full content."
    )

    def _term_card(label: str, info: Dict[str, str]) -> None:
        with st.expander(label, expanded=False):
            st.markdown(f"**What it is.** {info.get('what_it_is', '—')}")
            st.markdown(f"**Category.** {info.get('category', '—')}")
            st.markdown(f"**Where in FHIR.** `{info.get('where_in_fhir', '—')}`")
            st.markdown(f"**This demo's use.** {info.get('demo_usage', '—')}")
            st.markdown(f"**Maps to.** {_label_for(info.get('target_table', '—'))}")

    _term_card("🧪 LOINC",
               terminology.TERMINOLOGY_SYSTEMS["http://loinc.org"])
    _term_card("🩺 SNOMED CT",
               terminology.TERMINOLOGY_SYSTEMS["http://snomed.info/sct"])
    _term_card("📋 ICD-10-CM",
               terminology.TERMINOLOGY_SYSTEMS["http://hl7.org/fhir/sid/icd-10-cm"])
    _term_card("💊 RxNorm",
               terminology.TERMINOLOGY_SYSTEMS["http://www.nlm.nih.gov/research/umls/rxnorm"])
    _term_card("📚 MeSH (educational reference)", terminology.MESH_INFO)

    st.divider()
    st.info(
        "ℹ️ **Limitations.** This demo uses a **curated subset** of terminology "
        "mappings for educational purposes. Production clinical systems use full "
        "vocabulary tables (OHDSI Athena / UMLS / NLM RxNorm files), licensed "
        "terminology distributions, or terminology servers (HL7 TS, SNOMED "
        "Snowstorm, LOINC FHIR endpoints). This project is intended to "
        "demonstrate familiarity with terminology normalization concepts, "
        "not production-grade vocabulary coverage."
    )

# ----- OMOP-Inspired Tables ------------------------------------------------
with tab_omop:
    st.markdown("#### OMOP-inspired analytics schema")
    st.caption(
        "These categories are intentionally a simplified slice of the real OMOP CDM. "
        "Concept-id resolution, vocabulary tables, and a great deal of nuance have been omitted."
    )
    omop_tables: Dict[str, List[dict]] = dashboard.get("omop_tables", {}) or {}
    for table in [
        "fhir_demo_person",
        "fhir_demo_visit_occurrence",
        "fhir_demo_condition_occurrence",
        "fhir_demo_measurement",
        "fhir_demo_drug_exposure",
    ]:
        st.markdown(f"**{_label_for(table)}**")
        rows = omop_tables.get(table, [])
        if not rows:
            st.info("(empty)")
        else:
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

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
    report_rows: List[dict] = dashboard.get("mapping_report", []) or []
    if not report_rows:
        st.info("Run the transformation pipeline to generate a mapping report.")
    else:
        st.dataframe(pd.DataFrame(report_rows), width="stretch", hide_index=True)

# ----- Analytics Dashboard -------------------------------------------------
with tab_analytics:
    st.markdown("#### Analytics dashboard")
    analytics_payload: Dict[str, List[dict]] = dashboard.get("analytics", {}) or {}
    a_col1, a_col2 = st.columns(2)

    with a_col1:
        st.markdown("**Conditions by frequency**")
        rows = analytics_payload.get("conditions_by_frequency", []) or []
        if not rows:
            st.info("No conditions yet.")
        else:
            df = pd.DataFrame(rows)
            st.bar_chart(df.set_index("condition")["occurrences"])

        st.markdown("**Encounters by visit type**")
        rows = analytics_payload.get("encounters_by_type", []) or []
        if not rows:
            st.info("No encounters yet.")
        else:
            df = pd.DataFrame(rows)
            st.bar_chart(df.set_index("visit_type")["encounters"])

    with a_col2:
        st.markdown("**Measurements over time**")
        rows = analytics_payload.get("measurements_over_time", []) or []
        if not rows:
            st.info("No measurements yet.")
        else:
            df = pd.DataFrame(rows)
            st.line_chart(df.set_index("date")["measurements"])

        st.markdown("**Drug exposures by display name**")
        rows = analytics_payload.get("drug_counts", []) or []
        if not rows:
            st.info("No drug exposures yet.")
        else:
            df = pd.DataFrame(rows)
            st.bar_chart(df.set_index("drug")["prescriptions"])

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
        normalized to a standard *concept_id*, and clinical events live in a
        small set of canonical categories (Patients, Visits, Conditions,
        Measurements, Drug Exposures, …). This demo mirrors that *shape* —
        without the concept-id resolution that real OMOP ETL performs.

        **Service split.**

        ```
        Browser
           │
           ▼
        Streamlit front-end ── one dashboard fetch per page render
           │                   action buttons post to the backend
           ▼
        Backend service ── single-transaction writes
           │                connection retry + idempotency keys
           ▼
        PostgreSQL database (raw landing + curated analytics schema)
        ```

        The page is a thin HTTP client; the backend owns all database I/O.
        That lets the backend bound failures (connection timeouts + retries)
        and surface them as actionable errors instead of blank pages. Writes
        carry idempotency keys so transient retries don't duplicate data.

        **ETL pipeline used here.**

        ```
        FHIR Bundle JSON
              ↓
        Resource Extraction      (parse + group by resourceType)
              ↓
        Terminology Extraction   (pull codings per resource)
              ↓
        Simplified Code Mapping  (classify against recognized vocabularies)
              ↓
        OMOP-Inspired Schema     (Patients, Visits, Conditions, ...)
              ↓
        Analytics Dashboard      (frequency + time-series queries)
        ```

        1. *Extract.* Read FHIR Bundle JSON from synthetic samples or from
           uploaded files.
        2. *Land.* Persist every resource as JSON in the raw landing zone,
           tagged to a single ingestion run, in one transaction.
        3. *Extract terminology.* The Clinical Terminology Explorer tab
           computes its rows **client-side** from the raw resources, so the
           filter controls don't cause back-end round-trips.
        4. *Transform.* Map FHIR fields into simplified OMOP-style columns.
           Patient ids are reconciled to internal ids inside the single
           transaction.
        5. *Report.* Emit one mapping-report row per coded resource with the
           classification status.

        **Terminology mapping.**
        SNOMED CT covers diagnoses and clinical findings; LOINC covers
        observations and lab tests; RxNorm covers medications; ICD-10-CM is
        used for diagnosis classification and billing; MeSH is included as an
        educational reference for biomedical literature indexing (not consumed
        by this pipeline). Real OMOP ETL invests heavily in resolving these
        to *concept_id*s through full vocabulary tables — this demo uses a
        curated subset of mappings to illustrate the *shape* of that work.

        **Why synthetic data.**
        All bundles are hand-authored to resemble Synthea output. No real
        patient data is involved. The intent is to demonstrate familiarity
        with the *shape* of FHIR R4 and OMOP-style workflows.

        **Why this project exists.**
        A portfolio familiarity demo — showing that the patterns of
        healthcare interoperability (resource-oriented JSON, terminology
        mapping, OMOP-style flattening, raw-then-curated ETL) are well
        understood, and deployable as a thin front-end backed by a dedicated
        service with idempotent writes and bounded failure modes.
        """
    )
