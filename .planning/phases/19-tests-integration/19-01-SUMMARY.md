---
phase: 19-tests-integration
plan: 01
subsystem: testing
tags: [crud, unit-tests, integration-tests, pytest, validation]
dependency_graph:
  requires: [16-01-md-writer, 16-02-crud-operations, 17-01-index-management, 18-01-image-management]
  provides: [crud-test-suite, integration-validation]
  affects: [ci-cd-pipeline, regression-detection]
tech_stack:
  added: []
  patterns: [pytest-tmp_path-isolation, class-based-test-organization, round-trip-validation]
key_files:
  created:
    - tests/test_crud_operations.py
  modified: []
decisions:
  - id: TESTS-01
    summary: "Use pytest tmp_path for filesystem isolation"
    rationale: "All CRUD tests create temporary files/directories to avoid side effects on real Delagrave/ data. Ensures tests can run in parallel and are reproducible."
    alternatives: "Use real Delagrave/ directory (rejected - too risky)"
  - id: TESTS-02
    summary: "Follow test_md_parser.py pattern (class-based organization)"
    rationale: "Consistent with existing test suite. Groups related tests, makes output readable, follows pytest conventions."
    alternatives: "Flat function-based tests (rejected - less organized)"
  - id: TESTS-03
    summary: "Integration test validates full lifecycle in single test method"
    rationale: "CRUD operations are sequential and stateful. Single comprehensive test validates real-world usage pattern better than isolated steps."
    alternatives: "Multiple smaller integration tests (rejected - more complex setup)"
metrics:
  duration_minutes: 2.4
  tasks_completed: 2
  files_modified: 1
  tests_added: 21
  test_execution_time_seconds: 0.22
  total_test_count: 108
  completed_date: 2026-02-15
---

# Phase 19 Plan 01: CRUD Operations Test Suite Summary

Comprehensive automated test coverage for all CRUD operations on product references, ensuring reliability and preventing regressions.

## One-liner

Complete test suite with 21 tests covering md_writer, image_handler, index_manager, and full lifecycle integration (108 total tests, all passing).

## Deliverables

### Created Files

**tests/test_crud_operations.py** (448 lines)
- `TestFormatProductSection`: 3 tests validating MD formatting
- `TestAppendProduct`: 4 tests for product creation and round-trip validation
- `TestUpdateProduct`: 4 tests for partial updates and error handling
- `TestRemoveProduct`: 3 tests for deletion and count updates
- `TestImageHandler`: 4 tests for copy/remove operations
- `TestIndexManager`: 2 tests for infrastructure and index refresh
- `TestCRUDIntegration`: 1 comprehensive lifecycle test
- All tests use `tmp_path` for filesystem isolation

### Test Coverage Summary

| Module | Tests | Coverage Areas |
|--------|-------|----------------|
| md_writer | 11 | format_product_section, append, update, remove |
| md_parser | (existing) | parse_family_md, find_product (used for verification) |
| image_handler | 4 | copy_product_images, remove_product_images |
| index_manager | 2 | ensure_family_infrastructure, refresh_index |
| Integration | 1 | Full add->lookup->update->delete lifecycle |
| **Total** | **21** | **Complete CRUD validation** |

## Implementation Details

### Task 1: CRUD Unit Tests (20 tests)

**TestFormatProductSection** - Validates MD output format
1. Header includes product code (`## TEST-CRUD-001`)
2. Metadata table contains all required fields
3. Dimensions table renders correctly

**TestAppendProduct** - Validates product creation
1. Creates new file with header when none exists
2. Appends to existing file, updates count
3. Round-trip: write -> parse -> verify all fields match
4. Round-trip with dimensions: preserves dimension list

**TestUpdateProduct** - Validates partial updates
1. Update titre persists to disk
2. Partial update preserves other fields (texte, ref unchanged)
3. Rejects code change (structural identifier protected)
4. Raises ValueError for nonexistent code

**TestRemoveProduct** - Validates deletion
1. Returns removed product dict for confirmation
2. Updates reference count in header
3. Raises ValueError for nonexistent code

**TestImageHandler** - Validates image operations
1. copy_product_images creates files in target directory
2. Returns image dicts with correct 'chemin' format (Delagrave/images/{famille}/{filename})
3. Handles missing source files with per-file error recovery
4. remove_product_images deletes files from disk

**TestIndexManager** - Validates infrastructure
1. ensure_family_infrastructure creates images directory when needed
2. refresh_index writes _index.md with correct family counts

Commit: `5a615fd` - "test(19-01): add comprehensive CRUD unit tests"

### Task 2: Integration Test (1 test)

**TestCRUDIntegration.test_full_lifecycle_add_lookup_update_delete**

Validates complete workflow with temporary directory structure:
1. Setup: Create `references/` and `images/` directories
2. ADD: Use `append_product_to_family` to create product
3. LOOKUP: Use `find_product`, verify all fields
4. ENSURE INFRASTRUCTURE: Call `ensure_family_infrastructure`, verify images dir exists
5. UPDATE: Change titre via `update_product_in_family`, verify persistence
6. IMAGE COPY: Create temp PNG, copy to images dir, verify file exists
7. DELETE: Remove product via `remove_product_from_family`
8. VERIFY DELETED: `find_product` returns None

This test validates the complete user workflow and ensures all modules work together correctly.

Commit: `5a615fd` (included in same commit as Task 1 - both tasks modify same file)

## Test Execution Results

```
pytest tests/test_crud_operations.py -v
===================== 21 passed in 0.22s ======================

pytest tests/ -v
===================== 108 passed in 19.42s ====================
```

All tests pass with zero failures. No regressions on existing 87 tests.

## Deviations from Plan

None - plan executed exactly as written.

## Impact

### Before This Plan
- CRUD operations validated only via manual testing
- Risk of regressions when modifying md_writer, image_handler, or index_manager
- No automated validation of round-trip compatibility (write -> parse)

### After This Plan
- 21 automated tests covering all CRUD operations
- Round-trip validation ensures md_writer produces output that md_parser can read
- Image operations tested with error recovery scenarios
- Integration test validates real-world usage patterns
- CI/CD pipeline can catch regressions automatically

### Test Suite Growth
- Before: 87 tests (Phase 1-18)
- Added: 21 tests (Phase 19)
- After: 108 tests total
- Execution time: 19.42s (fast enough for frequent runs)

## Technical Insights

1. **tmp_path Pattern Works Well**: Pytest's built-in `tmp_path` fixture provides perfect isolation. Each test gets a clean directory, no cleanup needed, no side effects.

2. **Round-trip Validation is Essential**: Tests like `test_append_round_trip` catch subtle bugs where md_writer might format data that md_parser can't parse correctly.

3. **Integration Test Validates Real Workflow**: Single comprehensive test is more valuable than many isolated tests for CRUD operations, since they're inherently sequential.

4. **Per-file Error Recovery in Image Handler**: Tests verify that one failed image copy doesn't block other images. Matches Phase 18 design decision.

5. **Class-based Organization Scales Well**: 6 test classes organize 21 tests cleanly. Output is readable, test names are self-documenting.

## Known Limitations

- Tests don't validate PowerPoint generation (covered by existing test_family_generation.py)
- Tests don't cover MCP server layer (would require FastMCP test infrastructure)
- No performance/load testing (not needed for current scale - 359 references)

## Future Enhancements

If needed (not planned for v1.4):
- Add tests for concurrent CRUD operations (file locking)
- Add tests for malformed MD files (robustness)
- Add tests for very large families (performance)

## Self-Check: PASSED

Verified all claims:

**Created files exist:**
```
[FOUND] tests/test_crud_operations.py
```

**Commits exist:**
```
[FOUND] 5a615fd - test(19-01): add comprehensive CRUD unit tests
```

**Test execution:**
```
21 tests in test_crud_operations.py - ALL PASSED
108 total tests - ALL PASSED
Execution time: 0.22s (CRUD only), 19.42s (full suite)
```

All deliverables verified. Plan complete.
