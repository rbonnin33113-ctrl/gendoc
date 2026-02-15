---
phase: 16-crud-operations
plan: 02
subsystem: reference-management
tags: [crud, md-writer, mcp-tools, update-reference, delete-reference]
dependency_graph:
  requires: [md_parser.py, md_writer.py, server.py infrastructure, 16-01]
  provides: [update_reference MCP tool, delete_reference MCP tool, complete CRUD capability]
  affects: [reference catalog MD files]
tech_stack:
  added: [update and delete operations in md_writer]
  patterns: [read-modify-write, partial updates, existence validation]
key_files:
  created: []
  modified:
    - src/gendoc/parsers/md_writer.py
    - src/gendoc/mcp/server.py
decisions:
  - decision: update_product_in_family performs partial updates only
    rationale: "Allows updating only specific fields without touching others - more flexible than full replacement"
    alternatives: [full replacement, but requires client to send all fields]
  - decision: Cannot update code or famille fields via update_reference
    rationale: "These are structural identifiers - changing them requires delete + add to maintain consistency"
    alternatives: [allow code/famille updates, but risks breaking references]
  - decision: Local imports of md_parser in md_writer update/delete functions
    rationale: "Avoids circular dependency at module level while still allowing read-modify-write operations"
    alternatives: [module-level import would create circular dependency]
metrics:
  duration_minutes: 3
  tasks_completed: 2
  files_created: 0
  files_modified: 2
  commits: 2
  tests_status: "87 existing tests pass"
  completed_date: 2026-02-15
---

# Phase 16 Plan 02: Update and Delete Reference Tools Summary

**One-liner:** Complete CRUD capability with update_reference and delete_reference MCP tools plus supporting md_writer functions

## What Was Built

Completed the CRUD operations set by adding Update and Delete functionality to both md_writer.py and the MCP server.

### md_writer.py Extensions

Added three new functions to support update and delete operations:

**1. `_read_header(filepath: Path) -> str`**
   - Helper that extracts file header (everything before first `\n## ` section)
   - Preserves family name, metadata comments, extraction date when rewriting files
   - Used by both update and delete operations

**2. `update_product_in_family(filepath: Path, code: str, updates: dict) -> dict`**
   - Read-modify-write strategy for updating existing products
   - Partial update: only modifies fields present in updates dict
   - Case-insensitive code matching (uses `.upper()` comparison)
   - Validates: rejects attempts to update 'code' or 'famille' (structural identifiers)
   - Raises `ValueError` if code not found
   - Returns updated product dict for confirmation
   - Uses local import of `parse_family_md` to avoid circular dependency

**3. `remove_product_from_family(filepath: Path, code: str) -> dict`**
   - Read-filter-write strategy for removing products
   - Case-insensitive code matching
   - Automatically updates reference count in header after deletion
   - Raises `ValueError` if code not found
   - Returns removed product dict for confirmation
   - Uses local import of `parse_family_md` to avoid circular dependency

### MCP Tools

**1. `update_reference` MCP tool (CRUD-03)**

**Parameters:**
- Required: `code` (product code to update)
- Optional: `ref`, `titre`, `texte`, `dimensions` (JSON), `images` (JSON), `metadata_pptx` (JSON)

**Behavior:**
- Validates code is non-empty
- Uses `find_product` for existence check before updating (CRUD-05)
- Builds updates dict from only non-None parameters (partial update)
- Parses JSON strings for complex fields (dimensions, images, metadata_pptx)
- Rejects if no updates provided
- Rejects if code not found
- Returns success: `{"status": "ok", "code": "...", "famille": "...", "champs_modifies": [...], "resume": "..."}`
- Returns error: `{"error": "...", "resume": "..."}`

**2. `delete_reference` MCP tool (CRUD-04)**

**Parameters:**
- Required: `code` (product code to delete)

**Behavior:**
- Validates code is non-empty
- Uses `find_product` for existence check before deleting (CRUD-05)
- Rejects if code not found
- Calls `remove_product_from_family` to perform deletion
- Returns success: `{"status": "ok", "code": "...", "famille": "...", "resume": "..."}`
- Returns error: `{"error": "...", "resume": "..."}`

### Updated Import

Modified `server.py` import to include new functions:
```python
from gendoc.parsers.md_writer import append_product_to_family, update_product_in_family, remove_product_from_family
```

## Deviations from Plan

None - plan executed exactly as written.

## Technical Insights

**Read-modify-write pattern:** Both update and delete operations follow the same pattern:
1. Import `parse_family_md` locally (avoids circular dependency)
2. Parse all products from file
3. Find/filter the target product (case-insensitive code match)
4. Read and preserve the file header
5. Rewrite the entire file using `write_family_file`
6. Update reference count if needed

**Partial updates:** The update operation only modifies fields present in the `updates` dict. This allows clients to update just a title without needing to send all other fields. More flexible than full replacement.

**Structural identifier protection:** The code and famille fields cannot be updated via `update_reference`. These are structural identifiers that affect file organization and references. Changing them requires delete + add to maintain consistency.

**Local imports to avoid circular dependency:** The update/delete functions import `parse_family_md` inside the function body rather than at module level. This prevents circular dependency between md_writer.py and md_parser.py while still allowing the necessary read operations.

**CRUD-05 validation:** Both MCP tools use `find_product` to validate code existence before operating. This provides consistent error messages and prevents operations on non-existent codes.

## Testing Results

**Manual tests (md_writer.py):**
- Update product fields - OK
- Update persists correctly - OK
- Delete product - OK
- Delete updates count - OK
- Update non-existent code - ValueError raised correctly
- Delete non-existent code - ValueError raised correctly

**Manual tests (MCP tools):**
- update_reference with valid code - OK
- Update persists to file - OK
- update_reference with non-existent code - Error returned
- delete_reference with valid code - OK
- Delete persists to file - OK
- delete_reference with non-existent code - Error returned
- All responses include resume field - OK

**Existing pytest suite:** 87 tests pass (18.73s)

## Files Modified

**src/gendoc/parsers/md_writer.py:**
- Added `_read_header` helper (20 lines)
- Added `update_product_in_family` (58 lines)
- Added `remove_product_from_family` (48 lines)
- Total additions: 160 lines

**src/gendoc/mcp/server.py:**
- Updated import statement to include new md_writer functions
- Added `update_reference` tool (107 lines)
- Added `delete_reference` tool (55 lines)
- Total additions: 162 lines

## Commits

| Hash | Message | Files |
|------|---------|-------|
| 4d2767c | feat(16-crud-operations): add update and delete functions to md_writer | md_writer.py |
| daf16e5 | feat(16-crud-operations): implement update_reference and delete_reference MCP tools | server.py |

## Complete CRUD Capability

With this plan complete, the system now has full CRUD operations on product references:

| Operation | MCP Tool | md_writer Function | Status |
|-----------|----------|-------------------|--------|
| Create | add_reference | append_product_to_family | ✓ (16-01) |
| Read | find_product, search_products | parse_family_md | ✓ (pre-existing) |
| Update | update_reference | update_product_in_family | ✓ (16-02) |
| Delete | delete_reference | remove_product_from_family | ✓ (16-02) |

All operations:
- Validate inputs
- Check for existence/duplicates (CRUD-05)
- Maintain reference counts automatically
- Return JSON with resume field (v1.3 convention)
- Preserve file headers and formatting
- Support round-trip compatibility with md_parser

## Next Steps

Phase 16 complete. Next milestone (v1.4) phases:
- Phase 17: Family Management Tools (add/rename/delete families)
- Phase 18: Bulk Operations (import/export, batch updates)
- Phase 19: Reference Validation (consistency checks, orphan detection)

## Self-Check: PASSED

**Files modified:**
- [FOUND] src/gendoc/parsers/md_writer.py (160 lines added)
- [FOUND] src/gendoc/mcp/server.py (162 lines added)

**Commits:**
- [FOUND] 4d2767c (md_writer update/delete functions)
- [FOUND] daf16e5 (update/delete MCP tools)

**Functions added to md_writer:**
- [FOUND] _read_header
- [FOUND] update_product_in_family
- [FOUND] remove_product_from_family

**MCP tools added:**
- [FOUND] update_reference
- [FOUND] delete_reference

**Manual tests:**
- [PASSED] md_writer update/delete operations
- [PASSED] MCP tools update/delete operations
- [PASSED] Existence validation
- [PASSED] Error handling

**Existing tests:**
- [PASSED] 87 pytest tests
