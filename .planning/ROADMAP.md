# Roadmap: Generateur de Fiches Techniques Delagrave

## Milestones

- ✅ **v1.0 Systeme MCP** — Phases 1-6 (shipped 2026-02-10)
- ✅ **v1.1 Qualite et Couverture Familles** — Phases 7-8 (shipped 2026-02-10)
- 🚧 **v1.2 Outil de Selection SP** — Phases 9-11 (in progress)

## Phases

<details>
<summary>✅ v1.0 Systeme MCP (Phases 1-6) — SHIPPED 2026-02-10</summary>

- [x] Phase 1: Fondation Donnees (2/2 plans) — completed 2026-02-09
- [x] Phase 2: Infrastructure MCP (2/2 plans) — completed 2026-02-10
- [x] Phase 3: Analyse de Devis (2/2 plans) — completed 2026-02-10
- [x] Phase 4: Generation PowerPoint (2/2 plans) — completed 2026-02-10
- [x] Phase 5: Assemblage Document (1/1 plan) — completed 2026-02-10
- [x] Phase 6: Integration Pipeline (1/1 plan) — completed 2026-02-10

</details>

<details>
<summary>✅ v1.1 Qualite et Couverture Familles (Phases 7-8) — SHIPPED 2026-02-10</summary>

- [x] Phase 7: Verification et Correction des Familles (3/3 plans) — completed 2026-02-10
- [x] Phase 8: Suite de Tests Automatises (2/2 plans) — completed 2026-02-10

</details>

### 🚧 v1.2 Outil de Selection SP (In Progress)

**Milestone Goal:** Permettre a l'utilisateur de visualiser, selectionner et editer les articles speciaux (SP) d'un devis via une page HTML interactive, avec extraction automatique des designations depuis le PDF.

#### Phase 9: Detection et Extraction SP ✅
**Goal**: Les articles SP sont correctement detectes et leurs designations sont extraites du PDF
**Depends on**: Phase 8
**Requirements**: BUG-01, EXT-01, EXT-02
**Status**: Complete — 2026-02-10

Plans:
- [x] 09-01-PLAN.md — SP detection hardening + designation extraction from PDF

#### Phase 10: Interface HTML Interactive ✅
**Goal**: L'utilisateur peut visualiser, selectionner et editer les articles SP via une page HTML
**Depends on**: Phase 9
**Requirements**: UI-01, UI-02, UI-03, UI-04
**Status**: Complete — 2026-02-11

Plans:
- [x] 10-01-PLAN.md — HTML SP selector generator with catalog search, field editing, and JSON export

#### Phase 11: Integration MCP File-Based
**Goal**: Le workflow complet analyse-HTML-generation fonctionne de bout en bout
**Depends on**: Phase 10
**Requirements**: MCP-01, MCP-02
**Success Criteria** (what must be TRUE):
  1. Un outil MCP charge le fichier JSON exporte par le HTML et retourne des custom products prets pour la generation
  2. Le workflow complet fonctionne: analyze_devis detecte les SP → open_sp_selector genere le HTML → utilisateur edite → load_sp_selection charge le JSON → generate_slides produit le PowerPoint avec les SP edites
  3. Les articles SP edites apparaissent correctement dans le PowerPoint final avec tous les champs customises
**Plans**: 1 plan

Plans:
- [ ] 11-01-PLAN.md — MCP tools (open_sp_selector, load_sp_selection) + SP workflow tests + e2e verification

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Fondation Donnees | v1.0 | 2/2 | Complete | 2026-02-09 |
| 2. Infrastructure MCP | v1.0 | 2/2 | Complete | 2026-02-10 |
| 3. Analyse de Devis | v1.0 | 2/2 | Complete | 2026-02-10 |
| 4. Generation PowerPoint | v1.0 | 2/2 | Complete | 2026-02-10 |
| 5. Assemblage Document | v1.0 | 1/1 | Complete | 2026-02-10 |
| 6. Integration Pipeline | v1.0 | 1/1 | Complete | 2026-02-10 |
| 7. Verification et Correction des Familles | v1.1 | 3/3 | Complete | 2026-02-10 |
| 8. Suite de Tests Automatises | v1.1 | 2/2 | Complete | 2026-02-10 |
| 9. Detection et Extraction SP | v1.2 | 1/1 | Complete | 2026-02-10 |
| 10. Interface HTML Interactive | v1.2 | 1/1 | Complete | 2026-02-11 |
| 11. Integration MCP File-Based | v1.2 | 0/1 | Not started | - |
