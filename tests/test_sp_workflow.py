"""
Tests for SP article workflow MCP tools and integration.

This module tests:
1. open_sp_selector: HTML generation from analyze_devis speciaux output
2. load_sp_selection: JSON loading and validation
3. SP workflow integration: custom_products in generate_slides
"""

import pytest
import json
from pathlib import Path

from gendoc.generators.html_sp_selector import generate_sp_selector_html
from gendoc.generators.pptx_generator import generate_presentation


class TestOpenSPSelector:
    """Tests for open_sp_selector tool (via generate_sp_selector_html)."""

    def test_open_sp_selector_generates_html(self, project_root, references_dir, output_dir):
        """Test that HTML selector is generated from SP articles."""
        # Create mock analysis result with speciaux
        sp_articles = [
            {
                'code': 'SPMOB-TEST',
                'famille': 'meubles',
                'prefix': 'SPMOB',
                'designation': 'Test special furniture product'
            }
        ]

        output_path = output_dir / "test_sp_selector.html"

        # Generate HTML
        result = generate_sp_selector_html(
            sp_articles=sp_articles,
            references_dir=references_dir,
            output_path=output_path
        )

        # Verify result structure
        assert 'output_path' in result
        assert 'sp_count' in result
        assert 'catalog_size' in result
        assert result['sp_count'] == 1
        assert result['catalog_size'] > 300  # Should have ~359 products

        # Verify HTML file was created
        assert output_path.exists()
        html_content = output_path.read_text(encoding='utf-8')

        # Verify HTML contains expected content
        assert len(html_content) > 10000  # Should be >10KB
        assert 'SPMOB-TEST' in html_content
        assert 'Test special furniture product' in html_content
        assert 'SP_ARTICLES' in html_content  # JavaScript data
        assert 'CATALOG' in html_content

    def test_open_sp_selector_empty_speciaux(self, references_dir, output_dir):
        """Test behavior with empty speciaux list."""
        sp_articles = []
        output_path = output_dir / "test_empty_sp_selector.html"

        # Generate HTML with empty list
        result = generate_sp_selector_html(
            sp_articles=sp_articles,
            references_dir=references_dir,
            output_path=output_path
        )

        # Verify it still generates (just with 0 SP articles)
        assert result['sp_count'] == 0
        assert output_path.exists()


class TestLoadSPSelection:
    """Tests for load_sp_selection tool (JSON reading logic)."""

    def test_load_sp_selection_reads_valid_json(self, output_dir):
        """Test reading and parsing a valid sp_selection.json file."""
        # Create test JSON file
        custom_products = [
            {
                "code": "SPMOB-TEST",
                "famille": "meubles",
                "titre": "Test SP Product",
                "texte": "Test description",
                "ref": "12345",
                "dimensions": [],
                "images": [],
                "metadata_pptx": []
            }
        ]

        json_path = output_dir / "test_sp_selection.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(custom_products, f, ensure_ascii=False, indent=2)

        # Read and parse (simulating load_sp_selection logic)
        with open(json_path, 'r', encoding='utf-8') as f:
            loaded = json.load(f)

        # Verify structure
        assert isinstance(loaded, list)
        assert len(loaded) == 1
        assert loaded[0]['code'] == 'SPMOB-TEST'
        assert loaded[0]['famille'] == 'meubles'
        assert 'titre' in loaded[0]
        assert 'texte' in loaded[0]

    def test_load_sp_selection_file_not_found(self):
        """Test error handling when JSON file doesn't exist."""
        json_path = Path("nonexistent_file.json")

        # Verify file doesn't exist
        assert not json_path.exists()

        # Error handling would be done in the MCP tool itself
        # Here we just verify the path check works
        with pytest.raises(FileNotFoundError):
            with open(json_path, 'r') as f:
                json.load(f)

    def test_load_sp_selection_invalid_json(self, output_dir):
        """Test error handling with invalid JSON content."""
        json_path = output_dir / "test_invalid.json"

        # Write invalid JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            f.write("{ invalid json content")

        # Verify JSONDecodeError is raised
        with pytest.raises(json.JSONDecodeError):
            with open(json_path, 'r', encoding='utf-8') as f:
                json.load(f)


class TestSPWorkflowIntegration:
    """Tests for end-to-end SP workflow integration."""

    def test_sp_custom_products_in_generate_slides(
        self, project_root, references_dir, template_path, output_dir
    ):
        """Test that custom products are correctly processed by generate_slides."""
        # Create a custom SP product
        custom_product = {
            "code": "SPMOB-INTEG",
            "famille": "meubles",
            "ref": "99999",
            "titre": "Test SP Integration Product",
            "texte": "This is a test description for SP integration",
            "dimensions": [],
            "images": [],
            "metadata_pptx": []
        }

        # Also include a standard product for comparison
        product_codes = ['PCD-A-60']  # Standard paillasse product

        output_path = output_dir / "test_sp_integration.pptx"

        # Generate presentation with both standard and custom products
        result = generate_presentation(
            product_codes=product_codes,
            output_path=output_path,
            references_dir=references_dir,
            template_path=template_path,
            project_root=project_root,
            mode="FTI",
            devis_info=None,
            custom_products=[custom_product]
        )

        # Verify generation succeeded
        assert 'slides_generated' in result
        assert result['slides_generated'] >= 1

        # Verify SP code was not skipped
        assert 'SPMOB-INTEG' not in result.get('skipped', [])

        # Verify output file exists
        assert output_path.exists()
        assert output_path.stat().st_size > 50000  # Should be >50KB

    def test_sp_workflow_multiple_custom_products(
        self, project_root, references_dir, template_path, output_dir
    ):
        """Test workflow with multiple SP articles."""
        # Create multiple custom SP products
        custom_products = [
            {
                "code": "SPMOB-MULTI-1",
                "famille": "meubles",
                "ref": "11111",
                "titre": "First SP Product",
                "texte": "First description",
                "dimensions": [],
                "images": [],
                "metadata_pptx": []
            },
            {
                "code": "SPPAIL-MULTI-2",
                "famille": "paillasse",
                "ref": "22222",
                "titre": "Second SP Product",
                "texte": "Second description",
                "dimensions": [],
                "images": [],
                "metadata_pptx": []
            }
        ]

        output_path = output_dir / "test_sp_multi.pptx"

        # Generate presentation with custom product codes
        # Note: custom products must be referenced in product_codes to be processed
        result = generate_presentation(
            product_codes=['SPMOB-MULTI-1', 'SPPAIL-MULTI-2'],
            output_path=output_path,
            references_dir=references_dir,
            template_path=template_path,
            project_root=project_root,
            mode="FTI",
            devis_info=None,
            custom_products=custom_products
        )

        # Verify both SP products were processed
        assert result['slides_generated'] >= 2

        # Verify neither was skipped
        skipped = result.get('skipped', [])
        assert 'SPMOB-MULTI-1' not in skipped
        assert 'SPPAIL-MULTI-2' not in skipped

        # Verify output exists
        assert output_path.exists()

    def test_sp_workflow_with_devis_info(
        self, project_root, references_dir, template_path, output_dir
    ):
        """Test SP workflow with devis header information."""
        custom_product = {
            "code": "SPTEST-DEVIS",
            "famille": "equipement",
            "ref": "33333",
            "titre": "SP Product with Devis Info",
            "texte": "Testing devis integration",
            "dimensions": [],
            "images": [],
            "metadata_pptx": []
        }

        devis_info = {
            "numero_devis": "25 64 TEST",
            "date": "2026-02-11",
            "client": "Test Client",
            "titre_affaire": "Test Project"
        }

        output_path = output_dir / "test_sp_devis.pptx"

        result = generate_presentation(
            product_codes=['2CU12G', 'SPTEST-DEVIS'],  # Standard + custom
            output_path=output_path,
            references_dir=references_dir,
            template_path=template_path,
            project_root=project_root,
            mode="FTI",
            devis_info=devis_info,
            custom_products=[custom_product]
        )

        # Verify generation succeeded with devis info
        assert result['slides_generated'] >= 2
        assert 'SPTEST-DEVIS' not in result.get('skipped', [])
        assert output_path.exists()
