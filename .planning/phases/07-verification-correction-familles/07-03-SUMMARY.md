---
phase: 07-verification-correction-familles
plan: 03
subsystem: product-customization
tags: [sp-articles, custom-products, special-articles, mcp-tools]
dependency_graph:
  requires: [devis-analyzer, md-parser, pptx-generator, mcp-server]
  provides: [sp-article-detection, custom-product-creation, custom-product-generation]
  affects: [devis-workflow, slide-generation, mcp-api]
tech_stack:
  added: []
  patterns: [deep-copy, json-override, lookup-dict]
key_files:
  created: []
  modified:
    - src/gendoc/parsers/devis_analyzer.py
    - src/gendoc/mcp/server.py
    - src/gendoc/generators/pptx_generator.py
decisions:
  - SP codes detected by prefix before inconnus fallback (ensures full coverage)
  - Custom products use deep copy + field override pattern (flexible customization)
  - Custom lookup happens before normal catalog lookup (priority to custom)
  - Custom products list passed as JSON string in MCP (stateless protocol)
metrics:
  duration_minutes: 3
  tasks_completed: 3
  files_modified: 3
  commits: 3
  loc_added: 122
  completion_date: 2026-02-10
---

# Phase 7 Plan 3: SP Articles Support Summary

**One-liner:** SP-prefixed special articles now detected, customizable, and generate full documentation slides via MCP workflow.

## Objective Achievement

Added complete support for special articles (SP-prefixed product codes: SPMOB, SPPAIL, SPTABLEEN, SPUSE) that are not in the catalog but belong to a family. Users can now:
1. Analyze devis and detect SP codes with their family mappings
2. Clone a standard product as base and override any field
3. Generate documentation slides for custom products

This enables full coverage of real devis including custom/special articles that previously ended up as "inconnus" and were skipped.

## Tasks Completed

### Task 1: Add SP prefix detection to devis_analyzer
- **Files:** `src/gendoc/parsers/devis_analyzer.py`
- **Commit:** `f2010f9`
- **Changes:**
  - Added SP prefix detection logic before inconnus fallback
  - SP codes (SPMOB, SPPAIL, SPTABLEEN, SPUSE) now classified as 'speciaux'
  - Each special entry includes: code, famille (mapped), prefix
  - Updated classify_codes() and analyze_devis() to return speciaux list
  - Updated docstrings to document speciaux return value

**Verification:** SP_PREFIX_MAP contains all 4 prefixes with correct family mappings ✓

### Task 2: Create create_custom_product MCP tool
- **Files:** `src/gendoc/mcp/server.py`
- **Commit:** `6dc68e1`
- **Changes:**
  - New MCP tool: create_custom_product(base_code, custom_code, overrides)
  - Deep-copies base product and replaces code with custom code
  - Parses JSON overrides and applies to all fields (titre, texte, ref, dimensions, images, etc.)
  - Supports dict merging for complex fields
  - Returns complete custom product data ready for generate_slides

**Verification:** Custom product cloned from PM-D-H-75 with overridden title ✓

### Task 3: Add custom_products support to generate_presentation
- **Files:** `src/gendoc/generators/pptx_generator.py`, `src/gendoc/mcp/server.py`
- **Commit:** `2e11d6f`
- **Changes:**
  - Added custom_products parameter to generate_presentation()
  - Built custom_lookup dict at start of product processing
  - Check custom_lookup BEFORE normal catalog lookup (priority to custom)
  - Custom products added to family groups without find_product_pages() call
  - Updated MCP generate_slides tool to accept custom_products JSON string
  - Parse and pass custom_products_list to generate_presentation()

**Verification:** E2E test generated test_sp_article.pptx (162K) from custom product ✓

## Technical Implementation

### SP Prefix Detection
```python
SP_PREFIX_MAP = {
    'SPMOB': 'meubles',
    'SPPAIL': 'paillasse',
    'SPTABLEEN': 'tables-en',
    'SPUSE': 'equipement',
}
```

Detection occurs in classify_codes() after forfait detection and before inconnus fallback. This ensures SP codes are never classified as unknown.

### Custom Product Creation
Uses deep copy + field override pattern:
1. Deep copy base product dict
2. Replace 'code' field with custom code
3. Apply overrides from JSON (dict merge for complex fields, direct replace for simple)
4. Return complete product with same structure as catalog products

### Custom Product Lookup
Custom products have priority:
1. Build custom_lookup dict from custom_products list (keyed by code.upper())
2. For each product_code, check custom_lookup FIRST
3. If found, add to family groups directly
4. Only if not found, proceed to normal catalog lookup

This ensures custom products are never looked up in catalog and never skipped.

## Workflow Integration

**E2E Flow for SP Articles:**
1. User submits devis PDF with SP codes (e.g., SPPAIL-12345)
2. analyze_devis detects SP codes and returns in 'speciaux' list with family mappings
3. User (or automation) calls create_custom_product with base product + overrides
4. User calls generate_slides with product_codes + custom_products
5. Custom products generate full documentation slides identical to catalog products

**Stateless Design:**
- No server-side state required
- Custom products passed explicitly in each generate_slides call
- Enables parallel processing and horizontal scaling

## Deviations from Plan

None - plan executed exactly as written.

## Verification Results

All must-haves verified:

1. **SP detection:** SP codes detected by analyze_devis and classified as 'speciaux' with famille mapping ✓
2. **Custom product creation:** create_custom_product clones base product with custom code and applies overrides ✓
3. **Custom product generation:** generate_presentation accepts custom_products and generates slides without lookup ✓
4. **E2E test:** test_sp_article.pptx generated successfully from custom product ✓

**Test Output:**
```
SP_PREFIX_MAP: {'SPMOB': 'meubles', 'SPPAIL': 'paillasse', 'SPTABLEEN': 'tables-en', 'SPUSE': 'equipement'}
OK: SP prefix map correct

Code: SPPAIL-TEST
Titre: Paillasse Speciale Test
Famille: paillasse
OK: custom product created successfully

Slides: 1
Skipped: []
OK: custom product generated successfully
```

**Test Artifact:**
- File: `Delagrave/output/test_sp_article.pptx` (162K)
- Contains 1 slide for custom product SPPAIL-TEST

## Impact Analysis

**Devis Coverage:**
- Previously: SP codes ended up in "inconnus" and were skipped during generation
- Now: SP codes detected, customizable, and generate full slides
- Result: 100% coverage of devis articles (no more "inconnus" for known SP prefixes)

**User Workflow:**
- Manual step: User must select base product and provide overrides for each SP code
- Future automation opportunity: Could auto-suggest base products based on famille mapping
- Trade-off: Manual customization vs automated coverage (chose manual for accuracy)

**API Extensions:**
- New MCP tool: create_custom_product (no breaking changes)
- Updated MCP tool: generate_slides now accepts custom_products parameter (backward compatible - defaults to [])
- analyze_devis returns new 'speciaux' field (backward compatible - existing code ignores it)

## Known Limitations

1. **No auto-matching:** System does not auto-select base products for SP codes - user must provide
2. **No validation:** No validation that custom_code matches SP_PREFIX_MAP famille
3. **No persistence:** Custom products not saved - must be recreated for each generation
4. **No UI:** MCP tools only - requires Claude Code or API integration

These limitations are acceptable for v1.1 scope. Future enhancements could add auto-matching heuristics and custom product persistence.

## Files Modified

### src/gendoc/parsers/devis_analyzer.py (+33 lines)
- Added SP prefix detection before inconnus fallback
- Return 'speciaux' list in classification results

### src/gendoc/mcp/server.py (+61 lines)
- New tool: create_custom_product
- Updated tool: generate_slides (accepts custom_products parameter)

### src/gendoc/generators/pptx_generator.py (+28 lines)
- Added custom_products parameter to generate_presentation
- Custom lookup logic before normal catalog lookup

## Commits

| Commit | Message | Files |
|--------|---------|-------|
| f2010f9 | feat(07-03): add SP prefix detection to devis_analyzer | devis_analyzer.py |
| 6dc68e1 | feat(07-03): add create_custom_product MCP tool | server.py |
| 2e11d6f | feat(07-03): add custom_products support to generate_presentation | pptx_generator.py, server.py |

## Next Steps

**Immediate (Phase 7 continuation):**
- Visual verification of generated SP article slides (layout, formatting)
- Test with real devis containing SP codes
- Document SP article workflow in user guide

**Future Enhancements (v1.2+):**
- Auto-suggest base products based on famille + dimensions similarity
- Custom product persistence (save to temporary catalog)
- Batch custom product creation from CSV/Excel
- UI for SP article customization (web interface)

## Self-Check: PASSED

**Created files verified:**
```
FOUND: Delagrave/output/test_sp_article.pptx (162K)
```

**Modified files verified:**
```
FOUND: src/gendoc/parsers/devis_analyzer.py (modified)
FOUND: src/gendoc/mcp/server.py (modified)
FOUND: src/gendoc/generators/pptx_generator.py (modified)
```

**Commits verified:**
```
FOUND: f2010f9 feat(07-03): add SP prefix detection to devis_analyzer
FOUND: 6dc68e1 feat(07-03): add create_custom_product MCP tool
FOUND: 2e11d6f feat(07-03): add custom_products support to generate_presentation
```

All claims in summary verified against actual artifacts.
