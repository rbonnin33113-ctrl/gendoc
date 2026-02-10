# Requirements: Generateur de Fiches Techniques Delagrave

**Defined:** 2026-02-10
**Core Value:** Un utilisateur soumet un devis PDF et obtient automatiquement un dossier PowerPoint complet de fiches techniques

## v1.2 Requirements

Requirements for SP selection tool milestone.

### Bug Fix

- [ ] **BUG-01**: Les codes SP (SPMOB, SPPAIL, SPTABLEEN, SPUSE) sont correctement detectes et classes dans `speciaux` (pas dans `inconnus`)

### Extraction

- [ ] **EXT-01**: L'analyse du devis extrait la designation textuelle de chaque article SP depuis le PDF (ex: "Meuble bas mobile - Dim. 600x500x724mm - Melamine Blanc")
- [ ] **EXT-02**: L'analyse du devis retourne pour chaque SP : code, famille, designation extraite du PDF

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
| BUG-01 | TBD | Pending |
| EXT-01 | TBD | Pending |
| EXT-02 | TBD | Pending |
| UI-01 | TBD | Pending |
| UI-02 | TBD | Pending |
| UI-03 | TBD | Pending |
| UI-04 | TBD | Pending |
| MCP-01 | TBD | Pending |
| MCP-02 | TBD | Pending |

**Coverage:**
- v1.2 requirements: 9 total
- Mapped to phases: 0
- Unmapped: 9

---
*Requirements defined: 2026-02-10*
*Last updated: 2026-02-10 after initial definition*
