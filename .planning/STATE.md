# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-11)

**Core value:** Un utilisateur soumet un devis PDF et obtient automatiquement un dossier PowerPoint complet de fiches techniques — sans intervention manuelle.

**Current focus:** v1.3 Robustesse et Logging

## Current Position

Phase: 15 (Gestion Erreurs et Resume)
Status: In Progress
Last activity: 2026-02-11 — Completed 15-01 (Pipeline Fault Tolerance)

Progress: [███████░░░] 100% (4/4 phases)

## Performance Metrics

**Velocity:**
- Total plans completed: 22 (10 v1.0 + 5 v1.1 + 3 v1.2 + 4 v1.3)
- Average duration: ~1.4 hours per plan (v1.0), ~5 minutes per plan (v1.1+v1.2+v1.3)

**By Milestone:**

| Milestone | Phases | Plans | Duration |
|-----------|--------|-------|----------|
| v1.0 Systeme MCP | 1-6 | 10 | ~20h (2 days) |
| v1.1 Qualite et Couverture | 7-8 | 5 | ~13m (same day) |
| v1.2 Outil de Selection SP | 9-11 | 3 | ~15m (same day) |
| v1.3 Robustesse et Logging | 12-15 | 4 | ~18m (Phase 15 in progress) |

*Updated 2026-02-11 after 15-01 completed*
| Phase 15 P01 | 7 min | 2 tasks | 3 files |

## Accumulated Context

### Decisions

All decisions logged in PROJECT.md Key Decisions table (15 decisions across 3 milestones).

**Recent (Phase 15-01):**
- Warning returns from slide builders: Check `_insert_image` return value instead of modifying signature (preserves backward compatibility)
- Warning structure: Use list[dict] with 'code' and 'message' keys (enables downstream logging to associate warnings with products)
- Coating error handling: Wrap `_add_revetement_slides` in try/except with generic REVETEMENTS code (revetement errors affect multiple products)

**Previous (Phase 14-01):**
- Silent filtering for exclusion words (known non-products disappear from output entirely)
- Pattern-based filtering for measurements (regex \d+MM? catches measurement values)
- Individual error logging per unknown code (enables precise tracking for catalog expansion)

**Previous (Phase 13-01):**
- Use module-level _current_logger for pipeline state tracking (avoids client lifecycle management)
- Write partial logs on ANY tool failure (not just final step) - ensures diagnostic capture
- Try/except/finally pattern in generate_slides guarantees log writing
- Log skipped products individually via log_error after generation
- Exact French section headers (non-negotiable for test assertions and AI parsing)

### Pending Todos

None.

### Blockers/Concerns

None.

## Session Continuity

Last session: 2026-02-11
Stopped at: Completed Phase 15-01 (Pipeline Fault Tolerance)
Resume file: .planning/phases/15-gestion-erreurs-et-resume/15-01-SUMMARY.md
Next step: Execute 15-02 to format warnings for user consumption
