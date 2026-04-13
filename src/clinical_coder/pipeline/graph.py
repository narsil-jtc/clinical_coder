"""Legacy compatibility shim for older pipeline-style imports.

New code should import `run_workflow` from `clinical_coder.reasoning.orchestrator`.
"""

from clinical_coder.reasoning.orchestrator import run_workflow

run_pipeline = run_workflow

__all__ = ["run_pipeline"]
