"""
PowerPoint generation module for Delagrave tech sheets.
"""

from .pptx_generator import generate_presentation, load_template
from .document_assembler import assemble_document, add_cover_page, add_chapter_separator, add_toc_page, FAMILY_ORDER, FAMILY_DISPLAY_NAMES

__all__ = [
    'generate_presentation',
    'load_template',
    'assemble_document',
    'add_cover_page',
    'add_chapter_separator',
    'add_toc_page',
    'FAMILY_ORDER',
    'FAMILY_DISPLAY_NAMES'
]
