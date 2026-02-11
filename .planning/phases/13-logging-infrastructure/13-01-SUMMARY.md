---
phase: 13-logging-infrastructure
plan: 01
subsystem: logging
tags: [logging, diagnostics, transparency, AI-readable]
dependency_graph:
  requires: [hot-reload-mcp]
  provides: [pipeline-logging, structured-logs, diagnostic-files]
  affects: [mcp-server, all-tools]
tech_stack:
  added: [pipeline_logger]
  patterns: [module-level-state, try-except-finally-logging, partial-logs-on-failure]
key_files:
  created:
    - src/gendoc/utils/pipeline_logger.py
    - tests/test_pipeline_logger.py
  modified:
    - src/gendoc/mcp/server.py
decisions:
  - decision: "Use module-level _current_logger for pipeline state tracking"
    rationale: "Avoids requiring MCP client to manage logger lifecycle - logger is created in analyze_devis and written in generate_slides"
    outcome: "Clean API - tools work standalone (logger guards with if _current_logger)"
  - decision: "Write partial logs on ANY tool failure (not just final step)"
    rationale: "Issue #2 requirement - if preview_generation fails, user never reaches generate_slides, so log must be captured earlier"
    outcome: "All 5 MCP tools call _safe_write_log() in except blocks"
  - decision: "Use try/except/finally pattern in generate_slides"
    rationale: "Ensures log is always written even in edge cases where neither try nor except completes normally"
    outcome: "Log file guaranteed for every pipeline run (success or failure)"
  - decision: "Log skipped products individually via log_error after generation"
    rationale: "Generator already captures per-product errors in result['skipped'] - surface them in the log for Issue #1"
    outcome: "Each skipped product appears as individual error entry with code and reason"
  - decision: "Use exact French section headers (non-negotiable)"
    rationale: "Tests assert on exact strings - paraphrasing would break tests and AI parsing"
    outcome: "Log d'Execution Pipeline, Parametres d'Entree, Etapes du Pipeline, Erreurs Rencontrees, Solutions Appliquees"
metrics:
  duration_minutes: 5.4
  lines_added: 803
  lines_modified: 216
  files_created: 2
  files_modified: 1
  tests_added: 15
  test_coverage: "100% of PipelineLogger class"
completed: 2026-02-11
---

# Phase 13 Plan 01: Pipeline Logging Infrastructure Summary

Structured, AI-readable Markdown logs for every /gendoc-full execution with complete diagnostic context.

## What Was Built

**PipelineLogger module** (`src/gendoc/utils/pipeline_logger.py`) - 335 lines:
- Tracks pipeline execution with timestamped steps (start/end/fail)
- Records input parameters (PDF path, product codes, devis info)
- Logs errors with full context (product codes, file paths, tracebacks)
- Logs automatic solutions for resolved errors
- Writes structured Markdown to `Delagrave/output/logs/{YYYYMMDD_HHMMSS}_pipeline.md`
- Uses `perf_counter()` for precise duration measurements
- Handles interrupted steps (started but not completed)
- Idempotent `write_log()` - safe to call multiple times

**MCP server integration** (`src/gendoc/mcp/server.py`) - +191 lines:
- Module-level `_current_logger` tracks pipeline state
- `_safe_write_log()` helper writes log and resets logger
- `analyze_devis`: Creates logger, writes partial log on failure
- `preview_generation`: Logs step, writes partial log on failure
- `open_sp_selector`: Logs step, writes partial log on failure
- `load_sp_selection`: Logs step, writes partial log on failure
- `generate_slides`: Uses try/except/finally, always writes log, logs skipped products individually
- All tools include `log_path` in error responses

**Unit tests** (`tests/test_pipeline_logger.py`) - 277 lines, 15 tests:
- File creation and naming format
- All 5 French section headers present
- Input params, step durations, error context
- Solutions, failed steps, interrupted steps
- Overall status logic (OK/ERREURS/ECHOUE)
- Edge cases: empty pipeline, idempotent write

## Deviations from Plan

None - plan executed exactly as written.

All 3 critical issues addressed:
1. **Per-product errors**: Skipped products from `result["skipped"]` logged individually via `log_error()`
2. **Early failures**: All 5 tools write partial logs via `_safe_write_log()` in except blocks
3. **Try/finally**: `generate_slides` uses try/except/finally to guarantee log writing

## Key Technical Decisions

**Module-level logger state**: `_current_logger` is created in `analyze_devis` (pipeline start) and written/reset in tool except blocks or `generate_slides` success path. Tools guard all logger calls with `if _current_logger:` so they work standalone.

**Partial logs on failure**: Every tool that can fail (analyze_devis, preview_generation, open_sp_selector, load_sp_selection, generate_slides) has an except block that calls `_safe_write_log()` before returning error response. This ensures diagnostic info is captured even if pipeline never completes.

**Try/except/finally pattern**: `generate_slides` (final step) uses:
- **try block**: Success path - write log, include log_path in result
- **except block**: Failure path - fail step, write log, include log_path in error
- **finally block**: Safety net - write log if neither path completed (edge case protection)

**Exact French headers**: Log uses EXACT strings (`Log d'Execution Pipeline`, `Parametres d'Entree`, etc.) because tests assert on these and AI parsing depends on consistency. No translation or paraphrasing.

## Log File Format

```markdown
# Log d'Execution Pipeline

**Statut:** OK | ERREURS | ECHOUE
**Date:** 2026-02-11 14:23:45
**Duree totale:** 12.34s

## Parametres d'Entree

- **pdf_path:** /path/to/devis.pdf
- **codes_extraits:** ['PM-D-H-75', 'PM-C-75', ...]
- **product_codes:** ['PM-D-H-75', 'PM-C-75', ...]
- **output_path:** /path/to/output.pptx

## Etapes du Pipeline

### 1. Analyse PDF -- OK (1.23s)

- **references:** 42
- **revetements:** 5
- **speciaux:** 2

### 2. Preview generation -- OK (0.05s)

- **total_products:** 42
- **estimated_pages:** 87

### 3. Generation PPTX -- OK (8.45s)

- **slides_generated:** 42
- **total_pages:** 87
- **revetements_added:** 5
- **skipped:** 1

## Erreurs Rencontrees

### Erreur 1

**Message:** Produit ignore: SPPAIL-12345

**Contexte:**
- **code:** SPPAIL-12345
- **reason:** Image manquante

## Solutions Appliquees

*(Aucune solution enregistree)*
```

**Status logic:**
- **OK**: No errors, no failed steps
- **ERREURS**: Errors exist but pipeline completed (at least one step succeeded)
- **ECHOUE**: Critical failure (a step has ECHOUE status)

## Test Results

All 76 tests pass (61 existing + 15 new):
- 15 PipelineLogger unit tests (file creation, sections, params, durations, errors, solutions, status, edge cases)
- All existing tests unchanged (logging is additive, no behavior changes)

Test execution time: 19.15s (no significant slowdown from baseline 18.5s)

## Files Created/Modified

**Created:**
- `src/gendoc/utils/pipeline_logger.py` (335 lines) - Core logger class
- `tests/test_pipeline_logger.py` (277 lines) - 15 unit tests

**Modified:**
- `src/gendoc/mcp/server.py` (+191 lines, -25 lines) - MCP integration

## Commits

1. **01fd883** - feat(13-01): create PipelineLogger module
2. **ffd1809** - feat(13-01): integrate PipelineLogger into MCP server
3. **db86072** - test(13-01): add comprehensive PipelineLogger unit tests

## Success Criteria Met

- [x] PipelineLogger module exists and is importable with all documented methods
- [x] MCP tools instrumented: analyze_devis creates logger, generate_slides writes log
- [x] analyze_devis writes partial log on failure (not just on success)
- [x] preview_generation writes partial log on failure
- [x] open_sp_selector writes partial log on failure
- [x] load_sp_selection writes partial log on failure
- [x] generate_slides uses try/except/finally to always write log
- [x] Skipped products from generation individually logged as errors
- [x] Log files timestamped Markdown in Delagrave/output/logs/
- [x] Log contains EXACT French headers (5 required sections)
- [x] All existing 61 tests pass unchanged
- [x] New logger tests pass (15 tests, 100% coverage)
- [x] generate_slides result JSON includes log_path field

## Impact

**For users:**
- Every /gendoc-full execution now produces a diagnostic log file
- Errors include full context (codes, paths, tracebacks)
- Logs persist even when pipeline fails early
- Log path included in error responses for easy access

**For AI:**
- Structured Markdown format with consistent section headers
- Input parameters captured for reproduction
- Step-by-step execution trace with durations
- Error context enables root cause diagnosis without re-running
- Solutions section tracks automatic fixes

**For developers:**
- Diagnostic transparency - no more "what happened?" questions
- Logs survive even when exceptions are caught
- Per-product errors surfaced (not lost in generation result)
- Try/finally ensures logs are never lost

## Next Steps

Phase 13 Plan 02: Compact output summarizer (reduce console verbosity for /gendoc-full)

## Self-Check: PASSED

**Created files:**
- [x] `src/gendoc/utils/pipeline_logger.py` exists (335 lines)
- [x] `tests/test_pipeline_logger.py` exists (277 lines)

**Modified files:**
- [x] `src/gendoc/mcp/server.py` contains `from gendoc.utils.pipeline_logger import PipelineLogger`
- [x] `src/gendoc/mcp/server.py` contains `_current_logger: PipelineLogger | None = None`
- [x] `src/gendoc/mcp/server.py` contains `def _safe_write_log()`

**Commits:**
- [x] Commit 01fd883 exists: `git log --oneline | grep 01fd883` - feat(13-01): create PipelineLogger module
- [x] Commit ffd1809 exists: `git log --oneline | grep ffd1809` - feat(13-01): integrate PipelineLogger into MCP server
- [x] Commit db86072 exists: `git log --oneline | grep db86072` - test(13-01): add comprehensive PipelineLogger unit tests

**Tests:**
- [x] All 76 tests pass (61 existing + 15 new)
- [x] Test execution time: 19.15s (baseline: 18.5s, delta: +0.65s acceptable)

All checks passed.
