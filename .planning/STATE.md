# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-18)

**Core value:** Un utilisateur soumet un devis PDF et obtient automatiquement un dossier PowerPoint complet de fiches techniques — sans intervention manuelle.
**Current focus:** v1.7 SHIPPED — Systeme de Mise a Jour (Phases 26-27) complete

## Current Position

Phase: 27 of 27 (Outil MCP de Mise a Jour)
Plan: 2 of 2 in current phase
Status: Phase 27 complete — v1.7 milestone shipped
Last activity: 2026-02-18 — Plan 27-02 executed (update_gendoc MCP tool, 184 tests passing)

Progress: [██████████] 100% (v1.7 — all plans complete)

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
| v1.7 | 26-27 | 4 | Shipped 2026-02-18 |

**Totals:** 27 phases executed, 49 plans completed, 8 milestones shipped

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
- update_gendoc has no parameters -- all config from _config (no user input required)
- No _require_admin() on update_gendoc -- all users can trigger updates

### Pending Todos

None.

### Blockers/Concerns

- GitHub repo doit etre PRIVE — auth configuree au premier update (pas a l'install)
- La mise a jour necessite un redemarrage de Claude apres pip install

## Session Continuity

Last session: 2026-02-18
Stopped at: Completed 27-02-PLAN.md — update_gendoc MCP tool (184 tests passing, v1.7 shipped)
Resume file: None
Next: v1.7 shipped — define next milestone if needed
