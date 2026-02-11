---
phase: 10-interface-html-interactive
plan: 01
subsystem: html-sp-selector
tags: [ui, html, sp-articles, json-export]

dependency_graph:
  requires:
    - phase: 09
      plan: 01
      reason: "SP detection and designation extraction provides speciaux data"
  enables:
    - phase: 11
      plan: 01
      reason: "HTML selector output (JSON) feeds MCP integration"

key-files:
  created:
    - path: src/gendoc/generators/html_sp_selector.py
      purpose: "Self-contained HTML page generator for SP article editing"
  modified: []
---

## Summary

Created `html_sp_selector.py` — a Python module that generates a self-contained HTML page for editing SP (special) articles from a devis. The HTML embeds the full product catalog (320 products) as JSON and provides: SP article list panel, catalog search by code/titre, edit form (titre, texte, dimensions, famille), read-only image display, and JSON export compatible with `generate_slides` custom_products format.

## What Was Built

- **`generate_sp_selector_html(sp_articles, references_dir, output_path)`**: Main function that loads catalog from MD files, builds HTML with embedded data, writes to output path
- **`_build_catalog_json(references_dir)`**: Helper that builds lightweight product dicts from all family MD files (excludes fiches-existantes and empty titles)
- **HTML UI**: Responsive layout (side-by-side on desktop, stacked on mobile), French text, inline CSS/JS, no external dependencies
- **JSON export**: Downloads `sp_selection.json` with custom_products array (code, ref, titre, famille, texte, dimensions, images, metadata_pptx)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Partial export allowed | User doesn't have to configure all SP articles | Good — export enabled when >= 1 configured, only configured articles exported |
| Catalog embedded as JSON | Self-contained HTML, no server needed | Good — 320 products, ~500KB HTML file |
| String formatting (no Jinja2) | No extra dependency | Good — f-string with escaped braces |

## Deviations

- **Partial export**: Plan required all SP configured before export. User feedback during checkpoint: export should work with partial configuration. Fixed: button enabled when >= 1 configured, only configured articles in JSON.

## Verification

- Module imports correctly
- HTML generates at expected path (>10KB)
- 48 existing tests pass (no regressions)
- Human-verified in browser: SP list, catalog search, edit form, JSON export all functional

## Self-Check: PASSED

- [x] html_sp_selector.py created with generate_sp_selector_html()
- [x] SP articles displayed with code, famille, designation (UI-01)
- [x] Catalog search and selection works (UI-02)
- [x] All editable fields present (UI-03)
- [x] JSON export downloads valid file (UI-04)
- [x] Partial export supported (user feedback)
- [x] No regressions (48 tests pass)

## Commits

1. `45a40d8` — feat(10-01): add HTML SP selector generator
2. `7c48370` — fix(10-01): allow partial SP export — only configured articles included
