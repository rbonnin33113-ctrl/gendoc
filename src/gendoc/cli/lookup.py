"""
Product reference lookup CLI for Delagrave.

This module provides a command-line interface for querying product data
from the structured Markdown files. Uses gendoc.parsers.md_parser for
data access (no parsing logic here).
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import argparse
import json
import sys
import difflib

from gendoc.parsers.md_parser import (
    find_product,
    find_products_by_family,
    search_products,
    get_all_families,
    get_all_family_files
)


class ProductLookup:
    """CLI interface for product reference lookup."""

    def __init__(self, references_dir: Path):
        """
        Initialize the lookup interface.

        Args:
            references_dir: Path to Delagrave/references/
        """
        self.references_dir = Path(references_dir)

    def lookup_single(self, code: str, output_json: bool = False) -> bool:
        """
        Lookup a single product by code.

        Args:
            code: Product code
            output_json: Output as JSON instead of human-readable

        Returns:
            True if product found, False otherwise
        """
        product = find_product(code, self.references_dir)

        if not product:
            print(f"Product '{code}' not found.", file=sys.stderr)
            self._suggest_matches(code)
            return False

        if output_json:
            print(json.dumps(product, indent=2, ensure_ascii=False))
        else:
            self._print_product(product)

        return True

    def lookup_multiple(self, codes: List[str], output_json: bool = False) -> int:
        """
        Lookup multiple products by code.

        Args:
            codes: List of product codes
            output_json: Output as JSON instead of human-readable

        Returns:
            Number of products found
        """
        if output_json:
            results = []
            for code in codes:
                product = find_product(code, self.references_dir)
                if product:
                    results.append(product)
            print(json.dumps(results, indent=2, ensure_ascii=False))
            return len(results)
        else:
            found_count = 0
            for i, code in enumerate(codes):
                if i > 0:
                    print("\n" + "=" * 70 + "\n")
                if self.lookup_single(code, output_json=False):
                    found_count += 1
            return found_count

    def list_families(self, output_json: bool = False):
        """
        List all families with product counts.

        Args:
            output_json: Output as JSON instead of human-readable
        """
        families = get_all_families(self.references_dir)

        if output_json:
            print(json.dumps(families, indent=2, ensure_ascii=False))
        else:
            print("Product Families:")
            print()
            total = 0
            for family, count in sorted(families.items()):
                print(f"  {family:20s} {count:3d} products")
                total += count
            print()
            print(f"  {'TOTAL':20s} {total:3d} products")

    def list_family_products(self, family: str, output_json: bool = False) -> bool:
        """
        List all products in a specific family.

        Args:
            family: Family name
            output_json: Output as JSON instead of human-readable

        Returns:
            True if family found, False otherwise
        """
        products = find_products_by_family(family, self.references_dir)

        if not products:
            print(f"Family '{family}' not found or has no products.", file=sys.stderr)
            return False

        if output_json:
            print(json.dumps(products, indent=2, ensure_ascii=False))
        else:
            print(f"Products in family '{family}' ({len(products)} total):")
            print()
            for product in products:
                print(f"  {product['code']:15s} {product['titre'][:60]}")

        return True

    def search(self, query: str, output_json: bool = False) -> int:
        """
        Search for products by partial code or title.

        Args:
            query: Search query
            output_json: Output as JSON instead of human-readable

        Returns:
            Number of matching products
        """
        results = search_products(query, self.references_dir)

        if output_json:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            if not results:
                print(f"No products found matching '{query}'")
                return 0

            print(f"Found {len(results)} product(s) matching '{query}':")
            print()
            for product in results:
                print(f"  {product['code']:15s} [{product['famille']}] {product['titre'][:50]}")

        return len(results)

    def _print_product(self, product: Dict[str, Any]):
        """
        Print a product in human-readable format.

        Args:
            product: Product dictionary
        """
        print(f"=== {product['code']} ===")
        print(f"Famille:  {product['famille'].title()}")
        print(f"Ref:      {product['ref']}")
        print(f"Titre:    {product['titre']}")
        print()

        # Texte
        if product.get('texte'):
            print("Texte:")
            for line in product['texte'].split('\n'):
                print(f"  {line}")
            print()

        # Dimensions
        if product.get('dimensions'):
            print("Dimensions:")
            max_name_len = max(len(d['name']) for d in product['dimensions']) if product['dimensions'] else 0
            for dim in product['dimensions']:
                name = dim['name'].ljust(max_name_len)
                value = dim['valeur']
                prefix = f"(prefix: \"{dim['prefix']}\", " if dim['prefix'] else "("
                shape = f"shape: {dim['shape_index']})" if dim['shape_index'] else "shape: -)"
                print(f"  {name}  {value:15s} {prefix}{shape}")
            print()

        # Images
        if product.get('images'):
            print("Images:")
            for img in product['images']:
                print(f"  {img['position']}:")
                print(f"    Path: {img['chemin']}")
                if img.get('chemin_original'):
                    print(f"    Original: {img['chemin_original']}")
                if img.get('left') or img.get('top'):
                    print(f"    Position: left={img['left']}, top={img['top']}, " +
                          f"width={img['width']}, height={img['height']}, shape={img['shape_index']}")
            print()

        # PowerPoint Metadata
        if product.get('metadata_pptx'):
            print("PowerPoint Metadata:")
            for meta in product['metadata_pptx']:
                if meta['champ']:  # Skip empty rows
                    shape_info = f"shape {meta['shape_index']}" if meta['shape_index'] else "shape -"
                    type_info = meta['type'] or '-'
                    prefix_info = f"prefix: \"{meta['prefix']}\"" if meta['prefix'] else ""
                    print(f"  {meta['champ']:25s} -> {shape_info:10s} ({type_info}, {prefix_info})")

    def _suggest_matches(self, code: str):
        """
        Suggest close matches for an invalid code.

        Args:
            code: The code that wasn't found
        """
        # Collect all codes
        all_codes = []
        for family_file in get_all_family_files(self.references_dir):
            from gendoc.parsers.md_parser import parse_family_md
            products = parse_family_md(family_file)
            all_codes.extend([p['code'] for p in products])

        # Find close matches
        matches = difflib.get_close_matches(code.upper(), [c.upper() for c in all_codes], n=5, cutoff=0.4)

        if matches:
            print("\nDid you mean:", file=sys.stderr)
            for match in matches:
                # Find original case
                original = next((c for c in all_codes if c.upper() == match), match)
                print(f"  {original}", file=sys.stderr)


def main():
    """CLI entry point for product lookup."""
    parser = argparse.ArgumentParser(
        description="Lookup product references from Delagrave MD files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  gendoc-lookup PM-D-H-75              # Lookup a single product
  gendoc-lookup PM-D-H-75 S-A          # Lookup multiple products
  gendoc-lookup --family paillasse     # List all products in a family
  gendoc-lookup --list-families        # List all families with counts
  gendoc-lookup --search "PM-D"        # Search by partial code or title
  gendoc-lookup PM-D-H-75 --json       # Output as JSON
        """
    )

    parser.add_argument(
        'codes',
        nargs='*',
        help='Product code(s) to lookup'
    )
    parser.add_argument(
        '--family',
        help='List all products in a specific family'
    )
    parser.add_argument(
        '--list-families',
        action='store_true',
        help='List all families with product counts'
    )
    parser.add_argument(
        '--search',
        help='Search for products by partial code or title'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON instead of human-readable format'
    )
    parser.add_argument(
        '--references-dir',
        type=Path,
        default=Path('Delagrave/references'),
        help='Path to references directory (default: Delagrave/references)'
    )

    args = parser.parse_args()

    lookup = ProductLookup(args.references_dir)

    # Determine operation mode
    if args.list_families:
        lookup.list_families(output_json=args.json)
        sys.exit(0)

    if args.family:
        success = lookup.list_family_products(args.family, output_json=args.json)
        sys.exit(0 if success else 1)

    if args.search:
        count = lookup.search(args.search, output_json=args.json)
        sys.exit(0 if count > 0 else 1)

    if args.codes:
        if len(args.codes) == 1:
            success = lookup.lookup_single(args.codes[0], output_json=args.json)
            sys.exit(0 if success else 1)
        else:
            count = lookup.lookup_multiple(args.codes, output_json=args.json)
            sys.exit(0 if count > 0 else 1)

    # No operation specified
    parser.print_help()
    sys.exit(1)


if __name__ == '__main__':
    main()
