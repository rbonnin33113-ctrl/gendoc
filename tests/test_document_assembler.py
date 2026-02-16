"""
Unit tests for document_assembler.py multi-page family handling.

Validates:
- multi_page_families set includes armoire-securite and enceinte-ventilee
- Slide count estimation correctly adds 2 slides for multi-page families
- FAMILY_ORDER includes all 10 families in correct sequence
- FAMILY_DISPLAY_NAMES has French names for all 10 families
"""

import pytest
from collections import OrderedDict
from pathlib import Path
from gendoc.generators.document_assembler import (
    FAMILY_ORDER,
    FAMILY_DISPLAY_NAMES,
    assemble_document,
)
from gendoc.generators.pptx_generator import load_template


class TestFamilyConfiguration:
    """Test that FAMILY_ORDER and FAMILY_DISPLAY_NAMES include all 10 families."""

    def test_family_order_contains_all_ten_families(self):
        """FAMILY_ORDER includes all 10 families in documented sequence."""
        expected_families = [
            'paillasse',
            'sorbonne',
            'revetement',
            'meubles',
            'tables-en',
            'equipement',
            'elec-sorb',
            'complements',
            'armoire-securite',      # Added in commit 0b3600b
            'enceinte-ventilee'      # Added in commit 0cee8d5
        ]

        assert FAMILY_ORDER == expected_families, \
            f"FAMILY_ORDER mismatch. Expected {expected_families}, got {FAMILY_ORDER}"

        # Verify order is intentional (armoire-securite and enceinte-ventilee at end)
        assert FAMILY_ORDER[-2:] == ['armoire-securite', 'enceinte-ventilee'], \
            "New families should appear at end of FAMILY_ORDER"

    def test_family_display_names_covers_all_families(self):
        """FAMILY_DISPLAY_NAMES has French display names for all 10 families."""
        assert len(FAMILY_DISPLAY_NAMES) == 10, \
            f"Expected 10 display names, got {len(FAMILY_DISPLAY_NAMES)}"

        # Verify all FAMILY_ORDER families have display names
        for family in FAMILY_ORDER:
            assert family in FAMILY_DISPLAY_NAMES, \
                f"Family {family} missing from FAMILY_DISPLAY_NAMES"

        # Verify new families have correct French names
        assert FAMILY_DISPLAY_NAMES['armoire-securite'] == 'Armoires de Sécurité'
        assert FAMILY_DISPLAY_NAMES['enceinte-ventilee'] == 'Enceintes Ventilées (PSM)'

    def test_multi_page_families_set_is_correct(self, template_path, project_root, references_dir):
        """Verify multi_page_families logic in assemble_document."""
        # This test validates the internal logic by checking slide count estimation
        # We can't directly access multi_page_families (it's a local var in assemble_document)
        # So we test its effect via TOC page number calculation

        prs = load_template(template_path)

        # Create mock product groups with multi-page and single-page families
        product_groups = OrderedDict()
        product_groups['paillasse'] = [
            {'code': 'P1', 'titre': 'Paillasse 1', 'famille': 'paillasse'},
            {'code': 'P2', 'titre': 'Paillasse 2', 'famille': 'paillasse'}
        ]
        product_groups['armoire-securite'] = [
            {'code': 'A1', 'titre': 'Armoire 1', 'famille': 'armoire-securite'}
        ]

        devis_info = {
            'numero_devis': 'TEST-001',
            'date': '2026-02-16',
            'client': 'Test Client',
            'titre_affaire': 'Test Project'
        }

        # Run assemble_document (this internally calculates page numbers)
        result = assemble_document(product_groups, prs, devis_info, references_dir, project_root)

        # Extract TOC entries from result
        toc_entries = result['toc_entries']

        paillasse_entry = toc_entries[0]
        armoire_entry = toc_entries[1]

        # paillasse: 2 products, 1 slide each
        # Page structure: cover(1), TOC(2), separator(3), P1(4), P2(5), separator(6), A1(7-8)
        assert paillasse_entry['products'][0]['page_number'] == 4  # First paillasse
        assert paillasse_entry['products'][1]['page_number'] == 5  # Second paillasse

        # armoire-securite: 1 product, 2 slides (only first page number shown in TOC)
        assert armoire_entry['products'][0]['page_number'] == 7  # First slide of armoire

        # This validates that multi_page_families={'armoire-securite', 'enceinte-ventilee'}
        # is correctly implemented in document_assembler.py


class TestSlideCountEstimation:
    """Test that slide count estimation correctly handles multi-page families."""

    def test_page_counter_increments_correctly_for_multi_page(self, template_path, project_root, references_dir):
        """Page counter should add 2 for multi-page families, 1 for single-page."""
        prs = load_template(template_path)

        # Create product groups with enceinte-ventilee (multi-page) and meubles (single-page)
        # Note: assemble_document orders families by FAMILY_ORDER, not insertion order
        product_groups = OrderedDict()
        product_groups['enceinte-ventilee'] = [
            {'code': 'E1', 'titre': 'Enceinte 1', 'famille': 'enceinte-ventilee'},
            {'code': 'E2', 'titre': 'Enceinte 2', 'famille': 'enceinte-ventilee'}
        ]
        product_groups['meubles'] = [
            {'code': 'M1', 'titre': 'Meuble 1', 'famille': 'meubles'}
        ]

        devis_info = {
            'numero_devis': 'TEST-002',
            'date': '2026-02-16',
            'client': 'Test Client 2',
            'titre_affaire': 'Test Project 2'
        }

        result = assemble_document(product_groups, prs, devis_info, references_dir, project_root)

        toc_entries = result['toc_entries']

        # assemble_document orders by FAMILY_ORDER: meubles comes before enceinte-ventilee
        # Page structure: cover(1), TOC(2), separator(3), M1(4), separator(5), E1(6-7), E2(8-9)

        # Find entries by family (order is determined by FAMILY_ORDER)
        meubles_entry = next(e for e in toc_entries if e['family'] == 'meubles')
        enceinte_entry = next(e for e in toc_entries if e['family'] == 'enceinte-ventilee')

        # meubles: 1 product, 1 slide
        assert meubles_entry['products'][0]['page_number'] == 4  # M1 single page

        # enceinte-ventilee: 2 products × 2 slides each = 4 slides total
        # Only first page number of each product shown in TOC
        assert enceinte_entry['products'][0]['page_number'] == 6  # E1 first page
        assert enceinte_entry['products'][1]['page_number'] == 8  # E2 first page

        # This validates page_counter logic:
        # page_counter += 1 (separator)
        # page_counter += 1 (first product slide - shown in TOC)
        # page_counter += slides_per_product - 1 (additional slides for multi-page)
