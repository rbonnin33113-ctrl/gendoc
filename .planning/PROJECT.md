# Generateur de Fiches Techniques Delagrave

## What This Is

Un systeme MCP + commandes `/gendoc-*` pour Claude Code qui automatise la generation de dossiers de fiches techniques PowerPoint pour les produits Delagrave. L'utilisateur soumet un devis PDF via `/gendoc-full`, le systeme extrait les references, genere les fiches techniques avec le bon layout par famille, et produit un document PowerPoint complet (couverture avec logo, sommaire, chapitres, fiches, revetements). 3,914 lignes Python + 403 lignes de tests, 359 references produit, 8 outils MCP, 34 tests automatises.

## Core Value

Un utilisateur soumet un devis PDF et obtient automatiquement un dossier PowerPoint complet de fiches techniques — sans intervention manuelle.

## Current State (v1.1 shipped 2026-02-10)

- **Package**: `src/gendoc/` (extractors, parsers, generators, utils, mcp, cli)
- **Data**: 359 references dans 9 fichiers MD, 268 images locales
- **MCP Tools**: lookup_reference, search_references, list_families, analyze_devis, preview_generation, generate_slides, add_reference (stub), create_custom_product
- **Skills**: /gendoc-lookup, /gendoc-analyze, /gendoc-generate, /gendoc-full
- **Template**: Modele fiche technique vide - Ind J.potm (6 layouts, A4 portrait)
- **Families**: 8 familles validees (paillasse, sorbonne, revetement, meubles, tables-en, equipement, elec-sorb, complements)
- **Tests**: 34 tests pytest (8 generation par famille, 4 E2E pipeline, 13 unit md_parser, 9 lookup/util) — <9s

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

### Active

- [ ] Modes de generation CHI/DOE/FTI (deferred from v1.0)
- [ ] Integration des fiches-existantes (fichiers .pptx pre-existants)
- [ ] Implementation complete de add_reference (actuellement stub)
- [ ] Synchronisation automatique Excel -> MD

### Out of Scope

- Edition du fichier Excel original — les MD sont la source de verite
- Interface web ou GUI — tout passe par Claude via MCP
- Gestion des prix/tarifs — seules les fiches techniques sont generees
- Tests visuels automatiques — la validation visuelle reste manuelle

## Constraints

- **Tech stack**: Python, FastMCP, python-pptx, pdfplumber, pytest — Claude Code compatible
- **Template**: Le template .potm existant est reutilise tel quel (conversion zip pour contourner limitation python-pptx)
- **Format devis**: Les devis PDF Delagrave ont un format structure (sections hierarchiques)
- **Images**: Stockees localement dans Delagrave/images/{famille}/

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| MD comme source de verite | Decouple des macros Excel, versionnable | Good — 359 refs extraites, lookup fonctionnel |
| Serveur MCP unique FastMCP | Permet a Claude d'appeler les outils directement | Good — 8 outils, pipeline complet |
| Document complet (pas fiches isolees) | L'utilisateur veut un dossier pret a l'emploi | Good — couverture, sommaire, chapitres |
| Conversion .potm via zipfile | python-pptx ne lit pas les .potm natifs | Good — trick fiable |
| Split texte revetement en 3 zones | Texte debordait du cadre unique | Good — TEXTE/MEO/FINITION |
| VBA_TO_PLACEHOLDER pour toutes les familles | Mapping systematique VBA -> placeholder idx | Good — 8 familles couvertes |
| Custom products via deep copy + field override | Articles speciaux SP sans reference catalogue | Good — flexible, MCP tool cree |
| Pytest parametrize par famille | Un test par famille, execution rapide | Good — 34 tests en <9s |

---
*Last updated: 2026-02-10 after v1.1 milestone completion*
