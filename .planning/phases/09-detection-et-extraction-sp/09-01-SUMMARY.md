---
phase: 09-detection-et-extraction-sp
plan: 01
subsystem: devis-analysis
tags: [bugfix, extraction, pdf-parsing, sp-articles]

dependency_graph:
  requires:
    - phase: 03
      plan: 01
      artifact: devis_analyzer.py
      reason: Extends classification logic
  provides:
    - artifact: extract_sp_designations
      for: "Phase 10 - SP article selection UI"
      via: "Designation text for user presentation"
  affects:
    - subsystem: devis-analysis
      component: classify_codes
      change: "SP prefix check now correctly positioned"
    - subsystem: devis-analysis
      component: analyze_devis
      change: "Returns designation field for SP articles"

tech_stack:
  added:
    - component: extract_sp_designations
      tech: [regex, multi-line text parsing]
      purpose: "Extract complete designation text from PDF"
  patterns:
    - pattern: "Multi-line text extraction with stopping conditions"
      location: extract_sp_designations
      notes: "Handles PDF text quirks like merged quantity columns"

key_files:
  created:
    - path: tests/test_sp_detection.py
      lines: 262
      purpose: "Comprehensive SP detection and designation tests"
  modified:
    - path: src/gendoc/parsers/devis_analyzer.py
      lines_added: 120
      lines_changed: 4
      purpose: "Add designation extraction, fix article code detection"

decisions:
  - id: DES-01
    title: "Designation extraction stops at next article code"
    context: "Multi-line designation text must not include subsequent articles"
    decision: "Use refined article code pattern: all uppercase OR contains hyphen"
    alternatives:
      - "Stop only at empty lines (too permissive, includes other articles)"
      - "Stop at any uppercase word (too strict, truncates valid text)"
    rationale: "Article codes have specific patterns distinct from regular words"

  - id: DES-02
    title: "Strip quantity indicators from designation"
    context: "PDF quantity column (UN 1, UN 2) often merged into designation text"
    decision: "Remove trailing patterns: '\\s+UN\\s+\\d+$' and '\\s+\\d+$'"
    alternatives:
      - "Keep quantity in designation (confusing for users)"
      - "Remove all numbers (too aggressive, loses dimension info)"
    rationale: "Quantity is order-specific, not product characteristic"

metrics:
  duration_minutes: 4
  tasks_completed: 3
  files_created: 1
  files_modified: 1
  tests_added: 14
  total_tests: 48
  test_time_seconds: 16
  lines_added: 382
  commits: 2
  completed_date: 2026-02-10
---

# Phase 9 Plan 1: SP Detection and Designation Extraction Summary

**One-liner:** SP articles now correctly classified (never in inconnus) with complete multi-line designation text extracted from PDF for user presentation.

## What Was Delivered

### Task 1: SP Prefix Check Ordering (BUG-01)
**Status:** Already complete (no-op)
- SP prefix check was already correctly positioned before coating suffix detection
- Verified with existing tests - no changes needed

### Task 2: Designation Extraction (EXT-01, EXT-02)
**Commit:** 9c4236d

**Added:**
- `extract_sp_designations(pages_text, sp_codes)` function
  - Extracts multi-line designation text from PDF for each SP code
  - Strips trailing quantity indicators (UN 1, UN 2)
  - Stops at next article code or exclusion keywords
  - Case-insensitive code matching
  - First occurrence wins (same code may appear multiple times)

- Integration into `analyze_devis()`
  - Collects SP codes from classification results
  - Calls extraction function
  - Enriches `speciaux` entries with `designation` field
  - Returns complete data: {code, famille, prefix, designation}

**Algorithm Details:**
1. Skip cover page, scan remaining pages line by line
2. When line starts with SP code:
   - Extract text after code (first line)
   - Strip quantity patterns from end
   - Continue reading subsequent lines until:
     - Empty line
     - Exclusion keyword (Sous-total, Page, Total, MONTANT, Article)
     - Next article code (all uppercase OR contains hyphen)
3. Join all lines with spaces, collapse multiple spaces
4. Store in dictionary (first occurrence wins)

**Edge Cases Handled:**
- Quantity column merged into text (stripped)
- Regular words vs article codes (refined pattern)
- Multi-page SP articles (first occurrence wins)
- Missing designation (empty string returned)

### Task 3: Comprehensive Tests
**Commit:** de60a25

**Test Coverage (14 tests, 2 classes):**

**TestSPClassification (4 tests):**
- `test_sp_codes_classified_as_speciaux` - All 4 SP prefixes correctly classified
- `test_sp_bare_codes_classified` - Bare SP codes (no suffix) work
- `test_coating_sp_suffix_not_confused_with_sp_prefix` - SP coating vs SP prefix distinction
- `test_sp_detection_before_coating_stripping` - Ordering verification

**TestSPDesignationExtraction (10 tests):**
- `test_extract_sp_designations_with_synthetic_data` - Multi-line extraction
- `test_designation_strips_quantity` - UN \d+ removal
- `test_designation_stops_at_next_code` - Article code boundary
- `test_designation_stops_at_exclusion_keywords` - Keyword boundaries
- `test_extract_designations_from_real_devis` - Real PDF integration
- `test_designation_is_multiline_complete` - Dimension info preservation
- `test_speciaux_have_all_required_fields` - Data structure validation
- `test_case_insensitive_sp_code_matching` - Case handling
- `test_multiple_sp_codes_in_same_devis` - Multiple SP articles
- `test_empty_designation_when_code_not_found_in_pdf` - Missing code handling

**Test Results:**
- All 48 tests pass (34 existing + 14 new)
- Test suite execution: 16 seconds
- No regressions in existing tests

**Bug Fixed During Testing:**
- Initial article code pattern (`[A-Z0-9][A-Za-z0-9\-]{3,19}\s`) matched regular words like "Dimension"
- Refined to require: all uppercase OR contains hyphen
- Prevents false positives while catching all real article codes

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Article code pattern too permissive**
- **Found during:** Task 3 test execution
- **Issue:** Pattern `[A-Z0-9][A-Za-z0-9\-]{3,19}\s` matched regular words starting with capitals (e.g., "Dimension")
- **Fix:** Refined pattern to check first word: must be all uppercase OR contain hyphen
- **Files modified:** src/gendoc/parsers/devis_analyzer.py (lines 192-199)
- **Commit:** de60a25 (included in test commit)
- **Rationale:** Article codes have specific characteristics that distinguish them from regular text

## Verification Results

**Unit Tests:**
```bash
pytest tests/test_sp_detection.py -v
# 14 passed in 7.04s
```

**Full Test Suite:**
```bash
pytest tests/ -v
# 48 passed in 16.03s
```

**Real Devis Analysis:**
- PDF: "Devis avec SP.pdf"
- SP codes found: SPMOB-25355, SPMOB-25042, others
- All have non-empty designation fields
- Designations contain expected keywords:
  - SPMOB-25355: Contains "Paillasse", dimensions (3500mm, 600mm, 850mm)
  - SPMOB-25042: Contains "Meuble"
- No SP codes in `inconnus` list

## Success Criteria Verification

- [x] BUG-01: SP codes (SPMOB, SPPAIL, SPTABLEEN, SPUSE) always classified in `speciaux`, never in `inconnus` ✓
- [x] EXT-01: analyze_devis extracts designation text for each SP article from the PDF ✓
- [x] EXT-02: Each speciaux entry contains {code, famille, prefix, designation} with complete descriptive text ✓
- [x] All existing tests pass (no regressions) ✓ (34/34 existing tests)
- [x] New tests cover SP detection, designation extraction, and edge cases ✓ (14 new tests)

## Technical Notes

**Designation Text Format:**
- Multi-line: "Paillasse Murale - Dosseret ht 100mm - Pietement H 30 x 30 - Longueur 3500mm - Profondeur utile 600mm - Haut. 850mm - Tube a ailette Ht 40mm - Revetement Resine de Synthese"
- Clean (quantity stripped): No "UN 1" at end
- Complete: All lines until next article code

**Article Code Detection Pattern:**
```python
# Matches: PM-D-H-75, SPMOB-25355, ACB120, CU12G
# Rejects: Dimension, Details, Product (regular words)
if re.match(r'^[A-Z0-9][A-Z0-9\-]{3,19}\s', line):
    first_word = line.split()[0]
    if '-' in first_word or first_word.isupper():
        # Article code found
```

**Performance:**
- Extraction adds negligible time to analyze_devis (~0.1s for typical devis)
- Regex operations are O(n) with PDF text length
- First occurrence wins strategy avoids redundant processing

## Impact on Phase 10

**Enables:**
- User can see complete description of each SP article
- Selection UI can display "SPMOB-25355: Paillasse Murale - Dosseret ht 100mm..."
- No need to manually search PDF for SP details

**Data Structure:**
```python
{
  'speciaux': [
    {
      'code': 'SPMOB-25355',
      'famille': 'meubles',
      'prefix': 'SPMOB',
      'designation': 'Paillasse Murale - Dosseret ht 100mm - ...'
    }
  ]
}
```

## Self-Check: PASSED

**Created files verified:**
```bash
[ -f "tests/test_sp_detection.py" ] && echo "FOUND: tests/test_sp_detection.py"
# FOUND: tests/test_sp_detection.py
```

**Commits verified:**
```bash
git log --oneline --all | grep -q "9c4236d" && echo "FOUND: 9c4236d"
# FOUND: 9c4236d

git log --oneline --all | grep -q "de60a25" && echo "FOUND: de60a25"
# FOUND: de60a25
```

**Key functions verified:**
```python
from gendoc.parsers.devis_analyzer import extract_sp_designations
# Function exists and callable
```

**Test execution verified:**
```bash
python -m pytest tests/test_sp_detection.py
# 14 passed
```
