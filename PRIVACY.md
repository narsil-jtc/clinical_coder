# Privacy Boundary

- Development is for synthetic, sample, or heavily de-identified notes only.
- Parsing, terminology lookup, retrieval, validation, and export remain local.
- Hybrid mode sends only minimised and de-identified text to cloud providers.
- Hybrid routing is task-scoped: only tasks allowed by `CLOUD_ALLOWED_TASKS` may use cloud providers.
- If hybrid mode is requested but a provider is unavailable or misconfigured, the workflow falls back to local reasoning instead of sending unsafe payloads.
- Audit logs record metadata only by default, not raw note text.
