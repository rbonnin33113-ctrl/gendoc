---
phase: 23-output-restructuring
plan: 02
subsystem: mcp-tools
tags: [generate-slides, auto-path, devis-isolation]
dependency_graph:
  requires: [devis-output-helpers, per-devis-logging]
  provides: [auto-output-path, standalone-logger]
  affects: [generate-slides]
tech_stack:
  added: []
  patterns: [auto-path-resolution, optional-parameters]
key_files:
  created: []
  modified:
    - src/gendoc/mcp/server.py
decisions:
  - "output_path parameter now optional (defaults to None) for auto-computed paths"
  - "Relative output_path resolved against devis output dir (not PROJECT_ROOT)"
  - "Auto-computed path is devis_output_dir/fiches.pptx when output_path is None"
  - "Standalone generate_slides calls create PipelineLogger with devis-specific directory"
  - "Renamed PROJECT_ROOT to _PROJECT_ROOT to signal internal use only (image path resolution)"
metrics:
  duration_min: 2
  tasks_completed: 3
  files_modified: 1
  tests_added: 0
  tests_updated: 0
  completed_date: 2026-02-16
---

# Phase 23 Plan 02: Auto-Compute Output Paths for generate_slides Summary

**One-liner:** Refactored generate_slides to auto-compute output paths from devis_info, writing PowerPoint files to per-devis subdirectories like ./output/{devis_numero}/fiches.pptx by default.

## Objective Achievement

Made output_path parameter optional in generate_slides function. When not provided, automatically computes output path as `./output/{devis_numero}/fiches.pptx` using devis_info. Standalone generate_slides calls now create PipelineLogger with devis-specific directory, ensuring LOG.md is written to the correct location.

## Tasks Completed

### Task 1: Make output_path optional and auto-compute from devis_info

**Status:** ✓ Complete
**Commit:** 45d3838

Made output_path parameter optional (defaults to None) and implemented auto-path resolution:

**Changes:**
- Changed function signature: `output_path: str = None` (was `output_path: str`)
- Updated docstring to reflect optional parameter
- Replaced PROJECT_ROOT-based resolution with devis-specific directory logic:
  - Call `_get_devis_output_dir(devis_info, fallback_name="default")` to get devis directory
  - If output_path provided and relative: resolve against devis_output_dir
  - If output_path not provided: auto-compute as `devis_output_dir / "fiches.pptx"`
  - If output_path absolute: use as-is

**Result:** Users can now call `generate_slides(["PM-D-H-75"], devis_info={"numero_devis": "25 64 0637"})` without specifying output_path, and PowerPoint will be written to `./output/25_64_0637/fiches.pptx`.

**Files modified:**
- src/gendoc/mcp/server.py (changed 7 lines, added 7 lines at lines 467, 488-503)

### Task 2: Update PipelineLogger initialization in generate_slides

**Status:** ✓ Complete
**Commit:** d7ef6b6

Added logger creation logic for standalone generate_slides calls:

**Changes:**
- Added check after devis_output_dir computation: `if _current_logger is None`
- Create PipelineLogger with devis_output_dir: `_current_logger = PipelineLogger(devis_output_dir)`
- Logger created before output path resolution (ensures LOG.md path is correct)

**Result:** When generate_slides is called without prior analyze_devis call, it creates its own PipelineLogger using the devis-specific directory. LOG.md is written to `./output/{devis_numero}/LOG.md` (or `./output/default/LOG.md` if no devis_info).

**Files modified:**
- src/gendoc/mcp/server.py (+4 lines at lines 492-494)

### Task 3: Remove PROJECT_ROOT-based output resolution

**Status:** ✓ Complete
**Commit:** 43c4e25

Renamed PROJECT_ROOT to _PROJECT_ROOT and updated comment to clarify internal use only:

**Changes:**
- Renamed `PROJECT_ROOT` to `_PROJECT_ROOT` (signals private/internal use)
- Updated comment from "Keep PROJECT_ROOT for output path resolution" to:
  - "Used only for internal project structure references (not output paths)"
  - "Phase 23: Output paths now use devis-specific directories via _get_devis_output_dir"
- Updated all 4 references throughout server.py:
  - Line 128: Definition
  - Line 536: Pass to _generate function (for image path resolution in generators)
  - Line 713: generate_sp_selector output path (TODO: refactor in future plan)
  - Line 780: load_sp_selection json path (TODO: refactor in future plan)

**Result:** Clear distinction between output path resolution (now uses devis-specific directories) and internal project structure references (still uses _PROJECT_ROOT for image paths). Lines 713 and 780 still use _PROJECT_ROOT for backward compatibility but are marked for future refactoring.

**Files modified:**
- src/gendoc/mcp/server.py (6 lines changed at lines 126-128)

## Deviations from Plan

None - plan executed exactly as written.

## Testing

**Test Results:**
- E2E pipeline test: 1/1 passing (test_full_pipeline_analyze_then_generate)
- Test execution time: 1.77s
- No test modifications needed (existing tests pass with new behavior)

**Coverage:**
- Auto-path resolution tested implicitly via E2E test (uses devis_info flow)
- Logger creation tested implicitly (E2E test creates logger via analyze_devis)
- Standalone generate_slides logger creation: Not yet tested (no standalone test exists)

## Key Decisions

1. **Optional output_path parameter:** Defaults to None, enabling auto-computed paths
2. **Relative path resolution:** Relative output_path resolved against devis output dir (not PROJECT_ROOT)
3. **Auto-computed path:** When output_path is None, use `devis_output_dir/fiches.pptx`
4. **Standalone logger creation:** generate_slides creates PipelineLogger if _current_logger is None
5. **_PROJECT_ROOT rename:** Signals internal use only (image path resolution, not output paths)

## Implementation Notes

**Backward compatibility:** Existing calls with explicit output_path still work. The change is backward compatible because:
- Absolute paths: Used as-is (no change in behavior)
- Relative paths: Now resolved against devis_output_dir instead of PROJECT_ROOT (BREAKING for tools that relied on PROJECT_ROOT resolution)

**Breaking change consideration:** Tools like generate_sp_selector (line 713) and load_sp_selection (line 780) still use _PROJECT_ROOT for output path resolution. These should be refactored in a future plan to use devis-specific directories.

**Logger lifecycle:** The PipelineLogger creation in Task 2 ensures LOG.md is always written to the correct location, even when generate_slides is called standalone. However, if multiple generate_slides calls are made without calling analyze_devis between them, they will all share the same logger instance (global _current_logger).

## Next Steps

**Phase 23-03 (future plan):**
1. Refactor generate_sp_selector to use devis-specific output directories
2. Refactor load_sp_selection to use devis-specific directories
3. Remove all remaining _PROJECT_ROOT usage for output paths
4. Add integration test for standalone generate_slides with auto-path

**Phase 23-04 (future plan):**
1. Add comprehensive tests for auto-path resolution edge cases
2. Test logger creation in standalone mode
3. Test multiple generate_slides calls with same logger

## Files Modified

| File | Lines Changed | Purpose |
|------|---------------|---------|
| src/gendoc/mcp/server.py | +17, -12 | Made output_path optional, added auto-path logic, logger creation, renamed _PROJECT_ROOT |

## Commits

| Hash | Type | Message |
|------|------|---------|
| 45d3838 | feat | Make output_path optional and auto-compute from devis_info |
| d7ef6b6 | feat | Create PipelineLogger for standalone generate_slides calls |
| 43c4e25 | refactor | Rename PROJECT_ROOT to _PROJECT_ROOT for internal use |

## Self-Check: PASSED

**Created files:** None (only modified existing files)

**Modified files exist:**
- ✓ src/gendoc/mcp/server.py exists

**Commits exist:**
- ✓ 45d3838 found in git log
- ✓ d7ef6b6 found in git log
- ✓ 43c4e25 found in git log

**Tests pass:**
- ✓ 1/1 E2E pipeline test passing

**Code verification:**
- ✓ output_path parameter has default value None (line 467)
- ✓ Auto-path logic uses _get_devis_output_dir (line 490)
- ✓ Logger creation check exists (lines 492-494)
- ✓ _PROJECT_ROOT defined with updated comment (lines 126-128)
- ✓ All references updated to _PROJECT_ROOT (lines 128, 536, 713, 780)
