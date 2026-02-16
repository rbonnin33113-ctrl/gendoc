"""
Image Manager for Delagrave product references.

This module organizes product images from network share to local directories
and updates MD file paths accordingly. Uses gendoc.parsers.md_parser for
reading MD files (no parsing duplication).
"""

from pathlib import Path
from typing import List, Dict, Tuple, Set
import shutil
import argparse
import re
from datetime import datetime

from gendoc.parsers.md_parser import parse_family_md, get_all_family_files


class ImageOrganizer:
    """Manages image organization from network share to local directories."""

    # Network share base path
    DEFAULT_NETWORK_BASE = Path(r"\\tse\commun\BE\Chiffrage\Fiches Techniques\Génération FT")

    # Family name mappings (sheet name -> directory name)
    FAMILY_DIRS = {
        'paillasse': 'paillasse',
        'sorbonne': 'sorbonne',
        'revetement': 'revetement',
        'meubles': 'meubles',
        'tables-en': 'tables-en',
        'equipement': 'equipement',
        'elec-sorb': 'elec-sorb',
        'complements': 'complements',
        'fiches-existantes': 'fiches-existantes'
    }

    def __init__(
        self,
        references_dir: Path,
        images_dir: Path,
        source_dir: Path = None,
        dry_run: bool = False,
        force: bool = False,
        skip_copy: bool = False
    ):
        """
        Initialize the ImageOrganizer.

        Args:
            references_dir: Path to Delagrave/references/
            images_dir: Path to Delagrave/images/
            source_dir: Override network share base path (for testing)
            dry_run: Show what would be done without modifying files
            force: Re-copy even if local file exists
            skip_copy: Only update MD paths without copying images
        """
        self.references_dir = Path(references_dir)
        self.images_dir = Path(images_dir)
        self.source_dir = Path(source_dir) if source_dir else self.DEFAULT_NETWORK_BASE
        self.dry_run = dry_run
        self.force = force
        self.skip_copy = skip_copy

        # Statistics
        self.stats = {
            'total_images': 0,
            'copied': 0,
            'skipped': 0,
            'missing': 0,
            'md_files_updated': 0
        }

    def organize_images(self) -> Dict[str, int]:
        """
        Main orchestration: collect images, copy them, update MD files.

        Returns:
            Statistics dictionary
        """
        print(f"Image Manager - {'DRY RUN' if self.dry_run else 'LIVE RUN'}")
        print(f"References: {self.references_dir}")
        print(f"Images: {self.images_dir}")
        print(f"Source: {self.source_dir}")
        print()

        # Step 1: Create directory structure
        self._create_directories()

        # Step 2: Collect all image paths from MD files
        image_map = self._collect_image_paths()

        self.stats['total_images'] = len(image_map)
        print(f"Found {self.stats['total_images']} images in MD files")
        print()

        # Step 3: Copy images (unless --skip-copy)
        if not self.skip_copy:
            self._copy_images(image_map)
            print()

        # Step 4: Update MD file paths
        self._update_md_paths()

        # Step 5: Report
        self._print_report()

        return self.stats

    def _create_directories(self):
        """Create local image directory structure."""
        if self.dry_run:
            print(f"[DRY RUN] Would create directories under {self.images_dir}")
            return

        self.images_dir.mkdir(parents=True, exist_ok=True)

        for family_dir in self.FAMILY_DIRS.values():
            (self.images_dir / family_dir).mkdir(exist_ok=True)

        print(f"Created directory structure at {self.images_dir}")

    def _collect_image_paths(self) -> Dict[str, Tuple[str, str]]:
        """
        Collect all image paths from MD files.

        Returns:
            Dict mapping network_path -> (family, filename)
        """
        image_map = {}

        for family_file in get_all_family_files(self.references_dir):
            family = family_file.stem
            products = parse_family_md(family_file)

            for product in products:
                for image in product.get('images', []):
                    network_path = image.get('chemin', '')
                    if network_path and '\\\\' in network_path:
                        # Parse filename from path
                        filename = Path(network_path).name
                        image_map[network_path] = (family, filename)

        return image_map

    def _copy_images(self, image_map: Dict[str, Tuple[str, str]]):
        """
        Copy images from network share to local directories.

        Args:
            image_map: Dict mapping network_path -> (family, filename)
        """
        for network_path, (family, filename) in image_map.items():
            target_dir = self.images_dir / self.FAMILY_DIRS.get(family, family)
            target_file = target_dir / filename

            # Check if already exists
            if target_file.exists() and not self.force:
                print(f"[SKIP] {target_file.name} (already exists)")
                self.stats['skipped'] += 1
                continue

            # Resolve source path
            # Network path format: \\tse\commun\BE\Chiffrage\Fiches Techniques\Génération FT\{subfolder}\{filename}
            # We need to parse the subfolder from the network path
            source_file = self._resolve_source_path(network_path)

            if self.dry_run:
                if source_file and source_file.exists():
                    print(f"[DRY RUN] Would copy {filename} -> {target_dir.name}/")
                    self.stats['copied'] += 1
                else:
                    print(f"[DRY RUN] Would create .missing placeholder for {filename}")
                    self.stats['missing'] += 1
                continue

            # Try to copy
            if source_file and source_file.exists():
                try:
                    shutil.copy2(source_file, target_file)
                    print(f"[COPY] {filename} -> {target_dir.name}/")
                    self.stats['copied'] += 1
                except Exception as e:
                    print(f"[ERROR] Failed to copy {filename}: {e}")
                    self._create_missing_placeholder(target_file, network_path)
                    self.stats['missing'] += 1
            else:
                print(f"[MISSING] {filename} (network share not accessible)")
                self._create_missing_placeholder(target_file, network_path)
                self.stats['missing'] += 1

    def _resolve_source_path(self, network_path: str) -> Path:
        r"""
        Resolve source path from network UNC path.

        Args:
            network_path: UNC path like \\tse\commun\...\Vues\paillasses\file.png

        Returns:
            Resolved Path object
        """
        # Parse the subfolder structure from network path
        # Example: \\tse\commun\BE\Chiffrage\Fiches Techniques\Génération FT\Vues\paillasses\PM-D-H-75.png
        # We want: {source_dir}/Vues/paillasses/PM-D-H-75.png

        # Remove UNC prefix and extract relative path after base
        path_str = network_path.replace('\\', '/')

        # Find where the relative path starts after "Génération FT"
        base_marker = "Génération FT/"
        if base_marker in path_str:
            relative_part = path_str.split(base_marker, 1)[1]
            return self.source_dir / relative_part

        # Fallback: just take the filename
        return self.source_dir / Path(network_path).name

    def _create_missing_placeholder(self, target_file: Path, original_path: str):
        """
        Create a .missing placeholder file noting the original path.

        Args:
            target_file: Target file path
            original_path: Original network path
        """
        placeholder = target_file.with_suffix(target_file.suffix + '.missing')
        placeholder.write_text(
            f"Missing image\n"
            f"Original path: {original_path}\n"
            f"Date: {datetime.now().isoformat()}\n",
            encoding='utf-8'
        )

    def _update_md_paths(self):
        """Update MD files to use local paths instead of network paths."""
        for family_file in get_all_family_files(self.references_dir):
            family = family_file.stem

            if self.dry_run:
                print(f"[DRY RUN] Would update paths in {family_file.name}")
                continue

            # Read file content
            with open(family_file, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # Check if Images table already has "Chemin Original" column
            has_original_column = '| Position | Chemin | Chemin Original |' in content

            if not has_original_column:
                # Add "Chemin Original" column to header
                content = content.replace(
                    '| Position | Chemin | Left | Top | Width | Height | Shape Index |',
                    '| Position | Chemin | Chemin Original | Left | Top | Width | Height | Shape Index |'
                )
                content = content.replace(
                    '|----------|--------|------|-----|-------|--------|-------------|',
                    '|----------|--------|-----------------|------|-----|-------|--------|-------------|'
                )

            # Replace network paths with local paths
            # Pattern: \\tse\commun\BE\Chiffrage\Fiches Techniques\Génération FT\{path}\{filename}
            def replace_path(match):
                full_line = match.group(0)
                network_path = match.group(1)
                rest_of_line = match.group(2)

                # Extract filename
                filename = Path(network_path).name

                # Build local path
                local_path = f"Delagrave/images/{family}/{filename}"

                if has_original_column:
                    # Format already has Chemin Original, just update Chemin
                    return f"| {{}} | {local_path} | {network_path} {rest_of_line}"
                else:
                    # Insert Chemin Original column
                    return f"| {{}} | {local_path} | {network_path} {rest_of_line}"

            # Match image table rows: | {position} | {network_path} | {left} | ...
            # We need to preserve the position placeholder
            pattern = r'\| ([^|]+) \| (\\\\[^|]+) \| ([^|]+) \|'

            # Actually, let's do this more carefully by parsing line by line
            lines = content.split('\n')
            new_lines = []
            in_images_section = False

            for i, line in enumerate(lines):
                if line.strip() == '### Images':
                    in_images_section = True
                    new_lines.append(line)
                elif in_images_section and line.startswith('###'):
                    in_images_section = False
                    new_lines.append(line)
                elif in_images_section and '\\\\' in line and line.startswith('|'):
                    # This is an image path line
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 8:
                        position = parts[1]
                        network_path = parts[2]
                        filename = Path(network_path).name
                        local_path = f"Delagrave/images/{family}/{filename}"

                        if has_original_column:
                            # Already new format: | Pos | Chemin | Chemin Original | L | T | W | H | SI |
                            # parts: ['', pos, chemin, chemin_orig, left, top, width, height, shape_idx, '']
                            network_path = parts[3]
                            filename = Path(network_path).name
                            local_path = f"Delagrave/images/{family}/{filename}"
                            new_line = f"| {parts[1]} | {local_path} | {network_path} | {parts[4]} | {parts[5]} | {parts[6]} | {parts[7]} | {parts[8]} |"
                        else:
                            # Old format being converted: | Pos | Chemin | L | T | W | H | SI |
                            # parts: ['', pos, chemin, left, top, width, height, shape_idx, '']
                            new_line = f"| {position} | {local_path} | {network_path} | {parts[3]} | {parts[4]} | {parts[5]} | {parts[6]} | {parts[7]} |"

                        new_lines.append(new_line)
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)

            content = '\n'.join(new_lines)

            # Write back if changed
            if content != original_content:
                with open(family_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"[UPDATE] {family_file.name}")
                self.stats['md_files_updated'] += 1
            else:
                print(f"[NO CHANGE] {family_file.name}")

    def _print_report(self):
        """Print final statistics report."""
        print()
        print("=" * 50)
        print("IMAGE ORGANIZATION REPORT")
        print("=" * 50)
        print(f"Total images found:      {self.stats['total_images']}")
        print(f"Successfully copied:     {self.stats['copied']}")
        print(f"Already present (skipped): {self.stats['skipped']}")
        print(f"Missing (.missing created): {self.stats['missing']}")
        print(f"MD files updated:        {self.stats['md_files_updated']}")
        print("=" * 50)


def main():
    """CLI entry point for image manager."""
    parser = argparse.ArgumentParser(
        description="Organize product images from network share to local directories"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without modifying files'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Re-copy even if local file exists'
    )
    parser.add_argument(
        '--source-dir',
        type=Path,
        help='Override network share base path (for testing)'
    )
    parser.add_argument(
        '--skip-copy',
        action='store_true',
        help='Only update MD paths without copying images'
    )
    parser.add_argument(
        '--references-dir',
        type=Path,
        default=Path('Delagrave/references'),
        help='Path to references directory (default: Delagrave/references)'
    )
    parser.add_argument(
        '--images-dir',
        type=Path,
        default=Path('Delagrave/images'),
        help='Path to images directory (default: Delagrave/images)'
    )

    args = parser.parse_args()

    organizer = ImageOrganizer(
        references_dir=args.references_dir,
        images_dir=args.images_dir,
        source_dir=args.source_dir,
        dry_run=args.dry_run,
        force=args.force,
        skip_copy=args.skip_copy
    )

    organizer.organize_images()


if __name__ == '__main__':
    main()
