# Generateur de Fiches Techniques Delagrave

## What This Is

Un systeme MCP + commandes `/gendoc-*` pour Claude Code qui automatise la generation de dossiers de fiches techniques PowerPoint pour les produits Delagrave. L'utilisateur soumet un devis PDF via `/gendoc-full`, le systeme extrait les references, genere les fiches techniques avec le bon layout par famille, et produit un document PowerPoint complet (couverture avec logo, sommaire, chapitres, fiches, revetements). Les articles speciaux (SP) sont geres via une page HTML interactive pour selectionner/editer les fiches avant generation. Le catalogue de references est entierement gerable via CRUD MCP (ajout, modification, suppression) avec copie automatique des images et mise a jour de l'index. Le pipeline est resilient aux erreurs individuelles, logge chaque execution dans un fichier diagnostique, et affiche un resume compact en francais. 8,557 lignes Python + 2,288 lignes de tests, 317 references produit dans 11 familles, 12 outils MCP, 123 tests automatises.

## Core Value

Un utilisateur soumet un devis PDF et obtient automatiquement un dossier PowerPoint complet de fiches techniques — sans intervention manuelle.

## Current State (v1.5 shipped 2026-02-16)

- **Package**: `src/gendoc/` (extractors, parsers, generators, validators, utils, mcp, cli)
- **Data**: 317 references dans 11 fichiers MD, images reelles pour toutes les familles
- **MCP Tools**: lookup_reference, search_references, list_families, analyze_devis, preview_generation, generate_slides, add_reference, update_reference, delete_reference, create_custom_product, open_sp_selector, load_sp_selection
- **Skills**: /gendoc-lookup, /gendoc-analyze, /gendoc-generate, /gendoc-full, /gendoc-addarm
- **Template**: Modele fiche technique vide - Ind J.potm (6 layouts, A4 portrait)
- **Families**: 11 familles (paillasse, sorbonne, revetement, meubles, tables-en, equipement, elec-sorb, complements, armoire-securite, enceinte-ventilee, fiches-existantes)
- **SP Workflow**: analyze_devis -> open_sp_selector (HTML) -> load_sp_selection (JSON) -> generate_slides
- **CRUD**: add_reference, update_reference, delete_reference avec md_writer, image_handler, index_manager
- **Logging**: PipelineLogger cree un fichier LOG.md par execution dans Delagrave/output/logs/
- **Resilience**: try/except par produit, warnings propages, resume compact en francais
- **Detection**: EXCLUSION_WORDS (33 entries) + pattern mesures, inconnus logges individuellement
- **Hot-reload**: Modifications des generateurs prises en compte sans redemarrage MCP
- **Tests**: 123 tests pytest (22 family, 4 E2E, 14 md_parser, 14 SP detection, 8 SP workflow, 20 hot-reload, 6 detection, 5 error handling, 21 CRUD, 6 modern_template, 4 document_assembler) — <20s
- **Code quality**: armoire-securite Option C template et enceinte-ventilee entierement documentes avec docstrings, round-trip md_parser/md_writer valide

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
- Hot-reload MCP : changements de code pris en compte sans redemarrage serveur — v1.3
- Logging pipeline : fichier LOG par execution /gendoc-full avec toutes les etapes — v1.3
- Detection devis : reduction des faux positifs (33 mots exclusion + pattern mesures) — v1.3
- Gestion d'erreurs : pipeline resilient, try/except par produit, warnings propages — v1.3
- Sortie resume compact : progression concise en francais dans chaque outil MCP — v1.3
- CRUD complet des references (add, update, delete) via outils MCP — v1.4
- Copie automatique des images depuis chemin fourni sur add/update — v1.4
- Suppression automatique des images sur delete — v1.4
- Mise a jour automatique de _index.md apres chaque operation CRUD — v1.4
- Creation automatique infrastructure nouvelles familles (MD + images dir) — v1.4
- Suite de tests CRUD : 21 tests unitaires + integration lifecycle — v1.4
- Documentation projet synchronisee avec etat reel (11 familles, 317 refs, index complet) — v1.5
- References MD deduplicees et coherentes (52 doublons consolides, formats uniformes) — v1.5
- Code hors-milestone consolide et documente (armoire-securite Option C, enceinte-ventilee) — v1.5
- Tests armoire-securite et enceinte-ventilee (generation 2 pages, multi-page validation) — v1.5
- Tests modern_template dispatch et document_assembler multi-page — v1.5
- 123 tests passent avec zero regressions apres consolidation — v1.5

### Active

**Current Milestone: v1.6 Deploiement Multi-Postes**

**Goal:** Rendre le systeme deployable sur des postes PC utilisant Claude CLI, avec donnees partagees en lecture seule sur un lecteur reseau et output utilisateur local par devis.

**Target features:**
- Configuration locale pointant vers le dossier partage reseau
- Resolution de tous les chemins (references, images, template) depuis la config
- Output isole par devis dans le dossier de travail de l'utilisateur
- CRUD reserve a l'administrateur (lecture seule pour les utilisateurs)
- Package deployable par copie locale sur chaque poste

**Deferred:**
- [ ] Modes de generation CHI/DOE/FTI (deferred from v1.0)
- [ ] Integration des fiches-existantes (fichiers .pptx pre-existants)
- [ ] Synchronisation automatique Excel -> MD

### Out of Scope

- Edition du fichier Excel original — les MD sont la source de verite
- Interface web ou GUI — tout passe par Claude via MCP
- Gestion des prix/tarifs — seules les fiches techniques sont generees
- Tests visuels automatiques — la validation visuelle reste manuelle
- Serveur HTTP local — approche file-based preferee (HTML auto-contenu + export JSON)
- Gestion des quantites SP — non necessaire pour les fiches techniques
- Dashboard web de logs — les fichiers LOG.md suffisent
- Retry automatique — les erreurs doivent etre analysees, pas masquees
- Bulk import CSV/Excel — une reference a la fois via CRUD MCP

## Constraints

- **Tech stack**: Python, FastMCP, python-pptx, pdfplumber, pytest — Claude Code compatible
- **Template**: Le template .potm existant est reutilise tel quel (conversion zip pour contourner limitation python-pptx)
- **Format devis**: Les devis PDF Delagrave ont un format structure (sections hierarchiques)
- **Images**: Stockees localement dans Delagrave/images/{famille}/

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| MD comme source de verite | Decouple des macros Excel, versionnable | Good — 317 refs extraites, lookup fonctionnel |
| Serveur MCP unique FastMCP | Permet a Claude d'appeler les outils directement | Good — 12 outils, pipeline complet |
| Document complet (pas fiches isolees) | L'utilisateur veut un dossier pret a l'emploi | Good — couverture, sommaire, chapitres |
| Conversion .potm via zipfile | python-pptx ne lit pas les .potm natifs | Good — trick fiable |
| Split texte revetement en 3 zones | Texte debordait du cadre unique | Good — TEXTE/MEO/FINITION |
| VBA_TO_PLACEHOLDER pour toutes les familles | Mapping systematique VBA -> placeholder idx | Good — 9 familles couvertes |
| Custom products via deep copy + field override | Articles speciaux SP sans reference catalogue | Good — flexible, MCP tool cree |
| Pytest parametrize par famille | Un test par famille, execution rapide | Good — 108 tests en <20s |
| Designation extraction multi-lignes | Articles SP ont des descriptions longues dans le PDF | Good — texte complet avec dimensions |
| HTML auto-contenu avec catalogue embarque | Pas de serveur HTTP, pas de dependances externes | Good — 320 produits, ~500KB HTML |
| Partial export SP | L'utilisateur peut configurer seulement certains SP | Good — feedback utilisateur integre |
| MCP file-based workflow | HTML doit persister pour interaction navigateur | Good — workflow asynchrone utilisateur |
| mtime hot-reload | os.path.getmtime rapide, fiable Windows | Good — zero overhead quand inchange |
| Module-level PipelineLogger | Evite gestion lifecycle client, etat partage simple | Good — logs partiels garantis |
| EXCLUSION_WORDS set + pattern regex | Double filtrage : mots connus + mesures NNN+MM | Good — inconnus propres |
| try/except par slide builder | Erreur individuelle n'arrete pas le pipeline | Good — warnings propages jusqu'au resume |
| Resume compact en francais | L'utilisateur voit la progression, pas les details techniques | Good — exploitable directement par Claude |
| md_writer decouple de md_parser | Round-trip valide par tests, pas par couplage runtime | Good — modules independants, format compatible |
| Partial updates dans update_reference | Modifier un champ sans envoyer les autres | Good — API flexible |
| Code/famille protege en update | Identifiants structurels non modifiables | Good — coherence preservee |
| Index refresh secondaire | Echec index ne bloque pas CRUD | Good — operations CRUD fiables |
| Image operations secondaires | Echec copie/suppression ne bloque pas CRUD | Good — degradation gracieuse |
| Dedup references avant comptage | Les compteurs MD etaient faux (369 vs 317 reel) | Good — donnees fiables apres consolidation |
| armoire-securite Option C template documente | Seule famille multi-page, docstring complet | Good — maintenabilite assuree |
| Assertions tests realistes | SP catalog 283 visible (pas 317 total) | Good — tests stables apres dedup |
| Simple slide one-per-image | Multi-image products (BC1Vx 5 images) debordaient | Good — 1 slide/image comme VBA original |

---
*Last updated: 2026-02-16 after v1.6 milestone started*
