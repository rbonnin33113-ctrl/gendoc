"""
MD Writer for Delagrave product references.

This module provides functions to write product references to Markdown files
in the exact format that md_parser.py can parse. It is the write counterpart
to md_parser.py (the reader).

This is a pure library module with no I/O side effects (except for the
append/write functions which perform file operations).
"""

from pathlib import Path
from typing import Dict, List, Any
import re


def format_product_section(product: dict) -> str:
    """
    Format a product dictionary into a complete MD section.

    Args:
        product: Product dictionary with keys:
            - code (str): Product code
            - ref (str): Reference string
            - titre (str): Title (can be multiline)
            - famille (str): Family name
            - texte (str): Descriptive text
            - dimensions (list): List of dimension dicts
            - images (list): List of image dicts
            - metadata_pptx (list): List of PowerPoint metadata dicts

    Returns:
        Complete product section string including ## header and trailing ---

    Example:
        >>> product = {
        ...     'code': 'TEST-001',
        ...     'ref': 'Ref : TEST-001 2026-1',
        ...     'titre': 'Test Product',
        ...     'famille': 'test',
        ...     'texte': 'Description',
        ...     'dimensions': [],
        ...     'images': [],
        ...     'metadata_pptx': []
        ... }
        >>> section = format_product_section(product)
        >>> '## TEST-001' in section
        True
    """
    code = product.get('code', '')
    ref = product.get('ref', '')
    titre = product.get('titre', '')
    famille = product.get('famille', '')
    texte = product.get('texte', '')
    dimensions = product.get('dimensions', [])
    images = product.get('images', [])
    metadata_pptx = product.get('metadata_pptx', [])

    # Build the section
    lines = []

    # Header
    lines.append(f"## {code}")
    lines.append("")

    # Metadata table
    lines.append("| Champ | Valeur |")
    lines.append("|-------|--------|")
    lines.append(f"| code | {code} |")
    lines.append(f"| ref | {ref} |")
    lines.append(f"| titre | {titre} |")
    lines.append(f"| famille | {famille} |")
    lines.append("")

    # Texte section
    lines.append("### Texte")
    lines.append("")
    lines.append(texte)
    lines.append("")

    # Dimensions section
    lines.append("### Dimensions")
    lines.append("")
    lines.append("| Dimension | Valeur | Prefix | Shape Index |")
    lines.append("|-----------|--------|--------|-------------|")
    for dim in dimensions:
        name = dim.get('name', '')
        valeur = dim.get('valeur', '')
        prefix = dim.get('prefix', '')
        shape_index = dim.get('shape_index', '')
        lines.append(f"| {name} | {valeur} | {prefix} | {shape_index} |")
    lines.append("")

    # Images section
    lines.append("### Images")
    lines.append("")
    lines.append("| Position | Chemin | Chemin Original | Left | Top | Width | Height | Shape Index |")
    lines.append("|----------|--------|-----------------|------|-----|-------|--------|-------------|")
    for img in images:
        position = img.get('position', '')
        chemin = img.get('chemin', '')
        chemin_original = img.get('chemin_original', '')
        left = img.get('left', 0.0)
        top = img.get('top', 0.0)
        width = img.get('width', 0.0)
        height = img.get('height', 0.0)
        shape_index = img.get('shape_index', '')
        lines.append(f"| {position} | {chemin} | {chemin_original} | {left} | {top} | {width} | {height} | {shape_index} |")
    lines.append("")

    # Metadata PowerPoint section
    lines.append("### Metadata PowerPoint")
    lines.append("")
    lines.append("| Champ | Type | Prefix | Shape Index |")
    lines.append("|-------|------|--------|-------------|")
    for meta in metadata_pptx:
        champ = meta.get('champ', '')
        type_val = meta.get('type', '')
        prefix = meta.get('prefix', '')
        shape_index = meta.get('shape_index', '')
        lines.append(f"| {champ} | {type_val} | {prefix} | {shape_index} |")
    lines.append("")

    # Separator
    lines.append("---")
    lines.append("")

    return '\n'.join(lines)


def append_product_to_family(filepath: Path, product: dict) -> None:
    """
    Append a product to an existing family MD file, or create new file if needed.

    Args:
        filepath: Path to the family MD file
        product: Product dictionary to append

    Creates file with header if it doesn't exist. Updates reference count.

    Example:
        >>> from pathlib import Path
        >>> import tempfile
        >>> product = {'code': 'TEST', 'ref': '', 'titre': 'Title',
        ...            'famille': 'test', 'texte': '', 'dimensions': [],
        ...            'images': [], 'metadata_pptx': []}
        >>> tmp = Path(tempfile.mktemp(suffix='.md'))
        >>> append_product_to_family(tmp, product)
        >>> tmp.exists()
        True
        >>> tmp.unlink()
    """
    if not filepath.exists():
        # Create new file with header
        famille_name = product.get('famille', filepath.stem).capitalize()
        header = f"# {famille_name}\n\n> Total references: 1\n\n"
        content = header + format_product_section(product)
        filepath.write_text(content, encoding='utf-8')
    else:
        # Read existing file
        content = filepath.read_text(encoding='utf-8')

        # Update reference count
        count_match = re.search(r'> Total references: (\d+)', content)
        if count_match:
            old_count = int(count_match.group(1))
            new_count = old_count + 1
            content = re.sub(
                r'> Total references: \d+',
                f'> Total references: {new_count}',
                content
            )

        # Append product section
        # Remove trailing whitespace/newlines, then add product
        content = content.rstrip() + '\n\n' + format_product_section(product)

        # Write back
        filepath.write_text(content, encoding='utf-8')


def write_family_file(filepath: Path, header_lines: list[str], products: list[dict]) -> None:
    """
    Write a complete family MD file from scratch.

    Args:
        filepath: Path to the family MD file
        header_lines: Lines before the first ## section (including count)
        products: List of product dictionaries to write

    Used by update/delete operations (Phase 16 Plan 02).

    Example:
        >>> from pathlib import Path
        >>> import tempfile
        >>> header = ['# Test', '', '> Total references: 1', '']
        >>> products = [{'code': 'T1', 'ref': '', 'titre': 'Title',
        ...              'famille': 'test', 'texte': '', 'dimensions': [],
        ...              'images': [], 'metadata_pptx': []}]
        >>> tmp = Path(tempfile.mktemp(suffix='.md'))
        >>> write_family_file(tmp, header, products)
        >>> tmp.exists()
        True
        >>> tmp.unlink()
    """
    # Build content
    content_parts = []

    # Add header
    content_parts.append('\n'.join(header_lines))
    if header_lines and not header_lines[-1] == '':
        content_parts.append('')

    # Add products
    for product in products:
        content_parts.append(format_product_section(product))

    # Write to file
    content = '\n'.join(content_parts)
    filepath.write_text(content, encoding='utf-8')


def update_header_count(filepath: Path, new_count: int) -> None:
    """
    Update the reference count in a family MD file header.

    Args:
        filepath: Path to the family MD file
        new_count: New reference count

    Reads the file, updates the "Total references: N" line, writes back.

    Example:
        >>> from pathlib import Path
        >>> import tempfile
        >>> tmp = Path(tempfile.mktemp(suffix='.md'))
        >>> tmp.write_text('# Test\\n\\n> Total references: 1\\n', encoding='utf-8')
        29
        >>> update_header_count(tmp, 5)
        >>> content = tmp.read_text(encoding='utf-8')
        >>> 'Total references: 5' in content
        True
        >>> tmp.unlink()
    """
    if not filepath.exists():
        return

    content = filepath.read_text(encoding='utf-8')

    # Update count
    content = re.sub(
        r'> Total references: \d+',
        f'> Total references: {new_count}',
        content
    )

    filepath.write_text(content, encoding='utf-8')


def _read_header(filepath: Path) -> str:
    """
    Read the header section of a family MD file.

    The header is everything before the first product section (before first '\\n## ').

    Args:
        filepath: Path to the family MD file

    Returns:
        Header text (includes family name, metadata, extraction date, etc.)

    Example:
        >>> from pathlib import Path
        >>> import tempfile
        >>> tmp = Path(tempfile.mktemp(suffix='.md'))
        >>> tmp.write_text('# Test\\n\\n> Total references: 1\\n\\n## PROD1\\n', encoding='utf-8')
        44
        >>> header = _read_header(tmp)
        >>> '# Test' in header
        True
        >>> tmp.unlink()
    """
    if not filepath.exists():
        return ""

    content = filepath.read_text(encoding='utf-8')

    # Split on first product section
    parts = content.split('\n## ', 1)
    return parts[0] if parts else ""


def update_product_in_family(filepath: Path, code: str, updates: dict) -> dict:
    """
    Update an existing product in a family MD file.

    Performs read-modify-write of the entire file. Only updates fields present
    in the updates dict (partial update). Cannot update 'code' or 'famille'
    (structural identifiers).

    Args:
        filepath: Path to the family MD file
        code: Product code to update (case-insensitive match)
        updates: Dictionary of fields to update. Valid keys:
            - ref, titre, texte, dimensions, images, metadata_pptx

    Returns:
        Updated product dictionary

    Raises:
        ValueError: If code not found, or if trying to update code/famille

    Example:
        >>> from pathlib import Path
        >>> import tempfile
        >>> tmp = Path(tempfile.mktemp(suffix='.md'))
        >>> product = {'code': 'P1', 'ref': '', 'titre': 'Original',
        ...            'famille': 'test', 'texte': '', 'dimensions': [],
        ...            'images': [], 'metadata_pptx': []}
        >>> append_product_to_family(tmp, product)
        >>> updated = update_product_in_family(tmp, 'P1', {'titre': 'Updated'})
        >>> updated['titre']
        'Updated'
        >>> tmp.unlink()
    """
    # Import here to avoid circular dependency at module level
    from gendoc.parsers.md_parser import parse_family_md

    # Validate updates
    if 'code' in updates or 'famille' in updates:
        raise ValueError("Cannot update code or famille - use delete + add instead")

    # Parse all products
    products = parse_family_md(filepath)

    # Find product by code (case-insensitive)
    product_index = None
    for i, product in enumerate(products):
        if product.get('code', '').upper() == code.upper():
            product_index = i
            break

    if product_index is None:
        raise ValueError(f"Code non trouve dans {filepath.name}: {code}")

    # Apply updates to the found product
    for key, value in updates.items():
        products[product_index][key] = value

    # Read header to preserve it
    header = _read_header(filepath)
    header_lines = header.split('\n') if header else []

    # Rewrite file
    write_family_file(filepath, header_lines, products)

    return products[product_index]


def remove_product_from_family(filepath: Path, code: str) -> dict:
    """
    Remove a product from a family MD file.

    Performs read-filter-write of the entire file. Updates the reference count.

    Args:
        filepath: Path to the family MD file
        code: Product code to remove (case-insensitive match)

    Returns:
        Removed product dictionary (for confirmation)

    Raises:
        ValueError: If code not found

    Example:
        >>> from pathlib import Path
        >>> import tempfile
        >>> tmp = Path(tempfile.mktemp(suffix='.md'))
        >>> p1 = {'code': 'P1', 'ref': '', 'titre': 'Product 1',
        ...       'famille': 'test', 'texte': '', 'dimensions': [],
        ...       'images': [], 'metadata_pptx': []}
        >>> append_product_to_family(tmp, p1)
        >>> removed = remove_product_from_family(tmp, 'P1')
        >>> removed['code']
        'P1'
        >>> tmp.unlink()
    """
    # Import here to avoid circular dependency at module level
    from gendoc.parsers.md_parser import parse_family_md

    # Parse all products
    products = parse_family_md(filepath)

    # Find and remove product by code (case-insensitive)
    removed_product = None
    remaining_products = []
    for product in products:
        if product.get('code', '').upper() == code.upper():
            removed_product = product
        else:
            remaining_products.append(product)

    if removed_product is None:
        raise ValueError(f"Code non trouve dans {filepath.name}: {code}")

    # Read header to preserve it
    header = _read_header(filepath)
    header_lines = header.split('\n') if header else []

    # Rewrite file with remaining products
    write_family_file(filepath, header_lines, remaining_products)

    # Update reference count in header
    update_header_count(filepath, len(remaining_products))

    return removed_product
