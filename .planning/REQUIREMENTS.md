# Requirements: Generateur de Fiches Techniques Delagrave

**Defined:** 2026-02-15
**Core Value:** Un utilisateur soumet un devis PDF et obtient automatiquement un dossier PowerPoint complet de fiches techniques — sans intervention manuelle.

## v1.4 Requirements

Requirements pour le milestone v1.4 — Gestion CRUD des References.

### CRUD — Gestion des references

- [ ] **CRUD-01**: L'utilisateur peut ajouter une reference avec au minimum code + titre + famille
- [ ] **CRUD-02**: L'utilisateur peut ajouter des champs optionnels (texte, dimensions, ref commerciale)
- [ ] **CRUD-03**: L'utilisateur peut modifier les champs d'une reference existante (titre, texte, dimensions, ref, images)
- [ ] **CRUD-04**: L'utilisateur peut supprimer une reference du catalogue
- [ ] **CRUD-05**: Le systeme valide qu'un code n'existe pas deja avant ajout (et existe avant modification/suppression)

### FAM — Gestion des familles

- [ ] **FAM-01**: Si la famille existe, le produit est ajoute au fichier MD existant
- [ ] **FAM-02**: Si la famille n'existe pas, le systeme cree le fichier MD de la famille et le dossier images
- [ ] **FAM-03**: La nouvelle famille est enregistree dans `_index.md` avec son template de generation

### IMG — Gestion des images

- [ ] **IMG-01**: L'utilisateur peut fournir des chemins d'images lors de l'ajout ou la modification
- [ ] **IMG-02**: Le systeme copie automatiquement les images dans `Delagrave/images/{famille}/`
- [ ] **IMG-03**: Les images existantes sont supprimees lors de la suppression d'une reference

### IDX — Index automatique

- [ ] **IDX-01**: Le fichier `_index.md` est mis a jour automatiquement apres chaque ajout/modification/suppression
- [ ] **IDX-02**: Les compteurs par famille dans `_index.md` sont recalcules correctement

### TEST — Tests

- [ ] **TEST-01**: Tests unitaires pour add, update, delete
- [ ] **TEST-02**: Test d'integration : ajout + lookup + suppression

## Future Requirements

Deferred to future milestones.

### Generation

- **GEN-01**: Modes de generation CHI/DOE/FTI
- **GEN-02**: Integration des fiches-existantes (.pptx pre-existants)

### Synchronisation

- **SYNC-01**: Synchronisation automatique Excel -> MD

## Out of Scope

| Feature | Reason |
|---------|--------|
| Edition du fichier Excel | Les MD sont la source de verite |
| Interface web/GUI pour CRUD | Tout passe par Claude via MCP |
| Gestion des prix/tarifs | Seules les fiches techniques sont gerees |
| Validation visuelle auto | La validation visuelle reste manuelle |
| Bulk import CSV/Excel | Trop complexe pour v1.4, une reference a la fois |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| CRUD-01 | — | Pending |
| CRUD-02 | — | Pending |
| CRUD-03 | — | Pending |
| CRUD-04 | — | Pending |
| CRUD-05 | — | Pending |
| FAM-01 | — | Pending |
| FAM-02 | — | Pending |
| FAM-03 | — | Pending |
| IMG-01 | — | Pending |
| IMG-02 | — | Pending |
| IMG-03 | — | Pending |
| IDX-01 | — | Pending |
| IDX-02 | — | Pending |
| TEST-01 | — | Pending |
| TEST-02 | — | Pending |

**Coverage:**
- v1.4 requirements: 15 total
- Mapped to phases: 0
- Unmapped: 15

---
*Requirements defined: 2026-02-15*
*Last updated: 2026-02-15 after initial definition*
