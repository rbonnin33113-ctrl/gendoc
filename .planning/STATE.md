# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-09)

**Core value:** Un utilisateur soumet un devis PDF et obtient automatiquement un dossier PowerPoint complet de fiches techniques
**Current focus:** Phase 4 - Generation PowerPoint

## Current Position

Phase: 4 of 6 (Generation PowerPoint)
Plan: 1 of 2 in current phase
Status: In progress
Last activity: 2026-02-10 -- Completed 04-01-PLAN.md - PowerPoint Generator Core

Progress: [########..] 58%

## Performance Metrics

**Velocity:**
- Total plans completed: 7
- Average duration: 4.1 minutes
- Total execution time: 0.48 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01-fondation-donnees | 2 | 13.4 min | 6.7 min |
| 02-infrastructure-mcp | 2 | 4.9 min | 2.5 min |
| 03-analyse-de-devis | 2 | 7.9 min | 4.0 min |
| 04-generation-powerpoint | 1 | 3.8 min | 3.8 min |

**Recent Trend:**
- Last 5 plans: 02-02 (2.0 min), 03-01 (6.1 min), 03-02 (1.8 min), 04-01 (3.8 min)
- Trend: Excellent velocity maintained - quick integration tasks balance complex implementation

*Updated after each plan completion*

**Latest Execution:**
| Phase 03-analyse-de-devis P02 | 1.8 min | 2 tasks | 2 files |
| Phase 04-generation-powerpoint P01 | 3.8 min | 2 tasks | 3 files |

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

### Pending Todos

None yet.

### Blockers/Concerns

None yet.

## Session Continuity

Last session: 2026-02-10
Stopped at: Completed 04-01-PLAN.md - PowerPoint Generator Core (Phase 4 in progress)
Resume file: None
