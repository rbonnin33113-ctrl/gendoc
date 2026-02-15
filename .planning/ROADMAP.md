# Roadmap: Generateur de Fiches Techniques Delagrave

## Milestones

- ✅ **v1.0 Systeme MCP** — Phases 1-6 (shipped 2026-02-10)
- ✅ **v1.1 Qualite et Couverture Familles** — Phases 7-8 (shipped 2026-02-10)
- ✅ **v1.2 Outil de Selection SP** — Phases 9-11 (shipped 2026-02-11)
- ✅ **v1.3 Robustesse et Logging** — Phases 12-15 (shipped 2026-02-11)
- 🚧 **v1.4 Gestion CRUD des References** — Phases 16-19 (in progress)

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

<details>
<summary>✅ v1.2 Outil de Selection SP (Phases 9-11) — SHIPPED 2026-02-11</summary>

- [x] Phase 9: Detection et Extraction SP (1/1 plan) — completed 2026-02-10
- [x] Phase 10: Interface HTML Interactive (1/1 plan) — completed 2026-02-11
- [x] Phase 11: Integration MCP File-Based (1/1 plan) — completed 2026-02-11

</details>

<details>
<summary>✅ v1.3 Robustesse et Logging (Phases 12-15) — SHIPPED 2026-02-11</summary>

- [x] Phase 12: Hot-Reload MCP (1/1 plan) — completed 2026-02-11
- [x] Phase 13: Logging Infrastructure (1/1 plan) — completed 2026-02-11
- [x] Phase 14: Detection Robustesse (1/1 plan) — completed 2026-02-11
- [x] Phase 15: Gestion Erreurs et Resume (2/2 plans) — completed 2026-02-11

</details>

### 🚧 v1.4 Gestion CRUD des References (In Progress)

**Milestone Goal:** Permettre la gestion complete du catalogue de references produit (ajout, modification, suppression) via des outils MCP, avec copie automatique des images et mise a jour de l'index.

#### Phase 16: CRUD Operations
**Goal**: Les utilisateurs peuvent ajouter, modifier et supprimer des references produit via des outils MCP avec validation des codes
**Depends on**: Phase 15
**Requirements**: CRUD-01, CRUD-02, CRUD-03, CRUD-04, CRUD-05
**Success Criteria** (what must be TRUE):
  1. User can add a new product reference with minimum fields (code, titre, famille)
  2. User can add optional fields (texte, dimensions, ref commerciale) to new products
  3. User can update existing product fields (titre, texte, dimensions, ref, images)
  4. User can delete a product reference from the catalog
  5. System prevents duplicate codes on add and validates existence on update/delete
**Plans**: 2 plans in 2 waves

Plans:
- [x] 16-01-PLAN.md — MD writer foundation + add_reference
- [x] 16-02-PLAN.md — update_reference + delete_reference

#### Phase 17: Family and Index Management
**Goal**: Le systeme gere automatiquement les nouvelles familles et met a jour l'index apres chaque operation
**Depends on**: Phase 16
**Requirements**: FAM-01, FAM-02, FAM-03, IDX-01, IDX-02
**Success Criteria** (what must be TRUE):
  1. Adding a product to existing family appends to correct MD file
  2. Adding a product to new family creates family MD file and images directory
  3. New families are registered in _index.md with generation template
  4. _index.md updates automatically after every add/update/delete operation
  5. Family product counters in _index.md recalculate correctly
**Plans**: 1 plan in 1 wave

Plans:
- [x] 17-01-PLAN.md — Index manager module + MCP CRUD integration

#### Phase 18: Image Management
**Goal**: Les images produit sont copiees automatiquement depuis des chemins fournis et gerees lors des suppressions
**Depends on**: Phase 17
**Requirements**: IMG-01, IMG-02, IMG-03
**Success Criteria** (what must be TRUE):
  1. User can provide image paths when adding or updating products
  2. System copies images automatically to Delagrave/images/{famille}/
  3. Images are removed from filesystem when product is deleted
**Plans**: 1 plan in 1 wave

Plans:
- [ ] 18-01-PLAN.md — Image handler module + MCP CRUD integration

#### Phase 19: Tests and Integration
**Goal**: Le systeme CRUD est teste de maniere exhaustive avec tests unitaires et integration
**Depends on**: Phase 18
**Requirements**: TEST-01, TEST-02
**Success Criteria** (what must be TRUE):
  1. Unit tests cover add, update, and delete operations
  2. Integration test validates full workflow: add product, lookup, then delete
  3. All CRUD tests pass in CI pipeline
**Plans**: TBD

Plans:
- [ ] 19-01: TBD

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
| 11. Integration MCP File-Based | v1.2 | 1/1 | Complete | 2026-02-11 |
| 12. Hot-Reload MCP | v1.3 | 1/1 | Complete | 2026-02-11 |
| 13. Logging Infrastructure | v1.3 | 1/1 | Complete | 2026-02-11 |
| 14. Detection Robustesse | v1.3 | 1/1 | Complete | 2026-02-11 |
| 15. Gestion Erreurs et Resume | v1.3 | 2/2 | Complete | 2026-02-11 |
| 16. CRUD Operations | v1.4 | 2/2 | Complete | 2026-02-15 |
| 17. Family and Index Management | v1.4 | 1/1 | Complete | 2026-02-15 |
| 18. Image Management | v1.4 | 0/1 | Not started | - |
| 19. Tests and Integration | v1.4 | 0/1 | Not started | - |
