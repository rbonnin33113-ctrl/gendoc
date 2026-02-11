---
phase: 14-detection-robustesse
plan: 01
subsystem: devis-analysis
tags: [detection, filtering, logging, robustness]
dependency_graph:
  requires: [pipeline-logger]
  provides: [exclusion-filtering, unknown-code-logging]
  affects: [devis-analyzer, mcp-server]
tech_stack:
  added: [EXCLUSION_WORDS constant, measurement pattern filter]
  patterns: [silent filtering, individual error logging]
key_files:
  created:
    - tests/test_detection_robustesse.py
  modified:
    - src/gendoc/parsers/devis_analyzer.py
    - src/gendoc/mcp/server.py
decisions:
  - title: "Silent filtering for exclusion words"
    rationale: "Excluded words are known non-products, not unknown codes - they should disappear from output entirely (not appear in inconnus)"
  - title: "Pattern-based filtering for measurements"
    rationale: "Regex pattern \\d+MM? catches measurement values even if not in explicit exclusion list"
  - title: "Individual error logging per unknown code"
    rationale: "Enables precise tracking of which codes need catalog attention - each logged separately with context"
metrics:
  duration_minutes: 3
  tasks_completed: 2
  files_modified: 3
  tests_added: 6
  total_tests: 82
  completed_date: 2026-02-11
---

# Phase 14 Plan 01: Detection Robustesse Summary

**One-liner:** Exclusion list filtering silently removes 33+ common false positives (850MM, CONDITIONS, etc.) from inconnus output, with individual logging of genuinely unknown codes for catalog expansion.

## Objective Achieved

Hardened devis PDF detection by filtering common false positives through an EXCLUSION_WORDS constant (33 entries) and logging truly unknown codes individually. Users and AI reviewing pipeline output now see only genuine missing products in inconnus, not measurement values or section headers.

## Tasks Completed

### Task 1: Create exclusion list and update classify_codes filtering

**Commit:** d671b32

**Changes:**
- Added EXCLUSION_WORDS constant (33 entries) in devis_analyzer.py after SP_PREFIX_MAP
  - Measurement values: 850MM, 750MM, 600MM, 900MM, 1200MM, 1500MM
  - Section/header words: CONDITIONS, LIVRAISON, SALLE, DEPOSE, DIVERS, MONTANT, FORFAITS, etc.
  - Document structure words: DESIGNATION, ARTICLE, OPTION, TOTAL, REMISE, ACOMPTE, REGLEMENT
  - Preserved existing exclusions: PAILLASSE, SORBONNE, DELAGRAVE
- Added docstring explaining constant purpose and user editability
- Updated classify_codes() to check EXCLUSION_WORDS BEFORE any other classification
- Added measurement pattern filter (`\d+MM?$`) to catch measurement values not in explicit list
- Removed hardcoded exclusion check in favor of constant
- Silent filtering - excluded words don't appear in inconnus (not unknowns, not products)

**Verification:**
- EXCLUSION_WORDS constant importable with 33 entries
- All 76 existing tests pass unchanged
- Exclusion filtering does not affect valid product detection

### Task 2: Wire unknown code logging into MCP server and add tests

**Commit:** d86d1da

**Changes:**

**MCP Server (server.py):**
- Added unknown code logging loop in analyze_devis after run_analyze_devis() call
- Each unknown code logged individually via `_current_logger.log_error()` with context:
  - Message: "Code inconnu: {code}"
  - Context: {"code": code, "action": "a verifier dans le catalogue"}
- Logging happens BEFORE end_step and set_input_params calls

**Tests (test_detection_robustesse.py):**
- Created 6 new test cases:
  1. `test_exclusion_words_constant_exists` - Verify constant exists as set with 20+ entries
  2. `test_classify_codes_filters_exclusions` - Verify 850MM, CONDITIONS, LIVRAISON filtered from inconnus
  3. `test_classify_codes_filters_measurement_pattern` - Verify 1200MM, 2500MM, 750M filtered
  4. `test_genuine_unknown_codes_remain` - Verify XYZFOO123, NOTAPRODUCT99 stay in inconnus
  5. `test_exclusion_does_not_affect_real_products` - Verify PM-D-H-75, S-A, ACB120, 2CU12G, ELE all found correctly
  6. `test_preview_includes_inconnus_count` - Verify result includes inconnus list

**Verification:**
- All 6 new tests pass
- All 82 tests pass (76 existing + 6 new)
- Test suite runs in ~18 seconds

## Deviations from Plan

None - plan executed exactly as written.

## Technical Details

**Filtering Logic Flow:**

```python
for code in codes:
    # 1. Check exclusion words FIRST (before any classification)
    if code.upper() in EXCLUSION_WORDS:
        continue  # Silent filter

    # 2. Check measurement pattern
    if re.match(r'^\d+MM?$', code.upper()):
        continue  # Silent filter

    # 3. Try direct product lookup
    # 4. Try SP prefix detection
    # 5. Try coating suffix detection
    # 6. Check if forfait
    # 7. Add to inconnus if none of above
```

**Logging in MCP Server:**

```python
result = run_analyze_devis(path, REFERENCES_DIR)

# Log each unknown code individually
for code_inconnu in result.get("inconnus", []):
    _current_logger.log_error(
        f"Code inconnu: {code_inconnu}",
        context={"code": code_inconnu, "action": "a verifier dans le catalogue"}
    )

_current_logger.end_step(step, result={...})
```

**EXCLUSION_WORDS Categories:**

| Category | Count | Examples |
|----------|-------|----------|
| Measurement values | 6 | 850MM, 1200MM, 1500MM |
| Section/header words | 17 | CONDITIONS, LIVRAISON, SALLE, DEPOSE, DIVERS |
| Document structure | 7 | DESIGNATION, ARTICLE, TOTAL, REMISE |
| Preserved existing | 3 | PAILLASSE, SORBONNE, DELAGRAVE |

## Impact

**Before:**
- inconnus list polluted with measurement values (850MM, 1200MM) and section headers (CONDITIONS, LIVRAISON)
- Users cannot distinguish real missing products from garbage
- AI reviewing pipeline logs sees noise in inconnus output

**After:**
- inconnus list contains ONLY genuinely unknown codes (not in catalog, not in exclusions, not forfaits, not SP)
- Each unknown code logged individually in pipeline log with "a verifier dans le catalogue" action
- Users can review pipeline log to identify which codes need catalog attention
- EXCLUSION_WORDS constant is user-editable for expanding filtering

**Test Coverage:**
- Detection robustness: 6 dedicated tests
- Total test count increased: 76 → 82 tests
- Test duration: ~18 seconds (no significant increase)

## Success Criteria Met

- [x] DETECT-01: Common false positives (850MM, CONDITIONS, LIVRAISON, SALLE, etc.) are silently filtered by EXCLUSION_WORDS and measurement pattern in classify_codes()
- [x] DETECT-02: EXCLUSION_WORDS constant is a clearly documented, editable set in devis_analyzer.py -- users add entries to expand filtering
- [x] DETECT-03: Each unknown code (not in catalog, not excluded) is individually logged as an error in the pipeline log via PipelineLogger.log_error() in the analyze_devis MCP tool
- [x] All existing 76 tests pass unchanged
- [x] 6 new tests validate the detection robustness behavior

## Self-Check: PASSED

**Created files exist:**
- [FOUND] tests/test_detection_robustesse.py

**Modified files exist:**
- [FOUND] src/gendoc/parsers/devis_analyzer.py
- [FOUND] src/gendoc/mcp/server.py

**Commits exist:**
- [FOUND] d671b32: feat(14-01): add exclusion list filtering for false positives in devis classification
- [FOUND] d86d1da: feat(14-01): add unknown code logging and detection robustness tests

**Verification commands:**
```bash
# Verify constant exists
python -c "from gendoc.parsers.devis_analyzer import EXCLUSION_WORDS; print(len(EXCLUSION_WORDS), 'exclusion words')"
# Output: 33 exclusion words

# Run all tests
pytest tests/ -x -q
# Output: 82 passed in 17.91s
```

## Next Steps

This plan completes Phase 14 Plan 01. The detection system now:
1. Filters 33+ known false positives silently
2. Catches measurement patterns via regex
3. Logs truly unknown codes individually for review
4. Maintains 82 passing tests with full coverage

Users can now expand the EXCLUSION_WORDS set to filter additional false positives as they discover them in real-world devis PDFs.
