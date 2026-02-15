"""
Image handler for CRUD image operations.

This module provides functions to manage product images during CRUD operations:
- copy_product_images: Copy user-provided images to family directories
- remove_product_images: Remove image files when products are deleted

This is a pure library module following md_writer pattern (no print/logging).
"""

from pathlib import Path
import shutil
from typing import List, Dict


def copy_product_images(source_paths: list[str], famille: str, images_dir: Path) -> list[dict]:
    """
    Copy user-provided image files to the family images directory.

    Takes absolute source file paths, copies each to images_dir/{famille}/,
    and returns a list of image dicts in the MD format.

    Args:
        source_paths: List of absolute file paths to image files
        famille: Family name (e.g., "paillasse")
        images_dir: Base images directory (e.g., PROJECT_ROOT/Delagrave/images)

    Returns:
        List of image dicts with keys:
            - position: empty string (user sets via update_reference)
            - chemin: relative path as stored in MD (Delagrave/images/{famille}/{filename})
            - chemin_original: original source path (for traceability)
            - left, top, width, height: 0.0 (defaults, user sets via update)
            - shape_index: empty string
        Failed copies include an 'error' key with error message.

    Example:
        >>> images_dir = Path("/project/Delagrave/images")
        >>> source_paths = ["/tmp/image1.png", "/tmp/image2.jpg"]
        >>> result = copy_product_images(source_paths, "paillasse", images_dir)
        >>> len(result)
        2
        >>> result[0]['chemin']
        'Delagrave/images/paillasse/image1.png'
    """
    results = []
    target_dir = images_dir / famille

    # Ensure target directory exists
    target_dir.mkdir(parents=True, exist_ok=True)

    for source_path_str in source_paths:
        source_path = Path(source_path_str)

        # Validate source file exists
        if not source_path.exists():
            results.append({
                'position': '',
                'chemin': '',
                'chemin_original': source_path_str,
                'left': 0.0,
                'top': 0.0,
                'width': 0.0,
                'height': 0.0,
                'shape_index': '',
                'error': f"Fichier source non trouve: {source_path_str}"
            })
            continue

        # Extract filename
        filename = source_path.name

        # Build target path
        target_path = target_dir / filename

        # Copy file (overwrite if exists)
        try:
            shutil.copy2(source_path, target_path)

            # Build image dict
            relative_path = f"Delagrave/images/{famille}/{filename}"
            results.append({
                'position': '',
                'chemin': relative_path,
                'chemin_original': source_path_str,
                'left': 0.0,
                'top': 0.0,
                'width': 0.0,
                'height': 0.0,
                'shape_index': ''
            })
        except Exception as e:
            results.append({
                'position': '',
                'chemin': '',
                'chemin_original': source_path_str,
                'left': 0.0,
                'top': 0.0,
                'width': 0.0,
                'height': 0.0,
                'shape_index': '',
                'error': f"Erreur copie: {str(e)}"
            })

    return results


def remove_product_images(product: dict, images_dir: Path) -> dict:
    """
    Remove image files associated with a product from disk.

    Takes a product dict (as returned by remove_product_from_family) and
    deletes its image files from the family images directory.

    Args:
        product: Product dictionary with 'images' and 'famille' keys
        images_dir: Base images directory (e.g., PROJECT_ROOT/Delagrave/images)

    Returns:
        Stats dict with keys:
            - removed: number of files successfully deleted
            - not_found: number of files that didn't exist
            - errors: number of files that failed to delete
            - details: list of detail dicts with 'chemin' and 'status' keys

    Example:
        >>> product = {
        ...     'famille': 'paillasse',
        ...     'images': [
        ...         {'chemin': 'Delagrave/images/paillasse/test.png'}
        ...     ]
        ... }
        >>> images_dir = Path("/project/Delagrave/images")
        >>> result = remove_product_images(product, images_dir)
        >>> 'removed' in result
        True
    """
    stats = {
        'removed': 0,
        'not_found': 0,
        'errors': 0,
        'details': []
    }

    images = product.get('images', [])
    famille = product.get('famille', '')

    if not famille:
        return stats

    for image in images:
        chemin = image.get('chemin', '')
        if not chemin:
            continue

        # Extract filename from chemin
        filename = Path(chemin).name

        # Build absolute path
        target_path = images_dir / famille / filename

        # Try to delete file
        try:
            if target_path.exists():
                target_path.unlink()
                stats['removed'] += 1
                stats['details'].append({
                    'chemin': chemin,
                    'status': 'supprimee'
                })
            else:
                stats['not_found'] += 1
                stats['details'].append({
                    'chemin': chemin,
                    'status': 'non_trouvee'
                })
        except Exception as e:
            stats['errors'] += 1
            stats['details'].append({
                'chemin': chemin,
                'status': f'erreur: {str(e)}'
            })

    return stats
