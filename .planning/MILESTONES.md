# Milestones: Generateur de Fiches Techniques Delagrave

## v1.0 — Systeme MCP de Generation Automatique (SHIPPED 2026-02-10)

**Goal:** Permettre a un agent Claude via MCP d'analyser un devis PDF et de generer automatiquement un dossier PowerPoint complet de fiches techniques.

**Started:** 2026-02-09
**Shipped:** 2026-02-10
**Phases:** 6 (10 plans)
**Lines of code:** 3,775 Python
**Commits:** 44

**Key Accomplishments:**
1. Extracted 359 product references from Excel VBA into 9 structured Markdown files
2. Created MCP server with 7 tools (lookup, search, families, analyze, preview, generate, add)
3. Built PDF devis analyzer with coating detection and family classification
4. Built PowerPoint generator with .potm template, 5-family layouts, auto-sizing
5. Assembled complete documents with cover page, logo, TOC, chapter separators
6. Integrated end-to-end pipeline /gendoc-full (PDF -> preview -> PowerPoint)

**Deferred:** GEN-09 (modes CHI/DOE), fiches-existantes integration, add_reference implementation

See: `.planning/milestones/v1.0-ROADMAP.md` for full details.

## v1.1 — Qualite et Couverture Familles (SHIPPED 2026-02-10)

**Goal:** S'assurer que toutes les familles produit generent des fiches correctes et mettre en place des tests automatises pour prevenir les regressions.

**Started:** 2026-02-10
**Shipped:** 2026-02-10
**Phases:** 7-8 (5 plans)
**Tests:** 34 automated (8 family generation + 4 E2E + 13 unit + 9 lookup/util)
**Lines of code:** 3,914 Python (source) + 403 (tests)

**Key Accomplishments:**
1. VBA-to-placeholder mappings complete for all 8 product families (added tables-en, elec-sorb, complements)
2. Visual verification of all family layouts — human-approved quality for all 8 families
3. Special articles (SP-prefixed: SPMOB, SPPAIL, SPTABLEEN, SPUSE) support with custom product creation MCP tool
4. Pytest infrastructure with 34 automated tests covering all 8 families in <9s
5. E2E pipeline test validating the full analyze devis PDF -> generate PowerPoint workflow

**Deferred:** ADV-01 (modes CHI/DOE), ADV-02 (fiches-existantes integration), ADV-03 (add_reference), ADV-04 (Excel sync)

See: `.planning/milestones/v1.1-ROADMAP.md` for full details.

---


## v1.2 — Outil de Selection SP (SHIPPED 2026-02-11)

**Goal:** Permettre a l'utilisateur de visualiser, selectionner et editer les articles speciaux (SP) d'un devis via une page HTML interactive, avec extraction automatique des designations depuis le PDF.

**Started:** 2026-02-10
**Shipped:** 2026-02-11
**Phases:** 9-11 (3 plans)
**Tests:** 56 automated (22 new: 14 SP detection + 8 SP workflow)
**Lines of code:** 5,308 Python (source) + 932 (tests)
**Commits:** 21

**Key Accomplishments:**
1. Fixed SP article detection — SP-prefixed codes (SPMOB, SPPAIL, SPTABLEEN, SPUSE) correctly classified, never falling into inconnus
2. Built multi-line designation extraction from PDF devis for each SP article (handles quantity stripping, article code boundaries)
3. Created self-contained HTML page (no external dependencies) for browsing catalog (320 products), editing SP article fields, and exporting JSON
4. Added 2 new MCP tools (open_sp_selector, load_sp_selection) completing the file-based SP workflow
5. Full E2E chain: analyze_devis -> HTML selector -> JSON -> generate_slides with SP articles in PowerPoint

**Deferred:** ADV-01 (modes CHI/DOE), ADV-02 (fiches-existantes), ADV-03 (add_reference), ADV-04 (Excel sync)

See: `.planning/milestones/v1.2-ROADMAP.md` for full details.

---


## v1.3 — Robustesse et Logging (SHIPPED 2026-02-11)

**Goal:** Rendre le pipeline fiable et transparent avec hot-reload MCP, logging complet, detection devis amelioree, et gestion d'erreurs claire.

**Started:** 2026-02-11
**Shipped:** 2026-02-11
**Phases:** 12-15 (6 plans)
**Tests:** 87 automated (31 new: 20 hot-reload, 6 detection, 5 error handling)
**Lines of code:** 6,912 Python (source) + 1,517 (tests)

**Key Accomplishments:**
1. Hot-reload MCP avec mtime tracking — modifications des generateurs prises en compte sans redemarrage serveur
2. PipelineLogger avec logs Markdown structures — chaque execution cree un fichier diagnostique AI-lisible dans Delagrave/output/logs/
3. Filtrage faux positifs devis (EXCLUSION_WORDS: 33 entries + pattern mesures \d+MM?) — inconnus propres pour analyse catalogue
4. Pipeline resilient aux erreurs produit — try/except sur chaque slide builder, warnings propages dans la chaine modern_template -> document_assembler -> pptx_generator
5. Resume compact en francais sur chaque outil MCP — "Analyse OK -- 28 references, 5 revetements" au lieu du defilement technique

**Deferred:** ADV-01 (modes CHI/DOE), ADV-02 (fiches-existantes), ADV-03 (add_reference), ADV-04 (Excel sync)

See: `.planning/milestones/v1.3-ROADMAP.md` for full details.

---


## v1.4 — Gestion CRUD des References (SHIPPED 2026-02-15)

**Goal:** Permettre la gestion complete du catalogue de references produit (ajout, modification, suppression) via des outils MCP, avec copie automatique des images et mise a jour de l'index.

**Started:** 2026-02-15
**Shipped:** 2026-02-15
**Phases:** 16-19 (5 plans)
**Tests:** 108 automated (21 new CRUD tests)
**Lines of code:** 8,407 Python (source) + 1,965 (tests)

**Key Accomplishments:**
1. CRUD complet (add_reference, update_reference, delete_reference) via outils MCP avec validation duplicates et existence
2. Module md_writer avec compatibilite aller-retour md_parser (round-trip valide par tests)
3. Index automatique (_index.md) regenere apres chaque operation CRUD avec creation infrastructure nouvelles familles
4. Gestion automatique des images — copie depuis chemin fourni sur add/update, suppression sur delete
5. Suite de tests CRUD : 21 tests (md_writer, image_handler, index_manager) + test integration lifecycle complet

**Deferred:** GEN-01 (modes CHI/DOE), GEN-02 (fiches-existantes), SYNC-01 (Excel sync)

See: `.planning/milestones/v1.4-ROADMAP.md` for full details.

---


## v1.5 — Consolidation et Qualite (SHIPPED 2026-02-16)

**Goal:** Remettre au propre la documentation projet, le code modifie hors milestone, et ajouter les tests manquants pour les nouvelles familles et modifications recentes.

**Started:** 2026-02-16
**Shipped:** 2026-02-16
**Phases:** 20-21 (8 plans)
**Tests:** 123 automated (15 new: 1 multi-page validation, 1 SP fix, 6 modern_template dispatch, 4 document_assembler, 3 family additions)
**Lines of code:** 8,557 Python (source) + 2,288 (tests)

**Key Accomplishments:**
1. PROJECT.md et _index.md synchronises avec l'etat reel (11 familles, 317 references, armoire-securite + enceinte-ventilee documentes)
2. 52 doublons consolides dans les references (equipement 154->122, elec-sorb 32->14, complements 3->1)
3. Docstrings complets pour armoire-securite Option C template et round-trip validation md_parser/md_writer
4. Tests modern_template dispatch couvrant les 11 familles et 4 builder functions
5. Tests document_assembler validant FAMILY_ORDER, FAMILY_DISPLAY_NAMES, et page numbering multi-page
6. 123 tests passent avec zero regressions apres consolidation complete

**Deferred:** GEN-01 (modes CHI/DOE), GEN-02 (fiches-existantes), SYNC-01 (Excel sync)

See: `.planning/milestones/v1.5-ROADMAP.md` for full details.

---


## v1.6 — Deploiement Multi-Postes (SHIPPED 2026-02-16)

**Goal:** Rendre le systeme deployable sur des postes PC utilisant Claude CLI, avec donnees partagees en lecture seule sur un lecteur reseau et output utilisateur local par devis.

**Started:** 2026-02-16
**Shipped:** 2026-02-16
**Phases:** 22-25 (4 phases, 8 plans)
**Tests:** 138 automated (15 new: 8 config_loader + 4 server_config + 3 admin guard)
**Lines of code:** 8,894 Python (source) + 2,878 (tests)
**Commits:** 41

**Key Accomplishments:**
1. Config loader JSON avec recherche hierarchique (CWD -> home -> dev) et validation du dossier reseau au demarrage
2. MCP server integre avec config_loader — tous les chemins resolus depuis le dossier reseau partage
3. Output isole par devis dans ./output/{devis_numero}/ — PowerPoint, LOG.md, SP selector tous dans le meme dossier
4. Controle d'acces admin — _require_admin() bloque les outils CRUD pour les utilisateurs non-admin
5. Package deployable complet avec install.ps1, guide DEPLOY.md, PDF 19 pages, ZIP 32 Mo avec catalogue Delagrave
6. 138 tests automatises avec zero regressions apres refactorisation des chemins

**Deferred:** GEN-01 (modes CHI/DOE), GEN-02 (fiches-existantes), SYNC-01 (Excel sync), Phase 26 Testing (absorbed into phases 22-24)

See: `.planning/milestones/v1.6-ROADMAP.md` for full details.

---


## v1.7 — Systeme de Mise a Jour (SHIPPED 2026-02-18)

**Goal:** Permettre aux utilisateurs d'etre notifies des mises a jour disponibles au demarrage du serveur MCP et de les installer en un clic, via un repo GitHub prive.

**Started:** 2026-02-18
**Shipped:** 2026-02-18
**Phases:** 26-27 (3 plans)
**Tests:** 184 automated (46 new: 21 version_checker + 25 auto_updater)
**Lines added:** 1,307
**Commits:** 11

**Key Accomplishments:**
1. Version checking au demarrage MCP — comparaison automatique version locale (pyproject.toml semver) vs GitHub tag, notification francaise si MAJ disponible
2. Module auto_updater.py — detection Git, installation winget, clone/pull repo GitHub prive, pip install -e . en autonome
3. Outil MCP update_gendoc — mise a jour en un clic depuis Claude, zero parametres, double error containment
4. Config github_repo/github_token — integration dans gendoc.json, optionnel, check silencieux si absent
5. 46 tests unitaires avec mocks subprocess/urllib couvrant toutes les branches d'erreur

**Deferred:** GEN-01 (modes CHI/DOE), GEN-02 (fiches-existantes), SYNC-01 (Excel sync), DEP-01/02/03 (install.ps1 Git integration — deferred to next deployment update)

See: `.planning/milestones/v1.7-ROADMAP.md` for full details.

---

