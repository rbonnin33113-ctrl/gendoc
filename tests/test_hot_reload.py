"""Tests for the hot-reload mechanism in MCP server.

These tests verify that the _reload_generators() function correctly:
- Returns a callable function
- Tracks module mtimes
- Skips reloading when modules are unchanged
- Detects and reloads when files are modified
- Provides assembler constants via helper function
"""

import pytest
import json
from pathlib import Path
import sys


@pytest.fixture(scope="module")
def setup_config(tmp_path_factory):
    """Create a valid config file so server.py can be imported."""
    # Create temporary Delagrave structure
    tmp_path = tmp_path_factory.mktemp("test_hot_reload")
    network_share = tmp_path / "Delagrave"
    network_share.mkdir()

    # Create required subdirectories
    (network_share / "references").mkdir()
    (network_share / "images").mkdir()
    template_dir = network_share / "Modele fiches - Powerpoint"
    template_dir.mkdir()

    # Create template file
    template_file = template_dir / "Modèle fiche technique vide - Ind J.potm"
    template_file.write_text("mock template")

    # Create config file
    config_path = tmp_path / "gendoc.json"
    config_data = {"network_share_path": str(network_share)}
    config_path.write_text(json.dumps(config_data, ensure_ascii=False), encoding='utf-8')

    # Monkeypatch cwd to tmp_path for config loading
    import os
    original_cwd = os.getcwd
    os.getcwd = lambda: str(tmp_path)

    # Clear any cached server module
    if 'gendoc.mcp.server' in sys.modules:
        del sys.modules['gendoc.mcp.server']

    yield tmp_path

    # Restore original cwd
    os.getcwd = original_cwd


def test_reload_generators_returns_callable(setup_config):
    """_reload_generators should return a callable function (generate_presentation)."""
    from gendoc.mcp.server import _reload_generators
    result = _reload_generators()
    assert callable(result), "Expected _reload_generators to return a callable function"
    assert result.__name__ == "generate_presentation", "Expected function to be generate_presentation"


def test_reload_tracks_mtimes(setup_config):
    """After calling _reload_generators, _module_mtimes should contain 3 entries."""
    from gendoc.mcp.server import _reload_generators, _module_mtimes
    # Clear any existing mtimes
    _module_mtimes.clear()

    # Call reload
    _reload_generators()

    # Verify we tracked 3 modules
    assert len(_module_mtimes) == 3, f"Expected 3 tracked modules, got {len(_module_mtimes)}"

    # Verify all mtimes are positive floats
    for path, mtime in _module_mtimes.items():
        assert isinstance(mtime, float), f"Expected mtime to be float, got {type(mtime)}"
        assert mtime > 0, f"Expected positive mtime, got {mtime}"


def test_reload_skips_unchanged_modules(setup_config):
    """When called twice without file changes, second call should not re-track mtimes."""
    from gendoc.mcp.server import _reload_generators, _module_mtimes
    # First call (may populate mtimes)
    _reload_generators()

    # Capture mtimes after first call
    initial_mtimes = dict(_module_mtimes)

    # Second call - modules unchanged, mtimes should remain same
    _reload_generators()

    # Verify mtimes are unchanged (no reload occurred)
    assert _module_mtimes == initial_mtimes, \
        "Expected mtimes to remain unchanged when modules are unchanged"


def test_reload_detects_mtime_change(setup_config):
    """When a module's mtime changes, _reload_generators should reload it and update mtime."""
    from gendoc.mcp.server import _reload_generators, _module_mtimes
    # First call to populate mtimes
    _reload_generators()

    # Simulate a file change by setting one mtime to 0.0
    first_path = list(_module_mtimes.keys())[0]
    old_mtime = _module_mtimes[first_path]
    _module_mtimes[first_path] = 0.0

    # Call reload again
    _reload_generators()

    # Verify mtime was updated (no longer 0.0)
    assert _module_mtimes[first_path] != 0.0, "Expected mtime to be updated after reload"
    assert _module_mtimes[first_path] == old_mtime, \
        f"Expected mtime to be restored to {old_mtime}, got {_module_mtimes[first_path]}"


def test_reload_assembler_constants_returns_tuple(setup_config):
    """_reload_assembler_constants should return (FAMILY_ORDER, FAMILY_DISPLAY_NAMES)."""
    from gendoc.mcp.server import _reload_assembler_constants
    result = _reload_assembler_constants()

    # Verify it's a tuple with 2 elements
    assert isinstance(result, tuple), "Expected tuple return value"
    assert len(result) == 2, "Expected tuple with 2 elements"

    family_order, family_display_names = result

    # Verify FAMILY_ORDER is a list
    assert isinstance(family_order, list), "Expected FAMILY_ORDER to be a list"
    assert len(family_order) > 0, "Expected non-empty FAMILY_ORDER"

    # Verify FAMILY_DISPLAY_NAMES is a dict
    assert isinstance(family_display_names, dict), "Expected FAMILY_DISPLAY_NAMES to be a dict"
    assert len(family_display_names) > 0, "Expected non-empty FAMILY_DISPLAY_NAMES"
