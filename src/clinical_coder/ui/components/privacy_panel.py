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

    provider_name = _provider_name(provider_routes)
    title = f"Privacy boundary · {'Sent to ' + provider_name if use_cloud else 'Local review only'}"
    with st.expander(title, expanded=False):
        st.markdown(
            (
                '<div style="background:rgba(255,255,255,0.86);border:1px solid rgba(16,35,48,0.08);'
                'border-radius:18px;padding:0.95rem 1rem 1rem 1rem;margin-bottom:0.85rem;">'
                '<div style="text-transform:uppercase;letter-spacing:0.13em;font-size:0.67rem;font-weight:700;'
                'color:#1e6b73;margin-bottom:0.35rem;">Privacy summary</div>'
                '<div style="font-size:0.88rem;color:#233946;line-height:1.58;">'
                'Identifiers are hidden before any cloud call. This panel shows exactly what was redacted and the payload used for reasoning.'
                "</div></div>"
            ),
            unsafe_allow_html=True,
        )

        if redacted_items:
            for item in redacted_items:
                original_value = item.get("value", "")
                redaction_type = item.get("type", "redacted")
                st.markdown(
                    (
                        '<div style="background:#f7f2e8;border:1px solid #e4d9c5;border-radius:14px;'
                        'padding:0.72rem 0.82rem;margin-bottom:0.45rem;">'
                        f'<div style="font-size:0.77rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:#8b5a16;">{_redaction_label(redaction_type)}</div>'
                        f'<div style="font-size:0.84rem;color:#233946;margin-top:0.22rem;">"{original_value}" → <code>{_redaction_replacement(redaction_type)}</code></div>'
                        "</div>"
                    ),
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No identifiers were detected.")

        st.markdown("")
        if use_cloud:
            st.markdown(f"**De-identified payload sent to {provider_name}**")
        else:
            st.markdown("**De-identified payload that would be sent if cloud AI were enabled**")
        st.code(deidentified_text or "[No de-identified text available]", language=None)

        if use_cloud:
            st.caption("Only the de-identified payload above was sent externally.")
        else:
            st.caption("Your original note stayed inside the local workflow.")
