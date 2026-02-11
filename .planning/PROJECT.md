# Generateur de Fiches Techniques Delagrave

## What This Is

Un systeme MCP + commandes `/gendoc-*` pour Claude Code qui automatise la generation de dossiers de fiches techniques PowerPoint pour les produits Delagrave. L'utilisateur soumet un devis PDF via `/gendoc-full`, le systeme extrait les references, genere les fiches techniques avec le bon layout par famille, et produit un document PowerPoint complet (couverture avec logo, sommaire, chapitres, fiches, revetements). Les articles speciaux (SP) sont geres via une page HTML interactive pour selectionner/editer les fiches avant generation. 5,308 lignes Python + 932 lignes de tests, 359 references produit, 10 outils MCP, 56 tests automatises.

## Core Value

Un utilisateur soumet un devis PDF et obtient automatiquement un dossier PowerPoint complet de fiches techniques — sans intervention manuelle.

## Current Milestone: v1.3 Robustesse et Logging

**Goal:** Rendre le pipeline fiable et transparent — hot-reload MCP, logging complet, detection devis amelioree, gestion d'erreurs claire.

**Target features:**
- Hot-reload des modules generateurs dans le serveur MCP
- Systeme de logging pipeline (fichier LOG par execution, erreurs + solutions)
- Sortie resume compact pour /gendoc-full (au lieu du defilement)
- Reduction des faux positifs dans l'analyse devis PDF
- Messages d'erreur clairs et exploitables

## Current State (v1.2 shipped 2026-02-11)

- **Package**: `src/gendoc/` (extractors, parsers, generators, utils, mcp, cli)
- **Data**: 359 references dans 9 fichiers MD, 268 images locales
- **MCP Tools**: lookup_reference, search_references, list_families, analyze_devis, preview_generation, generate_slides, add_reference (stub), create_custom_product, open_sp_selector, load_sp_selection
- **Skills**: /gendoc-lookup, /gendoc-analyze, /gendoc-generate, /gendoc-full
- **Template**: Modele fiche technique vide - Ind J.potm (6 layouts, A4 portrait)
- **Families**: 8 familles validees (paillasse, sorbonne, revetement, meubles, tables-en, equipement, elec-sorb, complements)
- **SP Workflow**: analyze_devis -> open_sp_selector (HTML) -> load_sp_selection (JSON) -> generate_slides
- **Tests**: 56 tests pytest (16 family generation, 4 E2E pipeline, 14 unit md_parser, 14 SP detection, 8 SP workflow) — <17s

## Requirements

### Validated

- Fichiers MD de references produit organises par famille (source de verite) — v1.0
- Serveur MCP d'analyse de devis PDF (extraction des references) — v1.0
- Serveur MCP de generation PowerPoint (fiches techniques completes) — v1.0
- Document PowerPoint complet : couverture, sommaire, fiches par famille — v1.0
- Pipeline complet /gendoc-full (PDF -> preview -> PowerPoint) — v1.0
- Toutes les 8 familles generent des fiches correctes avec placeholders remplis — v1.1
- Auto-sizing (TEXT_TO_FIT_SHAPE) sur tous les placeholders texte — v1.1
- Placeholders vides supprimes pour toutes les familles — v1.1
- Articles speciaux (SP-prefixed) supportes via custom products — v1.1
- Suite de tests automatises : 34 tests couvrant toutes les familles et le pipeline E2E — v1.1
- Detection correcte des codes SP (SPMOB, SPPAIL, SPTABLEEN, SPUSE) dans speciaux — v1.2
- Extraction des designations SP multi-lignes depuis le PDF — v1.2
- Page HTML interactive pour selectionner/editer les articles SP du catalogue — v1.2
- Export JSON des articles SP edites au format custom_products — v1.2
- Outils MCP open_sp_selector et load_sp_selection pour le workflow file-based — v1.2
- Workflow complet analyze_devis -> HTML -> JSON -> generate_slides fonctionnel — v1.2

### Active

- [ ] Hot-reload MCP : changements de code pris en compte sans redemarrage serveur
- [ ] Logging pipeline : fichier LOG par execution /gendoc-full avec toutes les etapes
- [ ] Sortie resume compact : progression concise au lieu du defilement
- [ ] Detection devis : reduction des faux positifs (mots detectes a tort comme codes)
- [ ] Gestion d'erreurs : messages clairs, erreurs loggees meme quand resolues
- [ ] Modes de generation CHI/DOE/FTI (deferred from v1.0)
- [ ] Integration des fiches-existantes (fichiers .pptx pre-existants)
- [ ] Implementation complete de add_reference (actuellement stub)
- [ ] Synchronisation automatique Excel -> MD

### Out of Scope

- Edition du fichier Excel original — les MD sont la source de verite
- Interface web ou GUI — tout passe par Claude via MCP
- Gestion des prix/tarifs — seules les fiches techniques sont generees
- Tests visuels automatiques — la validation visuelle reste manuelle
- Serveur HTTP local — approche file-based preferee (HTML auto-contenu + export JSON)
- Gestion des quantites SP — non necessaire pour les fiches techniques

## Constraints

- **Tech stack**: Python, FastMCP, python-pptx, pdfplumber, pytest — Claude Code compatible
- **Template**: Le template .potm existant est reutilise tel quel (conversion zip pour contourner limitation python-pptx)
- **Format devis**: Les devis PDF Delagrave ont un format structure (sections hierarchiques)
- **Images**: Stockees localement dans Delagrave/images/{famille}/

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| MD comme source de verite | Decouple des macros Excel, versionnable | Good — 359 refs extraites, lookup fonctionnel |
| Serveur MCP unique FastMCP | Permet a Claude d'appeler les outils directement | Good — 10 outils, pipeline complet |
| Document complet (pas fiches isolees) | L'utilisateur veut un dossier pret a l'emploi | Good — couverture, sommaire, chapitres |
| Conversion .potm via zipfile | python-pptx ne lit pas les .potm natifs | Good — trick fiable |
| Split texte revetement en 3 zones | Texte debordait du cadre unique | Good — TEXTE/MEO/FINITION |
| VBA_TO_PLACEHOLDER pour toutes les familles | Mapping systematique VBA -> placeholder idx | Good — 8 familles couvertes |
| Custom products via deep copy + field override | Articles speciaux SP sans reference catalogue | Good — flexible, MCP tool cree |
| Pytest parametrize par famille | Un test par famille, execution rapide | Good — 56 tests en <17s |
| Designation extraction multi-lignes | Articles SP ont des descriptions longues dans le PDF | Good — texte complet avec dimensions |
| HTML auto-contenu avec catalogue embarque | Pas de serveur HTTP, pas de dependances externes | Good — 320 produits, ~500KB HTML |
| Partial export SP | L'utilisateur peut configurer seulement certains SP | Good — feedback utilisateur integre |
| MCP file-based workflow | HTML doit persister pour interaction navigateur | Good — workflow asynchrone utilisateur |

---
*Last updated: 2026-02-11 after v1.3 milestone start*
