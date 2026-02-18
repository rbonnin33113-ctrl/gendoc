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
import importlib
import os
import sys
import time
import traceback
from datetime import datetime
from fastmcp import FastMCP

from gendoc.parsers.md_parser import (
    find_product,
    get_all_families,
    search_products,
    find_products_by_family
)
from gendoc.parsers.md_writer import append_product_to_family, update_product_in_family, remove_product_from_family
from gendoc.parsers.index_manager import ensure_family_infrastructure, refresh_index
from gendoc.parsers.image_handler import copy_product_images, remove_product_images
from gendoc.parsers.devis_analyzer import analyze_devis as run_analyze_devis
from gendoc.generators.html_sp_selector import generate_sp_selector_html
from gendoc.utils.sp_server import start_sp_server
from gendoc.utils.pipeline_logger import PipelineLogger
from gendoc.utils.auto_updater import run_update

# Module mtime tracking for hot-reload mechanism
_module_mtimes: dict[str, float] = {}

# Pipeline logger tracking
_current_logger: PipelineLogger | None = None


def _reload_generators():
    """Hot-reload generator modules so code changes take effect without restarting the MCP server.

    Uses file modification time (mtime) tracking to avoid unnecessary reloads.
    Only reloads modules that have changed since last call.
    Logs reloaded modules with timestamps.

    Returns:
        The generate_presentation function from the (potentially refreshed) pptx_generator module.
    """
    import gendoc.generators.modern_template as mt
    import gendoc.generators.document_assembler as da
    import gendoc.generators.pptx_generator as pg

    # List of modules to check, in reload order (dependencies first)
    modules = [
        (mt, "modern_template"),
        (da, "document_assembler"),
        (pg, "pptx_generator")
    ]

    for module, module_name in modules:
        # Get the module's file path
        module_path = module.__file__
        if module_path is None:
            continue

        # Get current modification time
        try:
            current_mtime = os.path.getmtime(module_path)
        except OSError:
            continue

        # Check if module has changed (or first time)
        if module_path not in _module_mtimes or _module_mtimes[module_path] != current_mtime:
            # Reload the module
            importlib.reload(module)

            # Update stored mtime
            _module_mtimes[module_path] = current_mtime

            # Log the reload with timestamp (to log file, not console)
            timestamp = datetime.now().isoformat(timespec='seconds')
            if _current_logger:
                _current_logger.log_solution(
                    f"Hot-reload {module_name}",
                    f"Module {module_name} recharge ({timestamp})",
                    auto_resolved=True
                )
            # No print() -- hot-reload info is not user-facing

    return pg.generate_presentation


def _reload_assembler_constants():
    """Reload generators and return fresh FAMILY_ORDER and FAMILY_DISPLAY_NAMES.

    Ensures preview_generation picks up changes to family ordering and display names
    without server restart.

    Returns:
        Tuple of (FAMILY_ORDER, FAMILY_DISPLAY_NAMES) from the reloaded document_assembler.
    """
    _reload_generators()

    import gendoc.generators.document_assembler as da
    return (da.FAMILY_ORDER, da.FAMILY_DISPLAY_NAMES)

# Load configuration and resolve all resource paths
try:
    from gendoc.utils.config_loader import load_config, ConfigurationError
    _config = load_config()
    REFERENCES_DIR = _config["references_dir"]
    IMAGES_DIR = _config["images_dir"]
    TEMPLATE_PATH = _config["template_path"]
    # OUTPUT_DIR will be refactored in Phase 23 (per-devis subdirectories)
    # For now, keep it as local ./output for backward compatibility
    OUTPUT_DIR = Path("output").resolve()
except ConfigurationError as e:
    # MCP server cannot start without valid config
    print(f"[FATAL] Configuration error: {e}", file=sys.stderr)
    print("[FATAL] MCP server will not start. Please create gendoc.json.", file=sys.stderr)
    sys.exit(1)

# Image paths in MD files start with "Delagrave/images/..." so the root for
# resolving them is the parent of network_share_path (which points to Delagrave/)
_PROJECT_ROOT = _config["network_share_path"].parent

# Version check at startup -- silent, never blocks server start
_pending_update_notice: str | None = None
try:
    from gendoc.utils.version_checker import check_for_update, _format_update_message
    _update_info = check_for_update(
        github_repo=_config.get("github_repo", ""),
        github_token=_config.get("github_token", "") or None,
    )
    if _update_info is not None and _update_info.get("needs_update"):
        _v_local = _update_info.get("local_version", "?")
        _v_remote = _update_info.get("remote_version", "?")
        _pending_update_notice = (
            f"IMPORTANT: Une mise a jour gendoc est disponible (v{_v_local} -> v{_v_remote}). "
            f"Demandez a l'utilisateur s'il souhaite mettre a jour maintenant "
            f"en appelant l'outil update_gendoc. Apres la mise a jour, Claude doit etre redemarre."
        )
except Exception:
    pass  # Version check must never prevent MCP server startup


def _inject_update_notice(json_str: str) -> str:
    """Prepend pending update notice as plain text before JSON (once per session)."""
    global _pending_update_notice
    if _pending_update_notice:
        notice = _pending_update_notice
        _pending_update_notice = None
        return f"{notice}\n\n{json_str}"
    return json_str


def _sanitize_devis_numero(numero: str) -> str:
    """Sanitize devis numero for use in directory names.

    Args:
        numero: Raw devis numero (e.g., "25 64 0637", "25/64/0637")

    Returns:
        Sanitized string safe for directory names (e.g., "25_64_0637")
    """
    import re
    # Replace spaces with underscores
    result = numero.replace(" ", "_")
    # Replace forward slashes with dashes
    result = result.replace("/", "-")
    # Keep only alphanumeric, dots, dashes, underscores
    result = re.sub(r'[^a-zA-Z0-9._-]', '', result)
    return result


def _get_devis_output_dir(devis_info: dict | None, fallback_name: str = "output") -> Path:
    """Get or create output directory for a specific devis.

    Args:
        devis_info: Dictionary with 'numero_devis' key (from analyze_devis header)
        fallback_name: Directory name to use if devis_info is missing (default "output")

    Returns:
        Absolute path to devis output directory (creates it if needed)
    """
    if devis_info and "numero_devis" in devis_info:
        numero = devis_info["numero_devis"]
        sanitized = _sanitize_devis_numero(numero)
        devis_output_dir = Path("output") / sanitized
    else:
        devis_output_dir = Path("output") / fallback_name

    # Ensure directory exists
    devis_output_dir.mkdir(parents=True, exist_ok=True)

    # Return absolute path
    return devis_output_dir.resolve()


def _require_admin(operation_name: str) -> str | None:
    """Check if admin mode is enabled for write operations.

    Args:
        operation_name: Name of the operation (e.g., "ajout", "modification", "suppression")

    Returns:
        JSON error string if admin=false, None if admin=true (operation can proceed)
    """
    if not _config.get("admin", False):
        return json.dumps({
            "error": "Operation reservee a l'administrateur",
            "resume": f"ECHEC {operation_name}: mode administrateur requis"
        }, ensure_ascii=False)
    return None


# Create FastMCP server instance
_mcp_instructions = "Delagrave product reference and documentation generation tools"
if _pending_update_notice:
    _mcp_instructions += f"\n\n{_pending_update_notice}"
mcp = FastMCP("gendoc", instructions=_mcp_instructions)


def _safe_write_log() -> str | None:
    """Write the current pipeline log and reset. Returns log path or None."""
    global _current_logger
    if _current_logger is None:
        return None
    try:
        log_path = _current_logger.write_log()
        return str(log_path)
    except Exception:
        return None
    finally:
        _current_logger = None


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

    return _inject_update_notice(json.dumps(result, ensure_ascii=False, indent=2))


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
    global _current_logger
    path = Path(pdf_path)

    # Resolve relative paths from project root
    if not path.is_absolute():
        path = Path(__file__).resolve().parent.parent.parent.parent / path

    if not path.exists():
        return json.dumps({"error": f"Fichier PDF non trouve: {pdf_path}"}, ensure_ascii=False)

    try:
        # Analyze devis first to extract header (needed for devis-specific output directory)
        result = run_analyze_devis(path, REFERENCES_DIR)

        # Now we have the devis header, create proper output directory
        devis_output_dir = _get_devis_output_dir(result.get("header"))
        devis_output_dir.mkdir(parents=True, exist_ok=True)

        # Create logger with correct devis-specific output directory
        _current_logger = PipelineLogger(devis_output_dir)
        _current_logger.set_input_params(
            pdf_path=str(path),
            codes_extraits=[r["code"] for r in result.get("references", [])],
            devis_header=result.get("header", {})
        )
        step = _current_logger.start_step("Analyse PDF")

        # Log each unknown code individually for review
        for code_inconnu in result.get("inconnus", []):
            _current_logger.log_error(
                f"Code inconnu: {code_inconnu}",
                context={"code": code_inconnu, "action": "a verifier dans le catalogue"}
            )

        _current_logger.end_step(step, result={
            "references": len(result.get("references", [])),
            "revetements": len(result.get("revetements", [])),
            "speciaux": len(result.get("speciaux", [])),
            "forfaits": len(result.get("forfaits", [])),
            "inconnus": len(result.get("inconnus", []))
        })

        # Build compact resume
        refs_count = len(result.get("references", []))
        rev_count = len(result.get("revetements", []))
        sp_count = len(result.get("speciaux", []))
        inconnus_count = len(result.get("inconnus", []))
        resume_parts = [f"Analyse OK -- {refs_count} references"]
        if rev_count:
            resume_parts.append(f"{rev_count} revetements")
        if sp_count:
            resume_parts.append(f"{sp_count} speciaux")
        if inconnus_count:
            resume_parts.append(f"{inconnus_count} inconnus")
        result["resume"] = ", ".join(resume_parts)

        return _inject_update_notice(json.dumps(result, ensure_ascii=False, indent=2))
    except ValueError as e:
        _current_logger.fail_step(step, str(e), traceback_str=traceback.format_exc())
        log_path = _safe_write_log()
        resp = {"error": f"Erreur de lecture du PDF: {str(e)}"}
        resp["resume"] = f"ECHEC analyse: {str(e)}"
        if log_path:
            resp["log_path"] = log_path
        return json.dumps(resp, ensure_ascii=False)
    except Exception as e:
        _current_logger.fail_step(step, str(e), traceback_str=traceback.format_exc())
        log_path = _safe_write_log()
        resp = {"error": f"Erreur inattendue: {str(e)}"}
        resp["resume"] = f"ECHEC analyse: {str(e)}"
        if log_path:
            resp["log_path"] = log_path
        return json.dumps(resp, ensure_ascii=False)


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
    global _current_logger
    step = None

    try:
        # Log step if logger exists
        if _current_logger:
            step = _current_logger.start_step("Preview generation")

        # Hot-reload generators and get fresh constants
        FAMILY_ORDER, FAMILY_DISPLAY_NAMES = _reload_assembler_constants()

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

        # End step if logger exists
        if _current_logger and step:
            _current_logger.end_step(step, result={
                "total_products": total_products,
                "estimated_pages": estimated_pages,
                "families_count": len(families)
            })

        # Add compact resume
        result["resume"] = f"Preview OK -- {total_products} produits, {estimated_pages} pages estimees"

        return _inject_update_notice(json.dumps(result, ensure_ascii=False, indent=2))

    except Exception as e:
        if _current_logger and step:
            _current_logger.fail_step(step, str(e), traceback_str=traceback.format_exc())
        log_path = _safe_write_log()
        resp = {"error": f"Erreur de previsualisation: {str(e)}"}
        if log_path:
            resp["log_path"] = log_path
        return json.dumps(resp, ensure_ascii=False)


@mcp.tool()
async def generate_slides(product_codes: list[str], output_path: str = None, mode: str = "FTI", devis_info: dict = None, custom_products: str = "[]") -> str:
    """
    Generate a PowerPoint presentation with product slides.

    Args:
        product_codes: List of product codes to include
        output_path: Path for the output PowerPoint file (optional - auto-computed from devis_info if not provided)
        mode: Slide generation mode ("FTI" or other - default "FTI")
        devis_info: Optional dict with devis header info: 'numero_devis', 'date', 'client', 'titre_affaire'
        custom_products: JSON string of custom product dicts (for SP articles)

    Returns:
        JSON string with generation results: slides_generated, total_pages, revetements_added, skipped, output_path.

    Example:
        generate_slides(["PM-D-H-75", "PA-D-60"], "output.pptx") -> {"slides_generated": 2, "total_pages": 5, ...}
        generate_slides(["PM-D-H-75"], "output.pptx", devis_info={"numero_devis": "25 64 0637", "client": "TEST"})
    """
    global _current_logger
    step = None

    try:
        # Compute output directory from devis_info (uses helper from Plan 01)
        devis_output_dir = _get_devis_output_dir(devis_info, fallback_name="default")

        # If no logger exists (generate_slides called standalone), create one
        if _current_logger is None:
            _current_logger = PipelineLogger(devis_output_dir)

        # If output_path provided, use it (relative to devis output dir)
        if output_path:
            output = Path(output_path)
            if not output.is_absolute():
                output = devis_output_dir / output_path
        else:
            # Auto-compute: devis_output_dir/fiches.pptx
            output = devis_output_dir / "fiches.pptx"

        # Ensure parent directory exists
        output.parent.mkdir(parents=True, exist_ok=True)

        # Validate template exists
        if not TEMPLATE_PATH.exists():
            return json.dumps({"error": f"Template PowerPoint non trouve: {TEMPLATE_PATH}"}, ensure_ascii=False)

        # Parse custom_products JSON
        try:
            custom_products_list = json.loads(custom_products)
        except json.JSONDecodeError:
            custom_products_list = []

        # Log step if logger exists
        if _current_logger:
            _current_logger.set_input_params(
                product_codes=product_codes,
                output_path=str(output),
                devis_info=devis_info
            )
            step = _current_logger.start_step("Generation PPTX")

        # Hot-reload generators to pick up source changes
        _generate = _reload_generators()

        # Call the generator (alias resolution happens inside pptx_generator)
        result = _generate(
            product_codes=product_codes,
            output_path=output,
            references_dir=REFERENCES_DIR,
            template_path=TEMPLATE_PATH,
            project_root=_PROJECT_ROOT,
            mode=mode,
            devis_info=devis_info,
            custom_products=custom_products_list
        )

        # Log per-product errors from result (products skipped during generation)
        if _current_logger:
            for s in result.get("skipped", []):
                _current_logger.log_error(
                    f"Produit ignore: {s['code']}",
                    context={"code": s["code"], "reason": s["reason"]}
                )
            for w in result.get("warnings", []):
                _current_logger.log_error(
                    f"Avertissement produit: {w['code']} - {w['message']}",
                    context={"code": w["code"], "type": "warning", "detail": w["message"]}
                )
            _current_logger.end_step(step, result={
                "slides_generated": result.get("slides_generated", 0),
                "total_pages": result.get("total_pages", 0),
                "revetements_added": result.get("revetements_added", 0),
                "skipped": len(result.get("skipped", [])),
                "warnings": len(result.get("warnings", []))
            })

        # Write log in success path and capture log_path for the response
        if _current_logger:
            log_path = _current_logger.write_log()
            result['log_path'] = str(log_path)
            _current_logger = None

        # Build compact resume
        slides_ok = result.get('slides_generated', 0)
        warnings_list = result.get('warnings', [])
        skipped_list = result.get('skipped', [])
        total_pages = result.get('total_pages', 0)
        revetements = result.get('revetements_added', [])

        resume_lines = []
        resume_lines.append(f"Generation OK -- {slides_ok} fiches, {total_pages} pages")
        if revetements:
            resume_lines.append(f"Revetements ajoutes: {len(revetements)}")
        if warnings_list:
            resume_lines.append(f"Avertissements: {len(warnings_list)} produit(s) avec problemes")
            for w in warnings_list:
                resume_lines.append(f"  - {w['code']}: {w['message']}")
        if skipped_list:
            resume_lines.append(f"Ignores: {len(skipped_list)} produit(s) non trouves")
            for s in skipped_list:
                resume_lines.append(f"  - {s['code']}: {s['reason']}")
        resume_lines.append(f"Fichier: {output}")

        result['resume'] = "\n".join(resume_lines)

        # Add output path to result
        result['output_path'] = str(output)
        return _inject_update_notice(json.dumps(result, ensure_ascii=False, indent=2))

    except Exception as e:
        if _current_logger and step:
            _current_logger.fail_step(step, str(e), traceback_str=traceback.format_exc())
        log_path = _safe_write_log()
        resp = {"error": f"Erreur de generation: {str(e)}"}
        resp["resume"] = f"ECHEC generation: {str(e)}"
        if log_path:
            resp["log_path"] = log_path
        return json.dumps(resp, ensure_ascii=False)

    finally:
        # Safety net: if logger was not written by try or except, write now
        if _current_logger:
            _safe_write_log()


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
async def open_sp_selector(analysis_result: dict, output_path: str = None) -> str:
    """
    Generate an interactive HTML selector for configuring SP articles from devis analysis.

    Takes the output of analyze_devis, extracts SP articles (speciaux), and generates
    a self-contained HTML page for editing. User can search catalog, select base products,
    edit fields, and export JSON for use with generate_slides.

    Args:
        analysis_result: Dictionary from analyze_devis (must contain 'speciaux' key)
        output_path: Path for the HTML file (optional - auto-computed from analysis_result if not provided)

    Returns:
        JSON string with output_path, sp_count, catalog_size, and instructions.

    Example:
        open_sp_selector(analysis_result, "output/sp_selector.html")
    """
    global _current_logger
    step = None

    try:
        # Log step if logger exists
        if _current_logger:
            step = _current_logger.start_step("Selection SP (HTML)")

        # Extract speciaux list from analysis result
        speciaux = analysis_result.get("speciaux", [])

        if not speciaux or len(speciaux) == 0:
            if _current_logger and step:
                _current_logger.end_step(step, result={"sp_count": 0})
            return json.dumps({
                "error": "Aucun article special (SP) detecte dans ce devis",
                "sp_count": 0
            }, ensure_ascii=False)

        # Extract devis info from analysis_result
        devis_info = analysis_result.get("header", {})

        # Compute output directory from devis info
        devis_output_dir = _get_devis_output_dir(devis_info, fallback_name="default")

        # If output_path provided, use it (relative to devis output dir)
        if output_path:
            output = Path(output_path)
            if not output.is_absolute():
                output = devis_output_dir / output_path
        else:
            # Auto-compute: devis_output_dir/sp_selector.html
            output = devis_output_dir / "sp_selector.html"

        # Ensure directory exists
        output.parent.mkdir(parents=True, exist_ok=True)

        # Generate HTML
        result = generate_sp_selector_html(
            sp_articles=speciaux,
            references_dir=REFERENCES_DIR,
            output_path=output
        )

        # Start local server and open browser
        server_info = start_sp_server(output, output.parent)

        result['server_url'] = server_info['url']
        result['json_output'] = str(devis_output_dir / 'sp_selection.json')
        result['message'] = (
            f"Selecteur SP ouvert dans le navigateur ({server_info['url']}). "
            f"Configurez les articles puis cliquez 'Exporter JSON'. "
            f"Le fichier sera enregistre dans : {result['json_output']}"
        )

        # End step if logger exists
        if _current_logger and step:
            _current_logger.end_step(step, result={"sp_count": len(speciaux)})

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        if _current_logger and step:
            _current_logger.fail_step(step, str(e), traceback_str=traceback.format_exc())
        log_path = _safe_write_log()
        resp = {"error": f"Erreur lors de la generation du selecteur SP: {str(e)}"}
        if log_path:
            resp["log_path"] = log_path
        return json.dumps(resp, ensure_ascii=False)


@mcp.tool()
async def load_sp_selection(json_path: str = None) -> str:
    """
    Load SP article configuration from JSON file exported by the HTML selector.

    Reads the sp_selection.json file and returns custom product data ready for use
    with generate_slides's custom_products parameter.

    Args:
        json_path: Path to sp_selection.json (optional - reads from current devis context if not provided)

    Returns:
        JSON string with custom product data array (pass this to generate_slides).

    Example:
        load_sp_selection("output/sp_selection.json") -> JSON string of custom products
    """
    global _current_logger
    step = None

    try:
        # Log step if logger exists
        if _current_logger:
            step = _current_logger.start_step("Chargement selection SP")

        # If no path provided, try to infer from current logger context
        if json_path is None:
            # Try to get devis info from current logger
            devis_info = None
            if _current_logger and hasattr(_current_logger, 'input_params'):
                devis_info = _current_logger.input_params.get('devis_header')

            # Compute output directory (will use fallback if no devis info)
            devis_output_dir = _get_devis_output_dir(devis_info, fallback_name="default")
            path = devis_output_dir / "sp_selection.json"
        else:
            # Path provided - resolve relative to CWD or use absolute
            path = Path(json_path)
            if not path.is_absolute():
                # If relative, resolve from CWD (user-provided paths are relative to CWD)
                path = Path.cwd() / path

        # Validate file exists
        if not path.exists():
            if _current_logger and step:
                _current_logger.fail_step(step, f"Fichier sp_selection.json non trouve: {path}")
            log_path = _safe_write_log()
            resp = {
                "error": f"Fichier sp_selection.json non trouve: {path}",
                "hint": "Verifiez que le selecteur SP a bien ete exporte (bouton 'Exporter JSON')"
            }
            if log_path:
                resp["log_path"] = log_path
            return json.dumps(resp, ensure_ascii=False)

        # Read and parse JSON
        try:
            with open(path, 'r', encoding='utf-8') as f:
                custom_products = json.load(f)
        except json.JSONDecodeError as e:
            if _current_logger and step:
                _current_logger.fail_step(step, f"JSON invalide: {str(e)}")
            log_path = _safe_write_log()
            resp = {"error": f"JSON invalide: {str(e)}"}
            if log_path:
                resp["log_path"] = log_path
            return json.dumps(resp, ensure_ascii=False)

        # Validate structure
        if not isinstance(custom_products, list):
            if _current_logger and step:
                _current_logger.fail_step(step, "Le JSON doit contenir un tableau de produits")
            log_path = _safe_write_log()
            resp = {"error": "Le JSON doit contenir un tableau de produits"}
            if log_path:
                resp["log_path"] = log_path
            return json.dumps(resp, ensure_ascii=False)

        # Validate each product has minimum required keys
        for idx, product in enumerate(custom_products):
            if not isinstance(product, dict):
                error_msg = f"Produit a l'index {idx} n'est pas un objet"
                if _current_logger and step:
                    _current_logger.fail_step(step, error_msg)
                log_path = _safe_write_log()
                resp = {"error": error_msg}
                if log_path:
                    resp["log_path"] = log_path
                return json.dumps(resp, ensure_ascii=False)
            if 'code' not in product or 'famille' not in product:
                error_msg = f"Produit a l'index {idx} manque 'code' ou 'famille'"
                if _current_logger and step:
                    _current_logger.fail_step(step, error_msg)
                log_path = _safe_write_log()
                resp = {"error": error_msg}
                if log_path:
                    resp["log_path"] = log_path
                return json.dumps(resp, ensure_ascii=False)

        # End step if logger exists
        if _current_logger and step:
            _current_logger.end_step(step, result={"custom_products": len(custom_products)})

        # Return as JSON string (format expected by generate_slides)
        return json.dumps(custom_products, ensure_ascii=False, indent=2)

    except Exception as e:
        if _current_logger and step:
            _current_logger.fail_step(step, str(e), traceback_str=traceback.format_exc())
        log_path = _safe_write_log()
        resp = {"error": f"Erreur lors du chargement du fichier JSON: {str(e)}"}
        if log_path:
            resp["log_path"] = log_path
        return json.dumps(resp, ensure_ascii=False)


@mcp.tool()
async def add_reference(
    famille: str,
    code: str,
    titre: str,
    ref: str = "",
    texte: str = "",
    dimensions: str = "[]",
    images: str = "[]",
    metadata_pptx: str = "[]",
    image_sources: str = "[]"
) -> str:
    """
    Add a new product reference to a family.

    Args:
        famille: Family name (e.g., "paillasse")
        code: Product code
        titre: Product title
        ref: Reference string (optional)
        texte: Descriptive text (optional)
        dimensions: JSON string of dimension list (optional)
        images: JSON string of image list (optional)
        metadata_pptx: JSON string of PowerPoint metadata list (optional)
        image_sources: JSON string of absolute file paths to copy (optional)

    Returns:
        JSON string with status and resume, or error.

    Example:
        add_reference("paillasse", "PM-TEST", "Test product", ref="Ref: 123")
        -> {"status": "ok", "code": "PM-TEST", "famille": "paillasse", ...}
    """
    if (err := _require_admin("ajout")): return err
    try:
        # Validate required inputs
        code = code.strip()
        titre = titre.strip()
        famille = famille.strip()

        if not code:
            return json.dumps({
                "error": "Le code produit est requis",
                "resume": "Erreur: code vide"
            }, ensure_ascii=False)

        if not titre:
            return json.dumps({
                "error": "Le titre est requis",
                "resume": "Erreur: titre vide"
            }, ensure_ascii=False)

        if not famille:
            return json.dumps({
                "error": "La famille est requise",
                "resume": "Erreur: famille vide"
            }, ensure_ascii=False)

        # Check for duplicates
        existing = find_product(code, REFERENCES_DIR)
        if existing:
            return json.dumps({
                "error": f"Code deja existant: {code}",
                "famille_existante": existing.get('famille', ''),
                "resume": f"Erreur: {code} existe deja dans {existing.get('famille', '')}"
            }, ensure_ascii=False)

        # Parse JSON fields
        try:
            dimensions_list = json.loads(dimensions)
            images_list = json.loads(images)
            metadata_pptx_list = json.loads(metadata_pptx)
        except json.JSONDecodeError as e:
            return json.dumps({
                "error": f"Erreur JSON: {str(e)}",
                "resume": "Erreur: format JSON invalide"
            }, ensure_ascii=False)

        # Parse image source paths
        try:
            image_source_paths = json.loads(image_sources)
        except json.JSONDecodeError as e:
            return json.dumps({
                "error": f"Erreur JSON image_sources: {str(e)}",
                "resume": "Erreur: format JSON invalide"
            }, ensure_ascii=False)

        # If user provided source paths, copy images and use returned dicts
        if image_source_paths:
            copied_images = copy_product_images(image_source_paths, famille.lower(), IMAGES_DIR)
            # Merge: copied images replace any manual images list
            images_list = copied_images

        # Build product dict
        product = {
            'code': code,
            'ref': ref,
            'titre': titre,
            'famille': famille.lower(),
            'texte': texte,
            'dimensions': dimensions_list,
            'images': images_list,
            'metadata_pptx': metadata_pptx_list
        }

        # Ensure family infrastructure exists (creates images directory for new families)
        infra_result = ensure_family_infrastructure(famille, REFERENCES_DIR)

        # Write to family file
        family_path = REFERENCES_DIR / f"{famille.lower()}.md"
        append_product_to_family(family_path, product)

        # Refresh _index.md
        try:
            refresh_index(REFERENCES_DIR)
        except Exception as idx_err:
            # Index refresh failed but CRUD operation succeeded
            pass

        # Calculate relative path for response
        relative_path = f"Delagrave/references/{famille.lower()}.md"

        # Build response
        result = {
            "status": "ok",
            "code": code,
            "famille": famille.lower(),
            "fichier": relative_path,
            "resume": f"Reference ajoutee: {code} dans {famille.lower()}"
        }

        # Add nouvelle_famille flag if this was a new family
        if infra_result.get("images_dir_created"):
            result["nouvelle_famille"] = True
            result["resume"] += " (nouvelle famille)"

        # Add images count if any were copied
        if image_source_paths:
            result["images_copiees"] = len([i for i in images_list if "error" not in i])
            result["resume"] += f", {result['images_copiees']} image(s) copiee(s)"

        # Return success
        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "error": f"Erreur inattendue: {str(e)}",
            "resume": f"Erreur lors de l'ajout de {code}"
        }, ensure_ascii=False)


@mcp.tool()
async def update_reference(
    code: str,
    ref: str | None = None,
    titre: str | None = None,
    texte: str | None = None,
    dimensions: str | None = None,
    images: str | None = None,
    metadata_pptx: str | None = None,
    image_sources: str | None = None
) -> str:
    """
    Update an existing product reference.

    Args:
        code: Product code to update
        ref: Reference string (optional)
        titre: Product title (optional)
        texte: Descriptive text (optional)
        dimensions: JSON string of dimension list (optional)
        images: JSON string of image list (optional)
        metadata_pptx: JSON string of PowerPoint metadata list (optional)
        image_sources: JSON string of absolute file paths to copy (optional)

    Returns:
        JSON string with status and resume, or error.

    Example:
        update_reference("PM-TEST", titre="Updated title", texte="New text")
        -> {"status": "ok", "code": "PM-TEST", "famille": "paillasse", ...}
    """
    if (err := _require_admin("modification")): return err
    try:
        # Validate required inputs
        code = code.strip()

        if not code:
            return json.dumps({
                "error": "Le code produit est requis",
                "resume": "ECHEC modification: code vide"
            }, ensure_ascii=False)

        # Check existence (CRUD-05)
        product = find_product(code, REFERENCES_DIR)
        if not product:
            return json.dumps({
                "error": f"Code non trouve: {code}",
                "resume": f"ECHEC modification: code {code} non trouve"
            }, ensure_ascii=False)

        # Build updates dict from non-None parameters
        updates = {}

        if ref is not None:
            updates['ref'] = ref

        if titre is not None:
            updates['titre'] = titre

        if texte is not None:
            updates['texte'] = texte

        # Parse JSON fields
        try:
            if dimensions is not None:
                updates['dimensions'] = json.loads(dimensions)

            if images is not None:
                updates['images'] = json.loads(images)

            if metadata_pptx is not None:
                updates['metadata_pptx'] = json.loads(metadata_pptx)
        except json.JSONDecodeError as e:
            return json.dumps({
                "error": f"Erreur JSON: {str(e)}",
                "resume": "ECHEC modification: format JSON invalide"
            }, ensure_ascii=False)

        # Handle image source copying
        if image_sources is not None:
            try:
                image_source_paths = json.loads(image_sources)
            except json.JSONDecodeError as e:
                return json.dumps({
                    "error": f"Erreur JSON image_sources: {str(e)}",
                    "resume": "ECHEC modification: format JSON invalide"
                }, ensure_ascii=False)

            if image_source_paths:
                # Get famille from existing product
                famille = product.get('famille', '')
                copied_images = copy_product_images(image_source_paths, famille, IMAGES_DIR)
                updates['images'] = copied_images

        # Check if any updates provided
        if not updates:
            return json.dumps({
                "error": "Aucun champ a modifier",
                "resume": "ECHEC modification: aucun champ specifie"
            }, ensure_ascii=False)

        # Get family file from product
        famille = product.get('famille', '')
        family_path = REFERENCES_DIR / f"{famille}.md"

        # Update product
        update_product_in_family(family_path, code, updates)

        # Refresh _index.md
        try:
            refresh_index(REFERENCES_DIR)
        except Exception as idx_err:
            # Index refresh failed but CRUD operation succeeded
            pass

        # Return success
        champs_modifies = list(updates.keys())
        return json.dumps({
            "status": "ok",
            "code": code,
            "famille": famille,
            "champs_modifies": champs_modifies,
            "resume": f"Reference modifiee: {code} ({len(champs_modifies)} champ(s))"
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Erreur inattendue: {str(e)}",
            "resume": f"ECHEC modification de {code}"
        }, ensure_ascii=False)


@mcp.tool()
async def delete_reference(code: str) -> str:
    """
    Delete a product reference from the catalog.

    Args:
        code: Product code to delete

    Returns:
        JSON string with status and resume, or error.

    Example:
        delete_reference("PM-TEST")
        -> {"status": "ok", "code": "PM-TEST", "famille": "paillasse", ...}
    """
    if (err := _require_admin("suppression")): return err
    try:
        # Validate required inputs
        code = code.strip()

        if not code:
            return json.dumps({
                "error": "Le code produit est requis",
                "resume": "ECHEC suppression: code vide"
            }, ensure_ascii=False)

        # Check existence (CRUD-05)
        product = find_product(code, REFERENCES_DIR)
        if not product:
            return json.dumps({
                "error": f"Code non trouve: {code}",
                "resume": f"ECHEC suppression: code {code} non trouve"
            }, ensure_ascii=False)

        # Get family file from product
        famille = product.get('famille', '')
        family_path = REFERENCES_DIR / f"{famille}.md"

        # Delete product
        remove_product_from_family(family_path, code)

        # Remove associated image files from disk
        image_stats = remove_product_images(product, IMAGES_DIR)

        # Refresh _index.md
        try:
            refresh_index(REFERENCES_DIR)
        except Exception as idx_err:
            # Index refresh failed but CRUD operation succeeded
            pass

        # Build response
        result = {
            "status": "ok",
            "code": code,
            "famille": famille,
            "images_supprimees": image_stats.get("removed", 0),
            "resume": f"Reference supprimee: {code} de {famille}"
        }
        if image_stats.get("removed", 0) > 0:
            result["resume"] += f", {image_stats['removed']} image(s) supprimee(s)"

        # Return success
        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Erreur inattendue: {str(e)}",
            "resume": f"ECHEC suppression de {code}"
        }, ensure_ascii=False)


@mcp.tool()
async def update_gendoc() -> str:
    """
    Lance la mise a jour automatique de gendoc depuis GitHub.

    Detecte si Git est installe (l'installe si besoin via winget),
    puis execute git pull (ou clone initial) et pip install -e .
    Le resultat inclut les versions avant/apres et les etapes realisees.

    IMPORTANT: Apres une mise a jour reussie, il faut redemarrer Claude
    pour que les changements soient pris en compte.

    Returns:
        JSON string avec status, old_version, new_version, steps_completed, resume.

    Example:
        update_gendoc() -> {"status": "success", "old_version": "2.0.0", "new_version": "2.1.0", ...}
    """
    try:
        result = run_update(
            github_repo=_config.get("github_repo", ""),
            github_token=_config.get("github_token", "") or None,
        )
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": f"Erreur inattendue lors de la mise a jour: {str(e)}",
            "resume": f"ECHEC mise a jour: {str(e)}"
        }, ensure_ascii=False)


def main():
    """Main entry point for the MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
