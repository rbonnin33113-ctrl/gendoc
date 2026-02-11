---
phase: 15-gestion-erreurs-et-resume
plan: 01
subsystem: generation-pipeline
tags: [error-handling, resilience, warnings]
dependency_graph:
  requires: []
  provides: [per-product-warnings, fault-tolerant-pipeline]
  affects: [modern_template, document_assembler, pptx_generator]
tech_stack:
  added: []
  patterns: [try-except-safety, warning-propagation, structured-error-reporting]
key_files:
  created: []
  modified:
    - src/gendoc/generators/modern_template.py
    - src/gendoc/generators/document_assembler.py
    - src/gendoc/generators/pptx_generator.py
decisions:
  - context: "Image insertion failure detection"
    decision: "Check _insert_image return value instead of modifying signature"
    rationale: "Preserves backward compatibility, minimal invasiveness"
  - context: "Warning structure"
    decision: "Use list[dict] with 'code' and 'message' keys"
    rationale: "Enables downstream logging to associate warnings with specific products"
  - context: "Coating slide error handling"
    decision: "Wrap _add_revetement_slides in try/except with generic REVETEMENTS code"
    rationale: "Revetement errors affect multiple products, single error code is appropriate"
metrics:
  duration_minutes: 7
  tasks_completed: 2
  files_modified: 3
  tests_passing: 82
  completed_at: 2026-02-11T21:58:00Z
---

# Phase 15 Plan 01: Pipeline Fault Tolerance Summary

Error-resilient slide generation with per-product warnings.

## One-liner

Wrapped all slide builders in try/except, collect per-product warnings (missing images, unexpected errors), propagate through result chain to enable downstream logging.

## What Was Built

### Task 1: Modern Template Warning Returns
- Modified `build_product_slide` to return `list[str]` of warnings with top-level try/except
- Updated `_build_standard_slide`:
  - Wrapped entire function in try/except
  - Detects when `_insert_image` returns False despite having images → warning
  - Returns warnings list on success, single-item error list on exception
- Updated `_build_revetement_slide`:
  - Wrapped in try/except
  - Returns empty list on success (revetement images are supplementary)
  - Returns error warning on unexpected exception
- Updated `_build_simple_slide`:
  - Wrapped in try/except
  - Returns empty list on success
  - Returns error warning on unexpected exception

**Key implementation note:** Did NOT modify `_insert_image` or `_insert_all_images` signatures. They already handle errors gracefully via `continue`. Warning detection is at builder level (did any image get inserted?).

### Task 2: Warning Propagation Chain
- Modified `assemble_document` (document_assembler.py):
  - Initialized `all_warnings = []` before content slide loop
  - Captured return value from `build_product_slide` calls
  - Structured warnings as `[{"code": str, "message": str}]`
  - Added `'warnings': all_warnings` to return dict
- Modified `generate_presentation` (pptx_generator.py):
  - Extracted `all_warnings` from assembly_result
  - Wrapped `_add_revetement_slides` in try/except to catch coating errors
  - Coating errors appended as `{"code": "REVETEMENTS", "message": "..."}`
  - Added `'warnings': all_warnings` to final return dict

**Result chain:** modern_template → document_assembler → pptx_generator → (consumed by MCP server in plan 15-02)

## Verification

```bash
# Import checks
python -c "from gendoc.generators.modern_template import build_product_slide; print('OK')"
python -c "from gendoc.generators.pptx_generator import generate_presentation; print('OK')"

# Test suite
pytest tests/ -x -q
# All 82 existing tests pass unchanged (18-19s runtime)
```

**Backward compatibility verified:** Return value is additive — callers that ignore it (like existing tests) continue working unchanged.

## Deviations from Plan

None - plan executed exactly as written.

## Integration Points

**Provides:**
- `generate_presentation` now returns `'warnings': list[dict]` with per-product errors
- Enables plan 15-02 to:
  - Format warnings for user in French
  - Add warnings section to execution logs
  - Surface errors without crashing pipeline

**Depends on:**
- Nothing (foundational change)

**Affects:**
- All downstream callers of `generate_presentation` (MCP server tools)
- Prepares for user-facing error reporting in 15-02

## Performance Impact

Negligible - try/except overhead is minimal when no exceptions occur. Test suite runtime unchanged (18-19s).

## Success Criteria Met

- [x] ERR-01 partially satisfied: Generation errors produce warnings with product code (full ERR-01 completion in plan 15-02 which formats them for user)
- [x] ERR-02 satisfied: Pipeline continues after individual product errors (try/except in build_product_slide + coating generation)
- [x] generate_presentation result dict includes 'warnings' key
- [x] No existing test broken

## Commits

| Commit | Message | Files |
|--------|---------|-------|
| 207a4e3 | feat(15-01): add warning returns to modern_template build functions with try/except safety | modern_template.py |
| 7c05f92 | feat(15-01): capture warnings in assemble_document and propagate through generate_presentation | document_assembler.py, pptx_generator.py |

## Next Steps

Plan 15-02 will:
- Extract warnings from `generate_presentation` result in MCP server
- Format warnings in French with product codes
- Add "Avertissements" section to execution logs
- Surface errors to user without crashing generation
