from pathlib import Path

import pytest

from faust_avro_model_codegen.settings import Settings, ConfigNotFoundError


def test_settings_from_toml_returns_expected_settings_object_from_pyproject_toml(
    pyproject_toml: Path,
):
    actual = Settings.from_toml()
    expected = Settings(
        schema_dir=Path("tests/schemas"),
        outfile=Path("fake_app/models.py"),
        schema_registry_url="http://localhost:8082",
        faust_app_models_module="models",
    )
    assert actual == expected


def test_settings_from_toml_returns_expected_settings_object_from_standalone_toml(
    standalone_toml: Path,
):
    actual = Settings.from_toml()
    expected = Settings(
        schema_dir=Path("tests/other_schemas"),
        outfile=Path("fake_app/models.py"),
        schema_registry_url="http://localhost:8083",
        faust_app_models_module="models",
    )
    assert actual == expected


def test_settings_from_toml_returns_default_settings_object_when_no_toml_files_exist():
    with pytest.raises(ConfigNotFoundError):
        Settings.from_toml()
