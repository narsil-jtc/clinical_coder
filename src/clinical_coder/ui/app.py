import logging
from pathlib import Path as _Path

import streamlit as st

from clinical_coder.config import settings
from clinical_coder.reasoning.orchestrator import run_workflow
from clinical_coder.terminology.repository import get_terminology_scope_label
from clinical_coder.ui.components.code_panel import render_code_panel
from clinical_coder.ui.components.note_viewer import render_note_viewer
from clinical_coder.ui.components.privacy_panel import render_privacy_panel
from clinical_coder.ui.components.review_panel import render_review_panel
from clinical_coder.ui.state_manager import (
    clear_workflow_result,
    get_workflow_result,
    set_workflow_result,
)

logging.basicConfig(level=logging.INFO)

_CODE_LIST_DIR = settings.project_root / "config" / "code_lists"


def _cloud_provider_label() -> str:
    provider_name = settings.reasoning_provider_normalized or "cloud"
    if provider_name == "openai":
        return "OpenAI"
    if provider_name == "anthropic":
        return "Anthropic"
    return settings.reasoning_provider or "Cloud AI"


def _get_sample_note() -> str:
    return """\
DISCHARGE SUMMARY

PATIENT: [REDACTED]
DATE OF ADMISSION: [REDACTED]
DATE OF DISCHARGE: [REDACTED]

PRESENTING COMPLAINT:
Central crushing chest pain radiating to the left arm, onset 3 hours prior to admission.
Associated with diaphoresis and nausea. No syncope.

PAST MEDICAL HISTORY:
- Type 2 diabetes mellitus with nephropathy, on metformin
- Hypertension - on amlodipine
- Hypercholesterolaemia - on atorvastatin
- Non-smoker

INVESTIGATIONS:
ECG: 4mm ST elevation in leads V1-V4 (anterior pattern)
Troponin I: 2.8 ng/mL (reference < 0.04)
CXR: No pulmonary oedema
Echo: Anterior wall hypokinesis, EF 45%

ASSESSMENT AND PLAN:

1. Anterior ST-elevation myocardial infarction (STEMI) - confirmed on ECG and troponin.
   Plan: Emergent percutaneous coronary intervention (PCI) performed to left anterior descending artery (LAD).

2. Type 2 diabetes mellitus with nephropathy - HbA1c 9.1%.
   Plan: Continue metformin initially and arrange renal follow-up.
"""


def _render_header() -> None:
    st.markdown(
        """
<div style="
    background: linear-gradient(135deg, #1a5276 0%, #148f77 100%);
    border-radius: 10px;
    padding: 14px 22px;
    margin-bottom: 14px;
    color: white;
">
    <div style="font-size:1.35rem;font-weight:700;letter-spacing:-0.02em;">Clinical Coder</div>
    <div style="font-size:0.76rem;opacity:0.85;margin-top:3px;">
        ICD-10 code suggestions with human review &mdash; your notes stay on this device unless cloud AI is enabled
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


def _sidebar_controls() -> tuple[str, bool]:
    with st.sidebar:
        st.header("Settings")

        available_lists = sorted([path.name for path in _CODE_LIST_DIR.glob("*.xml")])
        current_name = _Path(settings.icd10_code_list_path).name
        default_idx = available_lists.index(current_name) if current_name in available_lists else 0
        selected = st.selectbox(
            "Code list",
            available_lists if available_lists else ["(none found)"],
            index=default_idx if available_lists else 0,
            help="Choose the ICD-10 XML code list used for lookups and validation.",
        )
        if available_lists:
            st.session_state["active_code_list"] = str(_CODE_LIST_DIR / selected)
        active_code_list = st.session_state.get("active_code_list", settings.icd10_code_list_path)
        previous_code_list = st.session_state.get("_last_active_code_list")
        if previous_code_list and previous_code_list != active_code_list:
            clear_workflow_result()
        st.session_state["_last_active_code_list"] = active_code_list

        note_type = st.selectbox(
            "Note type",
            ["discharge_summary", "clinic_letter", "operative_note", "emergency_note"],
            index=0,
        )

        if settings.hosted_mode:
            st.caption(f"Cloud AI: {_cloud_provider_label()} · Notes de-identified before sending")
            cloud_enabled = True
        else:
            cloud_enabled = st.toggle(
                "Use cloud AI (more accurate, de-identified notes sent externally)",
                value=settings.reasoning_mode == "hybrid",
                help="When turned on, only a de-identified version of the note is sent to the configured provider.",
            )
            st.caption(f"Provider: `{settings.reasoning_provider}`")
        st.caption(f"Terminology: `{get_terminology_scope_label(active_code_list)}`")

        if not settings.hosted_mode:
            with st.expander("AI engine settings"):
                st.session_state["llm_num_ctx"] = st.select_slider(
                    "AI memory size",
                    options=[2048, 4096, 8192, 16384, 32768],
                    value=settings.ollama_num_ctx,
                )
                st.session_state["llm_num_predict"] = st.slider(
                    "AI response length",
                    min_value=512,
                    max_value=4096,
                    step=128,
                    value=settings.ollama_num_predict,
                )
                keep_alive_opts = ["5m", "15m", "30m", "1h", "0"]
                st.session_state["llm_keep_alive"] = st.selectbox(
                    "Keep AI loaded in memory",
                    keep_alive_opts,
                    index=keep_alive_opts.index(settings.ollama_keep_alive)
                    if settings.ollama_keep_alive in keep_alive_opts
                    else 2,
                )

        if st.button("Start over", use_container_width=True):
            clear_workflow_result()
            st.rerun()

    return note_type, cloud_enabled


def _run(note_text: str, note_type: str, use_cloud: bool) -> dict:
    with st.status("Running orchestrator...", expanded=True) as status:
        st.write(
            "Parsing note, applying privacy boundary, retrieving WHO ICD-10 terminology, validating, and building review output."
        )
        result = run_workflow(
            raw_note=note_text,
            note_type=note_type,
            use_cloud=use_cloud,
            code_list_path=st.session_state.get("active_code_list", settings.icd10_code_list_path),
            llm_num_ctx=st.session_state.get("llm_num_ctx", settings.ollama_num_ctx),
            llm_num_predict=st.session_state.get("llm_num_predict", settings.ollama_num_predict),
            llm_keep_alive=st.session_state.get("llm_keep_alive", settings.ollama_keep_alive),
        )
        status.update(
            label="Run complete with warnings" if result.get("errors") else "Run complete",
            state="error" if result.get("errors") else "complete",
            expanded=False,
        )
    return result


def main() -> None:
    st.set_page_config(page_title="Clinical Coder", page_icon="H", layout="wide", initial_sidebar_state="collapsed")
    if settings.hosted_mode:
        st.info(
            "**Privacy notice:** This app processes clinical notes using cloud AI. "
            f"Notes are automatically de-identified on this server before being sent to {_cloud_provider_label()}. "
            "Your original note is never stored. "
            "By continuing you acknowledge this data flow.",
            icon="🔒",
        )
    _render_header()
    note_type, use_cloud = _sidebar_controls()

    col_note, col_codes, col_review = st.columns([3, 3, 2], gap="medium")
    result = get_workflow_result()

    with col_note:
        st.subheader("Clinical Note")
        if result is None:
            note_text = st.text_area(
                "Paste note",
                height=420,
                label_visibility="collapsed",
                placeholder="ASSESSMENT AND PLAN:\n1. Acute myocardial infarction...\n2. Type 2 diabetes mellitus...",
            )
            col_run, col_sample = st.columns([2, 1])
            with col_run:
                run_btn = st.button("Run", type="primary", use_container_width=True, disabled=not note_text.strip())
            with col_sample:
                sample_btn = st.button("Load sample", use_container_width=True)

            if sample_btn:
                st.session_state["_sample_loaded"] = True
                st.rerun()

            if st.session_state.get("_sample_loaded"):
                note_text = _get_sample_note()
                st.session_state.pop("_sample_loaded", None)
                run_btn = True

            if run_btn and note_text.strip():
                result = _run(note_text.strip(), note_type, use_cloud)
                set_workflow_result(result)
                st.rerun()

            if use_cloud:
                st.info(
                    "When cloud AI is enabled, only a de-identified version of your note is sent - names, dates, and IDs are replaced before sending."
                )
        else:
            evidence_spans = {item.get("code"): item.get("evidence_span", "") for item in result.get("validated_codes", [])}
            render_note_viewer(result.get("sections", {}), evidence_spans)
            render_privacy_panel(
                deidentified_text=result.get("deidentified_text", ""),
                redacted_items=result.get("redacted_items", []),
                use_cloud=result.get("use_cloud", False),
                provider_routes=result.get("provider_routes", {}),
            )
            if st.button("New note", use_container_width=True):
                clear_workflow_result()
                st.rerun()

    with col_codes:
        st.subheader("Suggested Codes")
        if result is None:
            st.info("Paste a note and run the workflow to see suggestions.")
        else:
            st.markdown(
                (
                    '<div style="font-size:0.8rem;color:#6b7280;margin-bottom:4px;">'
                    f"Found {len(result.get('entities', []))} clinical terms &middot; "
                    f"Suggested {len(result.get('validated_codes', []))} codes &middot; "
                    f"AI: {result.get('coding_model', result.get('extraction_model', '?'))}"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )
            st.caption(f"Active terminology: `{result.get('terminology_scope', settings.terminology_scope_label)}`")
            render_code_panel(result.get("validated_codes", []), result.get("explanations", []))

    with col_review:
        st.subheader("Review")
        if result is None:
            st.info("Run the workflow to start reviewing.")
        else:
            render_review_panel(
                validated_codes=result.get("validated_codes", []),
                all_flags=result.get("all_validation_flags", []),
                workflow_errors=result.get("errors", []),
                missing_specificity=result.get("missing_specificity_flags", []),
            )


if __name__ == "__main__":
    main()
