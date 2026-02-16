# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-16)

**Core value:** Un utilisateur soumet un devis PDF et obtient automatiquement un dossier PowerPoint complet de fiches techniques — sans intervention manuelle.
**Current focus:** v1.6 Deploiement Multi-Postes

## Current Position

Phase: 23 (Output Restructuring)
Plan: 03
Status: Plan 23-02 complete (auto-compute output paths, standalone logger)
Last activity: 2026-02-16 — Completed 23-02-PLAN.md (optional output_path, auto-path resolution, _PROJECT_ROOT rename)

Progress: ▰▰▱▱▱ 2/5 phases (40%)

## Performance Metrics

**By Milestone:**

| Milestone | Phases | Plans | Status |
|-----------|--------|-------|--------|
| v1.0 | 1-6 | 10 | Shipped 2026-02-10 |
| v1.1 | 7-8 | 5 | Shipped 2026-02-10 |
| v1.2 | 9-11 | 3 | Shipped 2026-02-11 |
| v1.3 | 12-15 | 6 | Shipped 2026-02-11 |
| v1.4 | 16-19 | 5 | Shipped 2026-02-15 |
| v1.5 | 20-21 | 8 | Shipped 2026-02-16 |
| v1.6 | 22-26 | TBD | In Progress |

**Totals:** 26 phases defined, 40 plans executed, 6 milestones shipped

**Recent execution:**

| Phase-Plan | Duration | Tasks | Files | Completed |
|------------|----------|-------|-------|-----------|
| 23-02 | 2 min | 3 | 1 | 2026-02-16 |
| 23-01 | 2 min | 3 | 3 | 2026-02-16 |
| 22-02 | 3 min | 2 | 3 | 2026-02-16 |

## Accumulated Context

### Decisions

**Recent (Phase 23-02):**
1. output_path parameter now optional (defaults to None) for auto-computed paths
2. Renamed PROJECT_ROOT to _PROJECT_ROOT to signal internal use only (image path resolution)
3. Auto-computed path is devis_output_dir/fiches.pptx when output_path is None
4. Standalone generate_slides calls create PipelineLogger with devis-specific directory

**Phase 23-01:**
1. Fixed LOG.md filename: Use "LOG.md" instead of timestamped filenames (each devis has isolated directory)
2. Sanitization rules: Spaces→underscores, slashes→dashes, strip non-alphanumeric except [._-]
3. Eager directory creation: _get_devis_output_dir creates directory immediately (fail-fast on permission issues)
4. Analyze first, log second: Call run_analyze_devis before creating logger to extract devis numero from header

**Phase 22-02:**
1. Config loading at module level: server.py loads config at import (fail-fast startup validation)
2. OUTPUT_DIR remains local for Phase 22: Path("output").resolve() (Phase 23 will refactor to per-devis subdirs)
3. PROJECT_ROOT kept for output resolution: used by tools at lines 442, 475, 652, 719 (Phase 23 will remove)
4. Graceful sys.exit(1) on config error: clear [FATAL] messages guide user to create gendoc.json

**Phase 22-01:**
1. Config search order: CWD → home dir → server.py dir (enables workstation-specific config without code changes)
2. Template name encoding: "Modèle fiche technique vide - Ind J.potm" with UTF-8 accent (matches production file)
3. Admin flag defaults to false (normal user mode, admin features require explicit opt-in)
4. Validation at load time: fail fast on startup (catch config issues before operation)

All decisions logged in PROJECT.md Key Decisions table.

### Pending Todos

None.

### Blockers/Concerns

None.

## Session Continuity

Last session: 2026-02-16
Stopped at: Completed 23-02-PLAN.md (auto-compute output paths, standalone logger)
Resume file: .planning/phases/23-output-restructuring/23-02-SUMMARY.md
Next: Execute 23-03 (refactor remaining tools for per-devis output)
