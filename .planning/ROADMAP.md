# Roadmap: Generateur de Fiches Techniques Delagrave

## Overview

Ce roadmap transforme un systeme Excel+VBA en un pipeline MCP automatise : d'abord migrer les donnees produit vers des fichiers Markdown (source de verite), puis construire les serveurs MCP qui analysent les devis PDF et generent les fiches techniques PowerPoint. Le parcours va de la fondation de donnees jusqu'a une commande unique `/gendoc-full` qui prend un PDF et produit un dossier complet.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Fondation Donnees** - Migration Excel vers MD et organisation des images locales ✓ (2026-02-09)
- [x] **Phase 2: Infrastructure MCP** - Squelettes des serveurs MCP et enregistrement des commandes CLI ✓ (2026-02-10)
- [x] **Phase 3: Analyse de Devis** - Parsing PDF, extraction de references, detection de familles et revetements ✓ (2026-02-10)
- [x] **Phase 4: Generation PowerPoint** - Creation de slides avec layouts corrects, placeholders et images ✓ (2026-02-10)
- [ ] **Phase 5: Assemblage Document** - Pages de garde, couvertures de chapitres, sommaire et modes de generation
- [ ] **Phase 6: Integration Pipeline** - Commande pipeline complete et previsualisation

## Phase Details

### Phase 1: Fondation Donnees
**Goal**: Les donnees produit sont disponibles dans des fichiers Markdown fiables, organisees par famille, avec images locales accessibles
**Depends on**: Nothing (first phase)
**Requirements**: DATA-01, DATA-02, DATA-03, DATA-04, IMG-01, IMG-02
**Success Criteria** (what must be TRUE):
  1. L'utilisateur peut executer `/gendoc-extract-refs` et obtenir des fichiers MD structures par famille contenant toutes les references du Excel
  2. L'utilisateur peut consulter les donnees d'une reference specifique via `/gendoc-lookup` et voir code, ref, titre, texte, dimensions et chemins images
  3. L'utilisateur peut ajouter une nouvelle reference ou modifier une existante dans les fichiers MD sans casser la structure
  4. Les images produit sont presentes localement, organisees par famille, et les chemins dans les MD pointent vers ces fichiers locaux accessibles
**Plans**: 2 plans

Plans:
- [x] 01-01-PLAN.md -- Extraction Excel vers Markdown (script Python + 9 MD + validation) ✓
- [x] 01-02-PLAN.md -- Organisation images locales et lookup references (images, parser MD, CLI lookup) ✓

### Phase 2: Infrastructure MCP
**Goal**: Les serveurs MCP sont operationnels et les commandes `/gendoc-*` sont enregistrees dans Claude Code CLI
**Depends on**: Phase 1
**Requirements**: MCP-01, MCP-02, MCP-03, MCP-04
**Success Criteria** (what must be TRUE):
  1. Un serveur MCP d'analyse de devis PDF demarre et repond aux appels d'outils depuis Claude Code
  2. Un serveur MCP de references produit demarre et permet de consulter/gerer les donnees MD
  3. Un serveur MCP de generation PowerPoint demarre et peut recevoir des instructions de generation
  4. Les commandes `/gendoc-*` sont disponibles dans Claude Code CLI et declenchent les bons serveurs MCP
**Plans**: 2 plans

Plans:
- [x] 02-01-PLAN.md -- Serveur MCP unique avec 6 outils (references, devis stub, generation stub) et configuration .mcp.json ✓
- [x] 02-02-PLAN.md -- Enregistrement des 4 commandes /gendoc-* comme skills Claude Code ✓

### Phase 3: Analyse de Devis
**Goal**: Un devis PDF soumis est parse et produit une liste structuree de references uniques avec familles et revetements detectes
**Depends on**: Phase 2
**Requirements**: DEV-01, DEV-02, DEV-03, DEV-04
**Success Criteria** (what must be TRUE):
  1. L'utilisateur soumet un devis PDF via `/gendoc-analyze` et obtient la liste des references produit uniques
  2. Chaque reference extraite est automatiquement associee a sa famille produit (Paillasse, Sorbonne, Meuble, etc.)
  3. Les references absentes des fichiers MD sont clairement signalees a l'utilisateur avec un rapport d'erreur
  4. Les produits lies a un revetement (paillasses GE/GR, sorbonnes autoportantes) sont detectes et le revetement associe est identifie dans le resultat
**Plans**: 2 plans

Plans:
- [x] 03-01-PLAN.md -- Modules PDF parser et devis analyzer (extraction texte, identification codes, classification familles/revetements) ✓
- [x] 03-02-PLAN.md -- Integration MCP et mise a jour skill /gendoc-analyze ✓

### Phase 4: Generation PowerPoint
**Goal**: Les fiches techniques individuelles sont generees correctement dans des slides PowerPoint avec le bon layout, les bonnes donnees et les bonnes images
**Depends on**: Phase 3
**Requirements**: GEN-01, GEN-02, GEN-03, GEN-04, GEN-05
**Success Criteria** (what must be TRUE):
  1. L'utilisateur peut generer un fichier PowerPoint contenant des fiches techniques via `/gendoc-generate`
  2. Chaque fiche utilise le layout PowerPoint correspondant a sa famille (Paillasse, Sorbonne, Revetement, Meuble, Equipement)
  3. Les donnees produit apparaissent dans les bons placeholders du template (titre, caracteristiques, reference, dimensions aux positions correctes)
  4. Les images produit sont inserees aux bonnes positions dans chaque slide
  5. Quand un produit avec revetement est inclus, la fiche revetement correspondante est automatiquement generee dans le document
**Plans**: 2 plans

Plans:
- [x] 04-01-PLAN.md -- Module pptx_generator.py: template loading, layouts par famille, mapping VBA-to-placeholder, images, revetements ✓
- [x] 04-02-PLAN.md -- Integration MCP (generate_slides fonctionnel) et mise a jour skill /gendoc-generate ✓

### Phase 5: Assemblage Document
**Goal**: Le document PowerPoint genere est un dossier complet et professionnel avec couverture, chapitres, sommaire et choix de mode
**Depends on**: Phase 4
**Requirements**: GEN-06, GEN-07, GEN-08, GEN-09
**Success Criteria** (what must be TRUE):
  1. Le document genere commence par une page de couverture utilisant le layout "Page de garde" du template
  2. Chaque famille/chapitre est introduite par une page de garde de chapitre
  3. Le document inclut un sommaire automatique avec les numeros de page corrects
  4. L'utilisateur peut choisir le mode de generation (CHI, DOE, FTI) et le document produit reflette ce choix
**Plans**: TBD

Plans:
- [ ] 05-01: Couverture, chapitres et sommaire
- [ ] 05-02: Modes de generation CHI/DOE/FTI

### Phase 6: Integration Pipeline
**Goal**: L'utilisateur peut executer le workflow complet en une seule commande, avec previsualisation avant generation
**Depends on**: Phase 5
**Requirements**: PIPE-01, PIPE-02
**Success Criteria** (what must be TRUE):
  1. L'utilisateur execute `/gendoc-full` avec un devis PDF et obtient un dossier PowerPoint complet sans etapes intermediaires manuelles
  2. L'utilisateur peut previsualiser la liste des fiches qui seront generees (avec familles et revetements) et confirmer avant de lancer la generation
**Plans**: TBD

Plans:
- [ ] 06-01: Pipeline complet et previsualisation

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5 -> 6

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Fondation Donnees | 2/2 | Complete ✓ | 2026-02-09 |
| 2. Infrastructure MCP | 2/2 | Complete ✓ | 2026-02-10 |
| 3. Analyse de Devis | 2/2 | Complete ✓ | 2026-02-10 |
| 4. Generation PowerPoint | 2/2 | Complete ✓ | 2026-02-10 |
| 5. Assemblage Document | 0/2 | Not started | - |
| 6. Integration Pipeline | 0/1 | Not started | - |
