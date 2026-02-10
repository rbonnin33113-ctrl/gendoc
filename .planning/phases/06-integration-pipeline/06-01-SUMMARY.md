---
phase: 06-integration-pipeline
plan: 01
status: complete
completed: 2026-02-10
one_liner: "End-to-end pipeline /gendoc-full with preview_generation MCP tool, tested on real devis PDF"
---

## What Was Done

### Task 1: preview_generation MCP tool + /gendoc-full skill rewrite

- Added `preview_generation` MCP tool to `src/gendoc/mcp/server.py`
  - Takes analyze_devis output, classifies references by family (FAMILY_ORDER)
  - Returns structured JSON: families with products/titles, revetements, inconnus, estimated_pages, suggested_filename
  - Filename derived from devis number (e.g., `fiches_25640637.pptx`)
- Rewrote `.claude/commands/gendoc-full.md` with complete 4-step pipeline:
  1. Analyze devis PDF (automatic)
  2. Preview + user confirmation (single pause point)
  3. Generate PowerPoint with devis_info passthrough
  4. Final report with structure breakdown
- Removed outdated "Statut actuel" placeholder note

### Task 2: End-to-end pipeline test

- Tested with `Delagrave/Devis - Modeles/Devis Test.pdf`
- Results: 2 products found, 1 revetement (GE) auto-added, 11 inconnus
- Preview estimated 7 pages, generation produced exactly 7 pages
- Output: 387 KB valid PowerPoint with cover, TOC, separators, product slides

## Key Decisions

- Preview estimation formula: 2 (cover+TOC) + per-family (1 separator + N products) + revetements
- Single confirmation point after preview (not after each step)

## Must-Haves Verified

- [x] /gendoc-full executes full pipeline without manual intermediate steps
- [x] User sees structured preview (families, revetements, inconnus) before generation
- [x] Pipeline passes devis header info to generator for cover page
- [x] Output file named from devis number (fiches_25640637.pptx)
- [x] Error handling with French messages at each step
