"""Generate the gendoc user manual as PDF in Deploy/ folder."""

from fpdf import FPDF
from pathlib import Path


class ManualPDF(FPDF):
    """Custom PDF class for the gendoc user manual."""

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(120, 120, 120)
            self.cell(0, 8, "GENDOC - Mode d'emploi", align="L")
            self.cell(0, 8, f"Page {self.page_no()}", align="R", new_x="LMARGIN", new_y="NEXT")
            self.line(10, 16, 200, 16)
            self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, "Delagrave EMSM - Generateur de Fiches Techniques v1.6", align="C")

    def cover_page(self):
        self.add_page()
        self.ln(50)
        self.set_font("Helvetica", "B", 32)
        self.set_text_color(0, 51, 102)
        self.cell(0, 15, "GENDOC", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)
        self.set_font("Helvetica", "", 18)
        self.set_text_color(80, 80, 80)
        self.cell(0, 10, "Generateur de Fiches Techniques", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(3)
        self.cell(0, 10, "Mode d'emploi", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(20)
        self.set_draw_color(0, 51, 102)
        self.set_line_width(0.8)
        self.line(60, self.get_y(), 150, self.get_y())
        self.ln(20)
        self.set_font("Helvetica", "", 12)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "Delagrave EMSM", align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 8, "Version 1.6 - Fevrier 2026", align="C", new_x="LMARGIN", new_y="NEXT")

    def chapter_title(self, num, title):
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(0, 51, 102)
        self.ln(8)
        self.cell(0, 12, f"{num}. {title}", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(0, 51, 102)
        self.set_line_width(0.5)
        self.line(10, self.get_y() + 1, 200, self.get_y() + 1)
        self.ln(6)

    def section_title(self, title):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(51, 51, 51)
        self.ln(4)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def subsection_title(self, title):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(80, 80, 80)
        self.ln(2)
        self.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def code_block(self, text):
        self.set_fill_color(240, 240, 240)
        self.set_font("Courier", "", 9)
        self.set_text_color(30, 30, 30)
        x = self.get_x()
        y = self.get_y()
        lines = text.strip().split("\n")
        block_h = len(lines) * 5.5 + 6
        # Check if we need a page break
        if y + block_h > 270:
            self.add_page()
            y = self.get_y()
        self.rect(10, y, 190, block_h, style="F")
        self.set_xy(13, y + 3)
        for i, line in enumerate(lines):
            self.cell(0, 5.5, line, new_x="LMARGIN", new_y="NEXT")
            if i < len(lines) - 1:
                self.set_x(13)
        self.ln(4)

    def bullet(self, text, bold_prefix=""):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        x = self.get_x()
        self.cell(8, 5.5, "-")
        if bold_prefix:
            self.set_font("Helvetica", "B", 10)
            self.cell(self.get_string_width(bold_prefix) + 1, 5.5, bold_prefix)
            self.set_font("Helvetica", "", 10)
            self.multi_cell(0, 5.5, text)
        else:
            self.multi_cell(0, 5.5, text)
        self.ln(1)

    def info_box(self, title, text):
        self.set_fill_color(230, 242, 255)
        self.set_draw_color(0, 102, 204)
        y = self.get_y()
        lines = text.split("\n")
        h = len(lines) * 5.5 + 14
        if y + h > 270:
            self.add_page()
            y = self.get_y()
        self.rect(10, y, 190, h, style="DF")
        self.set_xy(13, y + 3)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(0, 51, 102)
        self.cell(0, 6, title, new_x="LMARGIN", new_y="NEXT")
        self.set_x(13)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(40, 40, 40)
        for line in lines:
            self.cell(0, 5.5, line, new_x="LMARGIN", new_y="NEXT")
            self.set_x(13)
        self.set_y(y + h + 3)

    def warning_box(self, text):
        self.set_fill_color(255, 243, 224)
        self.set_draw_color(230, 126, 34)
        y = self.get_y()
        lines = text.split("\n")
        h = len(lines) * 5.5 + 10
        if y + h > 270:
            self.add_page()
            y = self.get_y()
        self.rect(10, y, 190, h, style="DF")
        self.set_xy(13, y + 3)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(180, 95, 6)
        self.cell(6, 5.5, "/!\\")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(40, 40, 40)
        for line in lines:
            self.cell(0, 5.5, line, new_x="LMARGIN", new_y="NEXT")
            self.set_x(13)
        self.set_y(y + h + 3)

    def table_header(self, cols, widths):
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(0, 51, 102)
        self.set_text_color(255, 255, 255)
        for col, w in zip(cols, widths):
            self.cell(w, 7, col, border=1, fill=True, align="C")
        self.ln()

    def table_row(self, cells, widths, fill=False):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(40, 40, 40)
        if fill:
            self.set_fill_color(245, 245, 245)
        for cell, w in zip(cells, widths):
            self.cell(w, 6.5, cell, border=1, fill=fill, align="L")
        self.ln()


def build_manual():
    pdf = ManualPDF()

    # =========================================================================
    # COVER PAGE
    # =========================================================================
    pdf.cover_page()

    # =========================================================================
    # TABLE OF CONTENTS
    # =========================================================================
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 12, "Table des matieres", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    toc = [
        ("1", "Presentation generale"),
        ("2", "Installation et configuration"),
        ("3", "Demarrage rapide"),
        ("4", "Workflow complet : du devis aux fiches"),
        ("5", "Outils disponibles"),
        ("6", "Gestion des articles speciaux (SP)"),
        ("7", "Administration du catalogue"),
        ("8", "Structure des dossiers"),
        ("9", "Depannage"),
        ("10", "Glossaire"),
    ]
    for num, title in toc:
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(8, 7, num + ".")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")

    # =========================================================================
    # 1. PRESENTATION GENERALE
    # =========================================================================
    pdf.add_page()
    pdf.chapter_title("1", "Presentation generale")

    pdf.body_text(
        "GENDOC est un outil de generation automatique de fiches techniques pour les produits Delagrave. "
        "Il fonctionne comme un assistant integre a Claude CLI (Intelligence Artificielle) qui transforme "
        "un devis PDF en un dossier PowerPoint complet de fiches techniques, pret a envoyer au client."
    )

    pdf.section_title("Principe de fonctionnement")
    pdf.body_text(
        "1. Vous fournissez un devis PDF a Claude\n"
        "2. L'outil analyse le devis et identifie les references produit\n"
        "3. Il recupere les informations de chaque produit dans le catalogue partage\n"
        "4. Il genere un fichier PowerPoint avec une fiche par produit\n"
        "5. Le resultat est sauvegarde dans un dossier dedie au devis"
    )

    pdf.section_title("Ce que l'outil gere automatiquement")
    pdf.bullet("Identification des references produit dans le devis PDF")
    pdf.bullet("Recherche des donnees produit (titre, description, dimensions, images)")
    pdf.bullet("Classement des fiches par famille de produits")
    pdf.bullet("Generation des pages de revetement quand necessaire")
    pdf.bullet("Creation du dossier de sortie isole par devis")
    pdf.bullet("Journal d'execution (LOG.md) pour tracer les operations")

    widths = [60, 25]
    families = [
        ("Paillasse", "54"), ("Meubles", "45"), ("Fiches existantes", "26"),
        ("Tables en", "23"), ("Equipement", "122"), ("Elec-sorb", "14"),
        ("Revetement", "12"), ("Sorbonne", "10"), ("Armoire securite", "6"),
        ("Enceinte ventilee", "4"), ("Complements", "1"),
    ]
    # Section title(15) + body text(20) + table: header(7) + rows(71.5) + total(6.5) = ~120
    section_and_table = 15 + 20 + 7 + len(families) * 6.5 + 6.5
    if pdf.get_y() + section_and_table > 272:
        pdf.add_page()

    pdf.section_title("Catalogue de references")
    pdf.body_text(
        "Le catalogue contient 317 references reparties en 11 familles de produits. "
        "Les donnees sont stockees sur le lecteur reseau partage et accessibles en lecture "
        "par tous les postes."
    )
    pdf.set_auto_page_break(auto=False)
    pdf.table_header(["Famille", "Nb ref."], widths)
    for i, (fam, nb) in enumerate(families):
        pdf.table_row([fam, nb], widths, fill=(i % 2 == 0))
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(0, 51, 102)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(60, 6.5, "Total", border=1, fill=True, align="L")
    pdf.cell(25, 6.5, "317", border=1, fill=True, align="L")
    pdf.ln(6)
    pdf.set_auto_page_break(auto=True, margin=25)

    # =========================================================================
    # 2. INSTALLATION ET CONFIGURATION
    # =========================================================================
    pdf.add_page()
    pdf.chapter_title("2", "Installation et configuration")

    pdf.body_text(
        "Ce chapitre explique comment installer GENDOC sur un nouveau poste de travail. "
        "L'installation complete prend environ 15 minutes."
    )

    pdf.section_title("2.1 Pre-requis logiciels")
    pdf.body_text("Trois logiciels doivent etre installes sur le poste :")
    pdf.bullet("Python 3.10 ou superieur (telechargeable sur python.org)", "Python : ")
    pdf.bullet("Node.js 18 ou superieur (telechargeable sur nodejs.org)", "Node.js : ")
    pdf.bullet("Claude CLI (installe via npm apres Node.js)", "Claude CLI : ")

    pdf.body_text("Verifier les installations :")
    pdf.code_block("python --version\nnode --version\nclaude --version")

    pdf.info_box("Installation rapide",
        "Le dossier Deploy/ contient un script automatique :\n"
        "Double-cliquez sur LANCER_INSTALLATION.bat\n"
        "Le script verifie et installe tout automatiquement.")

    pdf.section_title("2.2 Installation du package gendoc")
    pdf.body_text(
        "1. Copier le dossier du projet sur le poste local :\n"
        "   Exemple : C:\\gendoc\\\n\n"
        "2. Ouvrir un terminal dans ce dossier\n\n"
        "3. Installer le package :"
    )
    pdf.code_block("pip install -e .")
    pdf.body_text("4. Verifier l'installation :")
    pdf.code_block('python -c "from gendoc.mcp.server import main; print(\'OK\')"')

    pdf.section_title("2.3 Mise en place du catalogue Delagrave")
    pdf.body_text(
        "Le catalogue Delagrave contient les fiches produits, les images et le template PowerPoint. "
        "Il est inclus dans le ZIP de deploiement (dossier Delagrave/). "
        "Il doit etre accessible par tous les postes utilisateurs."
    )

    pdf.subsection_title("Option A : Dossier reseau partage (recommande)")
    pdf.body_text(
        "Copiez le dossier Delagrave/ du ZIP vers un emplacement partage sur le reseau, "
        "accessible en lecture par tous les utilisateurs :"
    )
    pdf.code_block(
        "1. Ouvrir le lecteur reseau partage (ex: S:\\)\n"
        "2. Copier le dossier Delagrave/ du ZIP vers S:\\Delagrave\\\n"
        "3. Verifier que les sous-dossiers sont presents :\n"
        "   S:\\Delagrave\\references\\     (14 fichiers .md)\n"
        "   S:\\Delagrave\\images\\          (321 images par famille)\n"
        "   S:\\Delagrave\\Modele fiches - Powerpoint\\  (1 fichier .potm)"
    )
    pdf.body_text(
        "Tous les postes pointeront vers ce meme dossier partage dans leur gendoc.json. "
        "Seul le poste administrateur (admin=true) peut modifier le catalogue."
    )

    pdf.subsection_title("Option B : Dossier local (poste autonome)")
    pdf.body_text(
        "Si le poste n'a pas acces au reseau, copiez le dossier Delagrave/ directement "
        "dans le dossier du projet :"
    )
    pdf.code_block(
        "C:\\gendoc\\\n"
        "  Delagrave/          <-- copier ici\n"
        "    references/\n"
        "    images/\n"
        "    Modele fiches - Powerpoint/\n"
        "  src/\n"
        "  gendoc.json\n"
        "  ..."
    )
    pdf.body_text(
        "Dans ce cas, le champ network_share_path de gendoc.json pointera vers "
        "C:\\\\gendoc\\\\Delagrave (chemin local)."
    )

    pdf.warning_box("Ne pas modifier les fichiers du catalogue manuellement.\n"
        "Utilisez les outils GENDOC (add_reference, update_reference)\n"
        "depuis le poste administrateur uniquement.")

    pdf.section_title("2.4 Configuration de gendoc.json")
    pdf.body_text(
        "Le fichier gendoc.json indique au systeme ou trouver les donnees partagees. "
        "Creez ce fichier dans le dossier du projet (ou copiez gendoc.json.example) :"
    )
    pdf.code_block(
        '{\n'
        '    "network_share_path": "S:\\\\Delagrave",\n'
        '    "admin": false\n'
        '}'
    )

    widths_cfg = [50, 140]
    pdf.table_header(["Champ", "Description"], widths_cfg)
    pdf.table_row(["network_share_path",
        "Chemin vers le dossier Delagrave partage (UNC ou lettre lecteur)"],
        widths_cfg, fill=True)
    pdf.table_row(["admin",
        "false = utilisateur normal, true = administrateur du catalogue"],
        widths_cfg)
    pdf.ln(3)

    pdf.body_text(
        "Le dossier reseau doit contenir trois sous-dossiers :"
    )
    pdf.bullet("references/ (les fiches produits au format markdown)")
    pdf.bullet("images/ (les photos des produits, classees par famille)")
    pdf.bullet("Modele fiches - Powerpoint/ (le template PowerPoint .potm)")

    pdf.body_text("Verifier la configuration :")
    pdf.code_block('python -c "from gendoc.utils.config_loader import load_config; '
                   'c = load_config(); print(\'OK:\', c[\'references_dir\'])"')

    pdf.warning_box("Si le chemin reseau est incorrect, le serveur MCP refuse de demarrer\n"
        "avec un message explicite indiquant le probleme.")

    pdf.section_title("2.5 Emplacement du fichier de configuration")
    pdf.body_text(
        "Le systeme recherche gendoc.json dans cet ordre :\n"
        "1. gendoc.json dans le dossier de travail courant\n"
        "2. .gendoc.json dans le dossier utilisateur (%USERPROFILE%)\n"
        "3. gendoc.json a cote de server.py (mode developpement)"
    )

    pdf.section_title("2.6 Enregistrement MCP pour Claude CLI")
    pdf.body_text(
        "Claude CLI detecte automatiquement les serveurs MCP via un fichier .mcp.json "
        "a la racine du projet. Copiez .mcp.json.example et adaptez les chemins :"
    )
    pdf.code_block(
        '{\n'
        '    "mcpServers": {\n'
        '        "gendoc": {\n'
        '            "command": "python",\n'
        '            "args": ["-m", "gendoc.mcp.server"],\n'
        '            "cwd": "C:/gendoc",\n'
        '            "env": {\n'
        '                "PYTHONPATH": "C:/gendoc/src"\n'
        '            }\n'
        '        }\n'
        '    }\n'
        '}'
    )
    pdf.body_text(
        "Remplacez C:/gendoc par le chemin reel du projet sur votre poste.\n"
        "Utilisez des / (slash) ou des \\\\\\\\ (double antislash) dans les chemins."
    )

    pdf.section_title("2.7 Verification finale")
    pdf.body_text("Ouvrez Claude CLI dans le dossier du projet :")
    pdf.code_block("cd C:\\gendoc\nclaude")
    pdf.body_text(
        "Les 12 outils GENDOC doivent apparaitre dans les outils MCP disponibles. "
        "Testez avec une commande simple :"
    )
    pdf.code_block('> Liste les familles de produits')

    # =========================================================================
    # 3. DEMARRAGE RAPIDE
    # =========================================================================
    pdf.add_page()
    pdf.chapter_title("3", "Demarrage rapide")

    pdf.body_text(
        "Ce chapitre vous guide pour votre premiere utilisation de l'outil."
    )

    pdf.section_title("Etape 1 : Ouvrir Claude CLI")
    pdf.body_text(
        "Ouvrez un terminal (invite de commandes ou PowerShell) dans le dossier du projet gendoc, "
        "puis lancez Claude :"
    )
    pdf.code_block("cd C:\\gendoc\nclaude")
    pdf.body_text(
        "Claude demarre et affiche un curseur de saisie. Les outils GENDOC sont charges automatiquement."
    )

    pdf.section_title("Etape 2 : Generer des fiches depuis un devis")
    pdf.body_text("Demandez simplement a Claude de generer les fiches :")
    pdf.code_block('> Genere les fiches techniques pour le devis "C:\\Devis\\devis-client.pdf"')
    pdf.body_text(
        "Claude va :\n"
        "  1. Analyser le devis PDF\n"
        "  2. Identifier les references produit\n"
        "  3. Vous montrer un apercu de ce qui sera genere\n"
        "  4. Generer le PowerPoint\n"
        "  5. Sauvegarder dans ./output/<numero_devis>/"
    )

    pdf.section_title("Etape 3 : Recuperer le resultat")
    pdf.body_text(
        "Le fichier PowerPoint et le journal d'execution se trouvent dans :"
    )
    pdf.code_block("output/\n  25_64_0637/           <-- numero du devis\n    fiches.pptx        <-- le PowerPoint\n    LOG.md             <-- journal d'execution")

    pdf.info_box("Conseil", "Vous pouvez aussi demander a Claude des operations ponctuelles :\n"
        "\"Cherche la reference PM-D-H-75\"\n"
        "\"Liste les familles de produits\"\n"
        "\"Donne-moi les infos du produit SH-E-105\"")

    # =========================================================================
    # 4. WORKFLOW COMPLET
    # =========================================================================
    pdf.add_page()
    pdf.chapter_title("4", "Workflow complet : du devis aux fiches")

    pdf.section_title("4.1 Analyse du devis")
    pdf.body_text(
        "La premiere etape consiste a analyser le devis PDF. L'outil extrait automatiquement :"
    )
    pdf.bullet("Le numero de devis, la date, le client, le titre de l'affaire", "En-tete : ")
    pdf.bullet("Les codes produit standard (ex: PM-D-H-75, SH-E-105)", "References : ")
    pdf.bullet("Les articles speciaux prefixes SP (ex: SPPAIL-12345)", "Articles SP : ")
    pdf.bullet("Les codes de revetement (ex: REV-GRES, REV-RES)", "Revetements : ")
    pdf.bullet("Les forfaits et lignes de service (automatiquement exclus)", "Forfaits : ")

    pdf.code_block('> Analyse le devis "C:\\Devis\\mon-devis.pdf"')

    pdf.section_title("4.2 Apercu de la generation")
    pdf.body_text(
        "Avant de generer, Claude affiche un apercu detaille :"
    )
    pdf.bullet("Produits identifies, groupes par famille")
    pdf.bullet("Revetements qui seront ajoutes automatiquement")
    pdf.bullet("Codes inconnus qui seront ignores")
    pdf.bullet("Nombre de pages estime")
    pdf.body_text("Vous pouvez valider ou demander des ajustements avant de continuer.")

    pdf.section_title("4.3 Generation du PowerPoint")
    pdf.body_text(
        "La generation cree un fichier PowerPoint utilisant le modele Delagrave officiel. "
        "Chaque produit genere une ou deux pages (selon la famille) avec :"
    )
    pdf.bullet("Titre et reference du produit")
    pdf.bullet("Description technique complete")
    pdf.bullet("Tableau des dimensions disponibles")
    pdf.bullet("Photo(s) du produit")

    pdf.section_title("4.4 Organisation des fiches")
    pdf.body_text(
        "Les fiches sont automatiquement classees par famille dans cet ordre :\n"
        "Paillasses > Sorbonnes > Meubles > Equipements > Armoires > Enceintes > "
        "Accessoires > Complements > Revetements"
    )

    pdf.section_title("4.5 Sortie par devis")
    pdf.body_text(
        "Chaque generation cree un dossier isole dans ./output/ nomme d'apres le numero du devis. "
        "Ainsi, plusieurs generations ne se melangent jamais."
    )

    # =========================================================================
    # 5. OUTILS DISPONIBLES
    # =========================================================================
    pdf.add_page()
    pdf.chapter_title("5", "Outils disponibles")

    pdf.body_text(
        "GENDOC expose 12 outils via le protocole MCP. Vous n'avez pas besoin de les appeler "
        "directement : demandez simplement a Claude ce que vous voulez faire, et il utilisera "
        "le bon outil automatiquement."
    )

    pdf.section_title("Outils de consultation (tous les utilisateurs)")

    pdf.subsection_title("lookup_reference")
    pdf.body_text("Recherche un produit par son code exact et renvoie toutes ses donnees.")
    pdf.code_block('> Donne-moi les infos du produit PM-D-H-75')

    pdf.subsection_title("search_references")
    pdf.body_text("Recherche par mot-cle partiel dans les codes et titres (limite a 50 resultats).")
    pdf.code_block('> Cherche tous les produits contenant "PM-D"')

    pdf.subsection_title("list_families")
    pdf.body_text("Liste toutes les familles de produits avec le nombre de references par famille.")
    pdf.code_block('> Liste les familles de produits')

    pdf.section_title("Outils de generation (tous les utilisateurs)")

    pdf.subsection_title("analyze_devis")
    pdf.body_text("Analyse un fichier PDF de devis et extrait les references, revetements, forfaits.")
    pdf.code_block('> Analyse le devis "C:\\Devis\\devis.pdf"')

    pdf.subsection_title("preview_generation")
    pdf.body_text("Affiche un apercu de ce que la generation produira (familles, pages, codes inconnus).")

    pdf.subsection_title("generate_slides")
    pdf.body_text("Genere le fichier PowerPoint a partir d'une liste de codes produit.")
    pdf.code_block('> Genere les fiches pour le devis "C:\\Devis\\devis.pdf"')

    pdf.section_title("Outils pour articles speciaux (SP)")

    pdf.subsection_title("create_custom_product")
    pdf.body_text("Clone un produit standard et applique des modifications pour un article special.")

    pdf.subsection_title("open_sp_selector")
    pdf.body_text("Ouvre un selecteur HTML interactif pour configurer les articles SP.")

    pdf.subsection_title("load_sp_selection")
    pdf.body_text("Charge la configuration SP depuis le fichier JSON exporte par le selecteur.")

    pdf.section_title("Outils d'administration (admin uniquement)")

    pdf.warning_box("Ces outils necessitent \"admin\": true dans gendoc.json.\nIls sont desactives sur les postes utilisateurs.")

    pdf.subsection_title("add_reference")
    pdf.body_text("Ajoute un nouveau produit au catalogue (famille, code, titre, description, images).")

    pdf.subsection_title("update_reference")
    pdf.body_text("Modifie un produit existant (titre, texte, dimensions, images).")

    pdf.subsection_title("delete_reference")
    pdf.body_text("Supprime un produit du catalogue.")

    # =========================================================================
    # 6. ARTICLES SPECIAUX (SP)
    # =========================================================================
    pdf.add_page()
    pdf.chapter_title("6", "Gestion des articles speciaux (SP)")

    pdf.body_text(
        "Les articles speciaux (prefixes SP, ex: SPPAIL-12345) sont des produits sur mesure "
        "qui n'existent pas dans le catalogue standard. L'outil offre un workflow dedie pour "
        "generer leurs fiches techniques."
    )

    pdf.section_title("Workflow SP")
    pdf.body_text(
        "1. L'analyse du devis detecte les codes SP automatiquement\n"
        "2. Claude propose d'ouvrir le selecteur SP (page HTML interactive)\n"
        "3. Dans le selecteur, vous :\n"
        "   - Associez chaque article SP a un produit standard de base\n"
        "   - Modifiez le titre, la description, les dimensions\n"
        "   - Exportez la configuration en JSON\n"
        "4. Claude charge le JSON et genere les fiches avec les personnalisations"
    )

    pdf.section_title("Selecteur HTML interactif")
    pdf.body_text(
        "Le selecteur s'ouvre dans votre navigateur. Il affiche la liste des articles SP "
        "detectes dans le devis et permet de :"
    )
    pdf.bullet("Rechercher dans le catalogue pour trouver le produit de base le plus proche")
    pdf.bullet("Visualiser les informations du produit de base")
    pdf.bullet("Editer les champs a personnaliser (titre, description)")
    pdf.bullet("Exporter la configuration finale en JSON")

    pdf.body_text(
        "Le fichier JSON exporte et le selecteur HTML sont sauvegardes dans le dossier "
        "de sortie du devis (./output/<numero_devis>/)."
    )

    # =========================================================================
    # 7. ADMINISTRATION
    # =========================================================================
    pdf.add_page()
    pdf.chapter_title("7", "Administration du catalogue")

    pdf.warning_box("Cette section concerne uniquement le poste administrateur (admin=true).")

    pdf.section_title("Ajouter un produit")
    pdf.body_text("Demandez a Claude d'ajouter un nouveau produit :")
    pdf.code_block('> Ajoute un nouveau produit dans la famille paillasse\n'
                   '  Code: PM-NEW-01\n'
                   '  Titre: Paillasse speciale 180cm\n'
                   '  Description: Paillasse de laboratoire...')
    pdf.body_text(
        "L'outil cree la reference dans le fichier markdown de la famille, copie les images "
        "fournies, et met a jour l'index automatiquement."
    )

    pdf.section_title("Modifier un produit")
    pdf.code_block('> Modifie le titre du produit PM-D-H-75 en\n'
                   '  "Paillasse droite HPL 750mm - version 2"')

    pdf.section_title("Supprimer un produit")
    pdf.code_block('> Supprime la reference PM-OLD-01')
    pdf.body_text(
        "La suppression retire le produit du fichier markdown de sa famille, "
        "supprime ses images, et rafraichit l'index."
    )

    pdf.info_box("Securite", "Les operations CRUD sont protegees par le flag admin.\n"
        "Sur un poste utilisateur (admin=false), toute tentative de modification\n"
        "renvoie : \"Operation reservee a l'administrateur\".")

    # =========================================================================
    # 8. STRUCTURE DES DOSSIERS
    # =========================================================================
    pdf.add_page()
    pdf.chapter_title("8", "Structure des dossiers")

    pdf.section_title("Dossier partage reseau (Delagrave)")
    pdf.code_block(
        "Delagrave/\n"
        "  references/                     Fiches produits (markdown)\n"
        "    _index.md                     Index des familles\n"
        "    _parametrage.md               Parametrage\n"
        "    paillasse.md                  54 references\n"
        "    sorbonne.md                   10 references\n"
        "    meubles.md                    45 references\n"
        "    equipement.md                 122 references\n"
        "    ...                           (11 familles au total)\n"
        "  images/                         Images produits\n"
        "    paillasse/\n"
        "    sorbonne/\n"
        "    ...                           (1 dossier par famille)\n"
        "  Modele fiches - Powerpoint/\n"
        "    Modele fiche technique...potm  Template PowerPoint"
    )

    pdf.section_title("Dossier local du projet")
    pdf.code_block(
        "C:\\gendoc\\\n"
        "  src/gendoc/                     Code source Python\n"
        "  gendoc.json                     Configuration locale\n"
        "  .mcp.json                       Enregistrement MCP\n"
        "  pyproject.toml                  Definition du package\n"
        "  Deploy/                         Scripts de deploiement\n"
        "  DEPLOY.md                       Guide de deploiement\n"
        "  output/                         Sorties generees\n"
        "    25_64_0637/                   Dossier par devis\n"
        "      fiches.pptx\n"
        "      LOG.md"
    )

    pdf.section_title("Configuration (gendoc.json)")
    pdf.code_block(
        '{\n'
        '    "network_share_path": "S:\\\\Delagrave",\n'
        '    "admin": false\n'
        '}'
    )
    pdf.bullet("Chemin UNC ou lettre de lecteur vers le dossier Delagrave partage", "network_share_path : ")
    pdf.bullet("true sur le poste admin, false sur les postes utilisateurs", "admin : ")

    # =========================================================================
    # 9. DEPANNAGE
    # =========================================================================
    pdf.add_page()
    pdf.chapter_title("9", "Depannage")

    problems = [
        ("Config file not found",
         "Le fichier gendoc.json est introuvable.",
         "Creez gendoc.json dans le dossier du projet avec le champ network_share_path."),
        ("network_share_path does not exist",
         "Le chemin reseau configure est inaccessible.",
         "Verifiez que le lecteur reseau est mappe. Verifiez le chemin dans gendoc.json."),
        ("Required subdirectory 'references/' not found",
         "Le chemin pointe vers le mauvais dossier.",
         "Corrigez network_share_path pour pointer vers le dossier Delagrave contenant references/."),
        ("Required template file not found",
         "Le template PowerPoint est absent.",
         "Verifiez que le fichier .potm existe dans 'Modele fiches - Powerpoint/'."),
        ("Operation reservee a l'administrateur",
         "Vous essayez une operation admin sur un poste utilisateur.",
         "Normal. Les modifications du catalogue sont reservees au poste admin (admin=true)."),
        ("Les outils MCP n'apparaissent pas dans Claude",
         "Configuration MCP incorrecte ou chemin errone.",
         "Verifiez .mcp.json (cwd et PYTHONPATH). Relancez Claude CLI dans le dossier du projet."),
        ("Import error au demarrage",
         "Le package n'est pas installe correctement.",
         "Relancez 'pip install -e .' depuis le dossier du projet."),
        ("Le PowerPoint est vide ou incomplet",
         "Certaines references du devis ne sont pas dans le catalogue.",
         "Verifiez le LOG.md pour identifier les codes inconnus. Ajoutez les au catalogue si necessaire."),
    ]

    for erreur, cause, solution in problems:
        pdf.subsection_title(erreur)
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5.5, f"Cause : {cause}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(0, 102, 0)
        pdf.cell(0, 5.5, f"Solution : {solution}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    # =========================================================================
    # 10. GLOSSAIRE
    # =========================================================================
    pdf.add_page()
    pdf.chapter_title("10", "Glossaire")

    glossary = [
        ("Claude CLI", "Interface en ligne de commande pour l'IA Claude d'Anthropic"),
        ("MCP", "Model Context Protocol - protocole de communication entre Claude et les outils"),
        ("Devis", "Document PDF listant les produits commandes par un client"),
        ("Fiche technique", "Page PowerPoint presentant un produit (titre, description, dimensions, photo)"),
        ("Famille", "Categorie de produits (paillasse, sorbonne, meuble, etc.)"),
        ("Article SP", "Article special sur mesure, non present dans le catalogue standard"),
        ("Revetement", "Materiau de surface (gres, resine, etc.) ajoute automatiquement aux fiches"),
        ("CRUD", "Create/Read/Update/Delete - operations de gestion du catalogue"),
        ("Network share", "Dossier partage sur le reseau contenant le catalogue Delagrave"),
        ("gendoc.json", "Fichier de configuration local du poste de travail"),
        (".mcp.json", "Fichier d'enregistrement du serveur MCP pour Claude CLI"),
        ("LOG.md", "Journal d'execution genere a chaque operation de generation"),
        ("Template POTM", "Modele PowerPoint Delagrave utilise pour generer les fiches"),
    ]

    widths_g = [40, 150]
    pdf.table_header(["Terme", "Definition"], widths_g)
    for i, (terme, definition) in enumerate(glossary):
        pdf.table_row([terme, definition], widths_g, fill=(i % 2 == 0))

    # =========================================================================
    # OUTPUT
    # =========================================================================
    out = Path("Deploy/GENDOC_Manuel.pdf")
    pdf.output(str(out))
    print(f"PDF genere : {out}")
    print(f"Pages : {pdf.pages_count}")


if __name__ == "__main__":
    build_manual()
