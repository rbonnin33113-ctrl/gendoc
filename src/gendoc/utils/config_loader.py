"""Configuration file loader and validator for gendoc.

This module handles loading and validating the gendoc.json configuration file
which specifies the network_share_path and other settings for multi-workstation
deployment.

Config Search Strategy (in order):
1. Look for gendoc.json in current working directory
2. Look for .gendoc.json in user home directory
3. Look for gendoc.json alongside server.py (fallback for dev)

Example gendoc.json:
{
    "network_share_path": "H:/IA/Generateur de doc/Delagrave",
    "admin": false
}
"""

import json
from pathlib import Path
from typing import TypedDict


class ConfigDict(TypedDict):
    """Type definition for configuration dictionary."""
    config_path: Path
    network_share_path: Path
    references_dir: Path
    images_dir: Path
    template_path: Path
    admin: bool


class ConfigurationError(Exception):
    """Exception raised for configuration-related errors."""
    pass


def _find_config_file() -> Path | None:
    """Search for config file in order: CWD, home dir, server.py dir.

    Returns:
        Path to config file if found, None otherwise.
    """
    # 1. Look in current working directory
    cwd_config = Path.cwd() / "gendoc.json"
    if cwd_config.exists():
        return cwd_config

    # 2. Look in user home directory (hidden file)
    home_config = Path.home() / ".gendoc.json"
    if home_config.exists():
        return home_config

    # 3. Look alongside server.py (for development)
    # Find server.py location: ../mcp/server.py from this file
    server_dir = Path(__file__).resolve().parent.parent / "mcp"
    server_config = server_dir / "gendoc.json"
    if server_config.exists():
        return server_config

    return None


def _validate_network_share(network_share_path: Path) -> None:
    """Validate that network share and required subdirectories exist.

    Args:
        network_share_path: Base path from config.

    Raises:
        ConfigurationError: If validation fails with specific details.
    """
    # Check base path exists
    if not network_share_path.exists():
        raise ConfigurationError(
            f"network_share_path does not exist: {network_share_path}\n"
            f"Create the directory or update gendoc.json with the correct path."
        )

    # Check required subdirectories
    references_dir = network_share_path / "references"
    if not references_dir.exists():
        raise ConfigurationError(
            f"Required subdirectory 'references/' not found in: {network_share_path}\n"
            f"Expected: {references_dir}"
        )

    images_dir = network_share_path / "images"
    if not images_dir.exists():
        raise ConfigurationError(
            f"Required subdirectory 'images/' not found in: {network_share_path}\n"
            f"Expected: {images_dir}"
        )

    template_dir = network_share_path / "Modele fiches - Powerpoint"
    if not template_dir.exists():
        raise ConfigurationError(
            f"Required subdirectory 'Modele fiches - Powerpoint/' not found in: {network_share_path}\n"
            f"Expected: {template_dir}"
        )

    # Check template file exists
    template_file = template_dir / "Modèle fiche technique vide - Ind J.potm"
    if not template_file.exists():
        raise ConfigurationError(
            f"Required template file not found: {template_file}\n"
            f"Ensure 'Modèle fiche technique vide - Ind J.potm' exists in {template_dir}"
        )


def load_config() -> ConfigDict:
    """Load and validate gendoc configuration.

    Searches for config file, validates network share accessibility,
    and returns resolved paths.

    Returns:
        Dictionary with configuration and resolved paths:
        - config_path: Where config file was found
        - network_share_path: Base path from config
        - references_dir: network_share_path / "references"
        - images_dir: network_share_path / "images"
        - template_path: Full path to template file
        - admin: Admin mode flag (default: False)

    Raises:
        ConfigurationError: If config not found, invalid, or validation fails.
    """
    # Find config file
    config_path = _find_config_file()
    if config_path is None:
        raise ConfigurationError(
            'Config file not found. Create gendoc.json with:\n'
            '{\n'
            '    "network_share_path": "path/to/shared/Delagrave",\n'
            '    "admin": false\n'
            '}'
        )

    # Load and parse JSON
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigurationError(f"Invalid JSON in {config_path}: {e}")
    except Exception as e:
        raise ConfigurationError(f"Failed to read {config_path}: {e}")

    # Validate required fields
    if "network_share_path" not in config_data:
        raise ConfigurationError(
            f'Missing required field "network_share_path" in {config_path}'
        )

    network_share_path_str = config_data["network_share_path"]
    if not isinstance(network_share_path_str, str) or not network_share_path_str.strip():
        raise ConfigurationError(
            f'"network_share_path" must be a non-empty string in {config_path}'
        )

    # Convert to Path
    network_share_path = Path(network_share_path_str).resolve()

    # Validate network share structure
    _validate_network_share(network_share_path)

    # Get optional admin flag
    admin = config_data.get("admin", False)
    if not isinstance(admin, bool):
        raise ConfigurationError(
            f'"admin" must be a boolean (true/false) in {config_path}'
        )

    # Build resolved paths
    references_dir = network_share_path / "references"
    images_dir = network_share_path / "images"
    template_path = network_share_path / "Modele fiches - Powerpoint" / "Modèle fiche technique vide - Ind J.potm"

    return {
        "config_path": config_path,
        "network_share_path": network_share_path,
        "references_dir": references_dir,
        "images_dir": images_dir,
        "template_path": template_path,
        "admin": admin,
    }
