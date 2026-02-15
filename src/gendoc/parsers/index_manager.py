"""
Index management for Delagrave family references.

This module provides functions to maintain the _index.md file and ensure
family infrastructure (directories) exists when adding products.

This is a pure library module with no print/logging.
"""

from pathlib import Path
from typing import Dict
import re

from gendoc.parsers.md_parser import get_all_families, get_all_family_files


# Type mapping for each family
TYPE_MAP = {
    'paillasse': 'PPT (texte + dimensions + image)',
    'sorbonne': 'PPT (texte + dimensions + image)',
    'revetement': 'PPT (texte + 2 images)',
    'meubles': 'PPT (texte + image)',
    'tables-en': 'PPT (texte + image)',
    'equipement': 'PPT (images positionnees)',
    'elec-sorb': 'PPT (images positionnees)',
    'complements': 'PPT (images positionnees)',
    'fiches-existantes': 'EXT (fichiers .pptx)',
}

# Display names for each family (with correct accents)
DISPLAY_MAP = {
    'paillasse': 'Paillasse',
    'sorbonne': 'Sorbonne',
    'revetement': 'Revètement',
    'meubles': 'Meubles',
    'tables-en': 'Tables EN',
    'equipement': 'Equipement',
    'elec-sorb': 'Elec sorb',
    'complements': 'Compléments',
    'fiches-existantes': 'Fiches Existantes',
}

# Family ordering (known families appear in this order)
FAMILY_ORDER = [
    'paillasse', 'sorbonne', 'revetement', 'meubles', 'tables-en',
    'equipement', 'elec-sorb', 'complements', 'fiches-existantes'
]


def ensure_family_infrastructure(famille: str, references_dir: Path) -> dict:
    """
    Ensure infrastructure exists for a family (images directory).

    Called when adding a product to a potentially new family. Creates the
    images directory if it doesn't exist. The family MD file creation is
    handled by append_product_to_family in md_writer.py.

    Args:
        famille: Family name (e.g., "paillasse")
        references_dir: Path to Delagrave/references/

    Returns:
        Dict with:
        - famille: normalized family name (lowercase)
        - md_existed: True if family MD file already exists
        - images_dir_created: True if images directory was created

    Example:
        >>> from pathlib import Path
        >>> result = ensure_family_infrastructure("paillasse", Path("Delagrave/references"))
        >>> result['famille']
        'paillasse'
    """
    famille_lower = famille.lower()

    # Check if MD file exists
    md_path = references_dir / f"{famille_lower}.md"
    md_existed = md_path.exists()

    # Check/create images directory
    # references_dir is Delagrave/references/
    # images dir is Delagrave/images/{famille}/
    images_dir = references_dir.parent / "images" / famille_lower
    images_dir_created = False

    if not images_dir.exists():
        images_dir.mkdir(parents=True, exist_ok=True)
        images_dir_created = True

    return {
        "famille": famille_lower,
        "md_existed": md_existed,
        "images_dir_created": images_dir_created
    }


def refresh_index(references_dir: Path) -> dict:
    """
    Regenerate the _index.md file based on actual family files on disk.

    Reads all family MD files, counts products, and rewrites _index.md
    with current state. Preserves Source and Extraction metadata from
    existing file if present.

    Args:
        references_dir: Path to Delagrave/references/

    Returns:
        Dict with:
        - total: total reference count
        - families: number of families
        - families_detail: {family_name: count, ...}

    Example:
        >>> from pathlib import Path
        >>> result = refresh_index(Path("Delagrave/references"))
        >>> result['total']
        359
    """
    # Get family counts from disk
    families = get_all_families(references_dir)

    # Calculate totals
    total_refs = sum(families.values())
    nb_families = len(families)

    # Read existing _index.md to preserve Source and Extraction
    index_path = references_dir / "_index.md"
    source = "Génération Fiche Technique DELAGRAVE.xlsm"
    extraction = "2026-02-10 12:06:27"

    if index_path.exists():
        try:
            existing_content = index_path.read_text(encoding='utf-8')

            # Extract Source
            source_match = re.search(r'> Source: (.+)', existing_content)
            if source_match:
                source = source_match.group(1)

            # Extract Extraction
            extraction_match = re.search(r'> Extraction: (.+)', existing_content)
            if extraction_match:
                extraction = extraction_match.group(1)
        except Exception:
            # If read fails, use defaults
            pass

    # Build family rows in specified order
    rows = []

    # First, add families in FAMILY_ORDER
    ordered_families = []
    for family in FAMILY_ORDER:
        if family in families:
            ordered_families.append(family)

    # Then add any new families not in FAMILY_ORDER (alphabetically, excluding fiches-existantes)
    new_families = sorted([f for f in families.keys() if f not in FAMILY_ORDER and f != 'fiches-existantes'])
    ordered_families.extend(new_families)

    # Finally, add fiches-existantes if present (always last)
    if 'fiches-existantes' in families and 'fiches-existantes' not in ordered_families:
        ordered_families.append('fiches-existantes')

    # Build table rows
    for family in ordered_families:
        count = families[family]
        display_name = DISPLAY_MAP.get(family, family.replace('-', ' ').title())
        type_val = TYPE_MAP.get(family, 'PPT (texte + image)')
        rows.append(f"| {display_name} | [{family}.md]({family}.md) | {count} | {type_val} |")

    # Build complete _index.md content
    content_lines = [
        "# Index des References Delagrave",
        "",
        f"> Source: {source}",
        f"> Extraction: {extraction}",
        f"> Total: {total_refs} references dans {nb_families} familles",
        "",
        "## Familles",
        "",
        "| Famille | Fichier | Nb references | Type |",
        "|---------|---------|---------------|------|",
    ]
    content_lines.extend(rows)
    content_lines.extend([
        "",
        "## Structure d'un fichier famille",
        "",
        "Chaque fichier MD contient :",
        "- En-tête : nom famille, source, date, compteur",
        "- Sections `## {Code}` : une par produit",
        "  - Tableau identité : code, ref, titre, famille",
        "  - `### Texte` : contenu descriptif",
        "  - `### Dimensions` : tableau avec valeur, prefix PPTX, shape index",
        "  - `### Images` : tableau avec chemin, position (left/top/width/height), shape index",
        "  - `### Metadata PowerPoint` : mapping complet colonnes -> shapes",
        "",
        "## Fichiers speciaux",
        "",
        "| Fichier | Role |",
        "|---------|------|",
        "| [_index.md](_index.md) | Ce fichier - point d'entree |",
        "| [_parametrage.md](_parametrage.md) | Config mapping famille -> template PowerPoint |",
        ""
    ])

    # Write to _index.md
    content = '\n'.join(content_lines)
    index_path.write_text(content, encoding='utf-8')

    return {
        "total": total_refs,
        "families": nb_families,
        "families_detail": families
    }
