-- Reset all FHIR-demo tables.
--
-- Truncates every fhir_demo_* table and resets their SERIAL sequences so the
-- next pipeline run starts from id 1. CASCADE is required because of the FK
-- chain: raw_fhir_resource → ingestion_run, and every OMOP-style event table
-- → person.
--
-- This is what the Streamlit "Reset Demo Data" button runs under the hood.
-- The synthetic FHIR bundles themselves live as JSON files under
-- projects/fhir_omop/sample_data/ — no separate "seed" SQL is needed.

TRUNCATE TABLE
    fhir_demo_code_mapping_report,
    fhir_demo_drug_exposure,
    fhir_demo_measurement,
    fhir_demo_condition_occurrence,
    fhir_demo_visit_occurrence,
    fhir_demo_person,
    fhir_demo_raw_fhir_resource,
    fhir_demo_ingestion_run
RESTART IDENTITY CASCADE;
