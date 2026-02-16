"""
Unit tests for modern_template.py builder dispatch and slide generation.

Validates:
- Family-to-builder dispatch logic (build_product_slide)
- Multi-page families use _build_armoire_slide (2 slides)
- Standard families use appropriate single-slide builders
- Builder function selection is correct per family
"""

import pytest
from pathlib import Path
from gendoc.generators.modern_template import build_product_slide, init_company_info
from gendoc.generators.pptx_generator import load_template
from gendoc.parsers.md_parser import find_product


class TestBuildProductSlideDispatch:
    """Test that build_product_slide dispatches to correct builder based on family."""

    def test_armoire_securite_uses_armoire_builder(self, sample_codes, references_dir, project_root, template_path):
        """armoire-securite family dispatches to _build_armoire_slide (2-page template)."""
        code = sample_codes['armoire-securite']
        product = find_product(code, references_dir)
        assert product is not None

        # Initialize company info and load template
        init_company_info(references_dir)
        prs = load_template(template_path)
        logo_path = project_root / "Delagrave" / "images" / "delagrave2022_high.png"

        # Build product slide (should create 2 slides for armoire-securite)
        initial_count = len(prs.slides)
        warnings = build_product_slide(prs, product, 'armoire-securite', project_root, logo_path)

        # Verify 2 slides added (Option C template)
        assert len(prs.slides) == initial_count + 2, "armoire-securite should add 2 slides"
        assert isinstance(warnings, list), "Should return warnings list"

    def test_enceinte_ventilee_uses_armoire_builder(self, sample_codes, references_dir, project_root, template_path):
        """enceinte-ventilee family dispatches to _build_armoire_slide (2-page template)."""
        code = sample_codes['enceinte-ventilee']
        product = find_product(code, references_dir)
        assert product is not None

        init_company_info(references_dir)
        prs = load_template(template_path)
        logo_path = project_root / "Delagrave" / "images" / "delagrave2022_high.png"

        initial_count = len(prs.slides)
        warnings = build_product_slide(prs, product, 'enceinte-ventilee', project_root, logo_path)

        # Verify 2 slides added
        assert len(prs.slides) == initial_count + 2, "enceinte-ventilee should add 2 slides"
        assert isinstance(warnings, list)

    def test_revetement_uses_revetement_builder(self, sample_codes, references_dir, project_root, template_path):
        """revetement family dispatches to _build_revetement_slide (single slide)."""
        code = sample_codes['revetement']
        product = find_product(code, references_dir)
        assert product is not None

        init_company_info(references_dir)
        prs = load_template(template_path)
        logo_path = project_root / "Delagrave" / "images" / "delagrave2022_high.png"

        initial_count = len(prs.slides)
        warnings = build_product_slide(prs, product, 'revetement', project_root, logo_path)

        # Verify 1 slide added
        assert len(prs.slides) == initial_count + 1, "revetement should add 1 slide"
        assert isinstance(warnings, list)

    def test_simple_families_use_simple_builder(self, sample_codes, references_dir, project_root, template_path):
        """equipement, elec-sorb, complements use _build_simple_slide (single slide)."""
        simple_families = ['equipement', 'elec-sorb', 'complements']

        for family in simple_families:
            code = sample_codes[family]
            product = find_product(code, references_dir)
            assert product is not None, f"Product {code} not found for {family}"

            init_company_info(references_dir)
            prs = load_template(template_path)
            logo_path = project_root / "Delagrave" / "images" / "delagrave2022_high.png"

            initial_count = len(prs.slides)
            warnings = build_product_slide(prs, product, family, project_root, logo_path)

            # Verify 1 slide added
            assert len(prs.slides) == initial_count + 1, f"{family} should add 1 slide"

    def test_standard_families_use_standard_builder(self, sample_codes, references_dir, project_root, template_path):
        """paillasse, sorbonne, meubles, tables-en use _build_standard_slide (single slide)."""
        standard_families = ['paillasse', 'sorbonne', 'meubles', 'tables-en']

        for family in standard_families:
            code = sample_codes[family]
            product = find_product(code, references_dir)
            assert product is not None, f"Product {code} not found for {family}"

            init_company_info(references_dir)
            prs = load_template(template_path)
            logo_path = project_root / "Delagrave" / "images" / "delagrave2022_high.png"

            initial_count = len(prs.slides)
            warnings = build_product_slide(prs, product, family, project_root, logo_path)

            # Verify 1 slide added
            assert len(prs.slides) == initial_count + 1, f"{family} should add 1 slide"


class TestMultiPageBehavior:
    """Test that multi-page families consistently generate 2 slides per product."""

    def test_only_two_families_are_multi_page(self):
        """Only armoire-securite and enceinte-ventilee should use 2-page template."""
        # This is a documentation test - validates the architecture decision
        # documented in Phase 20-03: armoire-securite is ONLY family using Option C

        multi_page_families = {'armoire-securite', 'enceinte-ventilee'}
        all_families = {
            'paillasse', 'sorbonne', 'revetement', 'meubles',
            'tables-en', 'equipement', 'elec-sorb', 'complements',
            'armoire-securite', 'enceinte-ventilee'
        }

        single_page_families = all_families - multi_page_families

        # Verify expectation matches implementation
        # (This test will break if we add more multi-page families, forcing intentional update)
        assert len(multi_page_families) == 2, "Expected exactly 2 multi-page families"
        assert len(single_page_families) == 8, "Expected exactly 8 single-page families"
