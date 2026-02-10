"""
Tests for SP (special article) detection and designation extraction.

This module tests:
- BUG-01: SP codes are correctly classified as 'speciaux', not 'inconnus'
- EXT-01: Designation text is extracted from PDF for each SP article
- EXT-02: Each speciaux entry contains complete {code, famille, prefix, designation}
"""

import pytest
from pathlib import Path

from gendoc.parsers.devis_analyzer import classify_codes, extract_sp_designations, analyze_devis


class TestSPClassification:
    """Tests for BUG-01 - SP codes classified correctly."""

    def test_sp_codes_classified_as_speciaux(self, references_dir):
        """All SP prefix codes should be classified as speciaux, not inconnus."""
        codes = ['SPMOB-12345', 'SPPAIL-999', 'SPTABLEEN-1', 'SPUSE-42']
        result = classify_codes(codes, references_dir)

        # All 4 should be in speciaux
        assert len(result['speciaux']) == 4
        assert len(result['inconnus']) == 0

        # Check family mappings
        sp_by_code = {item['code']: item for item in result['speciaux']}
        assert sp_by_code['SPMOB-12345']['famille'] == 'meubles'
        assert sp_by_code['SPPAIL-999']['famille'] == 'paillasse'
        assert sp_by_code['SPTABLEEN-1']['famille'] == 'tables-en'
        assert sp_by_code['SPUSE-42']['famille'] == 'equipement'

    def test_sp_bare_codes_classified(self, references_dir):
        """Bare SP codes (without suffix) should also be classified as speciaux."""
        codes = ['SPMOB', 'SPPAIL', 'SPUSE', 'SPTABLEEN']
        result = classify_codes(codes, references_dir)

        # All should be in speciaux
        assert len(result['speciaux']) == 4
        assert len(result['inconnus']) == 0

    def test_coating_sp_suffix_not_confused_with_sp_prefix(self, references_dir):
        """Coating suffix 'SP' should not be confused with SP prefix codes."""
        codes = ['PM-D-H-75-SP']
        result = classify_codes(codes, references_dir)

        # Should be in references with revetement='SP', NOT in speciaux
        assert len(result['references']) == 1
        assert len(result['speciaux']) == 0
        assert result['references'][0]['revetement'] == 'SP'

    def test_sp_detection_before_coating_stripping(self, references_dir):
        """SP prefix check should happen before coating suffix detection."""
        codes = ['SPMOB-25355', 'PM-D-H-75-GE']
        result = classify_codes(codes, references_dir)

        # SPMOB should be in speciaux
        assert len(result['speciaux']) == 1
        assert result['speciaux'][0]['code'] == 'SPMOB-25355'

        # PM-D-H-75-GE should be in references with coating
        assert len(result['references']) == 1
        assert result['references'][0]['code'] == 'PM-D-H-75-GE'
        assert result['references'][0]['revetement'] == 'GE'


class TestSPDesignationExtraction:
    """Tests for EXT-01, EXT-02 - designation extraction from PDF."""

    def test_extract_sp_designations_with_synthetic_data(self):
        """Extract designation from synthetic multi-line text."""
        pages = [
            "cover page",
            "SPMOB-TEST Description du produit special - UN 1\nDimension 500x300mm\nNEXTCODE Autre produit UN 1"
        ]
        result = extract_sp_designations(pages, ['SPMOB-TEST'])

        # Should extract the designation
        assert 'SPMOB-TEST' in result
        designation = result['SPMOB-TEST']

        # Should contain both lines but not NEXTCODE
        assert 'Description du produit special' in designation
        assert 'Dimension 500x300mm' in designation
        assert 'NEXTCODE' not in designation

    def test_designation_strips_quantity(self):
        """Quantity indicators should be stripped from designation."""
        pages = [
            "cover",
            "SPMOB-QTY Test Product with quantity UN 1"
        ]
        result = extract_sp_designations(pages, ['SPMOB-QTY'])

        assert 'SPMOB-QTY' in result
        designation = result['SPMOB-QTY']

        # Should contain product description but not quantity
        assert 'Test Product with quantity' in designation
        assert 'UN 1' not in designation

    def test_designation_stops_at_next_code(self):
        """Designation extraction should stop when encountering next article code."""
        pages = [
            "cover",
            "SPUSE-A First product line\nSecond product line\nPM-D-H-75 Different product"
        ]
        result = extract_sp_designations(pages, ['SPUSE-A'])

        assert 'SPUSE-A' in result
        designation = result['SPUSE-A']

        # Should contain only lines before PM-D-H-75
        assert 'First product line' in designation
        assert 'Second product line' in designation
        assert 'PM-D-H-75' not in designation
        assert 'Different product' not in designation

    def test_designation_stops_at_exclusion_keywords(self):
        """Designation extraction should stop at exclusion keywords."""
        pages = [
            "cover",
            "SPPAIL-X Product description\nMore details\nSous-total: 1500 EUR"
        ]
        result = extract_sp_designations(pages, ['SPPAIL-X'])

        assert 'SPPAIL-X' in result
        designation = result['SPPAIL-X']

        # Should not contain Sous-total line
        assert 'Product description' in designation
        assert 'More details' in designation
        assert 'Sous-total' not in designation

    def test_extract_designations_from_real_devis(self, project_root):
        """Extract designations from real PDF with SP articles."""
        pdf_path = project_root / "Delagrave" / "Devis - Modeles" / "Devis avec SP.pdf"

        if not pdf_path.exists():
            pytest.skip(f"Real devis PDF not found: {pdf_path}")

        references_dir = project_root / "Delagrave" / "references"
        result = analyze_devis(pdf_path, references_dir)

        # Should have speciaux entries
        assert len(result['speciaux']) > 0

        # All speciaux should have non-empty designation
        for item in result['speciaux']:
            assert 'designation' in item
            assert len(item['designation']) > 0

        # Check specific known SP codes
        sp_by_code = {item['code']: item for item in result['speciaux']}

        if 'SPMOB-25355' in sp_by_code:
            designation = sp_by_code['SPMOB-25355']['designation']
            # This is a "Paillasse Murale" custom product
            assert 'Paillasse' in designation or 'paillasse' in designation.lower()

        if 'SPMOB-25042' in sp_by_code:
            designation = sp_by_code['SPMOB-25042']['designation']
            # This is a "Meuble bas mobile" custom product
            assert 'Meuble' in designation or 'meuble' in designation.lower()

    def test_designation_is_multiline_complete(self, project_root):
        """Verify multi-line designation extraction works with real devis."""
        pdf_path = project_root / "Delagrave" / "Devis - Modeles" / "Devis avec SP.pdf"

        if not pdf_path.exists():
            pytest.skip(f"Real devis PDF not found: {pdf_path}")

        references_dir = project_root / "Delagrave" / "references"
        result = analyze_devis(pdf_path, references_dir)

        sp_by_code = {item['code']: item for item in result['speciaux']}

        if 'SPMOB-25355' in sp_by_code:
            designation = sp_by_code['SPMOB-25355']['designation']
            # Designation should contain dimension info from multiple lines
            # Looking for patterns like "3500mm" or "600mm" or "850mm"
            has_dimensions = any(
                dim in designation for dim in ['3500', '600', '850', 'mm']
            )
            assert has_dimensions, f"Expected dimension info in: {designation}"

    def test_speciaux_have_all_required_fields(self, project_root):
        """Each speciaux entry must have all required fields."""
        pdf_path = project_root / "Delagrave" / "Devis - Modeles" / "Devis avec SP.pdf"

        if not pdf_path.exists():
            pytest.skip(f"Real devis PDF not found: {pdf_path}")

        references_dir = project_root / "Delagrave" / "references"
        result = analyze_devis(pdf_path, references_dir)

        # Every speciaux entry must have all required fields
        for item in result['speciaux']:
            assert 'code' in item
            assert 'famille' in item
            assert 'prefix' in item
            assert 'designation' in item

            # Fields should have values
            assert len(item['code']) > 0
            assert len(item['famille']) > 0
            assert len(item['prefix']) > 0
            # designation can be empty if not found, but key must exist

    def test_case_insensitive_sp_code_matching(self):
        """SP code matching should be case-insensitive."""
        pages = [
            "cover",
            "spmob-lowercase Lowercase test product UN 1"
        ]
        result = extract_sp_designations(pages, ['SPMOB-LOWERCASE'])

        # Should find the code despite case mismatch
        assert 'SPMOB-LOWERCASE' in result
        assert 'Lowercase test product' in result['SPMOB-LOWERCASE']

    def test_multiple_sp_codes_in_same_devis(self):
        """Handle multiple different SP codes in the same document."""
        pages = [
            "cover",
            "SPMOB-A First mobile furniture\nDetails for SPMOB-A\n",
            "SPPAIL-B Custom bench product\nWith special coating\n",
            "SPUSE-C Special equipment item\n"
        ]
        sp_codes = ['SPMOB-A', 'SPPAIL-B', 'SPUSE-C']
        result = extract_sp_designations(pages, sp_codes)

        # All three should be found
        assert len(result) == 3
        assert 'First mobile furniture' in result['SPMOB-A']
        assert 'Custom bench product' in result['SPPAIL-B']
        assert 'Special equipment item' in result['SPUSE-C']

    def test_empty_designation_when_code_not_found_in_pdf(self, references_dir):
        """If SP code is not found in PDF text, designation should be empty."""
        # This simulates the integration with analyze_devis
        # Create a synthetic case where code exists but designation doesn't
        pages = ["cover", "Some random text without the code"]
        sp_codes = ['SPMOB-NOTFOUND']

        result = extract_sp_designations(pages, sp_codes)

        # Code should not be in result if not found
        assert 'SPMOB-NOTFOUND' not in result
