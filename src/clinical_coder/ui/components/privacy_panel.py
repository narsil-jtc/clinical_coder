"""Privacy transparency component for review results."""

import streamlit as st


def _provider_name(provider_routes: dict[str, str] | None) -> str:
    routes = provider_routes or {}
    for route in routes.values():
        if isinstance(route, str) and route.startswith("cloud:"):
            return route.split(":", 1)[1]
    return "the configured AI provider"


def _redaction_replacement(redaction_type: str) -> str:
    replacements = {
        "name": "[PERSON]",
        "date": "[DATE]",
        "identifier": "[IDENTIFIER]",
    }
    return replacements.get(redaction_type, "[REDACTED]")


def _redaction_label(redaction_type: str) -> str:
    labels = {
        "name": "Name",
        "date": "Date",
        "identifier": "Identifier",
    }
    return labels.get(redaction_type, redaction_type.replace("_", " ").title())


def render_privacy_panel(
    deidentified_text: str,
    redacted_items: list[dict],
    use_cloud: bool,
    provider_routes: dict[str, str] | None,
) -> None:
    """Render what was redacted and what was sent to cloud AI."""

    with st.expander("What was sent to the AI - tap to view", expanded=False):
        st.markdown("**Before sending to any AI, the following were automatically hidden:**")
        if redacted_items:
            for item in redacted_items:
                original_value = item.get("value", "")
                redaction_type = item.get("type", "redacted")
                st.markdown(
                    (
                        f'&#128274; <strong>{_redaction_label(redaction_type)}:</strong> '
                        f'"{original_value}" &rarr; <code>{_redaction_replacement(redaction_type)}</code>'
                    ),
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No identifiers were detected.")

        st.markdown("")
        provider_name = _provider_name(provider_routes)
        if use_cloud:
            st.markdown(f"**The following de-identified text was sent to {provider_name}:**")
        else:
            st.markdown(
                "**Cloud AI was not used. If it had been, this de-identified version would have been sent:**"
            )
        st.code(deidentified_text or "[No de-identified text available]", language=None)

        if use_cloud:
            st.caption("Only the de-identified version above was sent.")
        else:
            st.caption("Your original note never left this device.")
