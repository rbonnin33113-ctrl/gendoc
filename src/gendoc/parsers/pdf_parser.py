"""
PDF Parser for Delagrave quote documents.

This module provides core PDF text extraction functionality for analyzing
Delagrave quote PDFs. It is the single source of truth for PDF reading operations.

This is a pure library module with no I/O operations (no print/input).
"""

from pathlib import Path
from typing import Dict, List
import re
import pdfplumber


def extract_text(pdf_path: Path) -> List[str]:
    """
    Extract text from a PDF file, returning one string per page.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        List of strings, one per page

    Raises:
        FileNotFoundError: If the PDF file does not exist
        ValueError: If the file is not a valid PDF

    Example:
        >>> pages = extract_text(Path("Devis Test.pdf"))
        >>> len(pages)
        5
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            pages = []
            for page in pdf.pages:
                text = page.extract_text()
                pages.append(text if text else "")
            return pages
    except Exception as e:
        raise ValueError(f"Invalid PDF file: {pdf_path}") from e


def extract_header(pages_text: List[str]) -> Dict[str, str]:
    """
    Extract header metadata from the first page of the quote.

    Extracts:
    - numero_devis: Quote number (e.g., "25 64 0637")
    - date: Quote date (e.g., "20/10/2025")
    - client: Client company name (e.g., "INOVIE BIOPYRENEES")

    Args:
        pages_text: List of page texts from extract_text()

    Returns:
        Dictionary with keys: numero_devis, date, client
        Empty strings are returned for any field not found.

    Example:
        >>> header = extract_header(pages_text)
        >>> header['numero_devis']
        '25 64 0637'
    """
    header = {
        "numero_devis": "",
        "date": "",
        "client": ""
    }

    if not pages_text:
        return header

    first_page = pages_text[0]

    # Extract quote number: "OFFRE DE PRIX N°... 25 64 0637"
    # Pattern: OFFRE DE PRIX N followed by quote number (format: XX XX XXXX)
    numero_match = re.search(
        r'OFFRE DE PRIX N.*?(\d{2}\s*\d{2}\s*\d{4})',
        first_page,
        re.IGNORECASE
    )
    if numero_match:
        header["numero_devis"] = numero_match.group(1).strip()

    # Extract date: "Romilly sur Andelle le 20/10/2025"
    date_match = re.search(
        r'Romilly sur Andelle le (\d{2}/\d{2}/\d{4})',
        first_page,
        re.IGNORECASE
    )
    if date_match:
        header["date"] = date_match.group(1).strip()

    # Extract client name: Multiple strategies to find client name
    # The client name typically appears on the first line after Delagrave address

    # Strategy 1: First line pattern - "Address COMPANY NAME"
    # Example: "350, Rue Blingue INOVIE BIOPYRENEES"
    # Look for 2+ consecutive all-caps words at the end of the line
    lines = first_page.split('\n')
    if lines:
        first_line = lines[0].strip()
        # Pattern: Multiple consecutive all-caps words (company name) at end of line
        # Matches: "INOVIE BIOPYRENEES", "COMPANY NAME", etc.
        first_line_match = re.search(
            r'([A-Z]{2,}(?:\s+[A-Z]{2,})+)$',
            first_line
        )
        if first_line_match:
            candidate = first_line_match.group(1).strip()
            # Exclude "Delagrave" itself
            if 'DELAGRAVE' not in candidate.upper():
                header["client"] = candidate

    # Strategy 2: Look for company name after "Référence" or before "A l'attention de"
    if not header["client"]:
        for i, line in enumerate(lines[:20]):  # Check first 20 lines only
            line_stripped = line.strip()
            # Check if line contains "Référence" or similar
            if 'r�f�rence' in line_stripped.lower() or 'reference' in line_stripped.lower():
                # Company name might be on this line or next lines
                for j in range(i, min(i + 3, len(lines))):
                    candidate = lines[j].strip()
                    # Look for all-caps words (company names are typically in caps)
                    caps_match = re.search(r'([A-Z][A-Z\s&\'-]{5,})', candidate)
                    if caps_match and 'DELAGRAVE' not in caps_match.group(1):
                        header["client"] = caps_match.group(1).strip()
                        break
                if header["client"]:
                    break

    return header
