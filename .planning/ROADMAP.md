# Roadmap: Generateur de Fiches Techniques Delagrave

## Milestones

- ✅ **v1.0 Systeme MCP** — Phases 1-6 (shipped 2026-02-10)
- 🚧 **v1.1 Qualite et Couverture Familles** — Phases 7-8 (in progress)

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

### 🚧 v1.1 Qualite et Couverture Familles (In Progress)

**Milestone Goal:** S'assurer que toutes les familles produit generent des fiches correctes et mettre en place des tests automatises pour prevenir les regressions.

#### Phase 7: Verification et Correction des Familles

**Goal**: Toutes les familles (paillasse, sorbonne, meubles, tables-en, equipement, elec-sorb, complements) generent des fiches PowerPoint correctes avec placeholders remplis, textes auto-ajustes et images bien positionnees.

**Depends on**: Phase 6 (v1.0 pipeline complet)

**Requirements**: FAM-01, FAM-02, FAM-03, FAM-04, FAM-05, FAM-06, FAM-07, FAM-08, TXT-01, TXT-02

**Success Criteria** (what must be TRUE):
1. User can generate a sample fiche for each of the 8 families and visually verify layout correctness
2. All text fields use auto-sizing (TEXT_TO_FIT_SHAPE) and no text overflows placeholder boundaries
3. All placeholder images are correctly positioned and visible in the generated slides
4. Empty placeholders are removed from all generated slides (no "Cliquez pour ajouter" text remains)
5. Product reference codes are displayed correctly for all families

**Plans:** 3 plans

Plans:
- [x] 07-01-PLAN.md — Fix VBA-to-placeholder mappings for all 8 families and programmatic verification
- [x] 07-02-PLAN.md — Visual verification of all families with human checkpoint and targeted fixes
- [x] 07-03-PLAN.md — Support articles speciaux (SP-prefixed: SPMOB, SPPAIL, SPTABLEEN, SPUSE)

#### Phase 8: Suite de Tests Automatises

**Goal**: Un pipeline pytest execute automatiquement pour verifier que chaque famille genere des slides valides et que le flux E2E fonctionne.

**Depends on**: Phase 7

**Requirements**: TEST-01, TEST-02, TEST-03

**Success Criteria** (what must be TRUE):
1. User can run `pytest` and get a passing test suite that validates all families
2. Each family has at least one test that generates a .pptx file and verifies slide count and placeholder population
3. The E2E pipeline test (analyze -> preview -> generate) successfully processes the test devis PDF
4. Tests are integrated into the project structure and documented for future development

**Plans**: TBD

Plans:
- [ ] 08-01: TBD

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
| 8. Suite de Tests Automatises | v1.1 | 0/? | Not started | - |
