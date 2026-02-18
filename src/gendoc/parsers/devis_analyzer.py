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

# Special article prefixes (SP codes) with their family mappings
SP_PREFIX_MAP = {
    'SPMOB': 'meubles',
    'SPPAIL': 'paillasse',
    'SPTABLEEN': 'tables-en',
    'SPUSE': 'equipement',
}

# Alias mapping: devis codes -> catalog codes
# When a devis uses a different code than the catalog, map it here
CODE_ALIASES = {
    "P216": "ELEC-PC",
    "P216E": "ELEC-PC",
    "P320": "ELEC-PC",
    "P432": "ELEC-PC",
    "P432E": "ELEC-PC",
    "PCMOSA": "ELEC-PC",
    "PCONDU": "ELEC-PC",
    "CU12V": "CU12V / CU12PPH",
    "CU12PPH": "CU12V / CU12PPH",
    "CU2V": "CU2V / CU2PPH",
    "CU2PPH": "CU2V / CU2PPH",
    "CU9V": "CU9V / CU9PPH",
    "CU9PPH": "CU9V / CU9PPH",
}

# Exclusion list for common false positives in PDF extraction
# These strings are NOT product codes but frequently appear in devis PDFs:
# - Measurement values (850MM, 1200MM, etc.)
# - Section headers (CONDITIONS, LIVRAISON, SALLE, etc.)
# - Document structure words (DESIGNATION, TOTAL, REMISE, etc.)
#
# Users can add entries here to filter additional false positives.
# Filtering happens in classify_codes() - excluded words do not appear in inconnus output.
EXCLUSION_WORDS = {
    # Measurement values
    "850MM", "750MM", "600MM", "900MM", "1200MM", "1500MM",
    # Section/header words
    "CONDITIONS", "LIVRAISON", "SALLE", "DEPOSE", "DIVERS", "MONTANT",
    "FORFAITS", "MOBILIER", "EQUIPEMENT", "MENUISERIE", "VENTILATION",
    "PLOMBERIE", "ELECTRICITE", "MACONNERIE", "DEMOLITION", "PEINTURE",
    "ENSEIGNEMENT",
    # Document structure words
    "DESIGNATION", "ARTICLE", "OPTION", "TOTAL", "REMISE", "ACOMPTE",
    "REGLEMENT",
    # Existing exclusions (preserved from hardcoded checks)
    "PAILLASSE", "SORBONNE", "DELAGRAVE"
}


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


def extract_sp_designations(pages_text: List[str], sp_codes: List[str]) -> Dict[str, str]:
    """
    Extract designation text for SP (special) article codes from PDF page text.

    The designation is the complete descriptive text that follows the SP code
    in the PDF, often spanning multiple lines. This function extracts and joins
    that multi-line text while removing quantity indicators.

    Args:
        pages_text: List of page texts from extract_text()
        sp_codes: List of SP article codes to extract designations for

    Returns:
        Dictionary mapping SP code -> designation text (first occurrence wins)

    Example:
        >>> designations = extract_sp_designations(pages, ['SPMOB-25355'])
        >>> 'Paillasse Murale' in designations['SPMOB-25355']
        True
    """
    designations = {}

    # Skip first page (cover), process remaining pages
    for page in pages_text[1:]:
        lines = page.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Check if this line starts with any of our SP codes
            matched_code = None
            for sp_code in sp_codes:
                if sp_code in designations:
                    # Already found this code
                    continue

                # Case-insensitive match at start of line
                if line.upper().startswith(sp_code.upper()):
                    matched_code = sp_code
                    break

            if matched_code:
                # Extract designation starting from this line
                designation_parts = []

                # First line: text after the code
                first_line_text = line[len(matched_code):].strip()

                # Strip trailing quantity pattern: "UN \d+" or just "\d+"
                # The quantity column (e.g., "UN 1") often gets merged into the text
                first_line_text = re.sub(r'\s+UN\s+\d+$', '', first_line_text)
                first_line_text = re.sub(r'\s+\d+$', '', first_line_text)

                if first_line_text:
                    designation_parts.append(first_line_text)

                # Continue reading subsequent lines as continuation
                i += 1
                while i < len(lines):
                    continuation_line = lines[i].strip()

                    # Stop if empty line
                    if not continuation_line:
                        break

                    # Stop if line contains exclusion keywords
                    if any(keyword in continuation_line for keyword in [
                        'Sous-total', 'Page ', 'Total ', 'MONTANT', 'Article'
                    ]):
                        break

                    # Stop if next line starts with an article code
                    # Article codes have specific patterns:
                    # - Contain hyphens (PM-D-H-75, SPMOB-25355)
                    # - OR all uppercase short codes (ACB120, CU12G)
                    # - Must be followed by space to separate from description
                    # This avoids matching regular words like "Dimension"
                    if re.match(r'^[A-Z0-9][A-Z0-9\-]{3,19}\s', continuation_line):
                        # Check if it contains a hyphen or is all uppercase (no lowercase)
                        first_word = continuation_line.split()[0]
                        if '-' in first_word or first_word.isupper():
                            # This looks like a new article code
                            break

                    # Add this line to designation
                    designation_parts.append(continuation_line)
                    i += 1

                # Join all parts, collapse multiple spaces
                designation = ' '.join(designation_parts)
                designation = re.sub(r'\s+', ' ', designation).strip()
                designations[matched_code] = designation
            else:
                i += 1

    return designations


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
        - speciaux: List of special article dicts (code, famille, prefix)
        - inconnus: List of unknown code strings

    Example:
        >>> result = classify_codes(["PM-D-H-75-GE", "FPORT"], Path("Delagrave/references"))
        >>> result['references'][0]['revetement']
        'GE'
    """
    references = []
    revetements_detected = set()
    forfaits = []
    speciaux = []
    inconnus = []

    for code in codes:
        # Filter exclusion words FIRST (before any classification)
        # These are known non-product strings, not unknown codes
        code_upper = code.upper()
        if code_upper in EXCLUSION_WORDS:
            continue  # Silent filter - these are not products, not unknowns

        # Filter measurement patterns (NNN+MM, NNN+M)
        if re.match(r'^\d+MM?$', code_upper):
            continue  # Silent filter for measurement values

        # Try direct lookup first
        product = find_product(code, references_dir)

        # If not found, try alias mapping (devis code -> catalog code)
        if not product and code.upper() in CODE_ALIASES:
            product = find_product(CODE_ALIASES[code.upper()], references_dir)

        if product:
            # Found directly or via alias
            references.append({
                'code': code,
                'famille': product['famille'],
                'revetement': None
            })
            continue

        # Check if it's a special article (SP prefix)
        # SP codes: SPMOB, SPPAIL, SPTABLEEN, SPUSE with optional suffix
        code_upper = code.upper()
        matched_prefix = None
        detected_family = None

        for prefix, family in SP_PREFIX_MAP.items():
            if code_upper.startswith(prefix):
                matched_prefix = prefix
                detected_family = family
                break

        if matched_prefix:
            speciaux.append({
                'code': code,
                'famille': detected_family,
                'prefix': matched_prefix
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
            if not product:
                # Try stripping width suffix from base: S-P-15 -> S-P
                width_m = re.match(r'^(.+)-(\d{2,3})$', base_code)
                if width_m:
                    product = find_product(width_m.group(1), references_dir)
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

        # Try stripping numeric width suffix (e.g. S-P-12 -> S-P, S-P-A-15 -> S-P-A)
        # Devis codes often append width: -12=1200mm, -15=1500mm, -18=1800mm, etc.
        width_match = re.match(r'^(.+)-(\d{2,3})$', code)
        if width_match:
            base_no_width = width_match.group(1)
            product = find_product(base_no_width, references_dir)
            if product:
                references.append({
                    'code': code,
                    'famille': product['famille'],
                    'revetement': None
                })
                continue
            # Also try with coating: S-P-15-GE -> base=S-P, coating=GE
            for coating_code in REVETEMENT_CODES:
                if base_no_width.endswith(f'-{coating_code}'):
                    base_no_coating = base_no_width[:-len(coating_code)-1]
                    product = find_product(base_no_coating, references_dir)
                    if product:
                        references.append({
                            'code': code,
                            'famille': product['famille'],
                            'revetement': coating_code
                        })
                        revetements_detected.add(coating_code)
                        break

            if product:
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
        'speciaux': speciaux,
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
        - speciaux: List of special article dicts (code, famille, prefix)
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

    # Extract designations for SP articles
    sp_codes = [item['code'] for item in classification['speciaux']]
    if sp_codes:
        designations = extract_sp_designations(pages_text, sp_codes)
        # Enrich speciaux entries with designation field
        for item in classification['speciaux']:
            item['designation'] = designations.get(item['code'], '')

    # Return complete structured result
    return {
        'header': header,
        'references': classification['references'],
        'revetements': classification['revetements'],
        'forfaits': classification['forfaits'],
        'speciaux': classification['speciaux'],
        'inconnus': classification['inconnus']
    }
