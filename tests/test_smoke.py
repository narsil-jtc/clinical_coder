from clinical_coder.eval.smoke import run_smoke_test


def test_smoke_test_runs_end_to_end():
    summary = run_smoke_test()
    assert summary["provider"] == "smoke-provider"
    assert summary["entity_count"] >= 2
    assert summary["candidate_count"] >= 2
    assert summary["error_count"] == 0
    assert "I21.0" in summary["codes"]
