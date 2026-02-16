---
phase: 24-access-control
plan: 01
subsystem: access-control
tags: [security, admin-guard, crud, config]
dependency_graph:
  requires: [config-loader, mcp-server]
  provides: [admin-guard]
  affects: [crud-tools]
tech_stack:
  added: []
  patterns: [admin-check-guard]
key_files:
  created: []
  modified:
    - tests/test_mcp_server_config.py
decisions: []
metrics:
  duration_min: 2
  tasks_completed: 1
  tests_added: 0
  tests_fixed: 3
  completed_date: 2026-02-16
---

# Phase 24 Plan 01: Admin Guard on CRUD Tools Summary

**One-liner:** Fixed FastMCP tool test calls to use .fn attribute for admin guard verification

## What Was Done

### Implementation Already Complete

The admin guard implementation was already complete from a previous session:
- `_require_admin(operation_name)` helper function exists in server.py (lines 174-188)
- All three CRUD tools call the guard as their first line:
  - `add_reference` (line 928)
  - `update_reference` (line 1077)
  - `delete_reference` (line 1193)
- Tests for admin guard behavior existed in test_mcp_server_config.py (lines 265-324)

### Bug Fixed (Deviation Rule 1)

**Issue:** Tests were failing because FastMCP decorators wrap functions in `FunctionTool` objects, requiring `.fn` attribute access to call the underlying function.

**Fix Applied:**
- Updated `test_crud_blocked_when_admin_false` to use `server.add_reference.fn()`, `server.update_reference.fn()`, `server.delete_reference.fn()`
- Updated `test_crud_allowed_when_admin_true` to use `server.add_reference.fn()`
- Updated `test_readonly_tools_work_without_admin` to use `server.lookup_reference.fn()` and `server.list_families.fn()`

**Commit:** `55db153` - fix(24-01): correct MCP tool test calls to use .fn attribute

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed MCP tool test calls**
- **Found during:** Test verification (Task 1)
- **Issue:** Tests calling FastMCP-decorated functions directly (e.g., `server.add_reference()`) instead of using `.fn` attribute
- **Root cause:** FastMCP @mcp.tool() decorator wraps functions in FunctionTool objects
- **Fix:** Added `.fn` attribute access to all test function calls
- **Files modified:** tests/test_mcp_server_config.py
- **Commit:** 55db153

## Test Results

### Admin Guard Tests (7/7 passed)
- `test_server_loads_config_successfully` ✓
- `test_server_uses_config_paths_in_tools` ✓
- `test_server_output_dir_local` ✓
- `test_server_fails_without_config` ✓
- `test_crud_blocked_when_admin_false` ✓ (fixed)
- `test_crud_allowed_when_admin_true` ✓ (fixed)
- `test_readonly_tools_work_without_admin` ✓ (fixed)

### Full Test Suite
- **Total:** 138 tests
- **Passed:** 138
- **Failed:** 0
- **Duration:** 22.11s

## Verification Commands

All plan verification commands passed:

```bash
# Verify _require_admin helper exists
python -c "from gendoc.mcp.server import _require_admin; print('Helper exists')"
# Output: Helper exists and is callable

# Verify all CRUD tools are guarded
python -c "import gendoc.mcp.server as s; import inspect; src = inspect.getsource(s.add_reference.fn); assert '_require_admin' in src; print('OK: add_reference guarded')"
# Output: OK: add_reference guarded

python -c "import gendoc.mcp.server as s; import inspect; src = inspect.getsource(s.update_reference.fn); assert '_require_admin' in src; print('OK: update_reference guarded')"
# Output: OK: update_reference guarded

python -c "import gendoc.mcp.server as s; import inspect; src = inspect.getsource(s.delete_reference.fn); assert '_require_admin' in src; print('OK: delete_reference guarded')"
# Output: OK: delete_reference guarded
```

## Behavior

### Admin Mode (admin=true)
- CRUD operations (add_reference, update_reference, delete_reference) execute normally
- May fail for business reasons (duplicate code, not found, etc.) but NOT blocked by admin check

### Normal Mode (admin=false)
- CRUD operations immediately return: `{"error": "Operation reservee a l'administrateur", "resume": "ECHEC {operation}: mode administrateur requis"}`
- Read-only tools (lookup_reference, search_references, list_families, analyze_devis, generate_slides, preview_generation, open_sp_selector, load_sp_selection, create_custom_product) work normally

## Files Modified

### tests/test_mcp_server_config.py
- Fixed 3 test functions to use `.fn` attribute when calling FastMCP-decorated tools
- All 7 tests now pass

## Self-Check: PASSED

**Files checked:**
- tests/test_mcp_server_config.py exists ✓

**Commits verified:**
- 55db153 exists ✓

**Tests verified:**
- 7/7 admin guard tests pass ✓
- 138/138 full test suite passes ✓

## Success Criteria: MET

- [x] _require_admin helper checks _config["admin"] and returns JSON error for non-admins
- [x] All 3 CRUD tools gate on admin before any business logic
- [x] Non-admin CRUD returns correct error format
- [x] Admin CRUD proceeds normally (existing behavior preserved)
- [x] Read-only tools unaffected by admin flag
- [x] 7 tests pass in test_mcp_server_config.py (4 existing + 3 new)
- [x] Full test suite passes with zero regressions (138/138)

## Notes

The plan's Task 1 and Task 2 were already completed in a previous session. This execution only fixed a bug in the test implementation where FastMCP tool calls were missing the `.fn` attribute. The admin guard functionality itself was already working correctly.
