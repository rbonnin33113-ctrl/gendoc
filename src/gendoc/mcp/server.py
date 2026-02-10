"""
MCP server for gendoc - exposes all gendoc tools via Model Context Protocol.

This server provides Claude Code with direct access to:
- Reference lookup and search
- Devis PDF analysis (extract references, families, coatings)
- PowerPoint generation (stub - Phase 4)
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

# Resolve references directory relative to project root
# This ensures the path works regardless of where the MCP server is started from
REFERENCES_DIR = Path(__file__).resolve().parent.parent.parent.parent / "Delagrave" / "references"

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
async def generate_slides(product_codes: list[str], output_path: str, mode: str = "FTI") -> str:
    """
    Generate a PowerPoint presentation with product slides.

    Args:
        product_codes: List of product codes to include
        output_path: Path for the output PowerPoint file
        mode: Slide generation mode ("FTI" or other - default "FTI")

    Returns:
        Stub acknowledgement message (full implementation in Phase 4).

    Example:
        generate_slides(["PM-D-H-75", "PA-D-60"], "output.pptx") -> "Generate slides tool registered..."
    """
    return f"Generate slides tool registered. Full implementation in Phase 4. Received {len(product_codes)} codes, output: {output_path}, mode: {mode}"


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
