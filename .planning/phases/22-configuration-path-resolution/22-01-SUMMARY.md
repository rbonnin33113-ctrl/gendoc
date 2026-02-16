---
phase: 22-configuration-path-resolution
plan: 01
subsystem: configuration
tags: [config, validation, multi-workstation, deployment]
dependency_graph:
  requires: []
  provides: [config_loader, network_share_validation]
  affects: [mcp_server]
tech_stack:
  added: [json_config]
  patterns: [config_search_hierarchy, path_validation]
key_files:
  created:
    - src/gendoc/utils/config_loader.py
    - tests/test_config_loader.py
  modified: []
decisions:
  - Config search order: CWD -> home dir -> server.py dir (dev fallback)
  - Template name encoding: Modèle with accent (UTF-8)
  - Admin flag defaults to false (normal user mode)
  - Validation at load time (fail fast on startup)
metrics:
  duration_minutes: 2
  completed_date: 2026-02-16
  commits: 2
  tests_added: 8
  lines_added: 405
---

# Phase 22 Plan 01: Configuration Loader System Summary

**One-liner:** JSON-based config loader with network share validation enabling multi-workstation deployment with path resolution.

## Objective Achieved

Created configuration system that reads gendoc.json and validates network share accessibility, enabling multi-workstation deployment where each PC has local config pointing to shared network data.

## Tasks Completed

### Task 1: Create config_loader module with search, load, and validation
**Status:** ✅ Complete
**Commit:** e1aaf96
**Files:** src/gendoc/utils/config_loader.py

Implemented config_loader.py with:
- **Config Search Strategy** (in order): CWD/gendoc.json → ~/.gendoc.json → server.py/gendoc.json
- **load_config()** function: searches, reads JSON, validates structure, returns resolved paths
- **Validation**: requires network_share_path field, validates path exists, validates subdirectories (references/, images/, Modele fiches - Powerpoint/), validates template file exists
- **Return Structure**: dict with 6 keys (config_path, network_share_path, references_dir, images_dir, template_path, admin)
- **ConfigurationError Exception**: custom exception for clear, actionable error messages

**Key implementation details:**
- Uses pathlib.Path for all path operations
- Template name: "Modèle fiche technique vide - Ind J.potm" (with accent)
- Error messages tell user exactly what to create/fix
- Admin flag defaults to false if not specified

**Verification passed:**
- Module imports successfully
- Created test config with real Delagrave path
- Loaded config returns correct references_dir path
- Missing config raises clear error with example JSON
- Invalid network_share_path raises error with specific path

### Task 2: Create comprehensive unit tests for config_loader
**Status:** ✅ Complete
**Commit:** 4881309
**Files:** tests/test_config_loader.py

Created 8 unit tests covering:
1. **test_load_config_from_cwd**: Config loaded from current working directory
2. **test_load_config_from_home**: Config loaded from home directory (using monkeypatch)
3. **test_load_config_missing**: Error with guidance when config not found
4. **test_validate_network_share_not_exists**: Error when network path doesn't exist
5. **test_validate_missing_references_dir**: Error when references/ subdirectory missing
6. **test_validate_missing_template**: Error when template file missing
7. **test_admin_flag_defaults_false**: Admin flag defaults to False when not specified
8. **test_admin_flag_explicit_true**: Admin flag can be set to True explicitly

**Test infrastructure:**
- Uses tmp_path and monkeypatch fixtures for isolation
- valid_structure fixture creates complete network share structure
- No file system pollution - all tests clean up automatically

**Verification passed:**
- All 8 tests pass in 0.09s
- Coverage: config search, validation errors, admin flag handling
- Tests use proper fixtures for clean isolation

## Deviations from Plan

None - plan executed exactly as written.

## Verification Results

**Overall verification completed:**
- ✅ config_loader.py module exists and exports load_config, ConfigurationError
- ✅ All 8 unit tests in test_config_loader.py pass
- ✅ Manual test: Create valid gendoc.json, load_config() returns correct paths
- ✅ Manual test: Remove config, load_config() raises clear error
- ✅ Manual test: Invalid network_share_path raises error

**Success criteria met:**
- ✅ Config loader searches CWD → home dir → server.py dir for gendoc.json
- ✅ Missing config produces error: "Create gendoc.json with: {example JSON}"
- ✅ Invalid network_share_path produces error with specific path
- ✅ Missing subdirectories produce error with specific missing directory
- ✅ Missing template produces error with template filename
- ✅ load_config() returns dict with 6 keys (all paths resolved and validated)
- ✅ 8 unit tests pass covering all validation scenarios

## Self-Check: PASSED

**Created files verification:**
```
FOUND: src/gendoc/utils/config_loader.py
FOUND: tests/test_config_loader.py
```

**Commits verification:**
```
FOUND: e1aaf96 (feat: config_loader module)
FOUND: 4881309 (test: unit tests)
```

## Key Decisions

1. **Config search order**: CWD first (deployment), home second (user), server.py dir third (dev)
   - Rationale: Allows workstation-specific config without modifying codebase
   - Impact: Each PC can have gendoc.json pointing to network share

2. **Template name encoding**: "Modèle fiche technique vide - Ind J.potm" with UTF-8 accent
   - Rationale: Matches actual file name in production
   - Impact: Validation ensures correct template file

3. **Admin flag defaults to false**: Normal user mode by default
   - Rationale: Most workstations are read-only consumers
   - Impact: Admin features (CRUD) require explicit opt-in

4. **Validation at load time**: Fail fast on startup
   - Rationale: Better to catch config issues immediately than during operation
   - Impact: Clear error messages guide user to fix config before MCP server starts

## Technical Notes

**Config file structure:**
```json
{
    "network_share_path": "H:/IA/Generateur de doc/Delagrave",
    "admin": false
}
```

**Returned paths:**
- `config_path`: Where config was found (for debugging)
- `network_share_path`: Base path from config (resolved)
- `references_dir`: network_share_path / "references"
- `images_dir`: network_share_path / "images"
- `template_path`: network_share_path / "Modele fiches - Powerpoint" / "Modèle fiche technique vide - Ind J.potm"
- `admin`: Boolean flag

**Error handling:**
- ConfigurationError with actionable messages
- Specific path included in error (tells user exactly what's missing)
- Example JSON in error message (tells user how to create config)

## Next Steps

**Integration tasks (Phase 22 Plan 02):**
1. Update server.py to use load_config() instead of hardcoded paths
2. Replace PROJECT_ROOT/REFERENCES_DIR/IMAGES_DIR/TEMPLATE_PATH globals
3. Handle ConfigurationError on startup (return to MCP client)
4. Test with actual network share path
5. Update documentation with deployment instructions

**Dependencies:**
- server.py will import from gendoc.utils.config_loader
- All MCP tools will use paths from config instead of globals
- SP server may need config support for multi-workstation SP selection

## Impact Summary

**Files created:** 2 (config_loader.py, test_config_loader.py)
**Lines added:** 405 (187 source, 218 tests)
**Tests added:** 8 (all pass, 0.09s)
**Public API:** load_config() → ConfigDict, ConfigurationError exception

**Deployment readiness:**
- Config system ready for multi-workstation deployment
- Clear error messages guide users through setup
- Validated structure ensures correct network share
- Admin flag enables role-based features
