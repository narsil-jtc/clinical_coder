# Architecture Overview

## Runtime Flow

1. Parse note sections locally.
2. Minimise and de-identify locally.
3. Retrieve terminology context locally.
4. Run reasoning through the configured provider.
5. Validate deterministically against terminology and rules.
6. Present review output locally.

## Boundaries

- Note parsing lives in `notes/`, not in the UI or orchestration layer.
- Terminology ingestion is separate from runtime reasoning.
- Retrieval and rules are provider-independent.
- Cloud providers are optional and only used behind the privacy boundary.
- `pipeline/` is now a legacy shim layer, not the primary architecture.
