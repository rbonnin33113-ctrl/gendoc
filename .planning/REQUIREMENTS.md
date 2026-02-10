# Requirements: Generateur de Fiches Techniques Delagrave

**Defined:** 2026-02-10
**Core Value:** Un utilisateur soumet un devis PDF et obtient automatiquement un dossier PowerPoint complet de fiches techniques

## v1.1 Requirements

Requirements for quality and family coverage milestone.

### Tests

- [ ] **TEST-01**: L'utilisateur peut executer une suite de tests automatises qui genere une fiche par famille et verifie que le fichier PowerPoint est valide
- [ ] **TEST-02**: Chaque famille (paillasse, sorbonne, revetement, meubles, tables-en, equipement, elec-sorb, complements) a au moins un test de generation qui verifie le nombre de slides et placeholders remplis
- [ ] **TEST-03**: Un test du pipeline complet (analyze -> preview -> generate) valide le flux de bout en bout avec le devis PDF test

### Couverture Familles

- [ ] **FAM-01**: Les fiches paillasse sont generees avec le bon layout, les dimensions correctes et les images positionnees
- [ ] **FAM-02**: Les fiches sorbonne sont generees avec le bon layout, les dimensions correctes et les images positionnees
- [ ] **FAM-03**: Les fiches meubles sont generees avec le bon layout et les images
- [ ] **FAM-04**: Les fiches tables-en sont generees avec le bon layout et les images
- [ ] **FAM-05**: Les fiches equipement sont generees avec le bon layout, la reference et les images positionnees
- [ ] **FAM-06**: Les fiches elec-sorb sont generees avec le bon layout et les images positionnees
- [ ] **FAM-07**: Les fiches complements sont generees correctement
- [ ] **FAM-08**: Les placeholders vides sont supprimes (pas de "Cliquez pour ajouter") pour toutes les familles

### Qualite Texte

- [ ] **TXT-01**: L'auto-sizing (TEXT_TO_FIT_SHAPE) est applique sur tous les placeholders texte de toutes les familles
- [ ] **TXT-02**: Les textes longs ne debordent pas des cadres pour aucune famille

## v2 Requirements

### Fonctionnalites avancees

- **ADV-01**: Modes de generation CHI/DOE/FTI
- **ADV-02**: Integration des fiches-existantes (.pptx pre-existants)
- **ADV-03**: Implementation complete de add_reference
- **ADV-04**: Synchronisation automatique Excel -> MD

## Out of Scope

| Feature | Reason |
|---------|--------|
| Fidelite pixel-perfect avec VBA | Les slides doivent etre correctes et lisibles, pas identiques au pixel |
| Tests visuels automatiques | La validation visuelle reste manuelle, les tests verifient structure et contenu |
| Refactoring architectural | Le code v1.0 fonctionne, on corrige les bugs pas la structure |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| TEST-01 | TBD | Pending |
| TEST-02 | TBD | Pending |
| TEST-03 | TBD | Pending |
| FAM-01 | TBD | Pending |
| FAM-02 | TBD | Pending |
| FAM-03 | TBD | Pending |
| FAM-04 | TBD | Pending |
| FAM-05 | TBD | Pending |
| FAM-06 | TBD | Pending |
| FAM-07 | TBD | Pending |
| FAM-08 | TBD | Pending |
| TXT-01 | TBD | Pending |
| TXT-02 | TBD | Pending |

**Coverage:**
- v1.1 requirements: 13 total
- Mapped to phases: 0
- Unmapped: 13

---
*Requirements defined: 2026-02-10*
*Last updated: 2026-02-10 after initial definition*
