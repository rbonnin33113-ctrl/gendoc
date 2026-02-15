---
phase: 17-family-index-management
plan: 01
subsystem: reference-management
tags: [crud, index, infrastructure, automation]
dependency_graph:
  requires: [16-02-crud-operations]
  provides: [automatic-index-updates, family-infrastructure]
  affects: [add-reference, update-reference, delete-reference, _index.md]
tech_stack:
  added: [index_manager.py]
  patterns: [auto-refresh, infrastructure-creation]
key_files:
  created:
    - src/gendoc/parsers/index_manager.py
  modified:
    - src/gendoc/mcp/server.py
decisions:
  - Index refresh failures don't cause CRUD operations to fail (secondary operation)
  - New families get images directory created automatically on first add
  - Source and Extraction metadata preserved when regenerating _index.md
  - Empty families (count 0) appear in index until MD file deleted
  - Family ordering: known families in FAMILY_ORDER, new families alphabetically (before fiches-existantes)
metrics:
  duration_minutes: 3
  tasks_completed: 2
  files_created: 1
  files_modified: 1
  tests_passing: 87
  completed_date: 2026-02-15
---

# Phase 17 Plan 01: Family Index Management Summary

**One-liner:** Automatic _index.md refresh and family infrastructure creation integrated into all CRUD operations.

## What Was Built

Implemented automatic family and index management so that every CRUD operation (add/update/delete) keeps _index.md in sync with actual family files on disk, and new families get proper infrastructure (MD file + images directory) created automatically.

### New Module: index_manager.py

Created `src/gendoc/parsers/index_manager.py` with two key functions:

1. **`ensure_family_infrastructure(famille, references_dir)`**: Creates images directory for new families. Returns dict with:
   - `famille`: normalized family name (lowercase)
   - `md_existed`: True if family MD file already existed
   - `images_dir_created`: True if images directory was created

2. **`refresh_index(references_dir)`**: Regenerates `_index.md` based on actual family files on disk. Features:
   - Reads all family MD files using `get_all_families()` from md_parser
   - Preserves Source and Extraction metadata from existing _index.md
   - Maintains family ordering (FAMILY_ORDER list) with new families inserted alphabetically
   - Maps family names to display names (with accents: Revètement, Compléments) and PowerPoint types
   - Returns dict with total, families count, and families_detail

### MCP Integration

Modified `src/gendoc/mcp/server.py` to auto-refresh _index.md after every CRUD operation:

1. **add_reference tool**:
   - Calls `ensure_family_infrastructure()` BEFORE writing (creates images directory for new families)
   - Calls `refresh_index()` AFTER successful append
   - Sets `nouvelle_famille: True` flag when images directory was created
   - Appends " (nouvelle famille)" to resume string for new families

2. **update_reference tool**:
   - Calls `refresh_index()` AFTER successful update
   - No other changes (update doesn't change family membership)

3. **delete_reference tool**:
   - Calls `refresh_index()` AFTER successful deletion
   - Product counters recalculated automatically

All three tools catch index refresh exceptions to prevent CRUD failures - the CRUD write is the primary operation, index refresh is secondary.

## Deviations from Plan

None - plan executed exactly as written.

## Verification Results

### Unit Tests
- All 87 existing tests pass (18.89s runtime)
- No regressions introduced

### Manual Integration Tests

1. **New family creation test**:
   - Added product to `test-new-family` (non-existent)
   - Result: Images directory created at `Delagrave/images/test-new-family/`
   - Result: _index.md updated to show new family with count 1
   - Result: Family displayed as "Test New Family" with type "PPT (texte + image)"

2. **Product deletion test**:
   - Deleted product from `test-new-family`
   - Result: _index.md updated to show count 0
   - Empty family remained in index (correct behavior)

3. **Cleanup test**:
   - Removed test MD file and images directory
   - Ran `refresh_index()`
   - Result: _index.md back to original state (359 references, 9 families)

### Index Content Verification
- _index.md regenerates with same families, same counts, same structure
- Source and Extraction metadata preserved correctly
- Family ordering maintained (known families in defined order, new families alphabetically)
- Accented characters rendered correctly (Revètement, Compléments)

## Commits

| Task | Commit | Message |
|------|--------|---------|
| 1 | b6a8ea1 | feat(17-01): create index_manager module |
| 2 | 70b3c61 | feat(17-01): integrate index auto-refresh into MCP CRUD tools |

## Impact Analysis

### Benefits
- **Zero manual maintenance**: _index.md automatically stays in sync with family files
- **New family support**: Adding first product to a new family creates full infrastructure
- **Always accurate**: Product counts always match actual file contents
- **Fail-safe**: Index refresh failures don't block CRUD operations
- **Metadata preservation**: Source and Extraction fields never lost

### System Changes
- MCP CRUD operations now have slight overhead (index refresh on each write)
- Refresh overhead negligible: reads all family files, counts products, writes one file
- 359 references processed in <1 second

### Future Considerations
- Could optimize refresh to only update affected family row (not full regeneration)
- Could add index validation (detect orphaned MD files, missing images directories)
- Could add automatic cleanup of empty families (count 0)

## Self-Check: PASSED

### File Verification
- Created: `src/gendoc/parsers/index_manager.py` ✓
- Modified: `src/gendoc/mcp/server.py` ✓

### Commit Verification
- Commit b6a8ea1 exists ✓
- Commit 70b3c61 exists ✓

### Functional Verification
- index_manager imports successfully ✓
- refresh_index() regenerates _index.md correctly ✓
- ensure_family_infrastructure() creates images directory ✓
- All MCP CRUD tools call refresh_index() ✓
- add_reference calls ensure_family_infrastructure() ✓
- 87 tests pass ✓

All verification checks passed.
