---
phase: 16-crud-operations
plan: 01
subsystem: reference-management
tags: [crud, md-writer, mcp-tools, add-reference]
dependency_graph:
  requires: [md_parser.py, server.py infrastructure]
  provides: [md_writer.py, add_reference MCP tool]
  affects: [reference catalog MD files]
tech_stack:
  added: [md_writer module]
  patterns: [round-trip compatibility, write counterpart to parser]
key_files:
  created:
    - src/gendoc/parsers/md_writer.py
  modified:
    - src/gendoc/mcp/server.py
decisions:
  - decision: md_writer is pure library with no runtime dependency on md_parser
    rationale: "Writer and parser are decoupled - round-trip compatibility validated by tests, not by runtime coupling"
    alternatives: [could import parser for validation, but increases coupling]
  - decision: add_reference parameter renamed from 'family' to 'famille'
    rationale: "Consistent with French naming used throughout codebase (famille field in product dicts)"
    alternatives: [keep English 'family' but creates inconsistency]
  - decision: Complex fields (dimensions, images, metadata_pptx) passed as JSON strings
    rationale: "MCP tools receive string parameters - JSON is standard way to pass structured data"
    alternatives: [individual parameters for each field, but too many parameters]
metrics:
  duration_minutes: 3
  tasks_completed: 2
  files_created: 1
  files_modified: 1
  commits: 2
  tests_status: "87 existing tests pass"
  completed_date: 2026-02-15
---

# Phase 16 Plan 01: MD Writer and Add Reference Tool Summary

**One-liner:** MD writer module with round-trip compatibility + functional add_reference MCP tool with duplicate detection

## What Was Built

Created the write counterpart to md_parser.py and implemented the first CRUD operation (Create) via MCP tool.

### md_writer.py Module

Pure library module that writes product references in the exact MD format that md_parser can parse back.

**Key functions:**

1. `format_product_section(product: dict) -> str`
   - Formats product dict into complete `## {CODE}` section with all tables
   - Handles empty lists (produces headers with no data rows)
   - Includes trailing `---` separator

2. `append_product_to_family(filepath: Path, product: dict) -> None`
   - Appends product to existing family file
   - Creates file with header if it doesn't exist
   - Updates "Total references: N" counter automatically

3. `write_family_file(filepath: Path, header_lines: list[str], products: list[dict]) -> None`
   - Writes complete family file from scratch
   - Used by update/delete operations (Plan 02)

4. `update_header_count(filepath: Path, new_count: int) -> None`
   - Updates reference count in family header
   - Used after add/delete operations

**Round-trip verification:** Product written by md_writer and parsed by md_parser produces identical field values (code, ref, titre, famille, texte, dimensions, images, metadata_pptx).

### add_reference MCP Tool

Replaces stub with full implementation. Enables adding new products to the catalog via MCP.

**Parameters:**
- Required: `famille`, `code`, `titre`
- Optional: `ref`, `texte`, `dimensions` (JSON), `images` (JSON), `metadata_pptx` (JSON)

**Validation:**
- Non-empty code, titre, famille (after strip)
- Duplicate code detection using `find_product`
- JSON parsing for complex fields

**Behavior:**
- Writes to `Delagrave/references/{famille}.md`
- Creates family file if it doesn't exist
- Returns success JSON: `{"status": "ok", "code": "...", "famille": "...", "fichier": "...", "resume": "..."}`
- Returns error JSON: `{"error": "...", "resume": "..."}` on validation/duplicate/exception

## Deviations from Plan

None - plan executed exactly as written.

## Technical Insights

**Round-trip compatibility pattern:** The writer produces output that the parser can read back identically. This is validated by tests, not by runtime coupling - md_writer never imports md_parser. This keeps the modules decoupled while ensuring format compatibility.

**MD format structure observed from paillasse.md:**

```markdown
## {CODE}

| Champ | Valeur |
|-------|--------|
| code | {code} |
| ref | {ref} |
| titre | {titre} |
| famille | {famille} |

### Texte

{texte}

### Dimensions

| Dimension | Valeur | Prefix | Shape Index |
|-----------|--------|--------|-------------|
{rows}

### Images

| Position | Chemin | Chemin Original | Left | Top | Width | Height | Shape Index |
|----------|--------|-----------------|------|-----|-------|--------|-------------|
{rows}

### Metadata PowerPoint

| Champ | Type | Prefix | Shape Index |
|-------|------|--------|-------------|
{rows}

---
```

Empty lists produce table headers with no data rows (parser expects this).

**FastMCP tool wrapper:** The `@mcp.tool()` decorator wraps the async function. The underlying function is still accessible as a module attribute with the same name, allowing direct testing.

## Testing Results

**Manual tests:**
- Import verification: `from gendoc.parsers.md_writer import ...` - OK
- Round-trip test: write product → parse back → compare fields - OK
- add_reference tests:
  - Add valid reference - OK
  - Duplicate detection - OK
  - Empty code rejected - OK
  - Empty titre rejected - OK

**Existing pytest suite:** 87 tests pass (< 20s)

## Files Modified

**Created:**
- `src/gendoc/parsers/md_writer.py` (257 lines) - MD writer module with 4 functions

**Modified:**
- `src/gendoc/mcp/server.py`:
  - Added import: `from gendoc.parsers.md_writer import append_product_to_family`
  - Replaced add_reference stub (lines 776-794) with full implementation
  - Changed parameter name: `family` → `famille` (consistency)
  - Added validation, duplicate checking, JSON parsing, error handling

## Commits

| Hash | Message | Files |
|------|---------|-------|
| 7034321 | feat(16-crud-operations): create md_writer module | md_writer.py |
| f003248 | feat(16-crud-operations): implement add_reference MCP tool | server.py |

## Next Steps

Phase 16 Plan 02: Implement update_reference and delete_reference MCP tools using md_writer functions.

## Self-Check: PASSED

**Files created:**
- [FOUND] src/gendoc/parsers/md_writer.py

**Files modified:**
- [FOUND] src/gendoc/mcp/server.py

**Commits:**
- [FOUND] 7034321 (md_writer module)
- [FOUND] f003248 (add_reference tool)

**Functions exported:**
- [FOUND] format_product_section
- [FOUND] append_product_to_family
- [FOUND] write_family_file
- [FOUND] update_header_count

**Round-trip test:**
- [PASSED] Product written and parsed back with identical fields

**Existing tests:**
- [PASSED] 87 pytest tests
