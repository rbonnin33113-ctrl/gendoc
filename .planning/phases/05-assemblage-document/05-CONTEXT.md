# Phase 5: Assemblage Document - Context

**Gathered:** 2026-02-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Transformer les slides individuelles generees en Phase 4 en un dossier PowerPoint complet et professionnel : page de garde, pages de separation par famille/chapitre, sommaire avec numeros de page. Un seul format de sortie (les modes CHI/DOE/FTI sont hors scope v1).

</domain>

<decisions>
## Implementation Decisions

### Page de garde
- Construite programmatiquement (pas le layout 0 du template)
- Elements : bandeau couleur bleu Delagrave (extraire du template), logo Delagrave (fichier image dans le dossier projet), titre du projet extrait du devis PDF, infos devis (numero, date, client)
- Mise en page sobre : bandeau haut/bas, logo, titre centre, infos devis en dessous

### Structure chapitres
- Ordre fixe predetermine des familles (Paillasses, Sorbonnes, Revetements, Meubles, Tables EN, Equipement, Elec sorb, Complements)
- Page de separation programmatique entre chaque famille (meme style que la page de garde : bandeau couleur + nom de famille)
- Sous-groupes a l'interieur des familles equipement/elec-sorb/complements

### Sous-groupes
- Claude determine les sous-groupes logiques a partir des titres et codes produit
- Pas de mapping manuel requis

### Sommaire
- Place apres la page de garde (page 2)
- Niveau de detail : famille + chaque produit
- Numeros de page reels du PowerPoint affiches
- Format : nom famille en gras, puis liste des codes produit avec numero de page

### Modes de generation
- **Hors scope v1** — un seul format de sortie
- Le parametre mode="FTI" reste comme valeur par defaut mais n'affecte pas le contenu
- Les modes CHI/DOE seront implementes dans un futur milestone

### Claude's Discretion
- Couleur exacte du bleu Delagrave (extraire du template .potm)
- Localisation du logo dans le dossier projet
- Algorithme de sous-groupement des produits equipement/elec-sorb
- Typographie et espacement de la page de garde et des separateurs
- Format exact du sommaire (police, alignement, pointilles)

</decisions>

<specifics>
## Specific Ideas

- Pages de garde et separateurs construits programmatiquement (shapes Python, pas de layout template)
- Meme charte graphique entre page de garde et pages de separation de chapitre
- Titre du projet/affaire extrait automatiquement du devis PDF (pas de saisie utilisateur)

</specifics>

<deferred>
## Deferred Ideas

- Modes CHI/DOE/FTI — futur milestone, chaque mode definit un niveau d'exhaustivite different
- Integration des fiches existantes (.pptx pre-faits) dans le mode DOE
- Complements auto-lies aux familles (ex: fiche compact liee aux paillasses stratifie)

</deferred>

---

*Phase: 05-assemblage-document*
*Context gathered: 2026-02-10*
