# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-18)

**Core value:** Un utilisateur soumet un devis PDF et obtient automatiquement un dossier PowerPoint complet de fiches techniques — sans intervention manuelle.
**Current focus:** v1.7 Systeme de Mise a Jour — Phase 27: Outil MCP de Mise a Jour

## Current Position

Phase: 27 of 27 (Outil MCP de Mise a Jour)
Plan: 1 of 2 in current phase
Status: Plan 27-01 complete — ready for plan 27-02
Last activity: 2026-02-18 — Plan 27-01 executed (auto_updater module, 25 tests, 184 total passing)

Progress: [████████░░] 75% (v1.7 — plan 27-01 done, 27-02 pending)

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
| v1.6 | 22-25 | 8 | Shipped 2026-02-16 |
| v1.7 | 26-27 | TBD | In progress |

**Totals:** 27 phases executed, 47 plans completed, 7 milestones shipped (1 in progress)

## Accumulated Context

### Decisions

All decisions logged in PROJECT.md Key Decisions table.

Recent decisions for v1.7:
- MCP startup is the trigger point for version check (non-bloquant si GitHub inaccessible)
- Update = git pull + pip install -e . (script automatique, pas manuel)
- Auth GitHub configuree une fois a l'installation (token ou SSH, persistant)
- urllib.request used instead of requests (no extra dependency for non-critical feature)
- GitHub tags API (/tags?per_page=1) used -- simpler than /releases/latest
- github_repo and github_token are optional in gendoc.json -- no check if absent
- sys.executable used for pip to target correct interpreter regardless of PATH
- Post-winget PATH gap handled by _get_git_cmd() checking C:\Program Files\Git\cmd\git.exe
- install_dir deduced 4 levels up from __file__; falls back to C:\gendoc if pyproject.toml missing
- All errors returned in dict with French resume field -- no exceptions propagate to caller

### Pending Todos

None.

### Blockers/Concerns

- GitHub repo doit etre PRIVE — auth configuree au premier update (pas a l'install)
- La mise a jour MAJ necessite un redemarrage de Claude apres pip install

## Session Continuity

Last session: 2026-02-18
Stopped at: Completed 27-01-PLAN.md — auto_updater module (run_update + 7 helpers, 25 tests, 184 total passing)
Resume file: None
Next: /gsd:execute-phase 27-02 (MCP tool update_gendoc)
