"""
MCP server for gendoc - exposes all gendoc tools via Model Context Protocol.

This server provides Claude Code with direct access to:
- Reference lookup and search
- Devis PDF analysis (extract references, families, coatings)
- PowerPoint generation (fully functional)
- Reference management (stub - future)
"""

from pathlib import Path
import json
from fastmcp import FastMCP

from gendoc.parsers.md_parser import (
    find_product,
    get_all_families,
    search_products,
    find_products_by_family
)
from gendoc.parsers.devis_analyzer import analyze_devis as run_analyze_devis
from gendoc.generators.pptx_generator import generate_presentation as run_generate_presentation

# Resolve references directory relative to project root
# This ensures the path works regardless of where the MCP server is started from
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
REFERENCES_DIR = PROJECT_ROOT / "Delagrave" / "references"
TEMPLATE_PATH = PROJECT_ROOT / "Delagrave" / "Modele fiches - Powerpoint" / "Modèle fiche technique vide - Ind J.potm"

# Create FastMCP server instance
mcp = FastMCP("gendoc", instructions="Delagrave product reference and documentation generation tools")


@mcp.tool()
async def lookup_reference(code: str) -> str:
    """
    Look up a product by its code and return full product data.

    Args:
        code: Product code (e.g., "PM-D-H-75")

    Returns:
        JSON string with product data (code, ref, titre, famille, texte, dimensions, images, metadata)
        or a not found message.

    Example:
        lookup_reference("PM-D-H-75") -> full product JSON
    """
    product = find_product(code, REFERENCES_DIR)

    if product:
        return json.dumps(product, ensure_ascii=False, indent=2)
    else:
        return f"Product not found: {code}"


@mcp.tool()
async def list_families() -> str:
    """
    List all product families with their product counts.

    Returns:
        JSON string with family names, counts, and total.

    Example:
        list_families() -> {"paillasse": 54, "hotte": 38, ..., "total": 359}
    """
    families = get_all_families(REFERENCES_DIR)

    # Add total count
    result = dict(families)
    result["total"] = sum(families.values())

    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def search_references(query: str) -> str:
    """
    Search for products by partial code or title match.

    Args:
        query: Search query (case-insensitive, matches code or title)

    Returns:
        JSON string with list of matching products (limited to code, ref, titre, famille for conciseness).
        Limited to first 50 results.

    Example:
        search_references("PM-D") -> [{"code": "PM-D-H-75", "ref": "...", ...}, ...]
    """
    products = search_products(query, REFERENCES_DIR)

    # Limit to first 50 results and return only key fields for conciseness
    limited_products = [
        {
            "code": p["code"],
            "ref": p["ref"],
            "titre": p["titre"],
            "famille": p["famille"]
        }
        for p in products[:50]
    ]

    return json.dumps(limited_products, ensure_ascii=False, indent=2)


@mcp.tool()
async def analyze_devis(pdf_path: str) -> str:
    """
    Analyze a devis PDF and extract product references with families and coatings.

    Args:
        pdf_path: Path to the devis PDF file

    Returns:
        JSON string with analysis results: header, references, revetements, forfaits, inconnus.
    """
    path = Path(pdf_path)

    # Resolve relative paths from project root
    if not path.is_absolute():
        path = Path(__file__).resolve().parent.parent.parent.parent / path

    if not path.exists():
        return json.dumps({"error": f"Fichier PDF non trouve: {pdf_path}"}, ensure_ascii=False)

    try:
        result = run_analyze_devis(path, REFERENCES_DIR)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except ValueError as e:
        return json.dumps({"error": f"Erreur de lecture du PDF: {str(e)}"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"Erreur inattendue: {str(e)}"}, ensure_ascii=False)


@mcp.tool()
async def preview_generation(analysis_result: dict) -> str:
    """
    Build a structured preview of what PowerPoint generation would produce.

    Takes the output of analyze_devis and returns a detailed preview with:
    - Product references grouped by family with titles
    - Coatings that will be auto-generated
    - Unknown codes that will be skipped
    - Estimated page count

    Args:
        analysis_result: Dictionary from analyze_devis (header, references, revetements, forfaits, inconnus)

    Returns:
        JSON string with preview data: families (with products), revetements, inconnus, estimated_pages, suggested_filename
    """
    try:
        from gendoc.generators.document_assembler import FAMILY_ORDER, FAMILY_DISPLAY_NAMES

        references = analysis_result.get("references", [])
        header = analysis_result.get("header", {})

        # Classify each reference by family
        family_products = {f: [] for f in FAMILY_ORDER}

        for ref in references:
            code = ref.get("code", "")
            product = find_product(code, REFERENCES_DIR)

            # Try base code if not found (coating suffix)
            if not product and "-" in code:
                base_code = "-".join(code.split("-")[:-1])
                product = find_product(base_code, REFERENCES_DIR)

            if product:
                family = product.get("famille", "").lower()
                titre = product.get("titre", "")
                family_products.setdefault(family, []).append({
                    "code": code,
                    "titre": titre,
                    "revetement": ref.get("revetement", "")
                })

        # Build ordered families list
        families = []
        total_products = 0
        for family in FAMILY_ORDER:
            products = family_products.get(family, [])
            if products:
                families.append({
                    "name": family,
                    "display_name": FAMILY_DISPLAY_NAMES.get(family, family.title()),
                    "products": products
                })
                total_products += len(products)

        # Estimate pages: cover + TOC + (1 separator + N products) per family + revetements
        revetements = analysis_result.get("revetements", [])
        estimated_pages = 2  # cover + TOC
        for fam in families:
            estimated_pages += 1 + len(fam["products"])  # separator + products
        estimated_pages += len(revetements)

        # Suggested filename
        numero_devis = header.get("numero_devis", "")
        if numero_devis:
            safe_numero = numero_devis.replace(" ", "").replace("/", "-")
            suggested_filename = f"fiches_{safe_numero}.pptx"
        else:
            suggested_filename = "fiches_techniques.pptx"

        result = {
            "header": header,
            "families": families,
            "revetements": revetements,
            "forfaits": analysis_result.get("forfaits", []),
            "inconnus": analysis_result.get("inconnus", []),
            "total_products": total_products,
            "estimated_pages": estimated_pages,
            "suggested_filename": suggested_filename
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Erreur de previsualisation: {str(e)}"}, ensure_ascii=False)


@mcp.tool()
async def generate_slides(product_codes: list[str], output_path: str, mode: str = "FTI", devis_info: dict = None, custom_products: str = "[]") -> str:
    """
    Generate a PowerPoint presentation with product slides.

    Args:
        product_codes: List of product codes to include
        output_path: Path for the output PowerPoint file
        mode: Slide generation mode ("FTI" or other - default "FTI")
        devis_info: Optional dict with devis header info: 'numero_devis', 'date', 'client', 'titre_affaire'
        custom_products: JSON string of custom product dicts (for SP articles)

    Returns:
        JSON string with generation results: slides_generated, total_pages, revetements_added, skipped, output_path.

    Example:
        generate_slides(["PM-D-H-75", "PA-D-60"], "output.pptx") -> {"slides_generated": 2, "total_pages": 5, ...}
        generate_slides(["PM-D-H-75"], "output.pptx", devis_info={"numero_devis": "25 64 0637", "client": "TEST"})
    """
    try:
        # Resolve output path - if relative, make absolute from project root
        output = Path(output_path)
        if not output.is_absolute():
            output = PROJECT_ROOT / output

        # Create output directory if it doesn't exist
        output.parent.mkdir(parents=True, exist_ok=True)

        # Validate template exists
        if not TEMPLATE_PATH.exists():
            return json.dumps({"error": f"Template PowerPoint non trouve: {TEMPLATE_PATH}"}, ensure_ascii=False)

        # Parse custom_products JSON
        try:
            custom_products_list = json.loads(custom_products)
        except json.JSONDecodeError:
            custom_products_list = []

        # Call the generator
        result = run_generate_presentation(
            product_codes=product_codes,
            output_path=output,
            references_dir=REFERENCES_DIR,
            template_path=TEMPLATE_PATH,
            project_root=PROJECT_ROOT,
            mode=mode,
            devis_info=devis_info,
            custom_products=custom_products_list
        )

        # Add output path to result
        result['output_path'] = str(output)
        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Erreur de generation: {str(e)}"}, ensure_ascii=False)


@mcp.tool()
async def create_custom_product(
    base_code: str,
    custom_code: str,
    overrides: str = "{}"
) -> str:
    """
    Create a custom product by cloning a base product and applying overrides.
    Used for special articles (SP-prefixed codes) not in the catalog.

    Args:
        base_code: Code of the standard product to use as template (e.g., "PM-D-H-75")
        custom_code: The special article code (e.g., "SPPAIL-12345")
        overrides: JSON string with fields to override. All fields are modifiable:
                   titre, texte, ref, dimensions, images, metadata_pptx.
                   Example: {"titre": "Custom title", "texte": "Custom description"}

    Returns:
        JSON string with the complete custom product data ready for generate_slides.
    """
    import copy

    # Look up base product
    base_product = find_product(base_code, REFERENCES_DIR)

    if not base_product:
        return json.dumps({
            "error": f"Base product not found: {base_code}"
        }, ensure_ascii=False)

    # Deep copy the base product
    custom_product = copy.deepcopy(base_product)

    # Replace code with custom code
    custom_product['code'] = custom_code

    # Parse overrides JSON
    try:
        overrides_dict = json.loads(overrides)
    except json.JSONDecodeError as e:
        return json.dumps({
            "error": f"Invalid JSON in overrides: {str(e)}"
        }, ensure_ascii=False)

    # Apply overrides
    for key, value in overrides_dict.items():
        if key in custom_product:
            # For complex fields (lists/dicts), replace entirely or merge
            if isinstance(custom_product[key], dict) and isinstance(value, dict):
                # Merge dicts
                custom_product[key].update(value)
            else:
                # Replace directly
                custom_product[key] = value
        else:
            # Add new field
            custom_product[key] = value

    return json.dumps(custom_product, ensure_ascii=False, indent=2)


@mcp.tool()
async def add_reference(family: str, code: str, ref: str, titre: str, texte: str = "") -> str:
    """
    Add a new product reference to a family.

    Args:
        family: Family name (e.g., "paillasse")
        code: Product code
        ref: Reference string
        titre: Product title
        texte: Descriptive text (optional)

    Returns:
        Stub acknowledgement message (full implementation in Phase 3).

    Example:
        add_reference("paillasse", "PM-TEST", "123456", "Test product") -> "Add reference tool registered..."
    """
    return f"Add reference tool registered. Full implementation in Phase 3. Would add {code} to {family}"


def main():
    """Main entry point for the MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
