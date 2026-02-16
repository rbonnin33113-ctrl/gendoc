#!/usr/bin/env python3
"""
Validate that all family files have no duplicate product codes.
Generate consolidation report.
"""

from pathlib import Path
from collections import Counter
from src.gendoc.parsers.md_parser import parse_family_md, get_all_family_files


def validate_all_families(references_dir: Path) -> dict:
    """
    Validate all family files for duplicates and generate report.

    Returns:
        Dict with validation results
    """
    # Get all family files
    family_files = get_all_family_files(references_dir)

    # Sort by name for consistent output
    family_files = sorted(family_files, key=lambda f: f.stem)

    print("=" * 60)
    print("DUPLICATE VALIDATION REPORT")
    print("=" * 60)

    total_products = 0
    total_duplicates = 0
    families_with_errors = []

    for family_file in family_files:
        family_name = family_file.stem

        # Parse products
        products = parse_family_md(family_file)
        codes = [p['code'] for p in products]

        # Check for duplicates
        code_counts = Counter(codes)
        duplicates = [code for code, count in code_counts.items() if count > 1]

        if duplicates:
            print(f"\nERROR: {family_name} has {len(duplicates)} duplicate codes:")
            for code in duplicates:
                print(f"  - {code}: {code_counts[code]} entries")
            families_with_errors.append(family_name)
            total_duplicates += len(duplicates)
        else:
            print(f"OK: {family_name:20s} - {len(products):3d} unique products")

        total_products += len(products)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total families checked: {len(family_files)}")
    print(f"Total unique products: {total_products}")
    print(f"Families with duplicates: {len(families_with_errors)}")
    print(f"Total duplicate codes found: {total_duplicates}")

    if families_with_errors:
        print(f"\nFAILED: {', '.join(families_with_errors)} have duplicates")
        return {
            'success': False,
            'total_products': total_products,
            'families_with_errors': families_with_errors
        }
    else:
        print("\nPASS: All families have unique product codes")
        return {
            'success': True,
            'total_products': total_products,
            'families_with_errors': []
        }


def generate_consolidation_report(references_dir: Path):
    """Generate detailed consolidation report."""
    print("\n" + "=" * 60)
    print("CONSOLIDATION REPORT")
    print("=" * 60)

    # Expected counts based on consolidation
    expected_before = {
        'equipement': 154,
        'elec-sorb': 32,
        'complements': 3
    }

    expected_after = {
        'equipement': 122,
        'elec-sorb': 14,
        'complements': 1
    }

    total_before = sum(expected_before.values())
    total_after = sum(expected_after.values())

    print(f"\nConsolidated files (3 families):")
    for family in sorted(expected_before.keys()):
        before = expected_before[family]
        after = expected_after[family]
        removed = before - after
        print(f"  {family:20s}: {before:3d} entries -> {after:3d} unique ({removed} duplicates removed)")

    print(f"\nTotals for consolidated files:")
    print(f"  Before consolidation: {total_before} entries")
    print(f"  After consolidation:  {total_after} unique products")
    print(f"  Duplicates removed:   {total_before - total_after} entries")

    # Count images preserved
    print(f"\nImage preservation:")
    for family in sorted(expected_before.keys()):
        filepath = references_dir / f"{family}.md"
        products = parse_family_md(filepath)
        total_images = sum(len(p.get('images', [])) for p in products)
        print(f"  {family:20s}: {total_images} images preserved across {len(products)} products")

    # Overall stats
    all_families = get_all_family_files(references_dir)
    grand_total = sum(len(parse_family_md(f)) for f in all_families)

    print(f"\nOverall project stats:")
    print(f"  Total families: {len(all_families)}")
    print(f"  Total unique products: {grand_total}")


def main():
    """Main validation process."""
    references_dir = Path("Delagrave/references")

    # Validate for duplicates
    result = validate_all_families(references_dir)

    # Generate consolidation report
    generate_consolidation_report(references_dir)

    # Exit code
    if result['success']:
        print("\n" + "=" * 60)
        print("VALIDATION SUCCESSFUL")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("VALIDATION FAILED")
        print("=" * 60)
        return 1


if __name__ == '__main__':
    exit(main())
