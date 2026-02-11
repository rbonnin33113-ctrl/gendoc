---
phase: 12-hot-reload-mcp
plan: 01
subsystem: mcp-server
tags: [hot-reload, developer-experience, performance]
dependency_graph:
  requires: []
  provides: [hot-reload-mechanism]
  affects: [generate_slides, preview_generation]
tech_stack:
  added: []
  patterns: [mtime-tracking, importlib-reload, silent-when-unchanged]
key_files:
  created:
    - tests/test_hot_reload.py
  modified:
    - src/gendoc/mcp/server.py
decisions:
  - summary: "Use os.path.getmtime() for change detection instead of hash-based or file content comparison"
    rationale: "mtime is fast, reliable on Windows, and sufficient for dev workflow"
  - summary: "Silent logging (no output when modules unchanged) to avoid noise"
    rationale: "Most calls won't have changes; logging only on reload keeps console clean"
  - summary: "Reload order: modern_template, document_assembler, pptx_generator"
    rationale: "pptx_generator imports from the others, so dependencies must reload first"
metrics:
  duration_minutes: 3
  tasks_completed: 2
  files_modified: 2
  tests_added: 5
  completed_at: "2026-02-11T18:50:22Z"
---

# Phase 12 Plan 01: Hot-Reload MCP Summary

**One-liner:** mtime-based hot-reload for generator modules with logging and zero unnecessary reloads

## Objective

Complete and harden the hot-reload mechanism for MCP generator modules to allow developers to modify generator code and see changes reflected in the next MCP tool call without restarting the server.

## What Was Built

### 1. Hardened _reload_generators() (Task 1)

**File:** `src/gendoc/mcp/server.py`

**Changes:**
- Added `_module_mtimes: dict[str, float]` at module level to track file modification times
- Refactored `_reload_generators()` to:
  - Check file mtime via `os.path.getmtime()` before reloading
  - Compare against stored mtimes (skip reload if unchanged)
  - Log reloaded modules with ISO timestamps: `[gendoc hot-reload] Reloaded {module_name} ({timestamp})`
  - Return `generate_presentation` function reference
- Added `_reload_assembler_constants()` helper that:
  - Calls `_reload_generators()` to ensure modules are fresh
  - Returns tuple `(FAMILY_ORDER, FAMILY_DISPLAY_NAMES)` from reloaded `document_assembler`
- Updated `preview_generation` to use `_reload_assembler_constants()` instead of local import
- Removed unused import `run_generate_presentation`
- Added `import os` and `from datetime import datetime` for mtime tracking

**Behavior:**
- First call: Reloads all 3 modules (modern_template, document_assembler, pptx_generator), logs all 3
- Subsequent calls with no changes: Silent (no output, no unnecessary reloads)
- After file modification: Reloads only changed module(s), logs those modules

### 2. Unit Tests for Hot-Reload (Task 2)

**File:** `tests/test_hot_reload.py` (99 lines, 5 tests)

**Tests:**
1. `test_reload_generators_returns_callable` - Verifies return value is the `generate_presentation` function
2. `test_reload_tracks_mtimes` - Verifies `_module_mtimes` contains exactly 3 entries (all positive floats)
3. `test_reload_skips_unchanged_modules` - Verifies no output when called twice without changes (uses `capsys`)
4. `test_reload_detects_mtime_change` - Simulates mtime change, verifies reload and logging
5. `test_reload_assembler_constants_returns_tuple` - Verifies helper returns `(list, dict)` with correct types

**Coverage:** All core hot-reload behaviors tested without actual file modification

## Deviations from Plan

None - plan executed exactly as written.

## Success Criteria Met

- [x] RELOAD-01: `generate_slides` and `preview_generation` both call `_reload_generators()` before using generator code
- [x] RELOAD-02: mtime comparison prevents unnecessary reloads; no errors when modules unchanged; transparent to caller
- [x] Logging: Reloaded modules printed with name and ISO timestamp
- [x] Tests: 5 new tests validate the mechanism
- [x] All existing tests still pass (56 tests)
- [x] Full suite: 61 tests (56 + 5) passing in ~18 seconds

## Verification Results

```
✓ pytest tests/ -x -q                           → 61 passed in 17.95s
✓ pytest tests/test_hot_reload.py -v            → 5 passed in 1.43s
✓ _reload_generators() returns callable         → Function: generate_presentation
✓ Tracked modules count                         → Tracked modules: 3
✓ Unused import removed                         → grep returns nothing
✓ Reload logging present                        → [gendoc hot-reload] Reloaded...
```

## Key Technical Details

### mtime Tracking Dict
```python
_module_mtimes: dict[str, float] = {}
# Example content after first call:
# {
#   'H:/IA/Generateur de doc/src/gendoc/generators/modern_template.py': 1770831245.123,
#   'H:/IA/Generateur de doc/src/gendoc/generators/document_assembler.py': 1770831256.456,
#   'H:/IA/Generateur de doc/src/gendoc/generators/pptx_generator.py': 1770831267.789
# }
```

### Reload Logic
```python
current_mtime = os.path.getmtime(module_path)
if module_path not in _module_mtimes or _module_mtimes[module_path] != current_mtime:
    importlib.reload(module)
    _module_mtimes[module_path] = current_mtime
    timestamp = datetime.now().isoformat(timespec='seconds')
    print(f"[gendoc hot-reload] Reloaded {module_name} ({timestamp})")
```

### Integration Points
- `generate_slides` (line 279): `_generate = _reload_generators()`
- `preview_generation` (line 171): `FAMILY_ORDER, FAMILY_DISPLAY_NAMES = _reload_assembler_constants()`

## Impact

**Developer Experience:**
- Edit `modern_template.py`, `document_assembler.py`, or `pptx_generator.py`
- Call MCP tool (e.g., `generate_slides`)
- Changes reflected immediately without server restart
- Console shows which modules were reloaded and when

**Performance:**
- Zero overhead when no changes (mtime check is ~1μs per file)
- Reload only happens when files actually changed
- Silent operation prevents console spam

**Testing:**
- Hot-reload mechanism fully tested in isolation
- Test coverage for: return type, mtime tracking, skip-unchanged, detect-change, helper function
- No integration tests needed (unit tests sufficient for this mechanism)

## Commits

| Hash    | Message                                          | Files                          |
|---------|--------------------------------------------------|--------------------------------|
| 2550c3a | feat(12-01): add mtime-based hot-reload with logging | src/gendoc/mcp/server.py       |
| 68159a9 | test(12-01): add hot-reload unit tests           | tests/test_hot_reload.py       |

## Next Steps

This plan completes Phase 12-01. The hot-reload mechanism is now production-ready for developer use. Future enhancements could include:
- Configuration option to disable hot-reload in production
- Hot-reload for parsers/extractors/validators (currently only generators)
- Logging level control (verbose vs. silent)

## Self-Check: PASSED

**Files created:**
```
[✓] tests/test_hot_reload.py exists (99 lines, 5 tests)
```

**Files modified:**
```
[✓] src/gendoc/mcp/server.py contains _module_mtimes dict
[✓] src/gendoc/mcp/server.py contains mtime checking logic
[✓] src/gendoc/mcp/server.py contains _reload_assembler_constants
[✓] src/gendoc/mcp/server.py preview_generation uses reload mechanism
```

**Commits exist:**
```
[✓] 2550c3a feat(12-01): add mtime-based hot-reload with logging
[✓] 68159a9 test(12-01): add hot-reload unit tests
```

**Tests passing:**
```
[✓] 61/61 tests pass (56 existing + 5 new)
[✓] All hot-reload tests pass individually
[✓] No regressions in existing tests
```
