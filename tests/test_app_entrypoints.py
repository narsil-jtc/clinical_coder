from clinical_coder.app.main import run_workflow
from clinical_coder.app.streamlit_app import main as streamlit_main


def test_app_main_exports_run_workflow():
    assert callable(run_workflow)


def test_streamlit_entrypoint_exposes_main():
    assert callable(streamlit_main)
