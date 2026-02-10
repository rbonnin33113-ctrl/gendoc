# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-09)

**Core value:** Un utilisateur soumet un devis PDF et obtient automatiquement un dossier PowerPoint complet de fiches techniques
**Current focus:** Phase 5 - Document Assembly

## Current Position

Phase: 5 of 6 (Assemblage Document)
Plan: 1 of 1 in current phase
Status: Phase complete
Last activity: 2026-02-10 -- Completed 05-01-PLAN.md - Document Assembly with Cover, TOC, and Chapter Separators

Progress: [##########] 83%

## Performance Metrics

**Velocity:**
- Total plans completed: 9
- Average duration: 4.0 minutes
- Total execution time: 0.58 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01-fondation-donnees | 2 | 13.4 min | 6.7 min |
| 02-infrastructure-mcp | 2 | 4.9 min | 2.5 min |
| 03-analyse-de-devis | 2 | 7.9 min | 4.0 min |
| 04-generation-powerpoint | 2 | 6.3 min | 3.2 min |
| 05-assemblage-document | 1 | 4.7 min | 4.7 min |

**Recent Trend:**
- Last 5 plans: 03-02 (1.8 min), 04-01 (3.8 min), 04-02 (2.5 min), 05-01 (4.7 min)
- Trend: Strong velocity - consistent sub-5 minute execution across integration and implementation tasks

*Updated after each plan completion*

**Latest Execution:**
| Phase 04-generation-powerpoint P02 | 2.5 min | 2 tasks | 2 files |
| Phase 05-assemblage-document P01 | 4.7 min | 2 tasks | 5 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Analyse complete du Excel VBA : 305 references, 8 familles, 12 onglets
- Analyse du template PowerPoint : 6 layouts, placeholders indexes
- Analyse du devis PDF test : structure hierarchique, format des references
- Mapping VBA compris : Row 1=type, Row 2=position/prefix, Row 3=shape index, Row 4+=data
- Actual Excel contains 359 references (not 305) across 9 families
- Fiches Existantes has different structure (no metadata rows)
- Sheet names use accents: "Revètement" and "Compléments"
- **NEW:** md_parser.py is pure library with no I/O (enforces separation of concerns)
- **NEW:** Image paths updated in-place with new "Chemin Original" column
- **NEW:** Product code regex supports dots, slashes, plus signs, spaces, lowercase
- **NEW:** Created .missing placeholders for 268 inaccessible network images
- [Phase 02-01]: FastMCP uses 'instructions' parameter not 'description' for server description
- [Phase 02-01]: MCP server uses absolute path resolution for REFERENCES_DIR to work from any directory
- [Phase 02-02]: Skills written in French for French-speaking end users
- [Phase 02-02]: Status notes in stub skills set expectations about Phase 3/4 implementation
- [Phase 03-01]: Client name extracted from first line pattern (Address COMPANY NAME) - most reliable location
- [Phase 03-01]: Code extraction uses position + pattern (4+ chars, requires digits/hyphens/consonant-clusters)
- [Phase 03-01]: Coating suffixes (GE, GR, IN, etc.) detected and base code looked up (PM-D-H-75-GE -> PM-D-H-75)
- [Phase 03-01]: Forfaits (FPORT, FORPOSE1J) classified separately from product references
- [Phase 03-01]: No quantities - each code appears once regardless of quote sections (user requirement)
- [Phase 03-01]: Unknown codes listed in 'inconnus' array without blocking analysis
- [Phase 03-02]: MCP server analyze_devis returns JSON with 'error' key for all failures (consistent error handling)
- [Phase 03-02]: Relative paths resolved from project root (4 levels up from server.py) for MCP flexibility
- [Phase 03-02]: /gendoc-analyze skill guides Claude to present structured report with Markdown tables
- [Phase 03-02]: Import naming convention - alias library function to avoid name conflict with MCP tool
- [Phase 04-01]: Template conversion - .potm to .pptx via zipfile manipulation, removing VBA macros
- [Phase 04-01]: VBA shape indices mapped to python-pptx placeholder idx for each family layout
- [Phase 04-01]: Layout mapping - 1=paillasse, 2=sorbonne, 3=revetement, 4=meubles, 5=equipement
- [Phase 04-01]: Image insertion skips .missing files and non-existent paths gracefully
- [Phase 04-01]: Coating slides auto-generated when detected in product dimensions or provided explicitly
- [Phase 04-02]: generate_slides MCP tool wraps generate_presentation with path resolution and JSON error handling
- [Phase 04-02]: /gendoc-generate skill provides 4-step workflow: collect, validate, generate, present
- [Phase 04-02]: Relative output paths resolved from project root for MCP flexibility
- [Phase 04-02]: Result presentation includes revetement auto-detection summary
- [Phase 05]: Two-pass assembly: calculate page numbers first, then build document in order
- [Phase 05]: Programmatic shapes (python-pptx MSO_SHAPE) for cover and separators instead of template layouts

### Pending Todos

None yet.

### Blockers/Concerns

None yet.

## Session Continuity

Last session: 2026-02-10
Stopped at: Completed 05-01-PLAN.md - Document Assembly with Cover, TOC, and Chapter Separators (Phase 5 complete)
Resume file: None
