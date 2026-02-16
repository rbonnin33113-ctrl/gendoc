---
phase: 22-configuration-path-resolution
plan: 02
subsystem: configuration
tags: [config, path-resolution, mcp-server, deployment]
dependency_graph:
  requires: [config_loader]
  provides: [config_integrated_server]
  affects: [all_mcp_tools]
tech_stack:
  added: []
  patterns: [module_level_config, graceful_startup_failure]
key_files:
  created:
    - tests/test_mcp_server_config.py
  modified:
    - src/gendoc/mcp/server.py
    - tests/test_hot_reload.py
decisions:
  - Config loading at module level (startup validation)
  - OUTPUT_DIR remains local for Phase 22 (Phase 23 will refactor)
  - PROJECT_ROOT kept for output path resolution (used at lines 442, 475, 652, 719)
  - Graceful sys.exit(1) with clear error if config missing
metrics:
  duration_minutes: 3
  completed_date: 2026-02-16
  commits: 3
  tests_added: 4
  lines_added: 236
  lines_modified: 60
---

# Phase 22 Plan 02: MCP Server Path Resolution Integration Summary

**One-liner:** MCP server integrated with config_loader, resolving all resource paths from network share config at startup with graceful failure handling.

## Objective Achieved

Replaced hardcoded PROJECT_ROOT-based paths in server.py with config-resolved paths from gendoc.json, enabling MCP server to use network share paths with validation at startup and clear error messages when config is missing or invalid.

## Tasks Completed

### Task 1: Refactor server.py to use config_loader for path resolution
**Status:** ✅ Complete
**Commit:** 731d79a
**Files:** src/gendoc/mcp/server.py

Integrated config_loader into server.py at module level (lines 110-124):
- **Config Loading**: Import load_config and ConfigurationError, call load_config() at startup
- **Path Resolution**: Extract REFERENCES_DIR, IMAGES_DIR, TEMPLATE_PATH from config dict
- **OUTPUT_DIR**: Kept as Path("output").resolve() for Phase 22 (Phase 23 will refactor to per-devis subdirs)
- **PROJECT_ROOT**: Added at line 127 for output path resolution (used by tools at lines 442, 475, 652, 719)
- **Error Handling**: Try/except ConfigurationError with clear error messages and sys.exit(1)
- **Graceful Failure**: Prints [FATAL] messages to stderr with guidance to create gendoc.json

**Key implementation details:**
- Config loading happens once at module import (cached by Python)
- All 12 MCP tool functions already receive paths from these constants (no changes needed)
- Server cannot start without valid config (fail-fast validation)
- Clear error messages guide user to fix config issues

**Verification passed:**
- ✅ Module imports successfully with valid gendoc.json present
- ✅ Module exits gracefully with error if gendoc.json missing
- ✅ REFERENCES_DIR, IMAGES_DIR, TEMPLATE_PATH resolve to config-specified paths
- ✅ OUTPUT_DIR remains as Path("output").resolve()

### Task 2: Create integration tests for server config loading
**Status:** ✅ Complete
**Commit:** 2fba8db
**Files:** tests/test_mcp_server_config.py

Created 4 integration tests (all pass):
1. **test_server_loads_config_successfully**: Validates server loads config and paths resolve correctly
2. **test_server_uses_config_paths_in_tools**: Validates tools use config-resolved REFERENCES_DIR
3. **test_server_output_dir_local**: Validates OUTPUT_DIR is local (Phase 22 behavior)
4. **test_server_fails_without_config**: Validates graceful exit with SystemExit(1) when config missing

**Test infrastructure:**
- Uses tmp_path and monkeypatch fixtures for isolation
- valid_structure fixture creates complete Delagrave directory structure
- config_file fixture handles module state cleanup (removes gendoc.* from sys.modules)
- No file system pollution - all tests clean up automatically

**Verification passed:**
- ✅ All 4 tests pass in 1.5s
- ✅ Tests validate config-based operation
- ✅ Tests validate OUTPUT_DIR remains local (Phase 22 behavior)
- ✅ Tests validate graceful failure without config

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking Issue] test_hot_reload.py incompatible with module-level config loading**
- **Found during:** Running full test suite after Task 2
- **Issue:** test_hot_reload.py imported server.py at module level (line 12), triggering config loading during test collection. When no config file exists, server.py calls sys.exit(1), causing pytest to fail with INTERNALERROR before any tests run.
- **Fix:** Refactored test_hot_reload.py to:
  - Move server.py imports inside test functions (not module level)
  - Add setup_config fixture (module-scoped) to create valid config before imports
  - Add module state cleanup to prevent test interference
- **Files modified:** tests/test_hot_reload.py (+51 lines, -6 lines)
- **Commit:** bf4b88a
- **Rationale:** Module-level config loading in server.py is correct design (fail-fast validation). Tests must adapt to this pattern by creating config before importing.

## Verification Results

**Overall verification completed:**
- ✅ server.py successfully imports with valid gendoc.json present
- ✅ server.py exits gracefully with error if gendoc.json missing
- ✅ REFERENCES_DIR, IMAGES_DIR, TEMPLATE_PATH resolve to config-specified paths
- ✅ OUTPUT_DIR remains as Path("output").resolve()
- ✅ All 135 tests pass (123 original + 8 config_loader + 4 server_config integration)
- ✅ Integration tests in test_mcp_server_config.py pass
- ✅ Zero regressions (all existing tests still pass)

**Success criteria met:**
- ✅ server.py replaces hardcoded PROJECT_ROOT paths with config-loaded paths
- ✅ Config loading happens at module import (startup)
- ✅ ConfigurationError caught and reported clearly
- ✅ All MCP tools receive config-resolved paths (no code changes needed in tools)
- ✅ OUTPUT_DIR remains local for Phase 22 (Phase 23 will refactor)
- ✅ Existing 123 tests pass (zero regressions)
- ✅ Integration tests validate config-based operation

## Self-Check: PASSED

**Created files verification:**
```
FOUND: tests/test_mcp_server_config.py
```

**Modified files verification:**
```
FOUND: src/gendoc/mcp/server.py
FOUND: tests/test_hot_reload.py
```

**Commits verification:**
```
FOUND: 731d79a (refactor: server.py config integration)
FOUND: 2fba8db (test: integration tests)
FOUND: bf4b88a (fix: test_hot_reload.py compatibility)
```

## Key Decisions

1. **Config loading at module level (startup validation)**
   - Rationale: Fail-fast approach catches config issues before any operations
   - Impact: Server cannot start without valid config, clear error messages guide user
   - Alternative considered: Lazy loading (rejected - would delay error discovery)

2. **OUTPUT_DIR remains local for Phase 22**
   - Rationale: Phase 23 will refactor output to per-devis subdirectories
   - Impact: OUTPUT_DIR = Path("output").resolve() for now, not from config
   - Note: Documented in code comment for Phase 23 team

3. **PROJECT_ROOT kept for output path resolution**
   - Rationale: Lines 442, 475, 652, 719 use PROJECT_ROOT for relative output paths
   - Impact: Added PROJECT_ROOT calculation after config block
   - Note: Phase 23 will remove this when output paths move to config

4. **Graceful sys.exit(1) on config error**
   - Rationale: MCP server cannot function without valid config
   - Impact: Clear [FATAL] error messages with actionable guidance
   - Alternative considered: Return error to MCP client (rejected - server not started yet)

## Technical Notes

**Config loading flow:**
```python
# Module level (lines 110-127)
try:
    _config = load_config()
    REFERENCES_DIR = _config["references_dir"]
    IMAGES_DIR = _config["images_dir"]
    TEMPLATE_PATH = _config["template_path"]
    OUTPUT_DIR = Path("output").resolve()  # Phase 22 behavior
except ConfigurationError as e:
    print(f"[FATAL] Configuration error: {e}", file=sys.stderr)
    print("[FATAL] MCP server will not start. Please create gendoc.json.", file=sys.stderr)
    sys.exit(1)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
```

**MCP tool functions:**
- No changes needed - all tools already use REFERENCES_DIR, IMAGES_DIR, TEMPLATE_PATH parameters
- Tools receive config-resolved paths automatically
- Example: `lookup_reference(code)` calls `find_product(code, REFERENCES_DIR)`

**Test isolation pattern:**
```python
# Before importing server.py in tests:
if 'gendoc.mcp.server' in sys.modules:
    del sys.modules['gendoc.mcp.server']

# After test:
modules_to_remove = [key for key in sys.modules if key.startswith('gendoc')]
for module_key in modules_to_remove:
    del sys.modules[module_key]
```

## Next Steps

**Phase 22 Plan 03 (if exists):** Continue path resolution work, or move to Phase 23.

**Phase 23 (Output Refactoring):**
1. Move OUTPUT_DIR to config (per-devis subdirectories)
2. Remove PROJECT_ROOT constant (no longer needed)
3. Update lines 442, 475, 652, 719 to use config-based output paths
4. Update MCP tools to use config-based output directory structure

**Deployment readiness:**
- ✅ MCP server ready for multi-workstation deployment
- ✅ Each workstation creates gendoc.json pointing to network share
- ✅ Clear error messages guide users through setup
- ✅ Config validation ensures correct network share structure

## Impact Summary

**Files created:** 1 (test_mcp_server_config.py)
**Files modified:** 2 (server.py, test_hot_reload.py)
**Lines added:** 236 (3 server.py, 185 test_mcp_server_config.py, 51 test_hot_reload.py)
**Lines modified:** 60 (server.py config block + test_hot_reload.py refactoring)
**Tests added:** 4 (all pass, 1.5s)
**Total tests:** 135 (123 original + 8 config_loader + 4 server_config)

**Network share paths now used:**
- REFERENCES_DIR: {network_share}/references (317 products, 11 families)
- IMAGES_DIR: {network_share}/images (family-specific subdirectories)
- TEMPLATE_PATH: {network_share}/Modele fiches - Powerpoint/Modèle fiche technique vide - Ind J.potm

**Deployment behavior:**
- Config search order: CWD/gendoc.json → ~/.gendoc.json → server.py/gendoc.json
- Server exits with clear error if config missing or invalid
- All MCP tools use config-resolved paths automatically
- Zero code changes needed in tool functions (paths passed as parameters)
