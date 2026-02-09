"""Reference validator module.

Validates extracted MD files for completeness, structure, and data integrity.
"""

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple


# Expected reference counts per family (from actual Excel data)
EXPECTED_COUNTS = {
    "paillasse.md": 54,
    "sorbonne.md": 10,
    "revetement.md": 12,
    "meubles.md": 45,
    "tables-en.md": 23,
    "equipement.md": 154,
    "elec-sorb.md": 32,
    "complements.md": 3,
    "fiches-existantes.md": 26,
}

# Family files that should exist
FAMILY_FILES = [
    "paillasse.md",
    "sorbonne.md",
    "revetement.md",
    "meubles.md",
    "tables-en.md",
    "equipement.md",
    "elec-sorb.md",
    "complements.md",
    "fiches-existantes.md",
]

# Required sections for standard products
STANDARD_SECTIONS = ["### Texte", "### Dimensions", "### Images", "### Metadata PowerPoint"]


class ValidationError:
    def __init__(self, family: str, code: str, message: str):
        self.family = family
        self.code = code
        self.message = message

    def __str__(self):
        return f"[{self.family}] {self.code}: {self.message}"


def parse_product_sections(content: str, start_pos: int, end_pos: int) -> List[str]:
    """Parse section headers from a product block."""
    product_content = content[start_pos:end_pos]
    sections = re.findall(r"^###\s+(.+)$", product_content, re.MULTILINE)
    return sections


def parse_products_from_md(filepath: Path) -> List[Dict]:
    """Parse products from an MD file."""
    content = filepath.read_text(encoding="utf-8")
    products = []

    # Find all product sections (## {Code})
    pattern = r"^##\s+(.+)$"
    matches = list(re.finditer(pattern, content, re.MULTILINE))

    for i, match in enumerate(matches):
        code = match.group(1).strip()
        start_pos = match.end()

        # Find end position (next ## or end of file)
        if i < len(matches) - 1:
            end_pos = matches[i + 1].start()
        else:
            end_pos = len(content)

        product_content = content[start_pos:end_pos]

        # Parse basic fields from table
        product = {"code": code, "sections": []}

        # Extract ref and titre from identity table
        ref_match = re.search(r"\|\s*ref\s*\|\s*(.+?)\s*\|", product_content, re.IGNORECASE)
        titre_match = re.search(r"\|\s*titre\s*\|\s*(.+?)\s*\|", product_content, re.IGNORECASE)

        product["ref"] = ref_match.group(1).strip() if ref_match else ""
        product["titre"] = titre_match.group(1).strip() if titre_match else ""

        # Parse sections
        sections = parse_product_sections(content, start_pos, end_pos)
        product["sections"] = sections

        products.append(product)

    return products


def validate_file_exists(references_dir: Path, filename: str) -> Tuple[bool, str]:
    """Validate that a family file exists."""
    filepath = references_dir / filename
    if not filepath.exists():
        return False, f"File {filename} does not exist"
    return True, ""


def validate_product_structure(product: Dict, family: str, is_fiches_existantes: bool) -> List[ValidationError]:
    """Validate a single product's structure."""
    errors = []
    code = product["code"]

    # Check required fields
    if not product.get("code"):
        errors.append(ValidationError(family, code, "Empty code field"))
    if not product.get("ref") and not is_fiches_existantes:
        errors.append(ValidationError(family, code, "Empty ref field"))
    if not product.get("titre"):
        errors.append(ValidationError(family, code, "Empty titre field"))

    # Check required sections (except for Fiches Existantes)
    if not is_fiches_existantes:
        sections = product.get("sections", [])
        for required_section in STANDARD_SECTIONS:
            section_name = required_section.replace("### ", "")
            if section_name not in sections:
                errors.append(ValidationError(family, code, f"Missing section: {section_name}"))

    return errors


def validate_shape_indexes(filepath: Path, family: str) -> List[ValidationError]:
    """Validate that shape indexes are numeric."""
    errors = []
    content = filepath.read_text(encoding="utf-8")

    # Find Dimensions tables
    dimensions_pattern = r"### Dimensions\n\n\| Dimension \| Valeur \| Prefix \| Shape Index \|\n\|.*?\n((?:\|.*?\n)+)"
    for match in re.finditer(dimensions_pattern, content):
        table_content = match.group(1)
        rows = [row for row in table_content.split("\n") if row.strip()]

        for row in rows:
            cells = [cell.strip() for cell in row.split("|")]
            if len(cells) >= 5:
                dimension_name = cells[1]
                shape_index = cells[4]

                # Shape index should be numeric or empty
                if shape_index and not re.match(r"^\d+$", shape_index):
                    code = "Unknown"  # We'd need to track which product this is from
                    errors.append(ValidationError(family, code, f"Non-numeric shape index in dimension '{dimension_name}': {shape_index}"))

    # Find Images tables
    images_pattern = r"### Images\n\n\| Position \| Chemin \| Left \| Top \| Width \| Height \| Shape Index \|\n\|.*?\n((?:\|.*?\n)+)"
    for match in re.finditer(images_pattern, content):
        table_content = match.group(1)
        rows = [row for row in table_content.split("\n") if row.strip()]

        for row in rows:
            cells = [cell.strip() for cell in row.split("|")]
            if len(cells) >= 8:
                position_name = cells[1]
                shape_index = cells[7]

                # Shape index should be numeric or empty
                if shape_index and not re.match(r"^\d+$", shape_index):
                    code = "Unknown"
                    errors.append(ValidationError(family, code, f"Non-numeric shape index in image '{position_name}': {shape_index}"))

    return errors


def validate_family_file(filepath: Path) -> Tuple[int, List[ValidationError]]:
    """Validate a single family file."""
    errors = []
    family = filepath.stem

    # Parse products
    products = parse_products_from_md(filepath)
    count = len(products)

    # Check if Fiches Existantes (different structure)
    is_fiches_existantes = family == "fiches-existantes"

    # Validate each product
    for product in products:
        product_errors = validate_product_structure(product, family, is_fiches_existantes)
        errors.extend(product_errors)

    # Validate shape indexes
    shape_errors = validate_shape_indexes(filepath, family)
    errors.extend(shape_errors)

    # Check if products are sorted alphabetically
    codes = [p["code"] for p in products]
    sorted_codes = sorted(codes)
    if codes != sorted_codes:
        errors.append(ValidationError(family, "N/A", "Products not sorted alphabetically"))

    return count, errors


def validate_all(references_dir: Path, strict_counts: bool = False) -> Tuple[bool, Dict[str, int], List[ValidationError]]:
    """Validate all family files.

    Args:
        references_dir: Directory containing MD files
        strict_counts: If True, fail on count mismatches

    Returns:
        (all_passed, counts_dict, errors_list)
    """
    all_errors = []
    counts = {}

    print("Validating reference MD files...\n")

    # Check all family files exist
    for filename in FAMILY_FILES:
        exists, error_msg = validate_file_exists(references_dir, filename)
        if not exists:
            all_errors.append(ValidationError("SYSTEM", filename, error_msg))
            continue

        # Validate file structure
        filepath = references_dir / filename
        count, errors = validate_family_file(filepath)
        counts[filename] = count

        if errors:
            all_errors.extend(errors)

        # Report progress
        status = "PASS" if not errors else f"FAIL ({len(errors)} issues)"
        print(f"  {filename:25s} {count:4d} products  [{status}]")

        # Check count against expected
        expected = EXPECTED_COUNTS.get(filename)
        if expected and count != expected:
            msg = f"Count mismatch: expected {expected}, got {count}"
            if strict_counts:
                all_errors.append(ValidationError(filename, "COUNT", msg))
                print(f"    WARNING: {msg}")
            else:
                print(f"    INFO: {msg}")

    # Check special files exist
    print("\nChecking special files...")
    for special_file in ["_index.md", "_parametrage.md"]:
        exists, error_msg = validate_file_exists(references_dir, special_file)
        status = "PASS" if exists else "FAIL"
        print(f"  {special_file:25s} [{status}]")
        if not exists:
            all_errors.append(ValidationError("SYSTEM", special_file, error_msg))

    # Summary
    total_count = sum(counts.values())
    print(f"\nTotal references: {total_count}")
    print(f"Total families: {len(counts)}")

    all_passed = len(all_errors) == 0
    return all_passed, counts, all_errors


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Validate extracted reference MD files")
    parser.add_argument("--strict-counts", action="store_true", help="Fail on count mismatches")
    parser.add_argument("--references-dir", type=str, help="References directory (default: Delagrave/references/)")

    args = parser.parse_args()

    # Determine references directory
    if args.references_dir:
        references_dir = Path(args.references_dir)
    else:
        base_dir = Path(__file__).parent.parent.parent.parent
        references_dir = base_dir / "Delagrave" / "references"

    if not references_dir.exists():
        print(f"Error: References directory not found: {references_dir}")
        return 1

    # Run validation
    all_passed, counts, errors = validate_all(references_dir, strict_counts=args.strict_counts)

    # Print errors
    if errors:
        print(f"\n{'='*70}")
        print(f"VALIDATION ERRORS ({len(errors)}):")
        print(f"{'='*70}")
        for error in errors:
            print(f"  {error}")

    # Final result
    print(f"\n{'='*70}")
    if all_passed:
        print("VALIDATION RESULT: PASS")
        print(f"{'='*70}")
        return 0
    else:
        print("VALIDATION RESULT: FAIL")
        print(f"{'='*70}")
        return 1


if __name__ == "__main__":
    exit(main())
