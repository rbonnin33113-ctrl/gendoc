# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

MCP-based system for generating PowerPoint technical data sheets (fiches techniques) from PDF quotes (devis) for Delagrave EMSM. 317 product references across 11 families, exposed via 13 MCP tools through FastMCP.

## Commands

```bash
# Install (editable)
pip install -e .

# Run all tests (~184 tests, <25s)
pytest

# Run single test file
pytest tests/test_e2e_pipeline.py

# Run by name pattern
pytest -k "test_lookup"

# Start MCP server
python -m gendoc.mcp.server

# CLI tools
gendoc-lookup PM-D-H-75              # Product lookup
gendoc-lookup --family paillasse     # By family
gendoc-lookup --search "PM-D"        # Search
gendoc-lookup --list-families        # All families
gendoc-validate                      # Validate references
gendoc-extract                       # Extract from Excel
```

## Architecture

### Package: `src/gendoc/`

**Parsers** (`parsers/`):
- `md_parser.py` — Single source of truth for reading product data from Markdown files. All product lookups go through here.
- `md_writer.py` — Write counterpart, round-trip compatible with md_parser.
- `devis_analyzer.py` — PDF quote analysis: extracts article codes, classifies into families, resolves aliases (`CODE_ALIASES`), filters false positives (`EXCLUSION_WORDS`).
- `pdf_parser.py` — Raw PDF text extraction via pdfplumber.
- `index_manager.py` — Auto-refresh `_index.md` + create family infrastructure.
- `image_handler.py` — Copy/remove product images for CRUD operations.

**Generators** (`generators/`):
- `pptx_generator.py` — Core PowerPoint generator. Maps families to template layouts via `FAMILY_LAYOUT_MAP`. Handles alias resolution via lazy import (hot-reload compatible).
- `modern_template.py` — Modern 2-page design for armoire-securite and enceinte-ventilee families.
- `document_assembler.py` — Cover page, TOC, chapter separators. Defines `FAMILY_ORDER` for slide sequencing.
- `html_sp_selector.py` — Interactive HTML page for configuring SP (special) articles.

**MCP** (`mcp/`):
- `server.py` — FastMCP server registering 13 tools. Hot-reloads generator modules on file change (mtime tracking). **Not itself hot-reloaded** — requires restart for server.py changes.

**Utils** (`utils/`):
- `config_loader.py` — Loads `gendoc.json` (search: CWD → home → server.py dir). Keys: `network_share_path`, `admin`, optional `github_repo`/`github_token`.
- `pipeline_logger.py` — Structured execution logging to `output/{devis_numero}/LOG.md`. Uses module-level `_current_logger`.
- `version_checker.py` — Compares pyproject.toml version against GitHub tags.
- `auto_updater.py` — Returns bash commands for git pull (no subprocess — blocks on Windows).

### Data: `Delagrave/`

- `references/*.md` — 11 family files + `_index.md` + `_parametrage.md`. Each product is a `## CODE` section with metadata table, Texte, Dimensions, Images, Metadata PowerPoint subsections.
- `images/{family}/` — Product images per family.
- `Modele fiches - Powerpoint/Modèle fiche technique vide - Ind J.potm` — PowerPoint template with 6 layouts (indexed placeholders: idx 0,13,14,15,16-20,23,28).

### Tests: `tests/`

Session-scoped fixtures in `conftest.py`: `project_root`, `references_dir`, `template_path`, `output_dir`, `sample_codes`. Test output goes to `tests/output/`.

## Key Patterns

**Product codes** can contain dots, slashes, plus signs, spaces, and lowercase characters. Never assume alphanumeric-only.

**Sheet/family names use accents**: "Revètement", "Compléments" — encoding matters everywhere.

**Hot-reload**: Changes to `pptx_generator.py`, `modern_template.py`, `document_assembler.py` apply without MCP restart. `server.py` itself requires restart.

**Alias resolution** happens in two places: `devis_analyzer.py` (static `CODE_ALIASES` dict) and `pptx_generator.py` (lazy import for hot-reload compat). Keep both in sync.

**Admin gating**: `gendoc.json` `admin` flag controls CRUD tools (add/update/delete). Read-only tools always available.

**MCP tool return format**: All tools return a `resume` field with a compact French summary.

**Family-specific layouts**: armoire-securite and enceinte-ventilee use `_build_armoire_slide` (modern 2-page template, layout 0). Other families use template layouts 1-5 via `FAMILY_LAYOUT_MAP`.

**Pipeline flow**: `analyze_devis(pdf)` → review analysis → optional SP selector → `generate_slides(codes, devis_info)` → output in `./output/{devis_numero}/`.

## Configuration

`gendoc.json` (copy from `gendoc.json.example`):
```json
{
    "network_share_path": "H:/IA/Generateur de doc/Delagrave",
    "admin": false,
    "github_repo": "owner/repo",
    "github_token": "ghp_..."
}
```

Deployment dir: `C:\gendoc` (git clone, editable install). Update via `git pull` — pip reinstall not needed.
