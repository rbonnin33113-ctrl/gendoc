# Requirements: Generateur de Fiches Techniques Delagrave

**Defined:** 2026-02-10
**Core Value:** Un utilisateur soumet un devis PDF et obtient automatiquement un dossier PowerPoint complet de fiches techniques

## v1.2 Requirements

Requirements for SP selection tool milestone.

### Bug Fix

- [x] **BUG-01**: Les codes SP (SPMOB, SPPAIL, SPTABLEEN, SPUSE) sont correctement detectes et classes dans `speciaux` (pas dans `inconnus`)

### Extraction

- [x] **EXT-01**: L'analyse du devis extrait la designation textuelle de chaque article SP depuis le PDF (ex: "Meuble bas mobile - Dim. 600x500x724mm - Melamine Blanc")
- [x] **EXT-02**: L'analyse du devis retourne pour chaque SP : code, famille, designation extraite du PDF

### Interface HTML

- [ ] **UI-01**: La page HTML affiche la liste des articles SP du devis avec leurs designations pre-remplies
- [ ] **UI-02**: L'utilisateur peut choisir l'article standard du catalogue se rapprochant le plus de son SP (recherche/selection parmi les references existantes)
- [ ] **UI-03**: L'utilisateur peut modifier tous les champs de l'article choisi (titre, texte, dimensions, images) pour correspondre au descriptif du SP
- [ ] **UI-04**: La page HTML exporte un fichier JSON avec les articles selectionnes et edites

### Integration MCP

- [ ] **MCP-01**: Un outil MCP charge le fichier JSON exporte par la page HTML et retourne les custom products prets pour la generation
- [ ] **MCP-02**: Le workflow complet fonctionne : analyze_devis → open_sp_selector → load_sp_selection → generate_slides

## Future Requirements

### Fonctionnalites avancees

- **ADV-01**: Modes de generation CHI/DOE/FTI
- **ADV-02**: Integration des fiches-existantes (.pptx pre-existants)
- **ADV-03**: Implementation complete de add_reference
- **ADV-04**: Synchronisation automatique Excel -> MD

## Out of Scope

| Feature | Reason |
|---------|--------|
| Serveur HTTP local | Approche file-based preferee (HTML auto-contenu + export JSON) |
| Gestion des quantites SP | Non necessaire pour les fiches techniques |
| Upload d'images depuis le HTML | Les images sont dans le catalogue existant |
| Tests visuels automatiques du HTML | La validation du HTML reste manuelle |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| BUG-01 | Phase 9 | Done |
| EXT-01 | Phase 9 | Done |
| EXT-02 | Phase 9 | Done |
| UI-01 | Phase 10 | Pending |
| UI-02 | Phase 10 | Pending |
| UI-03 | Phase 10 | Pending |
| UI-04 | Phase 10 | Pending |
| MCP-01 | Phase 11 | Pending |
| MCP-02 | Phase 11 | Pending |

**Coverage:**
- v1.2 requirements: 9 total
- Mapped to phases: 9
- Unmapped: 0

**Phase Mapping:**
- Phase 9 (Detection et Extraction SP): 3 requirements (BUG-01, EXT-01, EXT-02)
- Phase 10 (Interface HTML Interactive): 4 requirements (UI-01, UI-02, UI-03, UI-04)
- Phase 11 (Integration MCP File-Based): 2 requirements (MCP-01, MCP-02)

---
*Requirements defined: 2026-02-10*
*Last updated: 2026-02-10 after v1.2 roadmap creation*
