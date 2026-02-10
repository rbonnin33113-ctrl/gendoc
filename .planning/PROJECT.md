# Generateur de Fiches Techniques Delagrave

## What This Is

Un systeme MCP + commandes `/gendoc-*` pour Claude Code qui automatise la generation de dossiers de fiches techniques PowerPoint pour les produits Delagrave. L'utilisateur soumet un devis PDF via `/gendoc-full`, le systeme extrait les references, genere les fiches techniques avec le bon layout par famille, et produit un document PowerPoint complet (couverture avec logo, sommaire, chapitres, fiches, revetements). 3,775 lignes Python, 359 references produit, 7 outils MCP.

## Core Value

Un utilisateur soumet un devis PDF et obtient automatiquement un dossier PowerPoint complet de fiches techniques — sans intervention manuelle.

## Current State (v1.0 shipped 2026-02-10)

- **Package**: `src/gendoc/` (extractors, parsers, generators, utils, mcp, cli)
- **Data**: 359 references dans 9 fichiers MD, 268 images locales
- **MCP Tools**: lookup_reference, search_references, list_families, analyze_devis, preview_generation, generate_slides, add_reference (stub)
- **Skills**: /gendoc-lookup, /gendoc-analyze, /gendoc-generate, /gendoc-full
- **Template**: Modele fiche technique vide - Ind J.potm (6 layouts, A4 portrait)

## Current Milestone: v1.1 Qualite et Couverture Familles

**Goal:** S'assurer que toutes les familles produit generent des fiches correctes et mettre en place des tests automatises pour prevenir les regressions.

**Target features:**
- Tests automatises par famille (generation + validation)
- Verification et correction de chaque famille (paillasse, sorbonne, meubles, tables-en, equipement, elec-sorb, complements)
- Auto-sizing et split texte generalises si necessaire

## Requirements

### Validated

- Fichiers MD de references produit organises par famille (source de verite) — v1.0
- Serveur MCP d'analyse de devis PDF (extraction des references) — v1.0
- Serveur MCP de generation PowerPoint (fiches techniques completes) — v1.0
- Document PowerPoint complet : couverture, sommaire, fiches par famille — v1.0
- Pipeline complet /gendoc-full (PDF -> preview -> PowerPoint) — v1.0

### Active

- [ ] Tests automatises par famille de produit
- [ ] Couverture complete de toutes les familles (corrections si necessaire)
- [ ] Modes de generation CHI/DOE/FTI (deferred from v1.0)
- [ ] Integration des fiches-existantes (fichiers .pptx pre-existants)
- [ ] Implementation complete de add_reference (actuellement stub)

### Out of Scope

- Edition du fichier Excel original — les MD sont la source de verite
- Interface web ou GUI — tout passe par Claude via MCP
- Gestion des prix/tarifs — seules les fiches techniques sont generees

## Constraints

- **Tech stack**: Python, FastMCP, python-pptx, pdfplumber — Claude Code compatible
- **Template**: Le template .potm existant est reutilise tel quel (conversion zip pour contourner limitation python-pptx)
- **Format devis**: Les devis PDF Delagrave ont un format structure (sections hierarchiques)
- **Images**: Stockees localement dans Delagrave/images/{famille}/

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| MD comme source de verite | Decouple des macros Excel, versionnable | Good — 359 refs extraites, lookup fonctionnel |
| Serveur MCP unique FastMCP | Permet a Claude d'appeler les outils directement | Good — 7 outils, pipeline complet |
| Document complet (pas fiches isolees) | L'utilisateur veut un dossier pret a l'emploi | Good — couverture, sommaire, chapitres |
| Conversion .potm via zipfile | python-pptx ne lit pas les .potm natifs | Good — trick fiable |
| Split texte revetement en 3 zones | Texte debordait du cadre unique | Good — TEXTE/MEO/FINITION |

---
*Last updated: 2026-02-10 after v1.1 milestone start*
