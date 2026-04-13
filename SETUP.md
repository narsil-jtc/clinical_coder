# Setup

## Local Development

```powershell
./scripts/bootstrap.ps1
Copy-Item .env.example .env
uv run pytest tests -q
uv run streamlit run src/clinical_coder/app/streamlit_app.py
```

## Deterministic Smoke Test

```powershell
uv run python scripts/smoke_test.py
```

This checks the workflow path end-to-end using a built-in deterministic provider, so it does not depend on Ollama, Chroma population, or cloud credentials.

## Build the Local Terminology Index

```powershell
uv run python scripts/setup_chroma.py
uv run python scripts/index_code_lists.py
```

## Reset Terminology Before Swapping Standards

```powershell
uv run python scripts/reset_terminology.py --rebuild
```

Run this whenever you replace the active XML terminology source so stale indexed material from the previous standard cannot influence retrieval.

## Generate Synthetic Notes

```powershell
uv run python scripts/generate_synthetic.py --count 10 --output data/synthetic_notes/
```

## Hybrid Mode

Set these in `.env`:

- `REASONING_MODE=hybrid`
- `REASONING_PROVIDER=anthropic` or `openai`
- `CLOUD_ALLOWED_TASKS=extract,coding,explain`
- the matching API key

The app still applies local minimisation and de-identification before any external call, and it falls back to local reasoning if the configured cloud provider is unavailable.
