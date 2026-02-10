---
phase: 05-assemblage-document
plan: 01
subsystem: document-assembly
tags: [powerpoint, structure, cover, toc, separators]
dependency_graph:
  requires:
    - phase: 04
      plan: 01
      artifact: pptx_generator.py
  provides:
    - document_assembler.py with cover/TOC/separator functions
    - complete_document assembly orchestration
  affects:
    - generate_presentation signature (added devis_info)
    - generate_slides MCP tool (added devis_info)
    - /gendoc-generate skill workflow
tech_stack:
  added:
    - python-pptx shapes API (programmatic slide building)
    - MSO_SHAPE.RECTANGLE for bandeaux
  patterns:
    - Two-pass assembly (calculate page numbers, then build slides)
    - Lazy import to avoid circular dependency
    - OrderedDict for family grouping
key_files:
  created:
    - src/gendoc/generators/document_assembler.py (476 lines)
  modified:
    - src/gendoc/generators/pptx_generator.py (generate_presentation refactored)
    - src/gendoc/generators/__init__.py (exports added)
    - src/gendoc/mcp/server.py (devis_info parameter)
    - .claude/commands/gendoc-generate.md (workflow guidance)
decisions:
  - "Use programmatic shapes instead of template layouts for cover/separators (more flexible)"
  - "Two-pass approach: calculate all page numbers first, then build document in order"
  - "FAMILY_ORDER defines fixed sequence: paillasse, sorbonne, revetement, meubles, tables-en, equipement, elec-sorb, complements"
  - "No logo file available yet - use text placeholder 'DELAGRAVE' in white on blue bandeau"
  - "Delagrave blue: RGB(0, 85, 164) - standard corporate blue"
metrics:
  duration: 283
  completed: 2026-02-10
---

# Phase 05 Plan 01: Document Assembly Summary

**Built the document assembly layer that transforms flat product slides into a polished PowerPoint document with cover page, table of contents, and chapter separators.**

## Objective Achieved

Created `document_assembler.py` module with complete document structure functions (cover, TOC, chapter separators, orchestration). Integrated into `generate_presentation()` with devis_info support. Updated MCP tool and skill to pass devis header information for personalized cover pages.

## Tasks Completed

### Task 1: Create document_assembler.py module
- **Status:** Complete
- **Commit:** 016d812
- **Files:** src/gendoc/generators/document_assembler.py (476 lines), __init__.py
- **Key Functions:**
  - `add_cover_page()` - Blue bandeau cover with devis info
  - `add_chapter_separator()` - Family separator pages with blue bandeau
  - `add_toc_page()` - Table of contents with families and page numbers
  - `assemble_document()` - Main orchestrator with two-pass approach
- **Constants:**
  - `FAMILY_ORDER` - 8-family fixed sequence
  - `FAMILY_DISPLAY_NAMES` - French display names with proper accents
  - `DELAGRAVE_BLUE` - RGB(0, 85, 164) corporate blue
- **Verification:** All imports successful, 8 families, 8 display names

### Task 2: Integrate assembly into generator and MCP
- **Status:** Complete
- **Commit:** fdd25b8
- **Files Modified:**
  - src/gendoc/generators/pptx_generator.py
  - src/gendoc/mcp/server.py
  - .claude/commands/gendoc-generate.md
- **Changes:**
  - `generate_presentation()` refactored to group products by family
  - Added `devis_info` optional parameter (numero_devis, date, client, titre_affaire)
  - Returns `total_pages` in addition to `slides_generated`
  - MCP tool `generate_slides` accepts devis_info parameter
  - Skill instructs Claude to extract header from analyze_devis results
  - Updated example reports to show complete document structure
- **Test Results:**
  - Test with 3 products (PM-D-H-75, S-A, RB801) generated 8-page document
  - Structure: Cover (1) + TOC (2) + Paillasse separator (3) + PM slide (4) + Sorbonne separator (5) + S-A slide (6) + Meubles separator (7) + RB801 slide (8)
  - Output file: 242 KB at Delagrave/output/test_phase5.pptx

## Deviations from Plan

None - plan executed exactly as written.

## Technical Implementation

**Document Structure:**
1. Cover page with blue bandeaux (top 15%, bottom 8%)
2. "DELAGRAVE" text placeholder (no logo file available)
3. Table of contents on page 2 with calculated page numbers
4. Chapter separators before each family group
5. Product slides grouped by family in fixed order
6. Coating slides appended at end

**Two-Pass Assembly:**
- First pass: Calculate page numbers for all content
- Build TOC entries with correct page references
- Second pass: Add cover → TOC → (separator + products per family) → coatings

**Lazy Import Pattern:**
- `document_assembler` imports are inside `generate_presentation()` function body
- Avoids circular dependency at module load time
- `document_assembler` imports `_populate_slide`, `_insert_images`, `FAMILY_LAYOUT_MAP` from pptx_generator

## Must-Haves Verification

| Must-Have | Status | Verification |
|-----------|--------|--------------|
| Cover page with bandeau bleu, logo, titre, devis info | ✓ Complete | Test file has cover with blue bandeaux, DELAGRAVE text, devis info |
| Chapter separator pages with bandeau and family name | ✓ Complete | Separators added before each family group |
| Table of contents on page 2 with real page numbers | ✓ Complete | TOC with families and product codes with page numbers |
| Families in fixed order | ✓ Complete | FAMILY_ORDER enforced: paillasse → sorbonne → revetement → meubles → tables-en → equipement → elec-sorb → complements |
| generate_slides produces complete document | ✓ Complete | MCP tool generates 8-page structured document (not flat slides) |

## Key Decisions

1. **Programmatic shapes over template layouts** - More flexible for cover/separators
2. **Two-pass page calculation** - Ensures accurate TOC page numbers
3. **Text placeholder for logo** - No logo file available, uses white "DELAGRAVE" on blue
4. **Lazy import for circular dependency** - Import document_assembler inside function
5. **OrderedDict for family grouping** - Preserves FAMILY_ORDER sequence

## Self-Check: PASSED

**Files exist:**
- src/gendoc/generators/document_assembler.py: ✓
- Delagrave/output/test_phase5.pptx: ✓ (242 KB)

**Commits exist:**
- 016d812: ✓ (document_assembler.py created)
- fdd25b8: ✓ (MCP integration)

**Functionality verified:**
- Document assembly produces 8-page structure
- Cover page with devis info
- TOC with page numbers
- Chapter separators before families
- Products grouped by family order

## Next Steps

- Phase 05 Plan 02: Handle fiches-existantes integration (if needed)
- Phase 06: User acceptance testing with real devis PDFs
- Future enhancement: Add actual logo image when available
