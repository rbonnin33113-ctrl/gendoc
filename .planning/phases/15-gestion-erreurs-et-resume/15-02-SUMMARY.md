---
phase: 15-gestion-erreurs-et-resume
plan: 02
subsystem: mcp-server
tags: [error-handling, user-experience, logging, compact-output]
dependency_graph:
  requires: [15-01]
  provides: [compact-resume, warning-logging, suppressed-noise]
  affects: [mcp-server, pipeline-logger]
tech_stack:
  added: []
  patterns: [compact-resume-formatting, per-product-warning-logging]
key_files:
  created:
    - tests/test_error_handling.py
  modified:
    - src/gendoc/mcp/server.py
    - tests/test_hot_reload.py
decisions:
  - decision: "Suppress hot-reload print() output"
    rationale: "Hot-reload is internal infrastructure — users don't need to see module reload timestamps"
    approach: "Log via PipelineLogger.log_solution instead of print()"
  - decision: "Resume field structure for generate_slides"
    rationale: "Users need to see warnings and skipped products at a glance"
    approach: "Multi-line resume with summary + detailed list of warnings and skipped products"
  - decision: "Log warnings individually via PipelineLogger"
    rationale: "Each warning needs to be logged with product code for diagnostic purposes"
    approach: "Loop through warnings list and call log_error for each one"
metrics:
  duration_minutes: 3
  completed_date: 2026-02-11
  tasks_completed: 2
  files_modified: 2
  files_created: 1
  tests_added: 5
  tests_total: 87
---

# Phase 15 Plan 02: Compact Progress Resume Summary

Compact French-language progress summaries added to all pipeline MCP tools for better user experience.

## What Was Built

**Three pipeline MCP tools now return compact 'resume' field:**

1. **analyze_devis**: "Analyse OK -- 28 references, 5 revetements, 3 speciaux, 2 inconnus"
2. **preview_generation**: "Preview OK -- 28 produits, 45 pages estimees"
3. **generate_slides**: Multi-line resume with warnings and skipped products details

**Warning logging:** Per-product warnings from generation now logged individually via PipelineLogger with product codes and messages.

**Hot-reload suppressed:** Module reload messages no longer print to console (logged to file via PipelineLogger instead).

**Error handling tests:** 5 new tests validate warnings propagation, pipeline continuation, and error catching.

## Tasks Completed

### Task 1: Add compact resume to MCP tools, log warnings, suppress hot-reload prints

**Changes to server.py:**

- Suppress hot-reload print(): Changed `_reload_generators()` to log via `PipelineLogger.log_solution` instead of printing to console
- Add resume to `analyze_devis` success path: "Analyse OK -- N references, M revetements, P speciaux, Q inconnus"
- Add resume to `analyze_devis` error paths: "ECHEC analyse: {error}"
- Add resume to `preview_generation`: "Preview OK -- N produits, M pages estimees"
- Add per-product warnings logging loop in `generate_slides` (after skipped loop)
- Update `end_step` result dict to include warnings count
- Build compact multi-line resume in `generate_slides`:
  - Summary: "Generation OK -- N fiches, M pages"
  - Revetements added count (if any)
  - Warnings list with product codes and messages
  - Skipped list with product codes and reasons
  - Output file path
- Add resume to `generate_slides` error path: "ECHEC generation: {error}"

**Fixed hot-reload tests:**
- `test_reload_skips_unchanged_modules`: Now validates mtimes unchanged instead of checking for print output
- `test_reload_detects_mtime_change`: Now validates mtime update instead of checking for print output

**Files modified:** src/gendoc/mcp/server.py, tests/test_hot_reload.py
**Commit:** 6a6f1b1

### Task 2: Add error handling and compact output tests

**Created tests/test_error_handling.py with 5 test cases:**

1. `test_generate_presentation_returns_warnings_key`: Validates warnings key always present in result
2. `test_generate_presentation_unknown_code_in_skipped`: Unknown codes go to skipped list, not crash
3. `test_pipeline_continues_after_unknown_code`: Pipeline generates valid slides AND records skipped
4. `test_build_product_slide_returns_list`: build_product_slide return type is list
5. `test_build_product_slide_catches_unexpected_error`: try/except catches errors, returns warning

**Files created:** tests/test_error_handling.py
**Commit:** 996c659

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed hot-reload test assertions**
- **Found during:** Task 1 verification
- **Issue:** `test_reload_detects_mtime_change` and `test_reload_skips_unchanged_modules` were checking for print() output via capsys, but we removed print() statements
- **Fix:** Updated tests to validate internal state (mtimes) instead of console output
- **Files modified:** tests/test_hot_reload.py
- **Commit:** 6a6f1b1 (bundled with Task 1)

## Technical Details

**Resume format examples:**

```python
# analyze_devis
"Analyse OK -- 28 references, 5 revetements, 3 speciaux, 2 inconnus"

# preview_generation
"Preview OK -- 28 produits, 45 pages estimees"

# generate_slides
"""Generation OK -- 28 fiches, 45 pages
Revetements ajoutes: 5
Avertissements: 2 produit(s) avec problemes
  - PM-D-H-75: Image manquante: plan.png
  - RB600G: Dimensions incorrectes
Ignores: 1 produit(s) non trouves
  - FAKECODE: Produit non trouve dans le catalogue
Fichier: H:\\IA\\Generateur de doc\\output\\fiches.pptx"""
```

**Warning logging pattern:**

```python
for w in result.get("warnings", []):
    _current_logger.log_error(
        f"Avertissement produit: {w['code']} - {w['message']}",
        context={"code": w["code"], "type": "warning", "detail": w["message"]}
    )
```

## Verification Results

All verification steps passed:

1. `pytest tests/ -x -q` -- all tests pass (87 total: 82 existing + 5 new)
2. Verified no print() in `_reload_generators` function -- only comment remains
3. `python -c "from gendoc.mcp.server import mcp; print('OK')"` -- server loads without error

## Success Criteria Met

- OUTPUT-01: MCP tools return compact 'resume' field in French ✓
- OUTPUT-02: Hot-reload prints suppressed, technical details in log only ✓
- ERR-01: Generation errors produce clear messages with product code in resume ✓
- ERR-03: Final resume lists products OK vs. in error with reasons ✓
- 5 new tests validate the behavior ✓
- All existing tests unchanged (except hot-reload tests fixed) ✓

## Key Decisions

1. **Suppress hot-reload print() output:** Users don't need to see internal module reload messages. Log to PipelineLogger instead for diagnostics.

2. **Multi-line resume for generate_slides:** Warnings and skipped products need details (code + message/reason), so use multi-line format instead of single-line summary.

3. **Log warnings individually via PipelineLogger:** Each warning logged with product code enables diagnostic correlation between warnings in resume and log file entries.

## Impact

**User experience:** Claude can now present compact, readable summaries instead of raw JSON. Users see "Analyse OK -- 28 references, 5 revetements" instead of scrolling through technical fields.

**Error visibility:** Warnings and skipped products are now clearly listed in the resume with product codes and reasons, making it easy to identify which products need attention.

**Console noise reduced:** Hot-reload messages no longer clutter console output. Technical details stay in log files where they belong.

**Error handling robustness:** 5 new tests ensure pipeline continues after errors and properly propagates warnings through the result dict.

## Next Steps

Phase 15 Plan 02 complete. Resume fields are now present in all pipeline tools. Next plan (if any) would continue Phase 15 objectives.

## Self-Check: PASSED

**Created files exist:**
- tests/test_error_handling.py ✓

**Modified files updated:**
- src/gendoc/mcp/server.py ✓
- tests/test_hot_reload.py ✓

**Commits exist:**
- 6a6f1b1 (Task 1) ✓
- 996c659 (Task 2) ✓

**Tests pass:**
- 87 tests total (82 existing + 5 new) ✓
- All tests passing ✓
