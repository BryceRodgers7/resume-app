# FHIR → OMOP Demo (front-end)

A **simplified healthcare interoperability demo** that lives inside the
existing Streamlit portfolio app. The Streamlit page is a thin HTTP client
over the **FHIR → OMOP backend service** (separate repo / Fly app), which
owns the database, the sample data, the DDL, and all transform logic.

The backend ingests synthetic **FHIR R4** patient bundles, transforms them
into an **OMOP-inspired** relational schema, and serves a single
`/dashboard` payload that drives every tab on the page.

This is a **FHIR familiarity project** — not production OMOP CDM, not
certified interoperability, and not validated for clinical use.

## What this demonstrates

- Reading **FHIR R4 Bundle JSON** that resembles Synthea output, from both
  bundled sample data *and* user-uploaded files (multi-file
  `st.file_uploader`) — both paths POST to the backend
- A typical healthcare-ETL shape: **raw landing zone (JSONB) → transform →
  curated tables → analytics queries**, with each stage visible in the UI
- Awareness of the standard biomedical vocabularies: **SNOMED CT**,
  **LOINC**, **RxNorm**, **ICD-10 / ICD-10-CM**
- A simplified **terminology mapping report** that flags presence vs.
  absence of recognized coding systems (stand-in for real `concept_id`
  resolution)
- An **OMOP-inspired** relational layout — `person`, `visit_occurrence`,
  `condition_occurrence`, `measurement`, `drug_exposure` — surfaced as
  `fhir_demo_*` tables by the backend
- **Service-oriented architecture** — Streamlit front-end → FHIR-OMOP
  backend → Postgres. The page makes one `GET /dashboard` call per rerun
  to render all tabs; action buttons POST with `Idempotency-Key` headers
  so retries don't duplicate rows.
- **Step-by-step progress UX** — every long handler (`Reset`, `Load`,
  `Run Transformation Pipeline`) uses `st.status(..., expanded=True)` with
  per-step messages and `time.perf_counter()` timings.
- **Pipeline-stage status banner** — when raw resources exist but the OMOP
  tables are empty, the page surfaces a hint to run the transformation
  step. Avoids the "I loaded data but everything is zero" papercut.
- **Clinical Terminology Explorer** — extracts every coding from the raw
  FHIR resources the backend returns, classifies each `(system, code)` pair
  as *mapped* / *system-known-code-unknown* / *unsupported* / *missing*,
  and surfaces summary metrics, a filterable table, a per-code detail
  view, and educational reference cards for LOINC, SNOMED CT, ICD-10-CM,
  RxNorm, and MeSH. Powered by a curated mapping table in
  `pipeline/terminology.py` (pure compute — no terminology server, no
  licensed downloads, no back-end round-trip from the filter controls).

## Architecture

```
projects/fhir_omop/pipeline/api_client.py  ◀── HTTP client over the backend
                       │
                       ▼
              FHIR → OMOP backend service                 ◀── owns DB I/O
                       │
                       ▼
              PostgreSQL (raw landing + curated)
                       │
                       ▼
         pages/fhir_omop.py renders the dashboard          ◀── render
       (terminology.py classifies codings client-side)
```

The Streamlit page no longer talks to the database directly. The backend
bounds connection failures (timeouts + retries) and surfaces them as
actionable errors instead of blank pages.

## Layout

```
projects/fhir_omop/
├── README.md                       # this file
└── pipeline/
    ├── api_client.py               # FhirOmopApiClient — retry + idempotency
    └── terminology.py              # curated terminology metadata + demo code
                                    # mappings; classify_coding() +
                                    # build_terminology_rows() power the
                                    # Clinical Terminology Explorer tab

pages/fhir_omop.py                  # the Streamlit page registered in nav.py
```

Everything else — sample FHIR bundles, the `fhir_demo_*` DDL, the ingest
and transform pipeline, the analytics SQL — lives in the FHIR-OMOP backend
repo.

## Technologies

- **Streamlit** — UI + page registration via `nav.config_navigation`
- **Python 3** — HTTP client + terminology compute
- **pandas** — DataFrames for the dashboard charts/tables
- **requests** — backend HTTP calls
- **FHIR-OMOP backend service** — separate Fly app, owns Postgres I/O

No new dependencies are introduced — everything required already ships in
`requirements.txt`.

## Demo workflow

1. Set `FHIR_OMOP_API_URL` (Fly secret on the Streamlit app) to point at
   the backend service.
2. Open the **FHIR → OMOP** page in the Streamlit app.
3. Click **Reset Demo Data** — backend truncates every `fhir_demo_*` table.
4. Load raw data — either:
   - Click **Load Sample FHIR Bundles** to ingest the backend's bundled
     synthetic patients, or
   - Expand **📤 Or upload your own FHIR Bundle JSON files**, drop one or
     more FHIR R4 Bundles into the file uploader, and click
     **Load Uploaded Bundles**.

   Both paths POST to the same `/ingest` family of endpoints with an
   `Idempotency-Key` header.
5. The status banner above the metrics will tell you "*N raw resources
   loaded — click Run Transformation Pipeline*". Click it.
6. **Run Transformation Pipeline** triggers `/transform` on the backend,
   which populates the OMOP-inspired tables and generates the mapping
   report inside one Supabase transaction.
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
- **No authentication, no multi-tenant separation.** The backend's tables
  share the public schema with the rest of the portfolio app via a
  `fhir_demo_` name prefix.
- **No migration framework.** Backend schema updates are applied manually
  via the SQL scripts shipped with the backend repo.
- **Synthetic data only.** No real PHI is involved.
