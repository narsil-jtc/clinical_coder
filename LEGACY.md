# Legacy Compatibility Surface

The `src/clinical_coder/pipeline/` package is retained only for backward compatibility.

Authoritative modules:

- `clinical_coder.notes`
- `clinical_coder.retrieval`
- `clinical_coder.rules`
- `clinical_coder.reasoning`
- `clinical_coder.app`

Preferred runtime entrypoint:

- `clinical_coder.reasoning.run_workflow`

Compatibility aliases retained for now:

- `clinical_coder.pipeline.graph.run_pipeline`
- `clinical_coder.pipeline.state.PipelineState`
- `clinical_coder.ui.state_manager.get_pipeline_result` and related aliases
