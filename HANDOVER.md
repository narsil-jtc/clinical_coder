# Handover Notes

## Minimum Setup

1. Install Python and `uv`.
2. Copy `.env.example` to `.env`.
3. Run `./scripts/bootstrap.ps1`.
4. Start the app with `uv run streamlit run src/clinical_coder/app/streamlit_app.py`.

## Demo Path

- Built-in sample note is available in the UI.
- Additional synthetic notes can be generated with `uv run python scripts/generate_synthetic.py`.
- A deterministic runtime check is available with `uv run python scripts/smoke_test.py`.

## Machine-Specific Items To Avoid Committing

- `.venv/`
- `.pytest_cache/`
- `data/chroma_db/`
- `.env`
