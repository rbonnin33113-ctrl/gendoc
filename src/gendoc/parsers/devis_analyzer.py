"""
Devis Analyzer for Delagrave quote documents.

This module provides comprehensive analysis of quote PDFs: identifies article codes,
classifies them into product families, detects coating suffixes, and separates
packages (forfaits) from product references.

This is a pure library module with no I/O operations (no print/input).
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import re

from gendoc.parsers.pdf_parser import extract_text, extract_header
from gendoc.parsers.md_parser import find_product, parse_family_md, get_all_family_files


# Known coating codes (revêtements) that can appear as suffixes
REVETEMENT_CODES = {"DA", "GE", "GED", "GR", "IN", "PP", "RP", "RP6", "RPR", "RS", "SP", "ST"}


def extract_article_codes(pages_text: List[str]) -> List[str]:
    """
    Extract unique article codes from PDF pages.

    Article codes are identified as the first word on a line in product pages.
    Section headers (all-caps without hyphens) and footer lines are excluded.

    Args:
        pages_text: List of page texts from extract_text()

    Returns:
        Sorted list of unique article codes

    Example:
        >>> codes = extract_article_codes(pages_text)
        >>> "PM-D-H-75-GE" in codes
        True
    """
    codes = set()

    # Skip first page (cover), process remaining pages
    for page in pages_text[1:]:
        lines = page.split('\n')

        for line in lines:
            line_stripped = line.strip()

            # Skip empty lines
            if not line_stripped:
                continue

            # Skip lines containing exclusion keywords
            if any(keyword in line_stripped for keyword in [
                'Page ', 'Sous-total', 'Total ', 'Article', 'SAS DELAGRAVE',
                'OFFRE DE PRIX', 'RCS ', 'SIRET', 'capital', 'Désignation',
                'Unit� Qte Prix', 'MONTANT', 'Conditions', 'Délai'
            ]):
                continue

            # Skip section headers (all-caps lines without hyphens or numbers)
            # These are titles like "PAILLASSE HUMIDE", "FORFAITS", "Transport", "Installation"
            # Section headers are typically:
            # - All uppercase or Title Case
            # - No hyphens
            # - No numbers
            # - Contain only letters and spaces
            # - Usually short (1-3 words)
            words_in_line = line_stripped.split()
            if len(words_in_line) <= 3 and '-' not in line_stripped and not re.search(r'\d', line_stripped):
                # Check if all words are letters only (section header pattern)
                if all(re.match(r'^[A-Za-z]+$', word) for word in words_in_line):
                    # Common section header keywords
                    if any(header in line_stripped for header in [
                        'PAILLASSE', 'SORBONNE', 'FORFAIT', 'Transport', 'Installation',
                        'HUMIDE', 'SECHE', 'DELAGRAVE'
                    ]):
                        continue

            # Extract first word (potential article code)
            words = line_stripped.split()
            if not words:
                continue

            first_word = words[0]

            # Article codes are alphanumeric with possible hyphens
            # Examples: PM-D-H-75-GE, SPMSE-1967, CU12V, EU40, FL12, FPORT, FORPOSE1J
            # Key characteristics:
            # 1. Starts with uppercase letter or digit
            # 2. Contains letters and possibly digits/hyphens
            # 3. Length between 4-20 characters (excludes short words like "DE", "LA")
            # 4. If no digits/hyphens, must be at least 5 chars and look like a code
            if re.match(r'^[A-Z0-9][A-Za-z0-9\-]{3,19}$', first_word):
                # Must contain at least one letter (excludes pure numbers)
                if re.search(r'[A-Za-z]', first_word):
                    # Allow codes with digits or hyphens immediately
                    if re.search(r'\d', first_word) or '-' in first_word:
                        codes.add(first_word.upper())
                    # For codes without digits/hyphens, be more strict
                    # Must be 5+ chars and contain at least 2 uppercase consonants in a row
                    # This catches FPORT, FORPOSE but excludes common words
                    elif len(first_word) >= 5:
                        # Check if it looks like a code (has consonant clusters)
                        if re.search(r'[BCDFGHJKLMNPQRSTVWXZ]{2,}', first_word):
                            codes.add(first_word.upper())

    return sorted(list(codes))


def classify_codes(codes: List[str], references_dir: Path) -> Dict[str, Any]:
    """
    Classify article codes into product references, coatings, packages, and unknowns.

    For each code:
    1. Try direct lookup in MD files
    2. If not found, check for coating suffix and try lookup without suffix
    3. If looks like a package (forfait), classify as such
    4. Otherwise, mark as unknown

    Args:
        codes: List of article codes from extract_article_codes()
        references_dir: Path to Delagrave/references/

    Returns:
        Dictionary with keys:
        - references: List of product dicts (code, famille, revetement)
        - revetements: List of coating dicts (code, titre)
        - forfaits: List of package code strings
        - inconnus: List of unknown code strings

    Example:
        >>> result = classify_codes(["PM-D-H-75-GE", "FPORT"], Path("Delagrave/references"))
        >>> result['references'][0]['revetement']
        'GE'
    """
    references = []
    revetements_detected = set()
    forfaits = []
    inconnus = []

    for code in codes:
        # Try direct lookup first
        product = find_product(code, references_dir)

        if product:
            # Found directly
            references.append({
                'code': code,
                'famille': product['famille'],
                'revetement': None
            })
            continue

        # Not found - check for coating suffix
        coating_detected = None
        base_code = code

        # Check if code ends with a known coating suffix
        for coating_code in REVETEMENT_CODES:
            # Try both "-SUFFIX" and "SUFFIX" patterns
            if code.endswith(f'-{coating_code}'):
                base_code = code[:-len(coating_code)-1]  # Remove "-SUFFIX"
                coating_detected = coating_code
                break
            elif code.endswith(coating_code) and len(code) > len(coating_code) + 1:
                # Only if there's substantial content before the suffix
                potential_base = code[:-len(coating_code)]
                if potential_base.endswith('-'):
                    base_code = potential_base[:-1]
                    coating_detected = coating_code
                    break

        # If coating detected, try lookup with base code
        if coating_detected:
            product = find_product(base_code, references_dir)
            if product:
                references.append({
                    'code': code,
                    'famille': product['famille'],
                    'revetement': coating_detected
                })
                revetements_detected.add(coating_detected)
                continue

        # Check if it's a package (forfait)
        # Packages typically start with "FOR" or "F" + keyword
        # Examples: FPORT, FORPOSE1J, FTRANSPORT
        # Exclude common section headers that got through
        if code in ['FORFAITS', 'PAILLASSE', 'SORBONNE', 'DELAGRAVE', 'CONDITIONS', 'MONTANT']:
            # These are section headers or common words, not codes
            inconnus.append(code)
            continue

        # Check if it's a package
        is_forfait = False
        if code.startswith('FOR') and len(code) > 3:
            # FORPOSE1J, etc. but not "FORFAITS" (already filtered above)
            is_forfait = True
        elif code.startswith('F') and len(code) <= 6:
            # Short F-codes that aren't equipment (like FL12)
            if not re.match(r'^F[A-Z]{1,2}\d+$', code):  # Exclude FL12, EU40 patterns
                is_forfait = True
        elif any(keyword in code.upper() for keyword in ['POSE', 'PORT', 'TRANSPORT']):
            if len(code) > 4:  # Avoid matching "PORT" itself
                is_forfait = True

        if is_forfait:
            forfaits.append(code)
            continue

        # Unknown code
        inconnus.append(code)

    # Handle self-standing cabinets that need coatings
    # Look for products in "sorbonne" family with "Autoportante" in title
    for ref in references:
        if ref['famille'] == 'sorbonne' and not ref['revetement']:
            # Load the product details to check if it's "Autoportante"
            product = find_product(ref['code'], references_dir)
            if product and 'autoportante' in product['titre'].lower():
                # Mark as needing coating selection
                ref['revetement'] = 'auto'

    # Build coating fiches list
    revetements = []
    revetement_products = parse_family_md(references_dir / 'revetement.md')

    for coating_code in sorted(revetements_detected):
        # Find the coating product info
        for rev_product in revetement_products:
            if rev_product['code'].upper() == coating_code.upper():
                revetements.append({
                    'code': coating_code,
                    'titre': rev_product['titre']
                })
                break

    return {
        'references': references,
        'revetements': revetements,
        'forfaits': forfaits,
        'inconnus': inconnus
    }


def analyze_devis(pdf_path: Path, references_dir: Path) -> Dict[str, Any]:
    """
    Analyze a complete quote PDF and return structured data.

    This is the main entry point for PDF quote analysis. It orchestrates
    text extraction, header parsing, code identification, and classification.

    Args:
        pdf_path: Path to the PDF quote file
        references_dir: Path to Delagrave/references/

    Returns:
        Dictionary with keys:
        - header: Dict with numero_devis, date, client
        - references: List of product dicts (code, famille, revetement)
        - revetements: List of coating dicts (code, titre)
        - forfaits: List of package code strings
        - inconnus: List of unknown code strings

    Raises:
        FileNotFoundError: If PDF file does not exist
        ValueError: If PDF file is invalid

    Example:
        >>> result = analyze_devis(
        ...     Path("Devis Test.pdf"),
        ...     Path("Delagrave/references")
        ... )
        >>> result['header']['numero_devis']
        '25 64 0637'
    """
    # Extract text from PDF
    pages_text = extract_text(pdf_path)

    # Parse header
    header = extract_header(pages_text)

    # Extract article codes
    codes = extract_article_codes(pages_text)

    # Classify codes
    classification = classify_codes(codes, references_dir)

    # Return complete structured result
    return {
        'header': header,
        'references': classification['references'],
        'revetements': classification['revetements'],
        'forfaits': classification['forfaits'],
        'inconnus': classification['inconnus']
    }
