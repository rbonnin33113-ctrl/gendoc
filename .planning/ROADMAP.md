# Roadmap: Generateur de Fiches Techniques Delagrave

## Milestones

- Shipped **v1.0 Systeme MCP** — Phases 1-6 (shipped 2026-02-10)
- Shipped **v1.1 Qualite et Couverture Familles** — Phases 7-8 (shipped 2026-02-10)
- Shipped **v1.2 Outil de Selection SP** — Phases 9-11 (shipped 2026-02-11)
- Shipped **v1.3 Robustesse et Logging** — Phases 12-15 (shipped 2026-02-11)
- Shipped **v1.4 Gestion CRUD des References** — Phases 16-19 (shipped 2026-02-15)
- Shipped **v1.5 Consolidation et Qualite** — Phases 20-21 (shipped 2026-02-16)
- Shipped **v1.6 Deploiement Multi-Postes** — Phases 22-25 (shipped 2026-02-16)
- Active **v1.7 Systeme de Mise a Jour** — Phases 26-27

## Archive

See `.planning/milestones/` for detailed roadmaps and requirements per version.

---

## v1.7 Systeme de Mise a Jour

**Milestone Goal:** Permettre aux utilisateurs d'etre notifies des mises a jour disponibles au demarrage du serveur MCP et de les installer en un clic, via un repo GitHub prive.

## Phases

- [x] **Phase 26: Versioning et Detection** - Version semver + comparaison locale/distante au demarrage MCP (completed 2026-02-18)
- [ ] **Phase 27: Outil MCP de Mise a Jour** - Installation Git a la demande + git pull + pip install en un clic

## Phase Details

### Phase 26: Versioning et Detection
**Goal**: Le serveur MCP connait sa version locale (pyproject.toml semver) et la compare a la version distante (GitHub) a chaque demarrage, avec notification dans Claude si MAJ disponible
**Depends on**: Phase 25 (deploiement v1.6 en place)
**Requirements**: VER-01, VER-02, NOTIF-01, NOTIF-02
**Plans:** 1/1 plans complete
**Success Criteria** (what must be TRUE):
  1. pyproject.toml contient la version semver et un module version_checker.py peut la lire
  2. Au demarrage MCP, le serveur compare la version locale avec le tag distant GitHub
  3. Si nouvelle version disponible, un message clair est retourne dans Claude (version actuelle + version disponible + resume changelog)
  4. Si a jour, aucun message supplementaire (silencieux)
  5. Si le reseau est indisponible, le check echoue silencieusement (pas de blocage)

Plans:
- [x] 26-01-PLAN.md — Module version_checker + integration demarrage MCP + tests

### Phase 27: Outil MCP de Mise a Jour
**Goal**: L'utilisateur peut lancer la mise a jour en un clic via un outil MCP qui gere tout (installation Git si absent, auth GitHub, clone ou pull, pip install)
**Depends on**: Phase 26
**Requirements**: MAJ-01, MAJ-02, MAJ-03, DEP-01, DEP-02, DEP-03
**Plans:** 2 plans

**Success Criteria** (what must be TRUE):
  1. Un outil MCP `update_gendoc` est disponible dans Claude
  2. Si Git n'est pas installe : l'outil installe Git, configure l'auth GitHub (token), et clone le repo
  3. Si Git est installe : l'outil execute git pull + pip install -e . automatiquement
  4. Le resultat (succes/echec, ancienne version, nouvelle version) est retourne dans Claude
  5. En cas d'erreur (conflit git, pip failure, auth), un message d'erreur clair guide l'utilisateur

Plans:
- [ ] 27-01-PLAN.md — Module auto_updater.py (detection Git, install, clone/pull, pip) + tests
- [ ] 27-02-PLAN.md — Outil MCP update_gendoc dans server.py

## Progress

**Execution Order:** 26 → 27

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 26. Versioning et Detection | v1.7 | Complete    | 2026-02-18 | - |
| 27. Outil MCP de Mise a Jour | v1.7 | 0/2 | Not started | - |

---
*Last updated: 2026-02-18 — Phase 27 planned (2 plans)*
