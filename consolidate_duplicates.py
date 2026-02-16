#!/usr/bin/env python3
"""
Consolidate duplicate product codes in reference MD files.

Products with multiple entries (e.g., 9203 appears 3 times) are consolidated
into single entries with all image variants preserved in the Images table.
"""

from pathlib import Path
from collections import defaultdict
from src.gendoc.parsers.md_parser import parse_family_md
from src.gendoc.parsers.md_writer import write_family_file, _read_header


def consolidate_family_file(filepath: Path, dry_run: bool = False) -> dict:
    """
    Consolidate duplicate product codes in a family MD file.

    Args:
        filepath: Path to the family MD file
        dry_run: If True, only report duplicates without modifying file

    Returns:
        Dict with stats: original_count, unique_count, duplicates_found
    """
    print(f"\n{'='*60}")
    print(f"Processing: {filepath.name}")
    print(f"{'='*60}")

    # Parse all products
    products = parse_family_md(filepath)
    original_count = len(products)

    # Group by code
    groups = defaultdict(list)
    for p in products:
        groups[p['code']].append(p)

    # Find duplicates
    duplicates = {code: prods for code, prods in groups.items() if len(prods) > 1}

    if duplicates:
        print(f"\nFound {len(duplicates)} duplicate product codes:")
        for code, prods in sorted(duplicates.items()):
            print(f"  - {code}: {len(prods)} entries")
            # Show image counts for each entry
            for i, p in enumerate(prods, 1):
                img_count = len(p.get('images', []))
                print(f"    Entry {i}: {img_count} images")
    else:
        print("No duplicates found.")
        return {
            'original_count': original_count,
            'unique_count': original_count,
            'duplicates_found': 0
        }

    if dry_run:
        print("\nDRY RUN - no changes made")
        return {
            'original_count': original_count,
            'unique_count': len(groups),
            'duplicates_found': len(duplicates)
        }

    # Consolidate duplicates
    print("\nConsolidating duplicates...")
    consolidated = []
    consolidated_count = 0

    for code in sorted(groups.keys()):
        prods = groups[code]
        if len(prods) == 1:
            # No duplication, keep as-is
            consolidated.append(prods[0])
        else:
            # Merge all entries
            base = prods[0].copy()

            # Merge all images from all duplicate entries
            all_images = []
            for p in prods:
                all_images.extend(p.get('images', []))

            # Merge all dimensions (typically identical, but keep all unique)
            all_dimensions = []
            dim_seen = set()
            for p in prods:
                for dim in p.get('dimensions', []):
                    dim_key = (dim.get('name'), dim.get('valeur'))
                    if dim_key not in dim_seen:
                        all_dimensions.append(dim)
                        dim_seen.add(dim_key)

            # Merge metadata_pptx (typically identical, keep unique)
            all_metadata = []
            meta_seen = set()
            for p in prods:
                for meta in p.get('metadata_pptx', []):
                    meta_key = (meta.get('champ'), meta.get('type'))
                    if meta_key not in meta_seen:
                        all_metadata.append(meta)
                        meta_seen.add(meta_key)

            base['images'] = all_images
            base['dimensions'] = all_dimensions
            base['metadata_pptx'] = all_metadata

            consolidated.append(base)
            consolidated_count += 1

            print(f"  OK {code}: merged {len(prods)} entries -> {len(all_images)} total images")

    unique_count = len(consolidated)
    print(f"\nConsolidation complete:")
    print(f"  Original entries: {original_count}")
    print(f"  Unique products: {unique_count}")
    print(f"  Products consolidated: {consolidated_count}")

    # Read header to preserve it
    header = _read_header(filepath)
    header_lines = header.split('\n') if header else []

    # Update count in header
    for i, line in enumerate(header_lines):
        if 'Total references:' in line:
            header_lines[i] = f"> Total references: {unique_count}"
            print(f"  Updated header count: {unique_count}")
            break

    # Write back consolidated products
    write_family_file(filepath, header_lines, consolidated)
    print(f"\nOK File written: {filepath}")

    return {
        'original_count': original_count,
        'unique_count': unique_count,
        'duplicates_found': len(duplicates)
    }


def main():
    """Main consolidation process."""
    base_dir = Path("Delagrave/references")

    # Files to process (as specified in the plan)
    files_to_process = [
        "equipement.md",
        "elec-sorb.md",
        "complements.md"
    ]

    total_stats = {
        'files_processed': 0,
        'total_duplicates': 0,
        'total_before': 0,
        'total_after': 0
    }

    for filename in files_to_process:
        filepath = base_dir / filename
        if not filepath.exists():
            print(f"\nWARNING File not found: {filepath}")
            continue

        stats = consolidate_family_file(filepath, dry_run=False)

        total_stats['files_processed'] += 1
        total_stats['total_duplicates'] += stats['duplicates_found']
        total_stats['total_before'] += stats['original_count']
        total_stats['total_after'] += stats['unique_count']

    # Print summary
    print(f"\n{'='*60}")
    print("CONSOLIDATION SUMMARY")
    print(f"{'='*60}")
    print(f"Files processed: {total_stats['files_processed']}")
    print(f"Total entries before: {total_stats['total_before']}")
    print(f"Total unique products after: {total_stats['total_after']}")
    print(f"Duplicate products consolidated: {total_stats['total_duplicates']}")
    print(f"Entries removed: {total_stats['total_before'] - total_stats['total_after']}")


if __name__ == '__main__':
    main()
