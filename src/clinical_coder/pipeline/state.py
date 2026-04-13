"""Legacy shim for the workflow state contract.

New code should import `WorkflowState` from `clinical_coder.reasoning.state`.
"""

from clinical_coder.reasoning.state import CodingWorkflowState, WorkflowState

PipelineState = WorkflowState

__all__ = ["CodingWorkflowState", "PipelineState", "WorkflowState"]
