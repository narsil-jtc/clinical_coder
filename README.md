# Clinical Coder

Local-first clinical coding prototype for synthetic, sample, or heavily de-identified notes.

## Quick Start

```powershell
./scripts/bootstrap.ps1
Copy-Item .env.example .env
uv run streamlit run src/clinical_coder/app/streamlit_app.py
```

## Smoke Test

```powershell
uv run python scripts/smoke_test.py
```

This runs a deterministic end-to-end workflow check without requiring Ollama or cloud API keys.

## Flush Terminology State

When changing the active terminology source, clear the persisted retrieval state before rebuilding:

```powershell
uv run python scripts/reset_terminology.py --rebuild
```

This removes the local Chroma terminology index and rebuilds it for the current `ICD10_CODE_LIST_PATH`.

## Architecture

- `src/clinical_coder/config`: one canonical settings layer
- `src/clinical_coder/notes`: note parsing and note-facing schemas
- `src/clinical_coder/ingestion`: XML terminology adapters
- `src/clinical_coder/terminology`: normalized terminology records and repository
- `src/clinical_coder/retrieval`: local retrieval over terminology
- `src/clinical_coder/rules`: deterministic validation
- `src/clinical_coder/privacy`: local minimisation and de-identification
- `src/clinical_coder/reasoning`: orchestration plus provider abstraction
- `src/clinical_coder/app`: application entrypoints
- `src/clinical_coder/ui`: Streamlit interface components
- `tests`: unit, orchestration, and regression coverage

## Authoritative Runtime Path

- New runtime code should use `clinical_coder.reasoning.run_workflow`.
- `src/clinical_coder/pipeline/` remains only as a legacy compatibility surface.

## Modes

- `local`: all reasoning stays on-device through Ollama
- `hybrid`: raw notes still stay local; only de-identified and minimised text may be sent to the configured cloud provider

In hybrid mode, cloud routing is task-level and config-driven:
- `extract`, `coding`, and `explain` can be allowed independently with `CLOUD_ALLOWED_TASKS`
- retrieval, validation, and export remain local
- if hybrid mode is requested but the provider is unavailable, the workflow falls back to local reasoning and records a warning

## Terminology Scope

- WHO ICD-10 XML is the canonical terminology source
- future UK ICD-10 XML can be added as another XML adapter without reintroducing US-specific code paths
