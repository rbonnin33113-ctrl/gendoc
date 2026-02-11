"""Tests for error handling and warnings propagation in the generation pipeline."""
import pytest
from pathlib import Path

from gendoc.generators.pptx_generator import generate_presentation
from gendoc.generators.modern_template import build_product_slide
from gendoc.parsers.md_parser import find_product


class TestWarningsPropagation:
    """Test that warnings key exists and propagates through the pipeline."""

    def test_generate_presentation_returns_warnings_key(
        self, project_root, references_dir, template_path, tmp_path
    ):
        """generate_presentation result always contains 'warnings' key."""
        output = tmp_path / "test_warnings.pptx"
        result = generate_presentation(
            product_codes=["PM-D-H-75"],
            output_path=output,
            references_dir=references_dir,
            template_path=template_path,
            project_root=project_root
        )
        assert "warnings" in result
        assert isinstance(result["warnings"], list)

    def test_generate_presentation_unknown_code_in_skipped(
        self, project_root, references_dir, template_path, tmp_path
    ):
        """Unknown product codes end up in 'skipped' list, not crash."""
        output = tmp_path / "test_skipped.pptx"
        result = generate_presentation(
            product_codes=["FAKECODE999"],
            output_path=output,
            references_dir=references_dir,
            template_path=template_path,
            project_root=project_root
        )
        assert any(s["code"] == "FAKECODE999" for s in result["skipped"])

    def test_pipeline_continues_after_unknown_code(
        self, project_root, references_dir, template_path, tmp_path
    ):
        """Pipeline generates valid slides AND records skipped, does not halt."""
        output = tmp_path / "test_continue.pptx"
        result = generate_presentation(
            product_codes=["PM-D-H-75", "FAKECODE999"],
            output_path=output,
            references_dir=references_dir,
            template_path=template_path,
            project_root=project_root
        )
        assert result["slides_generated"] >= 1
        assert len(result["skipped"]) >= 1
        assert output.exists()


class TestBuildProductSlideReturns:
    """Test that build_product_slide returns warnings list."""

    def test_build_product_slide_returns_list(
        self, project_root, references_dir, template_path
    ):
        """build_product_slide returns a list (even if empty for valid products)."""
        from gendoc.generators.pptx_generator import load_template, _strip_template_shapes
        prs = load_template(template_path)
        _strip_template_shapes(prs)

        product = find_product("PM-D-H-75", references_dir)
        assert product is not None

        logo_path = project_root / "Delagrave" / "images" / "logo_delagrave_emsm.png"
        result = build_product_slide(prs, product, "paillasse", project_root, logo_path)
        assert isinstance(result, list)

    def test_build_product_slide_catches_unexpected_error(
        self, project_root, references_dir, template_path
    ):
        """build_product_slide does not crash on bad product data, returns warning."""
        from gendoc.generators.pptx_generator import load_template, _strip_template_shapes
        prs = load_template(template_path)
        _strip_template_shapes(prs)

        # Pass a deliberately malformed product (missing expected keys)
        bad_product = {"code": "BADTEST", "titre": None, "images": "not-a-list"}
        logo_path = project_root / "Delagrave" / "images" / "logo_delagrave_emsm.png"
        result = build_product_slide(prs, bad_product, "paillasse", project_root, logo_path)
        assert isinstance(result, list)
        # Should have caught the error and returned a warning string
        assert len(result) >= 1
        assert "Erreur inattendue" in result[0]
