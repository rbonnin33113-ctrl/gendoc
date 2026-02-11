# Requirements: Generateur de Fiches Techniques Delagrave

**Defined:** 2026-02-11
**Core Value:** Un utilisateur soumet un devis PDF et obtient automatiquement un dossier PowerPoint complet de fiches techniques — sans intervention manuelle.

## v1.3 Requirements

Requirements pour le milestone v1.3 Robustesse et Logging.

### Hot-Reload MCP

- [x] **RELOAD-01**: Le serveur MCP prend en compte les modifications des modules generateurs sans redemarrage
- [x] **RELOAD-02**: Le hot-reload est transparent (pas d'erreur si les modules n'ont pas change)

### Logging Pipeline

- [ ] **LOG-01**: Chaque execution /gendoc-full cree un fichier log horodate dans `Delagrave/output/logs/`
- [ ] **LOG-02**: Le log contient chaque etape du pipeline : analyse PDF, preview, SP, generation, avec duree
- [ ] **LOG-03**: Les erreurs rencontrees sont loggees avec le contexte (code produit, fichier, traceback)
- [ ] **LOG-04**: Les erreurs resolues automatiquement sont loggees avec la solution appliquee
- [ ] **LOG-05**: Le fichier log.md est structure comme un prompt diagnostique : resume d'execution, erreurs avec contexte, solutions appliquees — exploitable par l'IA en mode dev pour deboguer et ameliorer le pipeline
- [ ] **LOG-06**: Le log inclut les parametres d'entree (chemin PDF, codes extraits, devis_info) pour permettre la reproduction du probleme

### Sortie Resume

- [ ] **OUTPUT-01**: /gendoc-full affiche un resume compact par etape (Analyse OK, 28 refs... Generation OK, 45 pages)
- [ ] **OUTPUT-02**: Les details techniques ne defilent plus a l'ecran pendant l'execution

### Detection Devis

- [ ] **DETECT-01**: Les faux positifs courants (850MM, CONDITIONS, LIVRAISON, SALLE, etc.) sont filtres
- [ ] **DETECT-02**: Un mecanisme de liste d'exclusion configurable existe pour les mots a ignorer
- [ ] **DETECT-03**: Les codes inconnus sont logges pour analyse ulterieure

### Gestion Erreurs

- [ ] **ERR-01**: Les erreurs de generation (image manquante, template non trouve, etc.) produisent des messages clairs
- [ ] **ERR-02**: Le pipeline continue malgre une erreur sur un produit individuel (skip + log)
- [ ] **ERR-03**: Le rapport final liste les produits en erreur avec la raison

## Future Requirements (v1.4+)

- **ADV-01**: Modes de generation CHI/DOE/FTI
- **ADV-02**: Integration des fiches-existantes (fichiers .pptx pre-existants)
- **ADV-03**: Implementation complete de add_reference
- **ADV-04**: Synchronisation automatique Excel -> MD

## Out of Scope

| Feature | Reason |
|---------|--------|
| Dashboard web de logs | Les fichiers LOG.md suffisent, pas besoin d'UI |
| Retry automatique | Les erreurs doivent etre analysees, pas masquees |
| Mode verbose/debug interactif | Le log file couvre ce besoin |
| Edition Excel | Les MD sont la source de verite |
| Interface web/GUI | Tout passe par Claude via MCP |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| RELOAD-01 | Phase 12 | Done |
| RELOAD-02 | Phase 12 | Done |
| LOG-01 | Phase 13 | Pending |
| LOG-02 | Phase 13 | Pending |
| LOG-03 | Phase 13 | Pending |
| LOG-04 | Phase 13 | Pending |
| LOG-05 | Phase 13 | Pending |
| LOG-06 | Phase 13 | Pending |
| DETECT-01 | Phase 14 | Pending |
| DETECT-02 | Phase 14 | Pending |
| DETECT-03 | Phase 14 | Pending |
| OUTPUT-01 | Phase 15 | Pending |
| OUTPUT-02 | Phase 15 | Pending |
| ERR-01 | Phase 15 | Pending |
| ERR-02 | Phase 15 | Pending |
| ERR-03 | Phase 15 | Pending |

**Coverage:**
- v1.3 requirements: 16 total
- Mapped to phases: 16
- Unmapped: 0

**Phase Distribution:**
- Phase 12 (Hot-Reload MCP): 2 requirements
- Phase 13 (Logging Infrastructure): 6 requirements
- Phase 14 (Detection Robustesse): 3 requirements
- Phase 15 (Gestion Erreurs et Resume): 5 requirements

---
*Requirements defined: 2026-02-11*
*Last updated: 2026-02-11 after roadmap creation*
