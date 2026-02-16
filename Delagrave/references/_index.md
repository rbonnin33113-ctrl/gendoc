# Index des References Delagrave

> Source: Génération Fiche Technique DELAGRAVE.xlsm
> Extraction: 2026-02-16
> Total: 317 references dans 11 familles

## Familles

| Famille | Fichier | Nb references | Type |
|---------|---------|---------------|------|
| Paillasse | [paillasse.md](paillasse.md) | 54 | PPT (texte + dimensions + image) |
| Sorbonne | [sorbonne.md](sorbonne.md) | 10 | PPT (texte + dimensions + image) |
| Revètement | [revetement.md](revetement.md) | 12 | PPT (texte + 2 images) |
| Meubles | [meubles.md](meubles.md) | 45 | PPT (texte + image) |
| Tables EN | [tables-en.md](tables-en.md) | 23 | PPT (texte + image) |
| Equipement | [equipement.md](equipement.md) | 122 | PPT (images positionnees) |
| Elec sorb | [elec-sorb.md](elec-sorb.md) | 14 | PPT (images positionnees) |
| Compléments | [complements.md](complements.md) | 1 | PPT (images positionnees) |
| Fiches Existantes | [fiches-existantes.md](fiches-existantes.md) | 26 | EXT (fichiers .pptx) |
| Armoire Securite | [armoire-securite.md](armoire-securite.md) | 6 | PPT (texte + image) |
| Enceinte Ventilée (PSM) | [enceinte-ventilee.md](enceinte-ventilee.md) | 4 | PPT (texte + image) |

## Structure d'un fichier famille

Chaque fichier MD contient :
- En-tête : nom famille, source, date, compteur
- Sections `## {Code}` : une par produit
  - Tableau identité : code, ref, titre, famille
  - `### Texte` : contenu descriptif
  - `### Dimensions` : tableau avec valeur, prefix PPTX, shape index
  - `### Images` : tableau avec chemin, position (left/top/width/height), shape index
  - `### Metadata PowerPoint` : mapping complet colonnes -> shapes

## Fichiers speciaux

| Fichier | Role |
|---------|------|
| [_index.md](_index.md) | Ce fichier - point d'entree |
| [_parametrage.md](_parametrage.md) | Config mapping famille -> template PowerPoint |
