# Re-establish Clinical Coder as a Modular Local-First Prototype

## Summary
- Keep `src/clinical_coder` as the only application package and remove duplicate config/import patterns.
- Rebuild around clear layers: notes, ingestion, terminology, retrieval, rules, reasoning, app, eval.
- Treat WHO ICD-10 XML as the current source adapter and make UK ICD-10 5th edition a future interchangeable adapter, not a rewrite.
- Keep all parsing, retrieval, rules, and privacy controls local; allow optional cloud reasoning only after local minimisation.

## Key Changes
- Replace the current flat code-list loader contract with a normalized terminology model containing source, edition, code, title, hierarchy, billable/leaf status, and any parsed notes/metadata available.
- Move actual retrieval and validation logic out of `pipeline/nodes` into first-class `retrieval/` and `rules/` modules; keep `pipeline` only as orchestration or replace it with `reasoning/orchestrator.py`.
- Replace direct Ollama usage in nodes with a provider interface supporting `ollama`, `anthropic`, and `openai`, selected by config.
- Add a local privacy boundary module that performs de-identification/minimisation before any cloud call and blocks cloud use if minimisation is unavailable.
- Make the Streamlit app a thin shell over one orchestration service instead of manually running each node.

## Migration Sequence
- Phase 1: consolidate config/imports, retire `config/settings.py`, fix scripts to import from the package only, and simplify docs around the real current state.
- Phase 2: introduce terminology ingestion/repository modules and rework indexing/validation to consume normalized terminology records instead of `{code: description}`.
- Phase 3: extract retrieval/rules/reasoning boundaries and route the UI through one orchestrator entrypoint.
- Phase 4: add hybrid mode with local minimisation plus pluggable Anthropic/OpenAI providers and safe audit logging.
- Phase 5: finish portability with bootstrap script, demo mode, clean env templates, and handover documentation.

## Test Plan
- Preserve current parser and validator unit tests.
- Add terminology ingestion tests for WHO XML and a fixture-shaped UK XML adapter.
- Add retrieval tests against a tiny local index fixture.
- Add orchestrator tests with stub providers for local-only, hybrid-disabled, and hybrid-enabled paths.
- Add one end-to-end regression using a synthetic note that verifies parsing, retrieval, candidate generation, validation, and export without requiring cloud access.

## Assumptions
- Python and `uv` remain the preferred runtime/tooling path.
- Streamlit remains acceptable as the local UI for the prototype stage.
- WHO ICD-10 XML is the current canonical terminology source until UK XML becomes available.
- Real identifiable patient data is out of scope for development; hybrid mode must never require raw identifiable text to leave the machine.
