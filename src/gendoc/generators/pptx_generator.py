"""
PowerPoint presentation generator for Delagrave product tech sheets.

This module provides the core PowerPoint slide generation engine that produces
product tech sheet slides from MD reference data. It handles template loading,
layout selection, text placeholder population, and image insertion.

This is a pure library module (no I/O beyond file operations).
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import tempfile
import zipfile
import shutil
from pptx import Presentation
from pptx.util import Pt

from gendoc.parsers.md_parser import find_product


# Family to layout index mapping
FAMILY_LAYOUT_MAP = {
    'paillasse': 1,   # Fiche technique profil paillasse
    'sorbonne': 2,    # Fiche technique sorbonne
    'revetement': 3,  # Fiche technique revetement
    'meubles': 4,     # Fiche technique meuble
    'tables-en': 4,   # Same layout as meubles
    'equipement': 5,  # Fiche technique equipement
    'elec-sorb': 5,   # Same layout as equipement
    'complements': 5, # Same layout as equipement
}

# VBA shape index to python-pptx placeholder index mapping
VBA_TO_PLACEHOLDER = {
    'paillasse': {
        1: 13,  # TEXTE
        2: 0,   # TITRE
        3: 14,  # Revetements
        4: 15,  # REF
        5: 16,  # dim 1
        6: 17,  # dim 2
        7: 18,  # dim 3
        8: 19,  # dim 4
        9: 20,  # dim 5
        10: 21, # page
    },
    'sorbonne': {
        1: 13,  # TEXTE
        2: 0,   # TITRE
        3: 14,  # Revetements
        4: 15,  # REF
        5: 16,  # dim 1
        6: 17,  # dim 2
        7: 18,  # dim 3
        8: 19,  # dim 4
        9: 20,  # dim 5
        10: 23, # dim 6
        11: 28, # dim 7
        12: 29, # page
    },
    'revetement': {
        1: 13,  # TEXTE
        2: 0,   # TITRE
        3: 14,  # Mise en oeuvre / Applications
        4: 15,  # REF
        5: 16,  # Finition
        6: 17,  # Applications
        7: 18,  # page
    },
    'meubles': {
        1: 13,  # TEXTE
        2: 0,   # TITRE
        3: 15,  # REF
        4: 16,  # page
    },
    'equipement': {
        1: 0,   # TITRE
        2: 15,  # Reference
        3: 16,  # page
    },
}


def load_template(template_path: Path) -> Presentation:
    """
    Load PowerPoint template from .potm (macro-enabled) file.

    python-pptx cannot open .potm directly, so this function:
    1. Copies .potm to temp file with .pptx extension
    2. Opens as zipfile and modifies content types
    3. Removes VBA macros
    4. Returns valid Presentation object

    Args:
        template_path: Path to the .potm template file

    Returns:
        Presentation object ready for slide generation

    Raises:
        FileNotFoundError: If template_path does not exist
        ValueError: If template cannot be converted
    """
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    # Create temporary directory for conversion
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Copy template to temp location
        temp_potm = temp_path / "template.potm"
        shutil.copy2(template_path, temp_potm)

        # Create output pptx path
        temp_pptx = temp_path / "template.pptx"

        # Convert .potm to .pptx by modifying zip contents
        with zipfile.ZipFile(temp_potm, 'r') as zip_in:
            with zipfile.ZipFile(temp_pptx, 'w', zipfile.ZIP_DEFLATED) as zip_out:
                for item in zip_in.infolist():
                    # Skip VBA project file
                    if 'vbaProject.bin' in item.filename:
                        continue

                    # Read file content
                    data = zip_in.read(item.filename)

                    # Modify [Content_Types].xml to remove macro references
                    if item.filename == '[Content_Types].xml':
                        data_str = data.decode('utf-8')
                        # Remove macro content type
                        data_str = data_str.replace(
                            'application/vnd.ms-powerpoint.template.macroEnabled.main+xml',
                            'application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml'
                        )
                        # Remove vbaProject content type entries
                        data_str = data_str.replace(
                            '<Default Extension="bin" ContentType="application/vnd.ms-office.vbaProject"/>',
                            ''
                        )
                        data = data_str.encode('utf-8')

                    # Write to output zip
                    zip_out.writestr(item, data)

        # Load the converted presentation
        prs = Presentation(str(temp_pptx))

        return prs


def _populate_slide(slide: Any, product: Dict[str, Any], family: str) -> None:
    """
    Populate slide text placeholders with product data.

    Args:
        slide: python-pptx Slide object
        product: Product dictionary from md_parser
        family: Family name (lowercase)
    """
    # Create mapping of placeholder idx to content
    placeholder_data = {}

    # Map standard fields
    placeholder_data[0] = product.get('titre', '')
    placeholder_data[13] = product.get('texte', '')
    placeholder_data[15] = product.get('ref', '')

    # Map dimensions to placeholders using VBA_TO_PLACEHOLDER
    vba_mapping = VBA_TO_PLACEHOLDER.get(family, {})

    for dimension in product.get('dimensions', []):
        shape_index_str = dimension.get('shape_index', '').strip()
        if not shape_index_str:
            continue

        try:
            vba_index = int(shape_index_str)
        except (ValueError, TypeError):
            continue

        # Get placeholder idx from VBA mapping
        placeholder_idx = vba_mapping.get(vba_index)
        if placeholder_idx is None:
            continue

        # Build text value with prefix if present
        prefix = dimension.get('prefix', '').strip()
        valeur = dimension.get('valeur', '').strip()

        if prefix:
            text_value = f"{prefix}{valeur}"
        else:
            text_value = valeur

        placeholder_data[placeholder_idx] = text_value

    # Populate placeholders
    for placeholder in slide.placeholders:
        try:
            idx = placeholder.placeholder_format.idx
            if idx in placeholder_data and placeholder_data[idx]:
                placeholder.text_frame.text = placeholder_data[idx]
        except (AttributeError, KeyError):
            # Some shapes may not have placeholder_format or idx
            continue


def _insert_images(slide: Any, product: Dict[str, Any], project_root: Path) -> int:
    """
    Insert product images into slide at specified positions.

    Args:
        slide: python-pptx Slide object
        product: Product dictionary from md_parser
        project_root: Root directory for resolving relative image paths

    Returns:
        Number of images successfully inserted
    """
    images_inserted = 0

    for image_data in product.get('images', []):
        chemin = image_data.get('chemin', '').strip()
        if not chemin:
            continue

        # Skip .missing files
        if chemin.endswith('.missing'):
            continue

        # Build absolute path
        image_path = project_root / chemin

        # Check if image exists
        if not image_path.exists():
            continue

        # Get position data (in VBA points)
        left = image_data.get('left', 0)
        top = image_data.get('top', 0)
        width = image_data.get('width', 0)
        height = image_data.get('height', 0)

        if left == 0 or top == 0 or width == 0:
            continue

        # Convert to EMUs using Pt (1 point = 12700 EMUs)
        left_emu = Pt(left)
        top_emu = Pt(top)
        width_emu = Pt(width)

        # If height is 0 or missing, let python-pptx calculate from aspect ratio
        try:
            if height > 0:
                height_emu = Pt(height)
                slide.shapes.add_picture(
                    str(image_path),
                    left_emu,
                    top_emu,
                    width_emu,
                    height_emu
                )
            else:
                slide.shapes.add_picture(
                    str(image_path),
                    left_emu,
                    top_emu,
                    width_emu
                )
            images_inserted += 1
        except Exception:
            # Image may be corrupted or invalid format
            continue

    return images_inserted


def _add_revetement_slides(
    prs: Presentation,
    revetement_codes: List[str],
    references_dir: Path,
    project_root: Path
) -> List[str]:
    """
    Add revetement (coating) slides for specified coating codes.

    Args:
        prs: Presentation object to add slides to
        revetement_codes: List of coating codes to generate slides for
        references_dir: Path to Delagrave/references/
        project_root: Root directory for resolving image paths

    Returns:
        List of coating codes that were successfully added
    """
    added = []

    for code in revetement_codes:
        # Look up coating product
        product = find_product(code, references_dir)
        if not product:
            continue

        # Use revetement layout (layout 3)
        layout_index = FAMILY_LAYOUT_MAP.get('revetement', 3)
        slide = prs.slides.add_slide(prs.slide_layouts[layout_index])

        # Populate slide
        _populate_slide(slide, product, 'revetement')
        _insert_images(slide, product, project_root)

        added.append(code)

    return added


def generate_presentation(
    product_codes: List[str],
    output_path: Path,
    references_dir: Path,
    template_path: Path,
    project_root: Path,
    mode: str = "FTI",
    revetement_codes: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Generate a PowerPoint presentation with product tech sheets.

    This is the main orchestrator function that:
    1. Loads the PowerPoint template
    2. Generates slides for each product code
    3. Auto-generates coating slides for products with coatings
    4. Saves the final presentation

    Args:
        product_codes: List of product codes to generate slides for
        output_path: Path where .pptx should be saved
        references_dir: Path to Delagrave/references/
        template_path: Path to .potm template file
        project_root: Root directory for resolving relative paths
        mode: Generation mode (default "FTI")
        revetement_codes: Optional list of coating codes to add manually

    Returns:
        Dictionary with generation results:
        {
            'slides_generated': int,
            'revetements_added': list of coating codes,
            'skipped': list of {'code': str, 'reason': str}
        }

    Raises:
        FileNotFoundError: If template or references not found
    """
    # Load template
    prs = load_template(template_path)

    slides_generated = 0
    skipped = []
    coating_codes_set = set()

    # Add revetement codes if provided explicitly
    if revetement_codes:
        coating_codes_set.update(revetement_codes)

    # Generate slides for each product
    for code in product_codes:
        # Look up product data
        product = find_product(code, references_dir)

        # Try with base code if coating suffix present
        if not product and '-' in code:
            # Try stripping last segment (potential coating suffix)
            base_code = '-'.join(code.split('-')[:-1])
            product = find_product(base_code, references_dir)
            if product:
                # Extract potential coating code from suffix
                potential_coating = code.split('-')[-1]
                if len(potential_coating) <= 3:  # Coating codes are short
                    coating_codes_set.add(potential_coating)

        if not product:
            skipped.append({'code': code, 'reason': 'Product not found in references'})
            continue

        # Get family
        family = product.get('famille', '').lower()

        # Skip fiches-existantes (Phase 5 handles these)
        if family == 'fiches-existantes':
            skipped.append({'code': code, 'reason': 'Fiches-existantes handled in Phase 5'})
            continue

        # Check if family has a layout mapping
        if family not in FAMILY_LAYOUT_MAP:
            skipped.append({'code': code, 'reason': f'No layout mapping for family: {family}'})
            continue

        # Get layout index
        layout_index = FAMILY_LAYOUT_MAP[family]

        # Add slide
        slide = prs.slides.add_slide(prs.slide_layouts[layout_index])

        # Populate text placeholders
        _populate_slide(slide, product, family)

        # Insert images
        _insert_images(slide, product, project_root)

        slides_generated += 1

        # Check if product has coating information in dimensions
        for dimension in product.get('dimensions', []):
            dim_name = dimension.get('name', '').lower()
            if 'revetement' in dim_name or 'revêtement' in dim_name:
                # Extract coating codes from the dimension value
                valeur = dimension.get('valeur', '')
                # Common coating codes: GE, GR, IN, DA, etc.
                # They appear in the list separated by commas
                for potential_code in valeur.split(','):
                    cleaned = potential_code.strip()
                    # Simple heuristic: 2-3 uppercase letters likely a coating code
                    if cleaned and len(cleaned) <= 3 and cleaned.isupper():
                        coating_codes_set.add(cleaned)

    # Generate coating slides
    revetements_added = []
    if coating_codes_set:
        revetements_added = _add_revetement_slides(
            prs,
            list(coating_codes_set),
            references_dir,
            project_root
        )

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save presentation
    prs.save(str(output_path))

    return {
        'slides_generated': slides_generated,
        'revetements_added': revetements_added,
        'skipped': skipped
    }
