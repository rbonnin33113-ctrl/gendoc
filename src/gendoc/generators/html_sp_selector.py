"""
HTML SP Selector Generator for Delagrave SP article editing.

This module generates a self-contained HTML page that allows users to:
1. View SP articles from a devis with their extracted designations
2. Search the catalog for a matching base product
3. Edit fields (titre, texte, dimensions, famille)
4. Export a JSON file compatible with generate_slides custom_products format

The HTML is fully self-contained with no external dependencies (CSS/JS inline).
"""

from pathlib import Path
from typing import Dict, List, Any
import json

from gendoc.parsers.md_parser import parse_family_md, get_all_family_files


def generate_sp_selector_html(
    sp_articles: List[Dict[str, Any]],
    references_dir: Path,
    output_path: Path
) -> Dict[str, Any]:
    """
    Generate a self-contained HTML page for SP article editing.

    Args:
        sp_articles: List of SP article dicts from analyze_devis 'speciaux' key
                    Each dict contains: {code, famille, prefix, designation}
        references_dir: Path to Delagrave/references/ directory
        output_path: Path where the HTML file will be written

    Returns:
        Dict with:
        - output_path: Path to generated HTML file
        - sp_count: Number of SP articles
        - catalog_size: Number of products in catalog

    Example:
        >>> result = generate_sp_selector_html(
        ...     sp_articles=[{'code': 'SPMOB-25355', 'famille': 'meubles', 'prefix': 'SPMOB', 'designation': 'Test'}],
        ...     references_dir=Path('Delagrave/references'),
        ...     output_path=Path('output/sp_selector.html')
        ... )
        >>> result['sp_count']
        1
    """
    # Ensure Path objects (accept strings too)
    references_dir = Path(references_dir)
    output_path = Path(output_path)

    # Build catalog from MD files
    catalog = _build_catalog_json(references_dir)

    # Get list of families for dropdown
    families = sorted(set(p['famille'] for p in catalog))

    # Generate HTML content
    html_content = _generate_html_template(sp_articles, catalog, families)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return {
        'output_path': str(output_path),
        'sp_count': len(sp_articles),
        'catalog_size': len(catalog)
    }


def _build_catalog_json(references_dir: Path) -> List[Dict[str, Any]]:
    """
    Build a lightweight catalog from MD files for embedding in HTML.

    Args:
        references_dir: Path to Delagrave/references/

    Returns:
        List of product dicts with essential fields for HTML UI

    Each product contains:
    - code: Product code
    - ref: Reference string
    - titre: Title
    - famille: Family name
    - texte: Descriptive text
    - dimensions: List of {name, valeur, prefix, shape_index}
    - images: List of {position, chemin}
    - metadata_pptx: List of {champ, type, prefix, shape_index}
    """
    catalog = []

    for family_file in get_all_family_files(references_dir):
        # Skip fiches-existantes (no standard product data)
        if family_file.stem == 'fiches-existantes':
            continue

        products = parse_family_md(family_file)

        for product in products:
            # Skip products with empty titles
            if not product.get('titre', '').strip():
                continue

            # Build lightweight product entry
            catalog_entry = {
                'code': product['code'],
                'ref': product['ref'],
                'titre': product['titre'],
                'famille': product['famille'],
                'texte': product['texte'],
                'dimensions': [
                    {
                        'name': dim['name'],
                        'valeur': dim['valeur'],
                        'prefix': dim.get('prefix', ''),
                        'shape_index': dim.get('shape_index', '')
                    }
                    for dim in product.get('dimensions', [])
                ],
                'images': [
                    {
                        'position': img['position'],
                        'chemin': img['chemin'],
                        'chemin_original': img.get('chemin_original', ''),
                        'left': img.get('left', 0),
                        'top': img.get('top', 0),
                        'width': img.get('width', 0),
                        'height': img.get('height', 0),
                        'shape_index': img.get('shape_index', '')
                    }
                    for img in product.get('images', [])
                ],
                'metadata_pptx': product.get('metadata_pptx', [])
            }

            catalog.append(catalog_entry)

    return catalog


def _generate_html_template(
    sp_articles: List[Dict[str, Any]],
    catalog: List[Dict[str, Any]],
    families: List[str]
) -> str:
    """
    Generate the complete HTML page with embedded data.

    Args:
        sp_articles: List of SP articles to edit
        catalog: List of products from catalog
        families: List of family names for dropdown

    Returns:
        Complete HTML string
    """
    # Convert data to JSON for embedding
    sp_articles_json = json.dumps(sp_articles, ensure_ascii=False, indent=2)
    catalog_json = json.dumps(catalog, ensure_ascii=False, indent=2)
    families_json = json.dumps(families, ensure_ascii=False, indent=2)

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sélecteur d'articles spéciaux (SP)</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #f5f5f5;
            padding: 20px;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1600px;
            margin: 0 auto;
        }}

        header {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}

        h1 {{
            color: #333;
            margin-bottom: 10px;
        }}

        .header-info {{
            color: #666;
            font-size: 14px;
        }}

        .main-content {{
            display: flex;
            gap: 20px;
        }}

        @media (max-width: 900px) {{
            .main-content {{
                flex-direction: column;
            }}
        }}

        .sp-panel {{
            flex: 0 0 40%;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            max-height: 800px;
            overflow-y: auto;
        }}

        .sp-panel h2 {{
            margin-bottom: 15px;
            color: #333;
            font-size: 18px;
        }}

        .sp-card {{
            border: 2px solid #e0e0e0;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .sp-card:hover {{
            border-color: #2196F3;
            background-color: #f8f9fa;
        }}

        .sp-card.selected {{
            border-color: #2196F3;
            background-color: #e3f2fd;
        }}

        .sp-card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}

        .sp-code {{
            font-weight: bold;
            font-size: 16px;
            color: #333;
        }}

        .status-badge {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }}

        .status-badge.unconfigured {{
            background-color: #ffebee;
            color: #c62828;
        }}

        .status-badge.configured {{
            background-color: #e8f5e9;
            color: #2e7d32;
        }}

        .famille-badge {{
            display: inline-block;
            padding: 2px 8px;
            background-color: #e3f2fd;
            color: #1976d2;
            border-radius: 4px;
            font-size: 12px;
            margin-bottom: 5px;
        }}

        .sp-designation {{
            color: #666;
            font-size: 13px;
            line-height: 1.4;
        }}

        .editor-panel {{
            flex: 1;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            max-height: 800px;
            overflow-y: auto;
        }}

        .editor-panel h2 {{
            margin-bottom: 15px;
            color: #333;
            font-size: 18px;
        }}

        .search-section {{
            margin-bottom: 20px;
        }}

        .search-input {{
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.2s;
        }}

        .search-input:focus {{
            outline: none;
            border-color: #2196F3;
        }}

        .search-results {{
            max-height: 300px;
            overflow-y: auto;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            margin-top: 10px;
            background: white;
        }}

        .search-result-item {{
            padding: 12px;
            border-bottom: 1px solid #f0f0f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .search-result-item:last-child {{
            border-bottom: none;
        }}

        .search-result-info {{
            flex: 1;
        }}

        .search-result-code {{
            font-weight: bold;
            color: #333;
            margin-bottom: 2px;
        }}

        .search-result-titre {{
            font-size: 13px;
            color: #666;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}

        .btn {{
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.2s;
        }}

        .btn-primary {{
            background-color: #2196F3;
            color: white;
        }}

        .btn-primary:hover {{
            background-color: #1976D2;
        }}

        .btn-primary:disabled {{
            background-color: #bdbdbd;
            cursor: not-allowed;
        }}

        .btn-success {{
            background-color: #4CAF50;
            color: white;
        }}

        .btn-success:hover {{
            background-color: #45a049;
        }}

        .btn-danger {{
            background-color: #f44336;
            color: white;
        }}

        .btn-danger:hover {{
            background-color: #d32f2f;
        }}

        .edit-form {{
            margin-top: 20px;
        }}

        .form-group {{
            margin-bottom: 20px;
        }}

        .form-label {{
            display: block;
            margin-bottom: 5px;
            font-weight: 500;
            color: #333;
        }}

        .form-control {{
            width: 100%;
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 4px;
            font-size: 14px;
            font-family: inherit;
        }}

        .form-control:focus {{
            outline: none;
            border-color: #2196F3;
        }}

        textarea.form-control {{
            resize: vertical;
            min-height: 80px;
        }}

        select.form-control {{
            cursor: pointer;
        }}

        .base-product-info {{
            background-color: #f8f9fa;
            padding: 12px;
            border-radius: 4px;
            margin-bottom: 20px;
            border-left: 4px solid #2196F3;
        }}

        .base-product-label {{
            font-size: 12px;
            color: #666;
            margin-bottom: 4px;
        }}

        .base-product-code {{
            font-weight: bold;
            color: #333;
        }}

        .dimensions-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 5px;
        }}

        .dimensions-table th,
        .dimensions-table td {{
            padding: 8px;
            border: 1px solid #e0e0e0;
            text-align: left;
        }}

        .dimensions-table th {{
            background-color: #f5f5f5;
            font-weight: 500;
            font-size: 13px;
        }}

        .dimensions-table td {{
            font-size: 13px;
        }}

        .dimensions-table input {{
            width: 100%;
            padding: 6px;
            border: 1px solid #e0e0e0;
            border-radius: 3px;
        }}

        .image-position {{
            font-weight: 500;
            color: #333;
            font-size: 13px;
        }}

        .export-section {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-top: 20px;
            text-align: center;
        }}

        .export-status {{
            margin-bottom: 15px;
            font-size: 16px;
            color: #333;
        }}

        .export-status strong {{
            color: #2196F3;
        }}

        .empty-state {{
            text-align: center;
            padding: 40px 20px;
            color: #999;
        }}

        .hidden {{
            display: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Sélecteur d'articles spéciaux (SP)</h1>
            <div class="header-info">
                <span id="sp-count">{len(sp_articles)} article(s) spécial(spéciaux) à configurer</span>
            </div>
        </header>

        <div class="main-content">
            <div class="sp-panel">
                <h2>Articles SP du devis</h2>
                <div id="sp-list"></div>
            </div>

            <div class="editor-panel">
                <h2>Configuration de l'article</h2>

                <div id="no-selection" class="empty-state">
                    <p>Sélectionnez un article SP dans la liste de gauche pour commencer.</p>
                </div>

                <div id="editor-content" class="hidden">
                    <div class="search-section">
                        <label class="form-label">Rechercher un produit de base dans le catalogue</label>
                        <input type="text" id="search-input" class="search-input" placeholder="Rechercher par code ou titre...">
                        <div id="search-results" class="search-results hidden"></div>
                    </div>

                    <div id="edit-form-container" class="hidden">
                        <div class="base-product-info">
                            <div class="base-product-label">Produit de base sélectionné</div>
                            <div class="base-product-code" id="base-product-code"></div>
                        </div>

                        <form id="edit-form" class="edit-form">
                            <div class="form-group">
                                <label class="form-label" for="edit-famille">Famille</label>
                                <select id="edit-famille" class="form-control">
                                </select>
                            </div>

                            <div class="form-group">
                                <label class="form-label" for="edit-titre">Titre</label>
                                <textarea id="edit-titre" class="form-control" rows="3"></textarea>
                            </div>

                            <div class="form-group">
                                <label class="form-label" for="edit-texte">Texte descriptif</label>
                                <textarea id="edit-texte" class="form-control" rows="5"></textarea>
                            </div>

                            <div class="form-group">
                                <label class="form-label">Dimensions</label>
                                <table class="dimensions-table" id="dimensions-table">
                                    <thead>
                                        <tr>
                                            <th>Dimension</th>
                                            <th>Valeur</th>
                                        </tr>
                                    </thead>
                                    <tbody id="dimensions-body"></tbody>
                                </table>
                            </div>

                            <div class="form-group">
                                <label class="form-label">Images</label>
                                <div id="images-editor"></div>
                            </div>

                            <div style="display: flex; gap: 10px;">
                                <button type="button" class="btn btn-success" onclick="validateArticle()">
                                    Valider cet article
                                </button>
                                <button type="button" class="btn btn-danger" id="cancel-btn" onclick="cancelArticle()" style="display:none;">
                                    Annuler la configuration
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>

        <div class="export-section">
            <div class="export-status">
                <span id="export-count">0 / {len(sp_articles)}</span> articles configurés
            </div>
            <button id="export-btn" class="btn btn-primary" onclick="exportJSON()" disabled>
                Exporter JSON
            </button>
            <button class="btn" style="background-color:#757575;color:white;margin-left:10px;" onclick="quitWithout()">
                Quitter sans configurer
            </button>
        </div>
    </div>

    <script>
        // Embedded data
        const SP_ARTICLES = {sp_articles_json};
        const CATALOG = {catalog_json};
        const FAMILIES = {families_json};

        // State management
        let selectedSPIndex = null;
        let selectedBaseProduct = null;
        let editedArticles = {{}};

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {{
            renderSPList();
            populateFamilySelect();
            updateExportButton();
        }});

        // Render SP article list
        function renderSPList() {{
            const container = document.getElementById('sp-list');
            container.innerHTML = '';

            SP_ARTICLES.forEach((sp, index) => {{
                const isConfigured = editedArticles.hasOwnProperty(index);

                const card = document.createElement('div');
                card.className = 'sp-card' + (selectedSPIndex === index ? ' selected' : '');
                card.onclick = () => selectSP(index);

                card.innerHTML = `
                    <div class="sp-card-header">
                        <div class="sp-code">${{sp.code}}</div>
                        <span class="status-badge ${{isConfigured ? 'configured' : 'unconfigured'}}">
                            ${{isConfigured ? 'Configuré' : 'Non configuré'}}
                        </span>
                    </div>
                    <div class="famille-badge">${{sp.famille}}</div>
                    <div class="sp-designation">${{sp.designation || 'Aucune désignation'}}</div>
                `;

                container.appendChild(card);
            }});
        }}

        // Select an SP article for editing
        function selectSP(index) {{
            selectedSPIndex = index;
            renderSPList();

            // Show editor, hide empty state
            document.getElementById('no-selection').classList.add('hidden');
            document.getElementById('editor-content').classList.remove('hidden');

            // Clear search
            document.getElementById('search-input').value = '';
            document.getElementById('search-results').classList.add('hidden');

            // If this SP was already configured, load its data
            if (editedArticles[index]) {{
                selectedBaseProduct = editedArticles[index].baseProduct;
                loadEditForm(editedArticles[index].data);
                document.getElementById('cancel-btn').style.display = '';
            }} else {{
                // Reset form
                document.getElementById('edit-form-container').classList.add('hidden');
                document.getElementById('cancel-btn').style.display = 'none';
                selectedBaseProduct = null;
            }}
        }}

        // Search catalog
        document.getElementById('search-input')?.addEventListener('input', function(e) {{
            const query = e.target.value.trim().toLowerCase();

            if (query.length < 2) {{
                document.getElementById('search-results').classList.add('hidden');
                return;
            }}

            const results = searchCatalog(query);
            renderSearchResults(results);
        }});

        function searchCatalog(query) {{
            const matches = CATALOG.filter(product =>
                product.code.toLowerCase().includes(query) ||
                product.titre.toLowerCase().includes(query)
            );

            return matches.slice(0, 20); // Limit to 20 results
        }}

        function renderSearchResults(results) {{
            const container = document.getElementById('search-results');

            if (results.length === 0) {{
                container.classList.add('hidden');
                return;
            }}

            container.innerHTML = '';

            results.forEach((product, index) => {{
                const item = document.createElement('div');
                item.className = 'search-result-item';

                item.innerHTML = `
                    <div class="search-result-info">
                        <div class="search-result-code">${{product.code}}</div>
                        <div class="search-result-titre">${{product.titre}}</div>
                        <small class="famille-badge">${{product.famille}}</small>
                    </div>
                    <button class="btn btn-primary" onclick="selectBaseProduct(${{index}}, event)">
                        Sélectionner
                    </button>
                `;

                container.appendChild(item);
            }});

            container.classList.remove('hidden');
        }}

        function selectBaseProduct(resultIndex, event) {{
            event.stopPropagation();

            const query = document.getElementById('search-input').value.trim().toLowerCase();
            const results = searchCatalog(query);
            const product = results[resultIndex];

            if (!product) return;

            selectedBaseProduct = product;

            // Auto-format title: "SPMOB-25042 (RB600D) - Meuble mobile ..."
            const sp = SP_ARTICLES[selectedSPIndex];
            const baseCode = product.code;
            // Strip base code prefix from title if present (e.g. "RB600D - Meuble..." -> "Meuble...")
            let desc = product.titre;
            if (desc.startsWith(baseCode)) {{
                desc = desc.substring(baseCode.length).replace(/^\\s*-\\s*/, '');
            }}
            const formattedProduct = Object.assign({{}}, product, {{
                titre: `${{sp.code}} (${{baseCode}}) - ${{desc}}`
            }});

            loadEditForm(formattedProduct);

            // Hide search results
            document.getElementById('search-results').classList.add('hidden');
        }}

        function loadEditForm(productData) {{
            document.getElementById('edit-form-container').classList.remove('hidden');
            document.getElementById('base-product-code').textContent = selectedBaseProduct.code;

            // Populate form fields
            document.getElementById('edit-famille').value = productData.famille || '';
            document.getElementById('edit-titre').value = productData.titre || '';
            document.getElementById('edit-texte').value = productData.texte || '';

            // Populate dimensions table
            const dimensionsBody = document.getElementById('dimensions-body');
            dimensionsBody.innerHTML = '';

            if (productData.dimensions && productData.dimensions.length > 0) {{
                productData.dimensions.forEach((dim, index) => {{
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${{dim.name}}</td>
                        <td><input type="text" class="dimension-value" data-index="${{index}}" value="${{dim.valeur || ''}}"></td>
                    `;
                    dimensionsBody.appendChild(row);
                }});
            }} else {{
                dimensionsBody.innerHTML = '<tr><td colspan="2" style="text-align: center; color: #999;">Aucune dimension</td></tr>';
            }}

            // Populate images editor
            const imagesEditor = document.getElementById('images-editor');
            imagesEditor.innerHTML = '';

            if (productData.images && productData.images.length > 0) {{
                productData.images.forEach((img, index) => {{
                    const div = document.createElement('div');
                    div.style.cssText = 'padding:8px;border:1px solid #e0e0e0;border-radius:4px;margin-bottom:8px;';
                    div.innerHTML = `
                        <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                            <span class="image-position">${{img.position}}</span>
                        </div>
                        <input type="text" class="form-control image-chemin" data-index="${{index}}" value="${{img.chemin || ''}}" placeholder="Chemin de l'image (ex: Delagrave/images/meubles/RB600D.jpg)">
                    `;
                    imagesEditor.appendChild(div);
                }});
            }} else {{
                imagesEditor.innerHTML = '<div style="color:#999;text-align:center;padding:10px;">Aucune image (produit de base sans image)</div>';
            }}
        }}

        function populateFamilySelect() {{
            const select = document.getElementById('edit-famille');
            select.innerHTML = '';

            FAMILIES.forEach(family => {{
                const option = document.createElement('option');
                option.value = family;
                option.textContent = family;
                select.appendChild(option);
            }});
        }}

        function collectImages() {{
            return (selectedBaseProduct.images || []).map((img, index) => {{
                const input = document.querySelector(`.image-chemin[data-index="${{index}}"]`);
                return {{
                    position: img.position,
                    chemin: input ? input.value : img.chemin,
                    chemin_original: img.chemin_original || '',
                    left: img.left || 0,
                    top: img.top || 0,
                    width: img.width || 0,
                    height: img.height || 0,
                    shape_index: img.shape_index || ''
                }};
            }});
        }}

        function cancelArticle() {{
            if (selectedSPIndex === null) return;

            delete editedArticles[selectedSPIndex];
            selectedBaseProduct = null;

            // Reset editor
            document.getElementById('edit-form-container').classList.add('hidden');
            document.getElementById('search-input').value = '';
            document.getElementById('search-results').classList.add('hidden');
            document.getElementById('cancel-btn').style.display = 'none';

            renderSPList();
            updateExportButton();
        }}

        function validateArticle() {{
            if (selectedSPIndex === null || !selectedBaseProduct) {{
                alert('Veuillez sélectionner un produit de base.');
                return;
            }}

            // Collect edited data
            const famille = document.getElementById('edit-famille').value;
            const titre = document.getElementById('edit-titre').value;
            const texte = document.getElementById('edit-texte').value;

            // Collect dimension values
            const dimensions = selectedBaseProduct.dimensions.map((dim, index) => {{
                const input = document.querySelector(`.dimension-value[data-index="${{index}}"]`);
                return {{
                    name: dim.name,
                    valeur: input ? input.value : dim.valeur,
                    prefix: dim.prefix,
                    shape_index: dim.shape_index
                }};
            }});

            // Build complete product data
            const editedData = {{
                code: SP_ARTICLES[selectedSPIndex].code,
                ref: selectedBaseProduct.ref,
                titre: titre,
                famille: famille,
                texte: texte,
                dimensions: dimensions,
                images: collectImages(),
                metadata_pptx: selectedBaseProduct.metadata_pptx || []
            }};

            // Save to state
            editedArticles[selectedSPIndex] = {{
                data: editedData,
                baseProduct: selectedBaseProduct
            }};

            // Update UI
            renderSPList();
            updateExportButton();

            // Move to next unconfigured SP if available
            const nextIndex = findNextUnconfigured();
            if (nextIndex !== null) {{
                selectSP(nextIndex);
            }}
        }}

        function findNextUnconfigured() {{
            for (let i = 0; i < SP_ARTICLES.length; i++) {{
                if (!editedArticles.hasOwnProperty(i)) {{
                    return i;
                }}
            }}
            return null;
        }}

        function updateExportButton() {{
            const configuredCount = Object.keys(editedArticles).length;
            document.getElementById('export-count').textContent = `${{configuredCount}} / ${{SP_ARTICLES.length}}`;

            const exportBtn = document.getElementById('export-btn');
            exportBtn.disabled = configuredCount === 0;
        }}

        async function quitWithout() {{
            if (!confirm('Quitter sans configurer les articles SP ? Aucun article SP ne sera inclus dans le dossier.')) return;

            // Save empty array so load_sp_selection finds the file
            if (window.location.protocol === 'http:' && window.location.hostname === '127.0.0.1') {{
                try {{
                    await fetch('/save', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: '[]'
                    }});
                }} catch (err) {{ /* ignore */ }}
            }}
            document.body.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;font-size:20px;color:#757575;">Aucun article SP configuré. Cette page va se fermer.</div>';
            setTimeout(() => window.close(), 1500);
        }}

        async function exportJSON() {{
            // Build custom_products array
            const customProducts = SP_ARTICLES.map((sp, index) => {{
                if (!editedArticles[index]) {{
                    console.error(`Article ${{sp.code}} not configured`);
                    return null;
                }}
                return editedArticles[index].data;
            }}).filter(item => item !== null);

            // Generate JSON
            const jsonStr = JSON.stringify(customProducts, null, 2);

            // If served from local server, POST to /save (saves directly to output dir)
            if (window.location.protocol === 'http:' && window.location.hostname === '127.0.0.1') {{
                try {{
                    const resp = await fetch('/save', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: jsonStr
                    }});
                    const result = await resp.json();
                    if (result.success) {{
                        document.body.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;font-size:20px;color:#2e7d32;">Fichier enregistré : ' + result.path + '<br>Cette page va se fermer.</div>';
                        setTimeout(() => window.close(), 1500);
                        return;
                    }}
                }} catch (err) {{
                    console.error('Erreur POST /save', err);
                }}
            }}

            // Fallback: trigger download (file:// protocol or server error)
            const blob = new Blob([jsonStr], {{ type: 'application/json' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'sp_selection.json';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            alert('Fichier JSON exporté dans le dossier Téléchargements.');
        }}
    </script>
</body>
</html>
"""

    return html
