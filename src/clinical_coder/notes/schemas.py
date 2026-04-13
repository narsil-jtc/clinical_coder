"""Small note-facing schemas for app and orchestration boundaries."""

from pydantic import BaseModel, Field


class NoteInput(BaseModel):
    """Inbound note payload for the coding workflow."""

    raw_note: str
    note_type: str = Field(default="discharge_summary")
    note_id: str | None = None
