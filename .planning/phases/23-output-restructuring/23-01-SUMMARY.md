---
phase: 23-output-restructuring
plan: 01
subsystem: output-management
tags: [infrastructure, logging, devis-isolation]
dependency_graph:
  requires: [config-loader]
  provides: [devis-output-helpers, per-devis-logging]
  affects: [analyze-devis, pipeline-logger]
tech_stack:
  added: []
  patterns: [devis-subdirectories, sanitized-paths]
key_files:
  created: []
  modified:
    - src/gendoc/mcp/server.py
    - src/gendoc/utils/pipeline_logger.py
    - tests/test_pipeline_logger.py
decisions:
  - "Use fixed LOG.md filename instead of timestamped {id}_pipeline.md (each devis has isolated directory)"
  - "Sanitize devis numero with spaces->underscores, slashes->dashes pattern"
  - "Create output directory eagerly in _get_devis_output_dir (fail-fast on filesystem issues)"
metrics:
  duration_min: 2
  tasks_completed: 3
  files_modified: 3
  tests_added: 0
  tests_updated: 2
  completed_date: 2026-02-16
---

# Phase 23 Plan 01: Infrastructure for Per-Devis Output Directories Summary

**One-liner:** Created devis-specific output directory infrastructure with sanitization helpers and refactored PipelineLogger to write LOG.md to isolated devis subfolders.

## Objective Achievement

Created complete infrastructure for per-devis output directories, enabling isolated output for each devis generation. PipelineLogger now writes LOG.md to devis-specific directories like `output/25_64_0637/LOG.md` instead of global `output/logs/{timestamp}_pipeline.md`.

## Tasks Completed

### Task 1: Add devis output directory helpers to server.py

**Status:** ✓ Complete
**Commit:** c7ee007

Added two helper functions to server.py:

1. `_sanitize_devis_numero(numero: str) -> str`:
   - Converts spaces to underscores
   - Converts forward slashes to dashes
   - Strips non-alphanumeric chars (except dots, dashes, underscores)
   - Example: "25 64 0637" → "25_64_0637"

2. `_get_devis_output_dir(devis_info: dict | None, fallback_name: str = "output") -> Path`:
   - Extracts numero_devis from header dict
   - Sanitizes numero and creates path like `output/{sanitized_numero}`
   - Creates directory if needed (mkdir parents=True)
   - Returns absolute resolved path
   - Falls back to `output/{fallback_name}` if no devis info

**Files modified:**
- src/gendoc/mcp/server.py (+44 lines after line 127)

### Task 2: Update PipelineLogger to accept devis-specific output directory

**Status:** ✓ Complete
**Commit:** 2fbfa7f

Refactored PipelineLogger to write LOG.md directly to provided output directory:

**Changes:**
- Removed `self.log_dir` attribute
- Changed `__init__` to accept devis-specific output_dir (not base dir)
- Changed `write_log()` to write to `output_dir/LOG.md` (not `output_dir/logs/{timestamp}_pipeline.md`)
- Updated docstrings to reflect new usage pattern

**Rationale:** Each devis has its own isolated directory, so LOG.md can use a fixed name without timestamp collisions.

**Files modified:**
- src/gendoc/utils/pipeline_logger.py (9 lines changed, removed log_dir references)

### Task 3: Update analyze_devis to use devis-specific output directory

**Status:** ✓ Complete
**Commit:** a2e2129

Modified analyze_devis function to create logger with devis-specific output directory:

**Changes:**
- Call `run_analyze_devis()` first to extract header
- Use extracted header to compute devis output directory via `_get_devis_output_dir()`
- Create `PipelineLogger` with devis-specific directory
- Consolidated input params setting into one call

**Result:** LOG.md now written to `./output/{devis_numero}/LOG.md` instead of `./output/logs/{timestamp}_pipeline.md`

**Files modified:**
- src/gendoc/mcp/server.py (14 lines changed, -9 removed)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed test assertions for new PipelineLogger behavior**

- **Found during:** Task 2 verification (pytest execution)
- **Issue:** Two tests (test_logger_creates_log_file, test_log_file_name_format) failed because they expected old behavior:
  - Expected log in `output_dir/logs/` subdirectory
  - Expected timestamped filename pattern `{timestamp}_pipeline.md`
- **Fix:** Updated both tests to expect new behavior:
  - Log written to `output_dir/LOG.md` (no logs/ subdirectory)
  - Fixed filename "LOG.md" (no timestamp)
- **Files modified:** tests/test_pipeline_logger.py
- **Commit:** 95857b4
- **Verification:** All 15 tests pass after fix

## Testing

**Test Results:**
- Pipeline logger tests: 15/15 passing
- Test suite execution time: <1s
- Tests updated: 2 (test_logger_creates_log_file, test_log_file_name_format)

**Coverage:**
- Helper functions: Implicitly tested via integration (will be fully tested in phase 23-02)
- PipelineLogger changes: 15 tests cover write_log behavior, directory creation, log structure
- Integration: analyze_devis integration verified by existing test coverage

## Key Decisions

1. **Fixed LOG.md filename:** Use "LOG.md" instead of timestamped "{id}_pipeline.md" since each devis has isolated directory
2. **Sanitization rules:** Spaces→underscores, slashes→dashes, strip non-alphanumeric except [._-]
3. **Eager directory creation:** _get_devis_output_dir creates directory immediately (fail-fast on permission issues)
4. **Analyze first, log second:** Call run_analyze_devis before creating logger to extract devis numero from header

## Implementation Notes

**Helper function placement:** Added after OUTPUT_DIR definition (line 127) and before FastMCP instantiation (line 172). Functions are module-level and can be used by all MCP tools.

**Backward compatibility:** OUTPUT_DIR global still exists (for now) but is unused by analyze_devis. Phase 23-02 will refactor generate_slides and other tools to use devis-specific directories.

**Error handling:** _get_devis_output_dir handles missing/None devis_info gracefully with fallback directory name.

## Next Steps

**Phase 23-02 (next plan):**
1. Update generate_slides to write PPTX to devis output directory
2. Update preview_generation and other tools to use devis helpers
3. Remove OUTPUT_DIR and PROJECT_ROOT globals (no longer needed)
4. Add integration tests for complete devis workflow

## Files Modified

| File | Lines Changed | Purpose |
|------|---------------|---------|
| src/gendoc/mcp/server.py | +44, -9 | Added helpers, updated analyze_devis |
| src/gendoc/utils/pipeline_logger.py | +9, -8 | Removed logs/ subdir, fixed filename |
| tests/test_pipeline_logger.py | +4, -9 | Updated test assertions |

## Commits

| Hash | Type | Message |
|------|------|---------|
| c7ee007 | feat | Add devis output directory helpers |
| 2fbfa7f | refactor | Update PipelineLogger to write to devis directory |
| a2e2129 | feat | Update analyze_devis to use devis-specific output dir |
| 95857b4 | fix | Update PipelineLogger tests for new behavior |

## Self-Check: PASSED

**Created files:** None (only modified existing files)

**Modified files exist:**
- ✓ src/gendoc/mcp/server.py exists
- ✓ src/gendoc/utils/pipeline_logger.py exists
- ✓ tests/test_pipeline_logger.py exists

**Commits exist:**
- ✓ c7ee007 found in git log
- ✓ 2fbfa7f found in git log
- ✓ a2e2129 found in git log
- ✓ 95857b4 found in git log

**Tests pass:**
- ✓ 15/15 pipeline_logger tests passing

**Functions exist:**
- ✓ _sanitize_devis_numero defined at line 130
- ✓ _get_devis_output_dir defined at line 149
- ✓ PipelineLogger writes to output_dir/LOG.md
- ✓ analyze_devis calls _get_devis_output_dir at line 291
