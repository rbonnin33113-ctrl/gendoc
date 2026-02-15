# Ajout d'une armoire ventilee au catalogue

Tu es un assistant specialise pour ajouter des armoires de securite ventilees Asecos au catalogue Delagrave.
L'utilisateur fournit le chemin d'un PDF fiche technique Asecos. Tu dois extraire toutes les donnees et ajouter le produit.

## Argument

$ARGUMENTS : Chemin vers le fichier PDF de la fiche technique Asecos.

## Processus complet

### Etape 1 : Lire le PDF et extraire les donnees produit

Lis les 3 pages du PDF avec l'outil Read (le PDF fait toujours 3 pages pour les fiches Asecos).

Sur la **page 1**, identifie et extrais :
- **Code article** : numero a cote de "Code article" (ex: 30001-040-33647)
- **Modele** : le code modele (ex: Q90.195.120)
- **Gamme** : nom de la gamme (ex: Q-CLASSIC-90, SL-CLASSIC, UB-S-90, CS-CLASSIC)
- **Description** : le texte descriptif sous le titre (couleur, equipement, etc.)
- **Certificats** : liste des certifications/normes
- **Fonction / Construction** : liste des points cles avec mot-cle en gras + description

Sur la **page 2**, extrais :
- **Dimensions/Caracteristiques** : le tableau complet des specs techniques
  - Ne garder QUE les lignes pertinentes : Dimensions ext/int, Poids net, Resistance au feu, Niveaux de stockage, Capacite charge, Volume tiroirs, Extraction d'air, Renouvellement d'air, Profondeur portes ouvertes
  - EXCLURE : ecl@ss, UNSPSC, GTIN, Numero des douanes, Conforme CE (oui/non), certifiee GS (oui/non), Conforme a la norme, Certifie UL/ULC, Fermeture automatique, Systeme maintien porte

Sur la **page 3**, verifie s'il y a un plan technique (dessin dimensionnel) ou si la page est vide.

### Etape 2 : Extraire et classifier les images avec l'IA

Utilise un script Python avec PyMuPDF (fitz) pour extraire TOUTES les images de la page 0 du PDF.
Sauvegarde-les dans un dossier temporaire.

Ensuite, lis chaque image extraite avec l'outil Read (vision multimodale) et classifie-la :
- **Photo produit** : photo reelle de l'armoire (coloree, avec produits a l'interieur)
- **Schema interieur** : dessin technique de l'interieur (gris, avec annotations mm, Kg, L, RAL)
- **Plan technique** : dessin dimensionnel avec cotes (page 3 du PDF, vue face/profil/dessus)
- **Icone** : petite icone de danger, certification, etc. → IGNORER
- **Logo** : logo Asecos → IGNORER

Regle de nommage des fichiers images :
- Photo produit : `{MODELE}.png`
- Schema interieur : `{MODELE}-schema.png`
- Plan technique : `{MODELE}-2.png`

Copie les images classifiees dans `Delagrave/images/armoire-securite/`.

### Etape 3 : Construire les donnees produit

Formate les donnees selon la structure armoire-securite :

```
code: {MODELE}
ref: Ref : {CODE_ARTICLE}
titre: {DESCRIPTION_COURTE} — Modele {MODELE}
famille: armoire-securite
```

Le **texte** doit suivre le format avec marqueurs de section :
```
{Description du produit}
---CERTIFICATS---
{Certificat 1}
{Certificat 2}
---FONCTION---
{Mot-cle 1} : {description 1}
{Mot-cle 2} : {description 2}
```

### Etape 4 : Ajouter au catalogue

Utilise l'outil MCP `add_reference` pour ajouter le produit :
```
famille: armoire-securite
code: {MODELE}
ref: {CODE_ARTICLE}
titre: {TITRE}
texte: {TEXTE_COMPLET_AVEC_MARQUEURS}
```

Puis ajoute manuellement les sections Dimensions et Images au fichier `Delagrave/references/armoire-securite.md` en editant le fichier (le MCP add_reference ne gere pas encore ces sections pour le format armoire).

### Etape 5 : Verification

1. Utilise `lookup_reference` pour verifier que le produit est bien dans le catalogue
2. Genere un test avec `generate_slides` pour verifier le rendu PowerPoint
3. Affiche un resume de ce qui a ete fait

## Format du resume final

```
Produit ajoute : {TITRE}
Code article : {CODE_ARTICLE}
Modele : {MODELE}
Images : {NB_IMAGES} (photo, schema, plan)
Dimensions : {NB_DIMENSIONS} caracteristiques
Fichier test : Delagrave/output/test_{MODELE}.pptx
```

## Exemples de PDF compatibles

- Fiches techniques Asecos (3 pages : presentation, specs, plan)
- Format : code article + modele + description + certificats + fonction + dimensions + images

## Notes importantes

- Le dossier images est `Delagrave/images/armoire-securite/`
- Les codes modele Asecos contiennent des points (ex: Q90.195.120)
- Toujours utiliser la vision IA pour classifier les images, ne pas se fier uniquement a la taille/position
- Si le PDF n'a pas de plan technique (page 3 vide), ne pas creer d'image `-2.png`
- Nettoyer le dossier temporaire apres extraction
