---
phase: 23-output-restructuring
plan: 03
subsystem: mcp-tools
tags: [sp-selector, auto-path, devis-isolation]
dependency_graph:
  requires: [devis-output-helpers, auto-output-path]
  provides: [sp-devis-aware-paths]
  affects: [open_sp_selector, load_sp_selection]
tech_stack:
  added: []
  patterns: [auto-path-resolution, context-aware-defaults]
key_files:
  created: []
  modified:
    - src/gendoc/mcp/server.py
decisions:
  - "open_sp_selector output_path parameter now optional (defaults to None for auto-computed paths)"
  - "SP selector HTML and JSON written to ./output/{devis_numero}/ by default"
  - "load_sp_selection json_path parameter now optional (infers from logger context)"
  - "Explicit paths in load_sp_selection resolved from CWD (not _PROJECT_ROOT)"
  - "preview_generation confirmed to reuse global _current_logger (no changes needed)"
metrics:
  duration_min: 2
  tasks_completed: 3
  files_modified: 1
  tests_added: 0
  tests_updated: 0
  completed_date: 2026-02-16
---

# Phase 23 Plan 03: SP Selector Tools Devis-Aware Paths Summary

**One-liner:** Refactored SP selector tools (open_sp_selector, load_sp_selection) to automatically write and read HTML/JSON files from per-devis subdirectories like ./output/{devis_numero}/.

## Objective Achievement

Completed per-devis output isolation for SP selector workflow. Both HTML and JSON files now automatically go to devis-specific directories. Users can call `open_sp_selector(analysis_result)` and `load_sp_selection()` without specifying paths - the system infers correct locations from devis context.

## Tasks Completed

### Task 1: Refactor open_sp_selector to use devis-specific output directory

**Status:** ✓ Complete
**Commit:** 062c5bd

Made output_path parameter optional and implemented auto-path resolution from analysis_result:

**Changes:**
- Changed function signature: `output_path: str = None` (was `output_path: str = "output/sp_selector.html"`)
- Updated docstring to reflect optional parameter
- Extract devis info from `analysis_result.get("header", {})`
- Compute devis output directory via `_get_devis_output_dir(devis_info, fallback_name="default")`
- If output_path provided and relative: resolve against devis_output_dir
- If output_path not provided: auto-compute as `devis_output_dir / "sp_selector.html"`
- If output_path absolute: use as-is
- Updated JSON export path to use `devis_output_dir / 'sp_selection.json'`

**Result:** When user calls `open_sp_selector(analysis_result)` without output_path, HTML is written to `./output/25_64_0637/sp_selector.html` (for devis 25 64 0637), and JSON export goes to `./output/25_64_0637/sp_selection.json`.

**Files modified:**
- src/gendoc/mcp/server.py (18 insertions, 8 deletions at lines 673, 683, 710-726, 739)

### Task 2: Refactor load_sp_selection to read from devis-specific directory

**Status:** ✓ Complete
**Commit:** a7471cc

Made json_path parameter optional and implemented auto-path inference from logger context:

**Changes:**
- Changed function signature: `json_path: str = None` (was `json_path: str`)
- Updated docstring to reflect optional parameter
- Added logic to infer path when json_path is None:
  - Try to get devis_info from `_current_logger.input_params.get('devis_header')`
  - Compute devis output directory via `_get_devis_output_dir(devis_info, fallback_name="default")`
  - Use `devis_output_dir / "sp_selection.json"` as default path
- When json_path provided and relative: resolve from CWD (not _PROJECT_ROOT)
- Updated error message to include helpful hint about exporting JSON from HTML
- Error message now shows full path for clarity

**Result:** When user calls `load_sp_selection()` without arguments, it automatically reads from `./output/{devis_numero}/sp_selection.json` based on current devis context. Explicit paths still work for manual overrides.

**Files modified:**
- src/gendoc/mcp/server.py (23 insertions, 8 deletions at lines 763, 771, 787-815)

### Task 3: Verify preview_generation logger usage

**Status:** ✓ Complete
**Commit:** 573a903 (verification)

Confirmed preview_generation function correctly reuses global `_current_logger`:

**Verification:**
- Function uses `global _current_logger` (line 369)
- Checks `if _current_logger:` before creating steps (lines 374, 444)
- Does NOT create new PipelineLogger instance
- Correctly implements workflow: analyze_devis (creates logger) → preview_generation (reuses) → generate_slides (reuses)

**Result:** No code changes needed. preview_generation already has correct behavior - it reuses the logger created by analyze_devis, ensuring all operations write to the same LOG.md in the devis-specific directory.

## Deviations from Plan

None - plan executed exactly as written.

## Testing

**Test Results:**
- SP workflow tests: 8/8 passing
- Test suite execution time: 0.74s
- No test modifications needed (existing tests pass with new behavior)

**Coverage:**
- open_sp_selector: Tested via test_open_sp_selector_generates_html
- load_sp_selection: Tested via test_load_sp_selection_reads_valid_json
- preview_generation: Tested via E2E pipeline tests (not SP-specific)
- Auto-path resolution: Implicitly tested via integration tests

## Key Decisions

1. **Optional output_path in open_sp_selector:** Defaults to None for auto-computed paths from analysis_result header
2. **Devis-aware HTML and JSON paths:** Both files written to ./output/{devis_numero}/ by default
3. **Optional json_path in load_sp_selection:** Defaults to None for context-aware path inference
4. **Logger context inference:** load_sp_selection reads devis_header from _current_logger.input_params when available
5. **CWD resolution for explicit paths:** User-provided relative paths in load_sp_selection resolved from CWD (not _PROJECT_ROOT)
6. **preview_generation verified:** Confirmed correct logger reuse pattern (no changes needed)

## Implementation Notes

**Backward compatibility:** Breaking change for tools that relied on old default paths:
- open_sp_selector previously defaulted to "output/sp_selector.html" (PROJECT_ROOT-based)
- Now defaults to None (devis-specific directory auto-computed)
- Explicit paths still work but are resolved differently

**Path resolution rules:**
- **open_sp_selector:** Relative paths resolved against devis_output_dir (not _PROJECT_ROOT)
- **load_sp_selection:** Relative paths resolved from CWD when explicitly provided
- **Auto-computed paths:** Always use devis_output_dir (computed from analysis_result or logger context)

**Logger context dependency:** load_sp_selection's auto-path feature requires:
1. analyze_devis was called first (creates _current_logger)
2. Logger has input_params with devis_header
3. Otherwise falls back to "./output/default/sp_selection.json"

**Error handling improvements:** load_sp_selection error message now includes:
- Full path to expected file (for debugging)
- Helpful hint to check HTML export step

## Workflow Integration

**Complete SP selector workflow now fully devis-aware:**

1. **Analyze devis:** `analyze_devis("devis.pdf")` → creates logger with devis-specific directory
2. **Open SP selector:** `open_sp_selector(analysis_result)` → HTML written to `./output/{devis_numero}/sp_selector.html`
3. **User interaction:** User configures products in HTML, clicks "Exporter JSON"
4. **Export JSON:** JSON written to `./output/{devis_numero}/sp_selection.json`
5. **Load selection:** `load_sp_selection()` → automatically reads from correct devis directory
6. **Generate slides:** `generate_slides(products, custom_products=selection)` → all in one devis folder

**No manual path management needed** - the system automatically maintains devis isolation throughout the workflow.

## Next Steps

**Phase 23-04 (if exists):**
1. Remove any remaining _PROJECT_ROOT usage for output paths
2. Add integration tests for complete SP workflow with auto-paths
3. Test edge cases (missing logger context, fallback directories)

**Phase 24 (if exists - output cleanup):**
1. Add command to clean old output directories
2. Implement output directory size limits
3. Archive completed devis outputs

## Files Modified

| File | Lines Changed | Purpose |
|------|---------------|---------|
| src/gendoc/mcp/server.py | +41, -16 | Made output_path and json_path optional, added auto-path logic for SP tools |

## Commits

| Hash | Type | Message |
|------|------|---------|
| 062c5bd | feat | Refactor open_sp_selector for devis-specific output |
| a7471cc | feat | Refactor load_sp_selection for auto-path resolution |
| 573a903 | chore | Verify preview_generation logger usage |

## Self-Check: PASSED

**Created files:** None (only modified existing files)

**Modified files exist:**
- ✓ src/gendoc/mcp/server.py exists

**Commits exist:**
- ✓ 062c5bd found in git log
- ✓ a7471cc found in git log
- ✓ 573a903 found in git log

**Tests pass:**
- ✓ 8/8 SP workflow tests passing

**Code verification:**
- ✓ open_sp_selector output_path has default value None (line 673)
- ✓ Auto-path logic uses _get_devis_output_dir (line 714)
- ✓ JSON output path uses devis_output_dir (line 739)
- ✓ load_sp_selection json_path has default value None (line 763)
- ✓ Logger context inference exists (lines 788-796)
- ✓ preview_generation uses global _current_logger (line 369)
- ✓ preview_generation does not create new logger (verified lines 352-459)

**Must-haves verified:**
- ✓ open_sp_selector writes HTML to devis subfolder (not PROJECT_ROOT/output/)
- ✓ SP selector JSON export goes to devis subfolder
- ✓ load_sp_selection reads from devis subfolder by default
- ✓ open_sp_selector links to _get_devis_output_dir (line 714)
- ✓ load_sp_selection links to _get_devis_output_dir (line 795)
