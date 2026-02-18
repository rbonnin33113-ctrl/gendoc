"""Unit tests for config_loader module."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from gendoc.utils.config_loader import ConfigurationError, load_config


@pytest.fixture
def valid_structure(tmp_path):
    """Create valid network share structure for testing.

    Args:
        tmp_path: pytest tmp_path fixture.

    Returns:
        Path to network share directory with valid structure.
    """
    network_share = tmp_path / "network_share"
    network_share.mkdir()

    # Create required subdirectories
    (network_share / "references").mkdir()
    (network_share / "images").mkdir()
    template_dir = network_share / "Modele fiches - Powerpoint"
    template_dir.mkdir()

    # Create template file
    template_file = template_dir / "Modèle fiche technique vide - Ind J.potm"
    template_file.write_text("dummy template", encoding="utf-8")

    return network_share


def test_load_config_from_cwd(tmp_path, valid_structure, monkeypatch):
    """Test loading config from current working directory."""
    # Create config in tmp_path
    config_file = tmp_path / "gendoc.json"
    config_data = {"network_share_path": str(valid_structure)}
    config_file.write_text(json.dumps(config_data), encoding="utf-8")

    # Change to tmp_path as CWD
    monkeypatch.chdir(tmp_path)

    # Load config
    result = load_config()

    # Verify config_path points to CWD/gendoc.json
    assert result["config_path"] == config_file

    # Verify all 8 keys present (including optional github fields)
    assert set(result.keys()) == {
        "config_path",
        "network_share_path",
        "references_dir",
        "images_dir",
        "template_path",
        "admin",
        "github_repo",
        "github_token",
    }

    # Verify paths resolve correctly
    assert result["network_share_path"] == valid_structure.resolve()
    assert result["references_dir"] == valid_structure / "references"
    assert result["images_dir"] == valid_structure / "images"
    assert result["template_path"] == (
        valid_structure / "Modele fiches - Powerpoint" / "Modèle fiche technique vide - Ind J.potm"
    )
    assert result["admin"] is False


def test_load_config_from_home(tmp_path, valid_structure, monkeypatch):
    """Test loading config from home directory."""
    # Monkeypatch Path.home() to return tmp_path
    def mock_home():
        return tmp_path

    monkeypatch.setattr(Path, "home", mock_home)

    # Create .gendoc.json in tmp_path (home dir)
    config_file = tmp_path / ".gendoc.json"
    config_data = {"network_share_path": str(valid_structure)}
    config_file.write_text(json.dumps(config_data), encoding="utf-8")

    # Change CWD to somewhere else without config
    other_dir = tmp_path / "other"
    other_dir.mkdir()
    monkeypatch.chdir(other_dir)

    # Load config
    result = load_config()

    # Verify config loaded from home directory
    assert result["config_path"] == config_file


def test_load_config_missing(tmp_path, monkeypatch):
    """Test error when config file is missing."""
    # Change to tmp_path with no config file
    monkeypatch.chdir(tmp_path)

    # Mock home() to return tmp_path (no config there either)
    def mock_home():
        return tmp_path

    monkeypatch.setattr(Path, "home", mock_home)

    # Expect ConfigurationError
    with pytest.raises(ConfigurationError) as exc_info:
        load_config()

    # Assert error message contains guidance
    error_message = str(exc_info.value)
    assert "Create gendoc.json" in error_message
    assert "network_share_path" in error_message
    assert "admin" in error_message


def test_validate_network_share_not_exists(tmp_path, monkeypatch):
    """Test error when network_share_path points to non-existent directory."""
    # Create config pointing to non-existent directory
    config_file = tmp_path / "gendoc.json"
    non_existent = tmp_path / "does_not_exist"
    config_data = {"network_share_path": str(non_existent)}
    config_file.write_text(json.dumps(config_data), encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    # Expect ConfigurationError
    with pytest.raises(ConfigurationError) as exc_info:
        load_config()

    error_message = str(exc_info.value)
    assert "network_share_path does not exist" in error_message
    assert str(non_existent.resolve()) in error_message


def test_validate_missing_references_dir(tmp_path, monkeypatch):
    """Test error when references/ subdirectory is missing."""
    # Create network share without references/
    network_share = tmp_path / "network_share"
    network_share.mkdir()
    (network_share / "images").mkdir()
    template_dir = network_share / "Modele fiches - Powerpoint"
    template_dir.mkdir()
    template_file = template_dir / "Modèle fiche technique vide - Ind J.potm"
    template_file.write_text("dummy", encoding="utf-8")

    # Create config
    config_file = tmp_path / "gendoc.json"
    config_data = {"network_share_path": str(network_share)}
    config_file.write_text(json.dumps(config_data), encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    # Expect ConfigurationError mentioning references/
    with pytest.raises(ConfigurationError) as exc_info:
        load_config()

    error_message = str(exc_info.value)
    assert "references/" in error_message


def test_validate_missing_template(tmp_path, valid_structure, monkeypatch):
    """Test error when template file is missing."""
    # Remove template file from valid structure
    template_file = (
        valid_structure / "Modele fiches - Powerpoint" / "Modèle fiche technique vide - Ind J.potm"
    )
    template_file.unlink()

    # Create config
    config_file = tmp_path / "gendoc.json"
    config_data = {"network_share_path": str(valid_structure)}
    config_file.write_text(json.dumps(config_data), encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    # Expect ConfigurationError mentioning template filename
    with pytest.raises(ConfigurationError) as exc_info:
        load_config()

    error_message = str(exc_info.value)
    assert "Modèle fiche technique vide - Ind J.potm" in error_message


def test_admin_flag_defaults_false(tmp_path, valid_structure, monkeypatch):
    """Test that admin flag defaults to False when not specified."""
    # Create config without admin field
    config_file = tmp_path / "gendoc.json"
    config_data = {"network_share_path": str(valid_structure)}
    config_file.write_text(json.dumps(config_data), encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    # Load config
    result = load_config()

    # Assert admin is False
    assert result["admin"] is False


def test_admin_flag_explicit_true(tmp_path, valid_structure, monkeypatch):
    """Test that admin flag can be set to True explicitly."""
    # Create config with admin: true
    config_file = tmp_path / "gendoc.json"
    config_data = {"network_share_path": str(valid_structure), "admin": True}
    config_file.write_text(json.dumps(config_data), encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    # Load config
    result = load_config()

    # Assert admin is True
    assert result["admin"] is True
