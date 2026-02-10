---
phase: 04-generation-powerpoint
plan: 01
subsystem: powerpoint-generation
tags: [python-pptx, template-conversion, slide-generation, layout-mapping]

# Dependency graph
requires:
  - phase: 01-fondation-donnees
    provides: MD reference files with product data and md_parser.py for data access
provides:
  - PowerPoint generator module that produces .pptx files from product codes
  - Template conversion logic (.potm to .pptx with VBA removal)
  - Family-to-layout mapping system for all 5 product families
  - VBA shape index to python-pptx placeholder index mapping
  - Text placeholder population engine
  - Image insertion at MD-specified positions
  - Auto-coating slide generation
affects: [04-02, Phase 5 (merge with existing fiches), MCP integration]

# Tech tracking
tech-stack:
  added: [python-pptx>=1.0.0]
  patterns: [Pure library module pattern, Template conversion via zipfile manipulation, VBA-to-placeholder index mapping]

key-files:
  created:
    - src/gendoc/generators/__init__.py
    - src/gendoc/generators/pptx_generator.py
  modified:
    - pyproject.toml

key-decisions:
  - "Template conversion: .potm converted to .pptx by modifying zipfile contents and removing VBA macros"
  - "VBA shape indices mapped to python-pptx placeholder idx for each family layout"
  - "Image insertion skips .missing files and non-existent paths gracefully"
  - "Coating slides auto-generated when revetement codes provided or detected in product dimensions"
  - "Layout 1=paillasse, 2=sorbonne, 3=revetement, 4=meubles, 5=equipement"

patterns-established:
  - "generate_presentation() returns dict with slides_generated, revetements_added, skipped"
  - "Template loading uses tempfile for safe .potm conversion"
  - "Placeholder population uses mapping dictionaries for family-specific VBA indices"
  - "Image insertion converts VBA points to EMUs using Pt() function"

# Metrics
duration: 3.8min
completed: 2026-02-10
---

# Phase 04 Plan 01: PowerPoint Generator Core Summary

**PowerPoint slide generation engine with .potm template conversion, 5-family layout support, VBA-to-placeholder mapping, text population, and image insertion**

## Performance

- **Duration:** 3.8 min
- **Started:** 2026-02-10T09:33:43Z
- **Completed:** 2026-02-10T09:37:32Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- Created complete PowerPoint generation module supporting all 5 product families
- Implemented template conversion from .potm (macro-enabled) to .pptx with VBA removal
- Established VBA shape index to python-pptx placeholder idx mapping for accurate text placement
- Verified all family types generate correctly with proper layout selection and placeholder population
- Image insertion logic handles missing network images gracefully
- Auto-coating slide generation works for revetement products

## Task Commits

Each task was committed atomically:

1. **Task 1: Create pptx_generator.py with template loading and slide generation for all families** - `810c187` (feat)

Task 2 was verification only (no code changes) - all family types verified working correctly.

## Files Created/Modified

- `src/gendoc/generators/__init__.py` - Package initialization with public API exports
- `src/gendoc/generators/pptx_generator.py` - Core PowerPoint generation engine (458 lines)
  - `load_template()` - Converts .potm to .pptx by modifying zipfile contents
  - `generate_presentation()` - Main orchestrator for slide generation
  - `_populate_slide()` - Text placeholder population with VBA-to-idx mapping
  - `_insert_images()` - Image insertion at MD-specified positions
  - `_add_revetement_slides()` - Auto-coating slide generation
  - `FAMILY_LAYOUT_MAP` - Family name to layout index mapping
  - `VBA_TO_PLACEHOLDER` - VBA shape index to placeholder idx for all families
- `pyproject.toml` - Added python-pptx>=1.0.0 dependency

## Decisions Made

- **Template conversion approach:** Used zipfile manipulation to convert .potm to .pptx by removing vbaProject.bin and modifying [Content_Types].xml to change content type from macro-enabled to standard presentation format
- **VBA index mapping:** Established explicit mapping dictionaries for each family type, converting VBA 1-based shape indices to python-pptx placeholder idx (which are non-sequential)
- **Dimension prefix handling:** When dimension has prefix field, concatenate with valeur; otherwise use valeur alone
- **Image height handling:** If height is 0 or missing, pass only width to add_picture() to let python-pptx calculate from aspect ratio
- **Coating detection:** Extract coating codes from "Liste des revetements" dimension values (short uppercase codes like GE, GR, IN)
- **Error handling:** Image insertion wrapped in try-except to handle corrupted/invalid files gracefully

## Deviations from Plan

None - plan executed exactly as written. All requirements met:
- Template loading works correctly with .potm conversion
- All 5 family types generate with correct layouts
- VBA-to-placeholder mapping verified accurate for all families
- Text placeholders populated correctly (titre, texte, ref, dimensions)
- Image insertion logic correct (skips missing files as expected)
- Coating auto-generation works when revetement codes provided
- Return value accurately reports generation results

## Issues Encountered

None - implementation proceeded smoothly. Template conversion logic worked on first try, VBA-to-placeholder mappings were accurate, and verification passed for all family types.

## User Setup Required

None - no external service configuration required. Module is self-contained and uses only python-pptx library.

## Next Phase Readiness

**Phase 04 Plan 02 ready:** MCP integration to expose generate_presentation() as MCP tool.

**Phase 5 ready:** Merge generated slides with fiches-existantes (pre-existing .pptx files).

**Blockers:** None. All 5 family types verified working. Image insertion logic handles missing network images gracefully.

**Key files available for next phases:**
- `src/gendoc/generators/pptx_generator.py` - Ready for MCP tool wrapping
- Generated test presentations verify layout/placeholder/image logic works correctly

---

## Self-Check: PASSED

### Files Created
- FOUND: src/gendoc/generators/__init__.py
- FOUND: src/gendoc/generators/pptx_generator.py

### Files Modified
- FOUND: pyproject.toml (python-pptx dependency added)

### Commits Exist
- FOUND: 810c187 (Task 1 commit)

### Generated Test Files
- FOUND: Delagrave/output/test_phase4.pptx
- FOUND: Delagrave/output/test_phase4_coating.pptx
- FOUND: Delagrave/output/test_all_families.pptx
- FOUND: Delagrave/output/test_task2_verification.pptx

### Verification Results
- Template loading: PASS (6 layouts found)
- Paillasse generation: PASS (layout 1, all placeholders populated)
- Sorbonne generation: PASS (layout 2, all placeholders populated)
- Revetement generation: PASS (layout 3, all placeholders populated)
- Meubles generation: PASS (layout 4, all placeholders populated)
- Equipement generation: PASS (layout 5, all placeholders populated)
- Coating auto-generation: PASS (revetement slides added)
- Return value accuracy: PASS (slides_generated, revetements_added, skipped)

---
*Phase: 04-generation-powerpoint*
*Completed: 2026-02-10*
