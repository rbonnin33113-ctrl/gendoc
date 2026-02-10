"""
Unit tests for md_parser core functions.

These tests validate the data access layer that reads structured Markdown
files containing product references. Tests cover:
- Product lookup by code
- Family listing and counts
- Product search
- MD file parsing
"""

import pytest
from pathlib import Path

from gendoc.parsers.md_parser import (
    find_product,
    find_product_pages,
    get_all_families,
    search_products,
    parse_family_md,
    get_all_family_files,
    find_products_by_family
)


class TestFindProduct:
    """Tests for find_product lookup function."""

    def test_find_existing_product(self, references_dir):
        """Known product code returns product dict."""
        product = find_product("PM-D-H-75", references_dir)
        assert product is not None
        assert product['code'] == 'PM-D-H-75'
        assert 'titre' in product
        assert 'ref' in product

    def test_find_product_case_insensitive(self, references_dir):
        """Lookup is case-insensitive."""
        product_upper = find_product("PM-D-H-75", references_dir)
        product_lower = find_product("pm-d-h-75", references_dir)
        assert product_upper is not None
        assert product_lower is not None
        assert product_upper['code'] == product_lower['code']

    def test_find_nonexistent_product(self, references_dir):
        """Unknown code returns None."""
        product = find_product("NONEXISTENT-CODE-999", references_dir)
        assert product is None

    def test_find_product_has_required_fields(self, references_dir):
        """Product dict has all expected fields."""
        product = find_product("S-A", references_dir)
        assert product is not None
        required_fields = ['code', 'ref', 'titre', 'famille', 'texte', 'dimensions', 'images', 'metadata_pptx']
        for field in required_fields:
            assert field in product, f"Missing field: {field}"


class TestGetAllFamilies:
    """Tests for get_all_families function."""

    def test_returns_all_families(self, references_dir):
        """Returns dict with all expected family names."""
        families = get_all_families(references_dir)
        expected = ['paillasse', 'sorbonne', 'revetement', 'meubles', 'tables-en', 'equipement', 'elec-sorb', 'complements']
        for fam in expected:
            assert fam in families, f"Family {fam} not found in families dict"

    def test_family_counts_positive(self, references_dir):
        """Each family has at least 1 product."""
        families = get_all_families(references_dir)
        for name, count in families.items():
            if name != 'fiches-existantes':
                assert count > 0, f"Family {name} has 0 products"

    def test_total_count_matches_expected(self, references_dir):
        """Total product count should be approximately 359 (known from Phase 1)."""
        families = get_all_families(references_dir)
        total = sum(families.values())
        # Allow some tolerance for fiches-existantes or minor changes
        assert total >= 300, f"Expected ~359 total products, got {total}"


class TestSearchProducts:
    """Tests for search_products function."""

    def test_search_by_code_prefix(self, references_dir):
        """Search by code prefix returns matching products."""
        results = search_products("PM-D", references_dir)
        assert len(results) > 0
        for r in results:
            assert "PM-D" in r['code'].upper() or "pm-d" in r['titre'].lower()

    def test_search_empty_query(self, references_dir):
        """Empty-ish search returns many results."""
        results = search_products("a", references_dir)
        assert len(results) > 0

    def test_search_no_results(self, references_dir):
        """Nonsense query returns empty list."""
        results = search_products("ZZZZNONEXISTENT999", references_dir)
        assert len(results) == 0


class TestParseFamilyMd:
    """Tests for parse_family_md function."""

    def test_parse_paillasse(self, references_dir):
        """Paillasse MD parses to expected product count."""
        products = parse_family_md(references_dir / "paillasse.md")
        assert len(products) == 54, f"Expected 54 paillasse products, got {len(products)}"

    def test_parse_nonexistent_file(self):
        """Nonexistent file returns empty list."""
        products = parse_family_md(Path("nonexistent.md"))
        assert products == []

    def test_parsed_product_has_dimensions(self, references_dir):
        """Products with dimensions have them parsed correctly."""
        products = parse_family_md(references_dir / "paillasse.md")
        # PCD-A-60 should have dimensions
        pcd = next((p for p in products if p['code'] == 'PCD-A-60'), None)
        assert pcd is not None
        assert len(pcd['dimensions']) > 0, "PCD-A-60 should have dimensions"
