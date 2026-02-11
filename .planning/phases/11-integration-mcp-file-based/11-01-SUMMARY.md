---
phase: 11-integration-mcp-file-based
plan: 01
subsystem: mcp-tools
tags: [mcp, sp-workflow, html-selector, file-integration]
completed: 2026-02-11
one_liner: "MCP tools for file-based SP workflow: generate HTML selector and load JSON configuration"

dependency_graph:
  requires:
    - phase: 10
      plan: 01
      artifact: "html_sp_selector.py (HTML generator)"
    - phase: 09
      plan: 01
      artifact: "devis_analyzer.py (SP detection)"
  provides:
    - "open_sp_selector MCP tool"
    - "load_sp_selection MCP tool"
    - "Complete SP workflow chain (analyze → HTML → JSON → slides)"
  affects:
    - "src/gendoc/mcp/server.py (10 tools total)"

tech_stack:
  added:
    - "MCP tool: open_sp_selector (file-based HTML generation)"
    - "MCP tool: load_sp_selection (JSON file reading)"
  patterns:
    - "Path resolution from PROJECT_ROOT for file operations"
    - "JSON validation for custom product structure"
    - "Error handling with JSON error returns"

key_files:
  created:
    - path: "tests/test_sp_workflow.py"
      lines: 278
      purpose: "Comprehensive tests for SP workflow MCP tools and integration"
  modified:
    - path: "src/gendoc/mcp/server.py"
      lines_added: 127
      purpose: "Added open_sp_selector and load_sp_selection MCP tools"

key_decisions:
  - decision: "MCP tools operate on files rather than direct data passing"
    rationale: "HTML selector must persist to disk for user interaction; JSON export is user-controlled"
    impact: "User workflow: generate HTML → edit in browser → export JSON → load JSON"
  - decision: "Custom products must be referenced in product_codes to be processed"
    rationale: "Existing generate_slides architecture requires codes in product_codes list"
    impact: "Callers must include SP codes in product_codes parameter alongside custom_products"
  - decision: "Partial SP export allowed (not all SP articles need configuration)"
    rationale: "User may only want to configure some SP articles from a devis"
    impact: "Export button enabled with any configured SP articles (Phase 10 decision carried forward)"

metrics:
  duration_minutes: 5
  tasks_completed: 3
  commits: 2
  tests_added: 8
  total_tests: 56
  test_runtime_seconds: 16
  files_modified: 2
  lines_added: 405
---

# Phase 11 Plan 01: MCP File-Based Integration Summary

**One-liner:** MCP tools for file-based SP workflow: generate HTML selector and load JSON configuration

## What Was Built

Two new MCP tools completing the SP article workflow bridge between analyze_devis and generate_slides:

### 1. open_sp_selector Tool

**Purpose:** Generate HTML selector from analyze_devis output

**Implementation:**
- Takes `analysis_result` dict from analyze_devis (with 'speciaux' key)
- Extracts SP articles and calls `generate_sp_selector_html`
- Returns JSON with output_path, sp_count, catalog_size, and user instructions
- Handles empty speciaux with error message
- Path resolution from PROJECT_ROOT for relative paths

**Signature:**
```python
async def open_sp_selector(
    analysis_result: dict,
    output_path: str = "output/sp_selector.html"
) -> str
```

### 2. load_sp_selection Tool

**Purpose:** Load exported JSON from HTML selector for use with generate_slides

**Implementation:**
- Takes `json_path` to sp_selection.json file
- Validates file existence and JSON structure
- Checks each product has required 'code' and 'famille' fields
- Returns JSON string ready for generate_slides custom_products parameter
- Path resolution from PROJECT_ROOT

**Signature:**
```python
async def load_sp_selection(json_path: str) -> str
```

## Full Workflow Chain

```
1. analyze_devis(pdf_path)
   ↓ returns: {speciaux: [...], references: [...], ...}

2. open_sp_selector(analysis_result, "output/sp_selector.html")
   ↓ generates: HTML file with embedded catalog
   ↓ returns: {output_path, sp_count, catalog_size, message}

3. [USER ACTION] Open HTML in browser
   - Search catalog for base products
   - Edit titre, texte, dimensions, famille for each SP
   - Export JSON file (sp_selection.json)

4. load_sp_selection("output/sp_selection.json")
   ↓ reads and validates JSON
   ↓ returns: JSON string of custom products array

5. generate_slides(
     product_codes=['SPMOB-12345', ...],
     custom_products=<loaded_json>,
     output_path="output.pptx"
   )
   ↓ generates: PowerPoint with SP articles
```

## Tests Added

**test_sp_workflow.py** (278 lines, 8 tests):

### TestOpenSPSelector
- `test_open_sp_selector_generates_html`: Verifies HTML generation from SP articles
- `test_open_sp_selector_empty_speciaux`: Handles empty speciaux list

### TestLoadSPSelection
- `test_load_sp_selection_reads_valid_json`: Reads and parses valid JSON
- `test_load_sp_selection_file_not_found`: Error handling for missing file
- `test_load_sp_selection_invalid_json`: Error handling for malformed JSON

### TestSPWorkflowIntegration
- `test_sp_custom_products_in_generate_slides`: E2E test with custom product
- `test_sp_workflow_multiple_custom_products`: Multiple SP articles in one presentation
- `test_sp_workflow_with_devis_info`: SP workflow with devis header information

**All 56 tests passing** (48 existing + 8 new), runtime 16 seconds.

## Deviations from Plan

None - plan executed exactly as written.

## Technical Decisions

### Decision 1: File-Based Workflow
**Context:** MCP tools could pass data in-memory or via files.

**Decision:** Use file-based approach (HTML to disk, JSON from disk).

**Rationale:**
- HTML selector must persist for user to open in browser
- JSON export is user-controlled action (not programmatic)
- Allows async workflow: generate → edit later → continue

**Impact:** User workflow includes file system steps but enables human-in-the-loop editing.

### Decision 2: Path Resolution from PROJECT_ROOT
**Context:** MCP server can be started from any directory.

**Decision:** Resolve relative paths from PROJECT_ROOT (server.py pattern).

**Rationale:**
- Consistent with existing MCP tools (generate_slides, analyze_devis)
- Works regardless of MCP server working directory
- Absolute paths pass through unchanged

**Implementation:**
```python
output = Path(output_path)
if not output.is_absolute():
    output = PROJECT_ROOT / output
```

### Decision 3: Custom Products Require product_codes Reference
**Context:** Tests revealed custom products only process when codes in product_codes list.

**Decision:** Document this requirement; don't change pptx_generator architecture.

**Rationale:**
- Existing generate_slides design: product_codes drives iteration
- Custom lookup happens during product_codes processing
- Changing this would be architectural (outside plan scope)

**Impact:** Callers must include SP codes in product_codes: `product_codes=['SPMOB-12345', ...]`

## Verification Results

### Self-Check: PASSED

**MCP tools registered:**
```bash
python -c "from gendoc.mcp.server import mcp; print([t.name for t in mcp._tool_manager._tools.values()])"
```
✓ Result: 10 tools including 'open_sp_selector' and 'load_sp_selection'

**Tests pass:**
```bash
python -m pytest tests/ -v
```
✓ Result: 56 passed in 16.02s (no failures, no regressions)

**Commits exist:**
- ✓ fbcd308: feat(11-01): add open_sp_selector and load_sp_selection MCP tools
- ✓ a55064b: test(11-01): add comprehensive tests for SP workflow MCP tools

**Files created:**
- ✓ tests/test_sp_workflow.py (278 lines)

**Files modified:**
- ✓ src/gendoc/mcp/server.py (+127 lines, import + 2 tools)

## Integration Points

### Upstream Dependencies
- **Phase 10-01**: html_sp_selector.py (generate_sp_selector_html function)
- **Phase 09-01**: devis_analyzer.py (analyze_devis returns 'speciaux')
- **Phase 04**: pptx_generator.py (generate_presentation accepts custom_products)

### Downstream Consumers
- **Claude Desktop / MCP clients**: Can now call open_sp_selector and load_sp_selection
- **End users**: Complete workflow for handling SP articles in devis

### Data Flow
```
analyze_devis.speciaux
  → open_sp_selector
  → HTML file (self-contained)
  → [user edits]
  → JSON file (sp_selection.json)
  → load_sp_selection
  → custom_products JSON string
  → generate_slides
  → PowerPoint with SP slides
```

## Performance Metrics

- **Execution time:** 5 minutes (2 tasks + tests + verification)
- **Commits:** 2 (1 per implementation task)
- **Test coverage:** 8 new tests, all passing
- **Code quality:** No regressions, all 56 tests pass
- **MCP tools:** 10 total (2 added)

## Lessons Learned

### Pattern: File-Based MCP Tools
- HTML generation requires disk persistence for user interaction
- JSON reading allows async user actions between MCP calls
- Path resolution from PROJECT_ROOT ensures consistency

### Pattern: Custom Products in generate_slides
- Custom products must be referenced in product_codes list
- This design was established in Phase 7; not changed here
- Tests confirm this behavior works correctly

### Pattern: Test Organization
- Group tests by tool/functionality (TestOpenSPSelector, TestLoadSPSelection, TestSPWorkflowIntegration)
- Use fixtures from conftest.py for consistency
- E2E integration tests verify full workflow

## Next Steps

Phase 11 is complete. The MCP toolset now provides:
1. Reference lookup and search (Phase 2)
2. Devis analysis with SP detection (Phases 3, 9)
3. PowerPoint generation with custom products (Phases 4, 7)
4. Preview generation (Phase 6)
5. Custom product creation (Phase 7)
6. HTML SP selector generation (Phase 10)
7. **File-based SP workflow integration (Phase 11)** ✓

**System status:** All planned features implemented. MCP server ready for production use.

