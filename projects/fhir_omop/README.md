# FHIR → OMOP Demo

A **simplified healthcare interoperability demo** that lives inside the
existing Streamlit portfolio app. It loads **synthetic FHIR R4** patient
bundles, transforms them into an **OMOP-inspired** relational schema in the
shared Supabase/Postgres database, and renders the result as metrics, tables,
charts, a code-mapping report, and a **Clinical Terminology Explorer**.

This is a **FHIR familiarity project** — not production OMOP CDM, not
certified interoperability, and not validated for clinical use.

This demo includes a **Clinical Terminology Explorer** that identifies common
terminology systems in FHIR resources, including **LOINC**, **SNOMED CT**,
**ICD-10-CM**, and **RxNorm**. It uses a **curated subset** of mappings to
show how coded clinical concepts flow into OMOP-inspired target tables.
**MeSH** is included as an educational reference for biomedical literature
indexing, but is not used directly in the transformation pipeline. No real
terminology server is integrated and no full vocabulary distribution is
downloaded — this is for portfolio illustration only.

## What this demonstrates

- Reading **FHIR R4 Bundle JSON** that resembles Synthea output, from both
  bundled sample data *and* user-uploaded files (multi-file
  `st.file_uploader`)
- A typical healthcare-ETL shape: **raw landing zone (JSONB) → transform →
  curated tables → analytics queries**, with each stage visible in the UI
- Awareness of the standard biomedical vocabularies: **SNOMED CT**,
  **LOINC**, **RxNorm**, **ICD-10 / ICD-10-CM**
- A simplified **terminology mapping report** that flags presence vs.
  absence of recognized coding systems (stand-in for real `concept_id`
  resolution)
- An **OMOP-inspired** relational layout — `person`, `visit_occurrence`,
  `condition_occurrence`, `measurement`, `drug_exposure` — implemented as
  plain `fhir_demo_*` tables in the existing public schema
- **Single-transaction ingest** — `pipeline/db.bulk_ingest_resources()`
  opens one Supabase connection and runs run-open + raw-insert + run-close
  in one transaction. The earlier three-round-trip pattern caused visible
  hangs on slow connections; one connection per click is dramatically more
  robust.
- **Step-by-step progress UX** — every long handler (`Reset`, `Load`,
  `Run Transformation Pipeline`) uses `st.status(..., expanded=True)` with
  per-step messages and `time.perf_counter()` timings, so the user can
  watch the pipeline run instead of staring at a blank spinner.
- **Pipeline-stage status banner** — when raw resources exist but the OMOP
  tables are empty, the page surfaces a hint to run the transformation
  step. Avoids the "I loaded data but everything is zero" papercut.
- **Structured logging at every step** — file discovery, bundle parsing,
  grouping, DB connect, run open/close, row counts, and per-step
  `perf_counter` elapsed are logged at INFO level. Useful for diagnosing
  network or Supabase slowness after the fact.
- **Clinical Terminology Explorer** — extracts every coding from the
  currently-loaded FHIR resources, classifies each `(system, code)` pair as
  *mapped* / *system-known-code-unknown* / *unsupported* / *missing*, and
  surfaces summary metrics, a filterable table, a per-code detail view, and
  educational reference cards for LOINC, SNOMED CT, ICD-10-CM, RxNorm, and
  MeSH. Powered by a curated mapping table in `pipeline/terminology.py` —
  no terminology server, no licensed downloads.

## Architecture

```
projects/fhir_omop/sample_data/*.json      ─┐
                                            │
projects/fhir_omop/pipeline/fhir_loader.py  │  extract
                                            ▼
                          fhir_demo_raw_fhir_resource (JSONB)   ◀── land
                                            │
projects/fhir_omop/pipeline/transformers.py │  transform
                                            ▼
       fhir_demo_person                                          ◀── curate
       fhir_demo_visit_occurrence
       fhir_demo_condition_occurrence
       fhir_demo_measurement
       fhir_demo_drug_exposure
       fhir_demo_code_mapping_report
                                            │
projects/fhir_omop/pipeline/analytics.py    │  query
                                            ▼
                        pages/fhir_omop_demo.py                  ◀── render
```

All persistence reuses the existing `database/db_manager.DatabaseManager` —
no new DB abstraction.

## Layout

```
projects/fhir_omop/
├── README.md                       # this file
├── sample_data/                    # synthetic FHIR R4 Bundle JSON files
│   ├── patient_001_smith.json      # hypertensive, SNOMED + LOINC + RxNorm
│   ├── patient_002_garcia.json     # T2D, glucose + A1c series
│   └── patient_003_chen.json       # CKD + hyperlipidemia, plus one local-code
│                                   # condition to demo the "unmapped" path
└── pipeline/
    ├── db.py                       # thin SQL helpers built on DatabaseManager,
    │                               # including bulk_ingest_resources() single-tx ingest
    ├── fhir_loader.py              # parse Bundle JSON, group resources by type
    │                               # (group_bundles_by_resource_type works on
    │                               # already-parsed bundles for the upload path)
    ├── terminology.py              # curated terminology metadata + demo code
    │                               # mappings; classify_coding() + build_terminology_rows()
    │                               # power both the explorer tab and the mapping report
    ├── transformers.py             # FHIR → OMOP-inspired row dicts + mapping report
    │                               # (delegates classification to terminology.py)
    └── analytics.py                # SQL behind the dashboard metrics/charts

database/fhir_omop_sql/
├── 001_create_tables.sql           # one-time DDL — run manually
└── 002_seed_reset.sql              # TRUNCATE + RESTART IDENTITY CASCADE

pages/fhir_omop_demo.py             # the Streamlit page registered in nav.py
```

## Technologies

- **Streamlit** — UI + page registration via `nav.config_navigation`
- **Python 3** — pipeline modules
- **pandas** — DataFrames for the dashboard charts/tables
- **psycopg2** — Postgres driver (reused from the rest of the app)
- **Supabase / PostgreSQL** — managed Postgres, shared with other portfolio
  features
- **Local JSON files** — synthetic FHIR Bundles in `sample_data/`

No new dependencies are introduced — everything required already ships in
`requirements.txt`.

## Demo workflow

1. **One-time setup** — run `database/fhir_omop_sql/001_create_tables.sql`
   against the database used by the rest of the app.
2. Open the **FHIR → OMOP** page in the Streamlit app.
3. Click **Reset Demo Data** — truncates every `fhir_demo_*` table.
4. Load raw data — either:
   - Click **Load Sample FHIR Bundles** to ingest the three bundled
     synthetic patients, or
   - Expand **📤 Or upload your own FHIR Bundle JSON files**, drop one or
     more FHIR R4 Bundles into the file uploader, and click
     **Load Uploaded Bundles**.

   Both paths funnel through the same `bulk_ingest_resources()` helper, so
   they produce the same audit trail (one `fhir_demo_ingestion_run` row per
   click) and the same status / logging surface.
5. The status banner above the metrics will tell you "*N raw resources
   loaded — click Run Transformation Pipeline*". Click it.
6. **Run Transformation Pipeline** reads the raw resources back out,
   populates the OMOP-inspired tables, and generates the mapping report.
7. Browse the tabs: raw resources, **Clinical Terminology Explorer**,
   curated OMOP-inspired tables, code mapping report, analytics dashboard,
   architecture notes.

## Limitations (by design)

- **OMOP-inspired, not OMOP CDM.** No `concept_id` resolution, no
  vocabulary tables, no `concept_relationship`. Real OHDSI workflows
  resolve every source code through the OMOP vocabulary tables.
- **Curated terminology only.** The Clinical Terminology Explorer ships
  with a hand-built mapping for a small set of LOINC / SNOMED CT /
  ICD-10-CM / RxNorm codes covering the sample data. Production systems
  use full vocabulary tables (OHDSI Athena, UMLS, NLM RxNorm),
  licensed terminology distributions, or terminology servers
  (HL7 TS, SNOMED Snowstorm, LOINC FHIR endpoints). MeSH is included as
  educational reference only — it indexes literature, not clinical events,
  so the pipeline does not consume it.
- **Happy-path FHIR only.** No validation, no reference resolution beyond
  `subject`, no handling of FHIR datatypes other than `valueQuantity` on
  Observations.
- **No authentication, no multi-tenant separation.** Tables share the
  public schema with the rest of the portfolio app via a `fhir_demo_`
  name prefix.
- **No migration framework.** Schema updates are applied manually via the
  SQL scripts.
- **Synthetic data only.** No real PHI is involved.
