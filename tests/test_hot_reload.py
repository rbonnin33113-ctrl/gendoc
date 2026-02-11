"""Tests for the hot-reload mechanism in MCP server.

These tests verify that the _reload_generators() function correctly:
- Returns a callable function
- Tracks module mtimes
- Skips reloading when modules are unchanged
- Detects and reloads when files are modified
- Provides assembler constants via helper function
"""

import pytest
from gendoc.mcp.server import _reload_generators, _reload_assembler_constants, _module_mtimes


def test_reload_generators_returns_callable():
    """_reload_generators should return a callable function (generate_presentation)."""
    result = _reload_generators()
    assert callable(result), "Expected _reload_generators to return a callable function"
    assert result.__name__ == "generate_presentation", "Expected function to be generate_presentation"


def test_reload_tracks_mtimes():
    """After calling _reload_generators, _module_mtimes should contain 3 entries."""
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


def test_reload_skips_unchanged_modules(capsys):
    """When called twice without file changes, second call should produce no output."""
    # First call (may produce output)
    _reload_generators()

    # Clear captured output
    capsys.readouterr()

    # Second call - modules unchanged, should be silent
    _reload_generators()

    # Verify no reload messages
    captured = capsys.readouterr()
    assert "[gendoc hot-reload]" not in captured.out, \
        "Expected no reload output when modules are unchanged"


def test_reload_detects_mtime_change(capsys):
    """When a module's mtime changes, _reload_generators should reload it and log."""
    # First call to populate mtimes
    _reload_generators()
    capsys.readouterr()  # Clear output

    # Simulate a file change by setting one mtime to 0.0
    first_path = list(_module_mtimes.keys())[0]
    old_mtime = _module_mtimes[first_path]
    _module_mtimes[first_path] = 0.0

    # Call reload again
    _reload_generators()

    # Capture output
    captured = capsys.readouterr()

    # Verify reload message was logged
    assert "[gendoc hot-reload] Reloaded" in captured.out, \
        "Expected reload message when mtime changed"

    # Verify mtime was updated (no longer 0.0)
    assert _module_mtimes[first_path] != 0.0, "Expected mtime to be updated after reload"
    assert _module_mtimes[first_path] == old_mtime, \
        f"Expected mtime to be restored to {old_mtime}, got {_module_mtimes[first_path]}"


def test_reload_assembler_constants_returns_tuple():
    """_reload_assembler_constants should return (FAMILY_ORDER, FAMILY_DISPLAY_NAMES)."""
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
