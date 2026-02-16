"""Integration tests for MCP server configuration loading.

Tests that server.py correctly loads config_loader at startup and uses
config-resolved paths for all operations.
"""

import asyncio
import json
import pytest
from pathlib import Path
import sys
import importlib


@pytest.fixture
def valid_structure(tmp_path):
    """Create a valid Delagrave directory structure for testing.

    Returns:
        Dictionary with paths to created structure.
    """
    # Create base structure
    network_share = tmp_path / "Delagrave"
    network_share.mkdir()

    # Create subdirectories
    references_dir = network_share / "references"
    references_dir.mkdir()

    images_dir = network_share / "images"
    images_dir.mkdir()

    template_dir = network_share / "Modele fiches - Powerpoint"
    template_dir.mkdir()

    # Create template file
    template_file = template_dir / "Modèle fiche technique vide - Ind J.potm"
    template_file.write_text("mock template")

    # Create at least one product for lookup tests
    paillasse_md = references_dir / "paillasse.md"
    paillasse_md.write_text("""# Paillasse

> Extracted from: Test
> Date: 2026-02-16
> Total references: 1

## PM-TEST

| Champ | Valeur |
|-------|--------|
| code | PM-TEST |
| ref | Réf : TEST-001 |
| titre | Test Product |
| famille | Paillasse |

### Texte

Product description

### Dimensions

| Dimension | Valeur | Prefix | Shape Index |
|-----------|--------|--------|-------------|

### Images

| Filename | Type | Idx |
|----------|------|-----|

### Métadonnées PPT

| Propriété | Valeur |
|-----------|--------|
""", encoding='utf-8')

    return {
        'network_share': network_share,
        'references_dir': references_dir,
        'images_dir': images_dir,
        'template_path': template_file
    }


@pytest.fixture
def config_file(tmp_path, valid_structure, monkeypatch):
    """Create a valid gendoc.json and monkeypatch cwd to use it.

    This fixture:
    1. Creates gendoc.json in tmp_path with valid network_share_path
    2. Monkeypatches os.getcwd() to return tmp_path
    3. Cleans up sys.modules after test to reset module state
    """
    # First remove any cached server module
    if 'gendoc.mcp.server' in sys.modules:
        del sys.modules['gendoc.mcp.server']
    if 'gendoc.utils.config_loader' in sys.modules:
        del sys.modules['gendoc.utils.config_loader']

    config_path = tmp_path / "gendoc.json"
    config_data = {
        "network_share_path": str(valid_structure['network_share'])
    }
    config_path.write_text(json.dumps(config_data, ensure_ascii=False), encoding='utf-8')

    # Monkeypatch cwd to tmp_path so config_loader finds our config
    import os
    monkeypatch.setattr(os, 'getcwd', lambda: str(tmp_path))

    # Store original sys.modules state for cleanup
    original_modules = dict(sys.modules)

    yield config_path

    # Cleanup: remove gendoc modules from sys.modules to reset state
    modules_to_remove = [key for key in sys.modules.keys() if key.startswith('gendoc')]
    for module_key in modules_to_remove:
        if module_key not in original_modules:
            del sys.modules[module_key]


@pytest.fixture
def admin_config_file(tmp_path, valid_structure, monkeypatch):
    """Create a valid gendoc.json with admin=true and monkeypatch cwd to use it.

    This fixture:
    1. Creates gendoc.json in tmp_path with admin=true
    2. Monkeypatches os.getcwd() to return tmp_path
    3. Cleans up sys.modules after test to reset module state
    """
    # First remove any cached server module
    if 'gendoc.mcp.server' in sys.modules:
        del sys.modules['gendoc.mcp.server']
    if 'gendoc.utils.config_loader' in sys.modules:
        del sys.modules['gendoc.utils.config_loader']

    config_path = tmp_path / "gendoc.json"
    config_data = {
        "network_share_path": str(valid_structure['network_share']),
        "admin": True
    }
    config_path.write_text(json.dumps(config_data, ensure_ascii=False), encoding='utf-8')

    # Monkeypatch cwd to tmp_path so config_loader finds our config
    import os
    monkeypatch.setattr(os, 'getcwd', lambda: str(tmp_path))

    # Store original sys.modules state for cleanup
    original_modules = dict(sys.modules)

    yield config_path

    # Cleanup: remove gendoc modules from sys.modules to reset state
    modules_to_remove = [key for key in sys.modules.keys() if key.startswith('gendoc')]
    for module_key in modules_to_remove:
        if module_key not in original_modules:
            del sys.modules[module_key]


@pytest.fixture
def non_admin_config_file(tmp_path, valid_structure, monkeypatch):
    """Create a valid gendoc.json with admin=false and monkeypatch cwd to use it.

    This fixture:
    1. Creates gendoc.json in tmp_path with admin=false
    2. Monkeypatches os.getcwd() to return tmp_path
    3. Cleans up sys.modules after test to reset module state
    """
    # First remove any cached server module
    if 'gendoc.mcp.server' in sys.modules:
        del sys.modules['gendoc.mcp.server']
    if 'gendoc.utils.config_loader' in sys.modules:
        del sys.modules['gendoc.utils.config_loader']

    config_path = tmp_path / "gendoc.json"
    config_data = {
        "network_share_path": str(valid_structure['network_share']),
        "admin": False
    }
    config_path.write_text(json.dumps(config_data, ensure_ascii=False), encoding='utf-8')

    # Monkeypatch cwd to tmp_path so config_loader finds our config
    import os
    monkeypatch.setattr(os, 'getcwd', lambda: str(tmp_path))

    # Store original sys.modules state for cleanup
    original_modules = dict(sys.modules)

    yield config_path

    # Cleanup: remove gendoc modules from sys.modules to reset state
    modules_to_remove = [key for key in sys.modules.keys() if key.startswith('gendoc')]
    for module_key in modules_to_remove:
        if module_key not in original_modules:
            del sys.modules[module_key]


def test_server_loads_config_successfully(config_file, valid_structure):
    """Test that server.py loads config and resolves paths correctly."""
    # Import server module (triggers config loading at module level)
    import gendoc.mcp.server as server

    # Verify constants are set from config
    assert server.REFERENCES_DIR == valid_structure['references_dir']
    assert server.IMAGES_DIR == valid_structure['images_dir']
    assert server.TEMPLATE_PATH == valid_structure['template_path']

    # Verify paths exist and are accessible
    assert server.REFERENCES_DIR.exists()
    assert server.IMAGES_DIR.exists()
    assert server.TEMPLATE_PATH.exists()

    # Verify OUTPUT_DIR is local (Phase 22 behavior)
    assert server.OUTPUT_DIR == Path("output").resolve()


def test_server_uses_config_paths_in_tools(config_file, valid_structure):
    """Test that MCP tools use config-resolved paths."""
    # Import server module
    import gendoc.mcp.server as server

    # Import find_product directly to test config-resolved paths are used
    from gendoc.parsers.md_parser import find_product

    # Call find_product with config-resolved REFERENCES_DIR
    product = find_product("PM-TEST", server.REFERENCES_DIR)

    # Verify product was found (proves tools would use config-resolved REFERENCES_DIR)
    assert product is not None
    assert product["code"] == "PM-TEST"
    assert product["titre"] == "Test Product"


def test_server_output_dir_local(config_file, valid_structure):
    """Test that OUTPUT_DIR remains local (Phase 22 behavior before Phase 23)."""
    # Import server module
    import gendoc.mcp.server as server

    # Verify OUTPUT_DIR is local output directory (not from config)
    assert server.OUTPUT_DIR == Path("output").resolve()

    # Verify it's NOT derived from network_share_path
    assert valid_structure['network_share'] not in server.OUTPUT_DIR.parents


def test_server_fails_without_config(tmp_path, monkeypatch):
    """Test that server exits gracefully with clear error if config missing."""
    # Monkeypatch cwd to empty tmp_path (no gendoc.json)
    import os
    monkeypatch.setattr(os, 'getcwd', lambda: str(tmp_path))

    # Remove any cached gendoc modules
    modules_to_remove = [key for key in sys.modules.keys() if key.startswith('gendoc')]
    for module_key in modules_to_remove:
        del sys.modules[module_key]

    # Attempt to import server module should cause sys.exit(1)
    with pytest.raises(SystemExit) as excinfo:
        import gendoc.mcp.server

    # Verify exit code is 1
    assert excinfo.value.code == 1


def test_crud_blocked_when_admin_false(non_admin_config_file):
    """Test that CRUD operations are blocked when admin=false."""
    import asyncio
    import gendoc.mcp.server as server

    # Test add_reference blocked
    result = asyncio.run(server.add_reference.fn("paillasse", "TEST", "Test"))
    assert "Operation reservee a l'administrateur" in result
    result_dict = json.loads(result)
    assert "error" in result_dict
    assert result_dict["error"] == "Operation reservee a l'administrateur"

    # Test update_reference blocked
    result = asyncio.run(server.update_reference.fn("TEST", titre="X"))
    assert "Operation reservee a l'administrateur" in result
    result_dict = json.loads(result)
    assert "error" in result_dict
    assert result_dict["error"] == "Operation reservee a l'administrateur"

    # Test delete_reference blocked
    result = asyncio.run(server.delete_reference.fn("TEST"))
    assert "Operation reservee a l'administrateur" in result
    result_dict = json.loads(result)
    assert "error" in result_dict
    assert result_dict["error"] == "Operation reservee a l'administrateur"


def test_crud_allowed_when_admin_true(admin_config_file, valid_structure):
    """Test that CRUD operations are allowed when admin=true."""
    import asyncio
    import gendoc.mcp.server as server

    # Test add_reference allowed (may fail for business reasons, but NOT admin check)
    result = asyncio.run(server.add_reference.fn("paillasse", "PM-ADMIN-TEST", "Admin Test"))
    # Admin check should NOT block - result should not contain admin error
    assert "Operation reservee" not in result

    # Parse result to verify it's not an admin error
    result_dict = json.loads(result)
    # If there's an error, it should be a business error (e.g., duplicate), not admin
    if "error" in result_dict:
        assert result_dict["error"] != "Operation reservee a l'administrateur"


def test_readonly_tools_work_without_admin(non_admin_config_file):
    """Test that read-only tools work for non-admin users."""
    import asyncio
    import gendoc.mcp.server as server

    # Test lookup_reference works
    result = asyncio.run(server.lookup_reference.fn("PM-TEST"))
    assert "Operation reservee" not in result

    # Test list_families works
    result = asyncio.run(server.list_families.fn())
    assert "Operation reservee" not in result
    # Verify it returns valid JSON
    result_dict = json.loads(result)
    assert "total" in result_dict
