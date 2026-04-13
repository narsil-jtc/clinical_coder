"""Unified package settings for the local-first Clinical Coder prototype."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Runtime settings loaded from the project-root `.env` file."""

    model_config = SettingsConfigDict(
        env_file=str(_PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    ollama_base_url: str = "http://localhost:11434"
    ollama_extraction_model: str = "llama3.1:8b"
    ollama_coding_model: str = "llama3.1:8b"
    ollama_explanation_model: str = "llama3.1:8b"
    ollama_embedding_model: str = "nomic-embed-text"

    reasoning_mode: str = "local"
    reasoning_provider: str = "ollama"
    reasoning_model: str = ""
    cloud_allowed_tasks: str = "extract,coding,explain"
    deidentify_required_for_cloud: bool = True
    send_raw_notes: bool = False

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-sonnet-latest"
    openai_api_key: str = ""
    openai_model: str = "gpt-5.4-mini"

    high_confidence_threshold: float = Field(default=0.80, ge=0.0, le=1.0)
    low_confidence_threshold: float = Field(default=0.50, ge=0.0, le=1.0)

    chroma_persist_dir: str = str(_PROJECT_ROOT / "data" / "chroma_db")
    terminology_source: str = "who_icd10_2019"
    terminology_edition: str = "WHO ICD-10 2019"
    icd10_code_list_path: str = str(_PROJECT_ROOT / "config" / "code_lists" / "icd102019en.xml")
    validation_rules_path: str = str(_PROJECT_ROOT / "config" / "code_lists" / "validation_rules.json")

    ollama_num_ctx: int = 4096
    ollama_num_predict: int = 2048
    ollama_keep_alive: str = "30m"

    audit_log_path: str = str(_PROJECT_ROOT / "data" / "audit.log")
    debug_log_prompts: bool = False
    hosted_mode: bool = False

    @property
    def reasoning_mode_normalized(self) -> str:
        return self.reasoning_mode.strip().lower()

    @property
    def reasoning_provider_normalized(self) -> str:
        return self.reasoning_provider.strip().lower()

    @property
    def cloud_allowed_task_set(self) -> set[str]:
        return {
            item.strip().lower()
            for item in self.cloud_allowed_tasks.split(",")
            if item.strip()
        }

    @property
    def terminology_scope_label(self) -> str:
        return f"{self.terminology_edition} ({self.terminology_source})"

    @property
    def project_root(self) -> Path:
        return _PROJECT_ROOT

    @property
    def code_list_path(self) -> Path:
        return Path(self.icd10_code_list_path)

    @property
    def validation_rules_file(self) -> Path:
        return Path(self.validation_rules_path)


settings = Settings()
