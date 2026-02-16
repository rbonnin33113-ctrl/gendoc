"""
MD Parser for Delagrave product references.

This module provides the core data access layer for reading structured
Markdown files containing product references. It is the single source of
truth for parsing MD files - all other modules (lookup, image_manager,
validators, MCP servers) must use these functions.

This is a pure library module with no I/O operations (no print/input).

Round-trip compatibility:
  - parse_family_md() -> md_writer.write_family_file() -> parse_family_md()
  - Validated: 2026-02-16 (phase 20) — all families pass round-trip test
  - Last modified: 2026-02-16 (commit 0cee8d5)

Changes since v1.4 milestone:
  - Fixed image table column count detection (10 parts for new "Chemin Original" field)
  - Added find_product_pages() function for multi-page product lookup
  - Both changes maintain backward compatibility with existing MD files
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import re


def parse_family_md(filepath: Path) -> List[Dict[str, Any]]:
    """
    Parse a family MD file and return a list of product dictionaries.

    Args:
        filepath: Path to the MD file to parse

    Returns:
        List of product dictionaries, each containing:
        - code (str): Product code
        - ref (str): Reference string
        - titre (str): Title
        - famille (str): Family name
        - texte (str): Descriptive text
        - dimensions (list): List of dimension dicts
        - images (list): List of image dicts
        - metadata_pptx (list): List of PowerPoint metadata dicts

    Example:
        >>> products = parse_family_md(Path("Delagrave/references/paillasse.md"))
        >>> len(products)
        54
        >>> products[0]['code']
        'PCD-A-60'
    """
    if not filepath.exists():
        return []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    products = []

    # Split by product sections (## followed by product code)
    # Product sections start with ## {CODE}
    # Pattern allows: letters, digits, spaces, and common punctuation (-, _, ., /, +)
    sections = re.split(r'\n## ([A-Za-z0-9_. /+-]+)\n', content)

    # First section is header, skip it
    if len(sections) < 3:
        return []

    # Process pairs: (code, content)
    for i in range(1, len(sections), 2):
        if i + 1 >= len(sections):
            break

        code = sections[i]
        section_content = sections[i + 1]

        product = _parse_product_section(code, section_content, filepath.stem)
        if product:
            products.append(product)

    return products


def _parse_product_section(code: str, content: str, family: str) -> Optional[Dict[str, Any]]:
    """
    Parse a single product section from MD content.

    Args:
        code: Product code
        content: Section content (everything under ## {CODE})
        family: Family name (from filename)

    Returns:
        Product dictionary or None if parsing fails
    """
    product = {
        'code': code,
        'ref': '',
        'titre': '',
        'famille': family,
        'texte': '',
        'dimensions': [],
        'images': [],
        'metadata_pptx': []
    }

    # Parse metadata table (| Champ | Valeur |)
    metadata_match = re.search(
        r'\| Champ \| Valeur \|.*?\n\|----',
        content,
        re.DOTALL
    )
    if metadata_match:
        metadata_section = content[metadata_match.end():].split('\n###')[0]
        for line in metadata_section.strip().split('\n'):
            if line.startswith('|') and 'ref' in line.lower():
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3 and parts[1].lower() == 'ref':
                    product['ref'] = parts[2]
            elif line.startswith('|') and 'titre' in line.lower():
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3 and parts[1].lower() == 'titre':
                    # Titre can be multiline, collect until next table row
                    product['titre'] = parts[2]

    # Parse Texte section
    texte_match = re.search(r'### Texte\n\n(.*?)\n###', content, re.DOTALL)
    if texte_match:
        product['texte'] = texte_match.group(1).strip()

    # Parse Dimensions table
    dimensions_match = re.search(
        r'### Dimensions\n\n\| Dimension \| Valeur \| Prefix \| Shape Index \|(.*?)\n###',
        content,
        re.DOTALL
    )
    if dimensions_match:
        table_content = dimensions_match.group(1)
        for line in table_content.strip().split('\n'):
            if line.startswith('|') and not line.startswith('|---'):
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 5 and parts[1]:  # Has dimension name
                    product['dimensions'].append({
                        'name': parts[1],
                        'valeur': parts[2],
                        'prefix': parts[3],
                        'shape_index': parts[4]
                    })

    # Parse Images table
    images_match = re.search(
        r'### Images\n\n\| Position \| Chemin \|.*?\n\|---.*?\n(.*?)\n###',
        content,
        re.DOTALL
    )
    if images_match:
        table_content = images_match.group(1)
        for line in table_content.strip().split('\n'):
            if line.startswith('|') and not line.startswith('|---'):
                parts = [p.strip() for p in line.split('|')]
                # Check if this is the new format with "Chemin Original" column
                # Old: | Position | Chemin | Left | Top | Width | Height | Shape Index |
                # New: | Position | Chemin | Chemin Original | Left | Top | Width | Height | Shape Index |
                if len(parts) >= 8 and parts[1]:  # Has position
                    # Old: | Pos | Chemin | Left | Top | W | H | SI | -> 7 cols -> 9 parts
                    # New: | Pos | Chemin | Chemin Orig | Left | Top | W | H | SI | -> 8 cols -> 10 parts
                    if len(parts) >= 10:  # New format with Chemin Original
                        product['images'].append({
                            'position': parts[1],
                            'chemin': parts[2],
                            'chemin_original': parts[3],
                            'left': _parse_float(parts[4]),
                            'top': _parse_float(parts[5]),
                            'width': _parse_float(parts[6]),
                            'height': _parse_float(parts[7]),
                            'shape_index': parts[8]
                        })
                    else:  # Old format without Chemin Original
                        product['images'].append({
                            'position': parts[1],
                            'chemin': parts[2],
                            'chemin_original': '',
                            'left': _parse_float(parts[3]),
                            'top': _parse_float(parts[4]),
                            'width': _parse_float(parts[5]),
                            'height': _parse_float(parts[6]),
                            'shape_index': parts[7]
                        })

    # Parse Metadata PowerPoint table
    metadata_pptx_match = re.search(
        r'### Metadata PowerPoint\n\n\| Champ \| Type \| Prefix \| Shape Index \|(.*?)(?:\n---|\n##|\Z)',
        content,
        re.DOTALL
    )
    if metadata_pptx_match:
        table_content = metadata_pptx_match.group(1)
        for line in table_content.strip().split('\n'):
            if line.startswith('|') and not line.startswith('|---'):
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 5 and parts[1]:  # Has field name
                    product['metadata_pptx'].append({
                        'champ': parts[1],
                        'type': parts[2],
                        'prefix': parts[3],
                        'shape_index': parts[4]
                    })

    return product


def _parse_float(value: str) -> float:
    """Convert string to float, return 0.0 if invalid."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def get_all_family_files(references_dir: Path) -> List[Path]:
    """
    Get all family MD files in the references directory.

    Args:
        references_dir: Path to Delagrave/references/

    Returns:
        List of Path objects for family MD files (excludes _index.md, _parametrage.md)
    """
    if not references_dir.exists():
        return []

    return [
        f for f in references_dir.glob('*.md')
        if not f.name.startswith('_')
    ]


def find_product(code: str, references_dir: Path) -> Optional[Dict[str, Any]]:
    """
    Find a product by code across all family MD files.

    Args:
        code: Product code to search for (case-insensitive)
        references_dir: Path to Delagrave/references/

    Returns:
        Product dictionary if found, None otherwise

    Example:
        >>> product = find_product("PM-D-H-75", Path("Delagrave/references"))
        >>> product['titre']
        'PM-D-H-75 - Paillasse murale...'
    """
    code_upper = code.upper()

    for family_file in get_all_family_files(references_dir):
        products = parse_family_md(family_file)
        for product in products:
            if product['code'].upper() == code_upper:
                return product

    return None


def find_product_pages(code: str, references_dir: Path) -> List[Dict[str, Any]]:
    """
    Find all pages for a product code (multi-page products have duplicate entries).

    Args:
        code: Product code to search for (case-insensitive)
        references_dir: Path to Delagrave/references/

    Returns:
        List of product dictionaries (one per page), empty if not found
    """
    code_upper = code.upper()
    pages = []

    for family_file in get_all_family_files(references_dir):
        products = parse_family_md(family_file)
        for product in products:
            if product['code'].upper() == code_upper:
                pages.append(product)

    return pages


def find_products_by_family(family_name: str, references_dir: Path) -> List[Dict[str, Any]]:
    """
    Find all products in a specific family.

    Args:
        family_name: Family name (case-insensitive)
        references_dir: Path to Delagrave/references/

    Returns:
        List of product dictionaries

    Example:
        >>> products = find_products_by_family("paillasse", Path("Delagrave/references"))
        >>> len(products)
        54
    """
    family_file = references_dir / f"{family_name.lower()}.md"

    if not family_file.exists():
        return []

    return parse_family_md(family_file)


def search_products(query: str, references_dir: Path) -> List[Dict[str, Any]]:
    """
    Search for products by partial code or title match.

    Args:
        query: Search query (case-insensitive)
        references_dir: Path to Delagrave/references/

    Returns:
        List of matching product dictionaries

    Example:
        >>> results = search_products("PM-D", Path("Delagrave/references"))
        >>> len(results) > 0
        True
    """
    query_lower = query.lower()
    results = []

    for family_file in get_all_family_files(references_dir):
        products = parse_family_md(family_file)
        for product in products:
            if (query_lower in product['code'].lower() or
                query_lower in product['titre'].lower()):
                results.append(product)

    return results


def get_all_families(references_dir: Path) -> Dict[str, int]:
    """
    Get all families with product counts.

    Args:
        references_dir: Path to Delagrave/references/

    Returns:
        Dict mapping family name to product count

    Example:
        >>> families = get_all_families(Path("Delagrave/references"))
        >>> families['paillasse']
        54
    """
    families = {}

    for family_file in get_all_family_files(references_dir):
        products = parse_family_md(family_file)
        families[family_file.stem] = len(products)

    return families
