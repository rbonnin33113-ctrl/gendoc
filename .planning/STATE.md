# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-09)

**Core value:** Un utilisateur soumet un devis PDF et obtient automatiquement un dossier PowerPoint complet de fiches techniques
**Current focus:** Phase 3 - Analyse de Devis

## Current Position

Phase: 3 of 6 (Analyse de Devis)
Plan: 1 of 2 in current phase
Status: In progress
Last activity: 2026-02-10 -- Completed 03-01-PLAN.md - PDF Parsing Core Modules

Progress: [######....] 42%

## Performance Metrics

**Velocity:**
- Total plans completed: 5
- Average duration: 4.8 minutes
- Total execution time: 0.39 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01-fondation-donnees | 2 | 13.4 min | 6.7 min |
| 02-infrastructure-mcp | 2 | 4.9 min | 2.5 min |
| 03-analyse-de-devis | 1 | 6.1 min | 6.1 min |

**Recent Trend:**
- Last 5 plans: 01-02 (6.6 min), 02-01 (2.9 min), 02-02 (2.0 min), 03-01 (6.1 min)
- Trend: Good velocity - varies by complexity (2-7 min range)

*Updated after each plan completion*

**Latest Execution:**
| Phase 02-infrastructure-mcp P02 | 2.0 min | 2 tasks | 4 files |
| Phase 03-analyse-de-devis P01 | 6.1 min | 2 tasks | 3 files |

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

### Pending Todos

None yet.

### Blockers/Concerns

None yet.

## Session Continuity

Last session: 2026-02-10
Stopped at: Completed 03-01-PLAN.md - PDF Parsing Core Modules
Resume file: None
