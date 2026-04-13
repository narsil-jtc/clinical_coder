from clinical_coder.config.settings import Settings


def test_settings_defaults_hosted_mode_to_false():
    settings = Settings(_env_file=None)

    assert settings.hosted_mode is False


def test_settings_reads_hosted_mode_from_environment(monkeypatch):
    monkeypatch.setenv("HOSTED_MODE", "true")
    settings = Settings(_env_file=None)

    assert settings.hosted_mode is True
