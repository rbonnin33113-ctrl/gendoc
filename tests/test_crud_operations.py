"""
Unit tests for CRUD operations on product references.

These tests validate the create/update/delete operations on product data:
- md_writer: format_product_section, append_product_to_family, update_product_in_family, remove_product_from_family
- image_handler: copy_product_images, remove_product_images
- index_manager: ensure_family_infrastructure, refresh_index
- Integration: full lifecycle test (add -> lookup -> update -> delete)
"""

import pytest
from pathlib import Path

from gendoc.parsers.md_writer import (
    format_product_section, append_product_to_family,
    update_product_in_family, remove_product_from_family
)
from gendoc.parsers.md_parser import parse_family_md, find_product
from gendoc.parsers.image_handler import copy_product_images, remove_product_images
from gendoc.parsers.index_manager import ensure_family_infrastructure, refresh_index


@pytest.fixture
def sample_product():
    """Return a minimal valid product dict for testing."""
    return {
        'code': 'TEST-CRUD-001',
        'ref': 'Ref : TEST-CRUD-001',
        'titre': 'Produit de test CRUD',
        'famille': 'test-crud',
        'texte': 'Description de test pour operations CRUD',
        'dimensions': [],
        'images': [],
        'metadata_pptx': []
    }


class TestFormatProductSection:
    """Tests for format_product_section function."""

    def test_format_includes_header(self, sample_product):
        """Format output contains product code as header."""
        output = format_product_section(sample_product)
        assert '## TEST-CRUD-001' in output

    def test_format_includes_metadata_table(self, sample_product):
        """Format output contains metadata table with code and titre."""
        output = format_product_section(sample_product)
        assert '| code | TEST-CRUD-001 |' in output
        assert '| titre | Produit de test CRUD |' in output
        assert '| Champ | Valeur |' in output

    def test_format_with_dimensions(self, sample_product):
        """Product with dimension entry produces correct table row."""
        sample_product['dimensions'] = [
            {
                'name': 'Largeur',
                'valeur': '1200',
                'prefix': 'L',
                'shape_index': '15'
            }
        ]
        output = format_product_section(sample_product)
        assert '| Largeur | 1200 | L | 15 |' in output
        assert '### Dimensions' in output


class TestAppendProduct:
    """Tests for append_product_to_family function."""

    def test_append_creates_new_file(self, tmp_path, sample_product):
        """Append to non-existent path creates file with product code."""
        filepath = tmp_path / "test-crud.md"
        append_product_to_family(filepath, sample_product)

        assert filepath.exists()
        content = filepath.read_text(encoding='utf-8')
        assert '## TEST-CRUD-001' in content
        assert 'Total references: 1' in content

    def test_append_to_existing_file(self, tmp_path, sample_product):
        """Append second product to file, file contains both codes."""
        filepath = tmp_path / "test-crud.md"

        # Add first product
        append_product_to_family(filepath, sample_product)

        # Add second product
        product2 = sample_product.copy()
        product2['code'] = 'TEST-CRUD-002'
        product2['ref'] = 'Ref : TEST-CRUD-002'
        append_product_to_family(filepath, product2)

        content = filepath.read_text(encoding='utf-8')
        assert '## TEST-CRUD-001' in content
        assert '## TEST-CRUD-002' in content
        assert 'Total references: 2' in content

    def test_append_round_trip(self, tmp_path, sample_product):
        """Write product with append, read back with parse, verify fields match."""
        filepath = tmp_path / "test-crud.md"
        append_product_to_family(filepath, sample_product)

        products = parse_family_md(filepath)
        assert len(products) == 1
        product = products[0]

        assert product['code'] == sample_product['code']
        assert product['ref'] == sample_product['ref']
        assert product['titre'] == sample_product['titre']
        assert product['famille'] == sample_product['famille']
        assert product['texte'] == sample_product['texte']

    def test_append_with_dimensions_round_trip(self, tmp_path, sample_product):
        """Write product with dimensions, read back, verify dimensions list matches."""
        filepath = tmp_path / "test-crud.md"

        sample_product['dimensions'] = [
            {'name': 'Largeur', 'valeur': '1200', 'prefix': 'L', 'shape_index': '15'},
            {'name': 'Hauteur', 'valeur': '850', 'prefix': 'H', 'shape_index': '16'}
        ]
        append_product_to_family(filepath, sample_product)

        products = parse_family_md(filepath)
        assert len(products) == 1
        product = products[0]

        assert len(product['dimensions']) == 2
        assert product['dimensions'][0]['name'] == 'Largeur'
        assert product['dimensions'][0]['valeur'] == '1200'
        assert product['dimensions'][1]['name'] == 'Hauteur'


class TestUpdateProduct:
    """Tests for update_product_in_family function."""

    def test_update_titre(self, tmp_path, sample_product):
        """Create product, update titre, verify new titre persists."""
        filepath = tmp_path / "test-crud.md"
        append_product_to_family(filepath, sample_product)

        updated = update_product_in_family(filepath, 'TEST-CRUD-001', {'titre': 'Titre mis a jour'})
        assert updated['titre'] == 'Titre mis a jour'

        # Read back to verify persistence
        products = parse_family_md(filepath)
        assert products[0]['titre'] == 'Titre mis a jour'

    def test_update_partial_preserves_other_fields(self, tmp_path, sample_product):
        """Update only titre, verify texte and ref are unchanged."""
        filepath = tmp_path / "test-crud.md"
        append_product_to_family(filepath, sample_product)

        update_product_in_family(filepath, 'TEST-CRUD-001', {'titre': 'Nouveau titre'})

        products = parse_family_md(filepath)
        product = products[0]
        assert product['titre'] == 'Nouveau titre'
        assert product['texte'] == sample_product['texte']
        assert product['ref'] == sample_product['ref']

    def test_update_rejects_code_change(self, tmp_path, sample_product):
        """Updating 'code' raises ValueError."""
        filepath = tmp_path / "test-crud.md"
        append_product_to_family(filepath, sample_product)

        with pytest.raises(ValueError, match="Cannot update code or famille"):
            update_product_in_family(filepath, 'TEST-CRUD-001', {'code': 'NEW-CODE'})

    def test_update_nonexistent_code(self, tmp_path, sample_product):
        """Updating unknown code raises ValueError."""
        filepath = tmp_path / "test-crud.md"
        append_product_to_family(filepath, sample_product)

        with pytest.raises(ValueError, match="Code non trouve"):
            update_product_in_family(filepath, 'NONEXISTENT', {'titre': 'Test'})


class TestRemoveProduct:
    """Tests for remove_product_from_family function."""

    def test_remove_returns_product(self, tmp_path, sample_product):
        """Remove returns the removed product dict."""
        filepath = tmp_path / "test-crud.md"
        append_product_to_family(filepath, sample_product)

        removed = remove_product_from_family(filepath, 'TEST-CRUD-001')
        assert removed is not None
        assert removed['code'] == 'TEST-CRUD-001'

    def test_remove_updates_count(self, tmp_path, sample_product):
        """After removing one of two products, file contains 'Total references: 1'."""
        filepath = tmp_path / "test-crud.md"

        # Add two products
        append_product_to_family(filepath, sample_product)
        product2 = sample_product.copy()
        product2['code'] = 'TEST-CRUD-002'
        product2['ref'] = 'Ref : TEST-CRUD-002'
        append_product_to_family(filepath, product2)

        # Remove one
        remove_product_from_family(filepath, 'TEST-CRUD-001')

        content = filepath.read_text(encoding='utf-8')
        assert 'Total references: 1' in content
        assert '## TEST-CRUD-002' in content
        assert '## TEST-CRUD-001' not in content

    def test_remove_nonexistent_code(self, tmp_path, sample_product):
        """Removing unknown code raises ValueError."""
        filepath = tmp_path / "test-crud.md"
        append_product_to_family(filepath, sample_product)

        with pytest.raises(ValueError, match="Code non trouve"):
            remove_product_from_family(filepath, 'NONEXISTENT')


class TestImageHandler:
    """Tests for copy_product_images and remove_product_images functions."""

    def test_copy_creates_files(self, tmp_path):
        """Create temp source files, call copy_product_images, verify files exist in target dir."""
        # Create temp source files
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        source1 = source_dir / "image1.png"
        source2 = source_dir / "image2.jpg"
        source1.write_bytes(b'PNG fake data')
        source2.write_bytes(b'JPG fake data')

        # Create images directory structure
        images_dir = tmp_path / "images"
        images_dir.mkdir()

        # Copy images
        result = copy_product_images(
            [str(source1), str(source2)],
            'test-crud',
            images_dir
        )

        # Verify files were copied
        target_dir = images_dir / "test-crud"
        assert (target_dir / "image1.png").exists()
        assert (target_dir / "image2.jpg").exists()
        assert len(result) == 2

    def test_copy_returns_image_dicts(self, tmp_path):
        """Returned list has correct 'chemin' format."""
        # Create temp source file
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        source1 = source_dir / "test.png"
        source1.write_bytes(b'PNG data')

        images_dir = tmp_path / "images"
        images_dir.mkdir()

        # Copy image
        result = copy_product_images([str(source1)], 'test-crud', images_dir)

        assert len(result) == 1
        assert result[0]['chemin'] == 'Delagrave/images/test-crud/test.png'
        assert result[0]['chemin_original'] == str(source1)
        assert result[0]['left'] == 0.0
        assert result[0]['top'] == 0.0

    def test_copy_missing_source(self, tmp_path):
        """Non-existent source path produces entry with 'error' key."""
        images_dir = tmp_path / "images"
        images_dir.mkdir()

        result = copy_product_images(['/nonexistent/file.png'], 'test-crud', images_dir)

        assert len(result) == 1
        assert 'error' in result[0]
        assert 'non trouve' in result[0]['error'].lower()

    def test_remove_deletes_files(self, tmp_path):
        """Create files in images dir, call remove_product_images, verify files deleted."""
        # Create images directory and files
        images_dir = tmp_path / "images"
        family_dir = images_dir / "test-crud"
        family_dir.mkdir(parents=True)

        image1 = family_dir / "test1.png"
        image2 = family_dir / "test2.jpg"
        image1.write_bytes(b'PNG data')
        image2.write_bytes(b'JPG data')

        # Create product dict with images
        product = {
            'famille': 'test-crud',
            'images': [
                {'chemin': 'Delagrave/images/test-crud/test1.png'},
                {'chemin': 'Delagrave/images/test-crud/test2.jpg'}
            ]
        }

        # Remove images
        result = remove_product_images(product, images_dir)

        assert result['removed'] == 2
        assert not image1.exists()
        assert not image2.exists()


class TestIndexManager:
    """Tests for ensure_family_infrastructure and refresh_index functions."""

    def test_ensure_family_infrastructure_creates_dir(self, tmp_path):
        """Call with non-existent family, verify images directory created."""
        references_dir = tmp_path / "references"
        references_dir.mkdir()

        result = ensure_family_infrastructure("new-family", references_dir)

        images_dir = tmp_path / "images" / "new-family"
        assert images_dir.exists()
        assert result['images_dir_created'] is True
        assert result['famille'] == 'new-family'

    def test_refresh_index_writes_file(self, tmp_path, sample_product):
        """Create temp references dir with test family MD file, call refresh_index, verify _index.md."""
        references_dir = tmp_path / "references"
        references_dir.mkdir()

        # Create a test family file
        family_file = references_dir / "test-crud.md"
        append_product_to_family(family_file, sample_product)

        # Add second product to have count of 2
        product2 = sample_product.copy()
        product2['code'] = 'TEST-CRUD-002'
        product2['ref'] = 'Ref : TEST-CRUD-002'
        append_product_to_family(family_file, product2)

        # Refresh index
        result = refresh_index(references_dir)

        # Verify _index.md exists and contains correct data
        index_file = references_dir / "_index.md"
        assert index_file.exists()

        content = index_file.read_text(encoding='utf-8')
        assert 'test-crud.md' in content
        assert result['total'] == 2
        assert result['families'] == 1
        assert result['families_detail']['test-crud'] == 2


class TestCRUDIntegration:
    """Integration test for full CRUD lifecycle."""

    def test_full_lifecycle_add_lookup_update_delete(self, tmp_path):
        """
        Validate complete CRUD lifecycle using temporary references directory.

        Steps:
        1. Setup temp directory structure
        2. ADD: Use append_product_to_family
        3. LOOKUP: Use find_product, verify product found
        4. ENSURE INFRASTRUCTURE: Call ensure_family_infrastructure
        5. UPDATE: Use update_product_in_family, verify updated
        6. IMAGE COPY: Create temp PNG, copy it, verify file exists
        7. DELETE: Use remove_product_from_family
        8. VERIFY DELETED: find_product returns None
        """
        # Setup directory structure
        references_dir = tmp_path / "references"
        references_dir.mkdir()
        images_dir = tmp_path / "images"
        images_dir.mkdir()

        # Create minimal _parametrage.md for md_parser compatibility
        parametrage = references_dir / "_parametrage.md"
        parametrage.write_text("# Parametrage\n", encoding='utf-8')

        # === ADD ===
        product = {
            'code': 'INTEG-TEST-001',
            'ref': 'Ref : INTEG-TEST-001 2026-1',
            'titre': 'Integration Test Product',
            'famille': 'test-integ',
            'texte': 'Description for integration test',
            'dimensions': [],
            'images': [],
            'metadata_pptx': []
        }

        family_file = references_dir / "test-integ.md"
        append_product_to_family(family_file, product)

        # Verify file was created
        assert family_file.exists()

        # === LOOKUP ===
        found_product = find_product("INTEG-TEST-001", references_dir)
        assert found_product is not None
        assert found_product['titre'] == 'Integration Test Product'
        assert found_product['famille'] == 'test-integ'
        assert found_product['code'] == 'INTEG-TEST-001'

        # === ENSURE INFRASTRUCTURE ===
        infra_result = ensure_family_infrastructure("test-integ", references_dir)
        assert infra_result['famille'] == 'test-integ'
        assert (images_dir / "test-integ").exists()

        # === UPDATE ===
        updated = update_product_in_family(
            family_file,
            'INTEG-TEST-001',
            {'titre': 'Integration Test Product Updated'}
        )
        assert updated['titre'] == 'Integration Test Product Updated'

        # Verify update persisted
        found_after_update = find_product("INTEG-TEST-001", references_dir)
        assert found_after_update['titre'] == 'Integration Test Product Updated'

        # === IMAGE COPY ===
        # Create a temp PNG file
        temp_image_dir = tmp_path / "temp_images"
        temp_image_dir.mkdir()
        temp_image = temp_image_dir / "test-integration.png"
        temp_image.write_bytes(b'\x89PNG\r\n\x1a\n' + b'fake PNG data')

        # Copy image
        image_results = copy_product_images([str(temp_image)], 'test-integ', images_dir)
        assert len(image_results) == 1
        assert 'error' not in image_results[0]
        assert (images_dir / "test-integ" / "test-integration.png").exists()

        # === DELETE ===
        removed = remove_product_from_family(family_file, 'INTEG-TEST-001')
        assert removed['code'] == 'INTEG-TEST-001'
        assert removed['titre'] == 'Integration Test Product Updated'

        # === VERIFY DELETED ===
        found_after_delete = find_product("INTEG-TEST-001", references_dir)
        assert found_after_delete is None

        # Verify file still exists but is empty (or has only header)
        assert family_file.exists()
        content = family_file.read_text(encoding='utf-8')
        assert '## INTEG-TEST-001' not in content
        assert 'Total references: 0' in content
