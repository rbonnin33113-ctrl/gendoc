# Guide de Deploiement — Generateur de Fiches Techniques Delagrave

Ce guide permet de configurer un nouveau poste de travail pour utiliser le generateur de fiches techniques avec Claude CLI.

**Duree estimee : 15 minutes**

---

## 1. Pre-requis

Avant de commencer, verifier que le poste dispose de :

- **Python 3.10+** installe
  ```
  python --version
  ```
  Si absent : installer depuis [python.org](https://www.python.org/downloads/)

- **Claude CLI** installe et configure (acces au compte Anthropic)
  ```
  claude --version
  ```

- **Acces au lecteur reseau** contenant le dossier Delagrave partage (references, images, template PowerPoint)

---

## 2. Installation du package

1. Copier le dossier du projet sur le poste local (par exemple `C:\gendoc\`)

2. Ouvrir un terminal dans le dossier copie

3. Installer le package en mode developpement :
   ```
   pip install -e .
   ```

4. Verifier l'installation :
   ```
   python -c "from gendoc.mcp.server import main; print('OK')"
   ```
   Resultat attendu : `OK`

---

## 3. Configuration gendoc.json

Le systeme a besoin d'un fichier de configuration pour localiser les donnees partagees.

1. Copier le fichier `gendoc.json.example` et le renommer en `gendoc.json` :
   ```
   copy gendoc.json.example gendoc.json
   ```

2. Editer `gendoc.json` et adapter le chemin :
   ```json
   {
       "network_share_path": "S:\\Delagrave",
       "admin": false
   }
   ```

### Champs

| Champ | Description |
|-------|-------------|
| `network_share_path` | Chemin vers le dossier Delagrave partage. Accepte un chemin UNC (`\\\\serveur\\partage\\Delagrave`) ou une lettre de lecteur (`S:\Delagrave`). Ce dossier doit contenir `references/`, `images/`, et `Modele fiches - Powerpoint/`. |
| `admin` | Mettre `true` **uniquement** sur le poste administrateur qui gere le catalogue de references. Les postes utilisateurs gardent `false`. En mode utilisateur, les outils de modification du catalogue (ajout, modification, suppression) sont desactives. |

### Emplacement du fichier

Le systeme cherche le fichier de configuration dans cet ordre :
1. `gendoc.json` dans le dossier de travail courant
2. `.gendoc.json` dans le dossier utilisateur (`%USERPROFILE%`)
3. `gendoc.json` a cote de `server.py` (mode developpement)

### Verification

```
python -c "from gendoc.utils.config_loader import load_config; c = load_config(); print('Config OK:', c['references_dir'])"
```

Resultat attendu : `Config OK: S:\Delagrave\references` (avec votre chemin)

---

## 4. Enregistrement MCP pour Claude CLI

Claude CLI detecte automatiquement les serveurs MCP via un fichier `.mcp.json` a la racine du projet.

1. Copier le fichier `.mcp.json.example` et le renommer en `.mcp.json` :
   ```
   copy .mcp.json.example .mcp.json
   ```

2. Editer `.mcp.json` et adapter les chemins :
   ```json
   {
       "mcpServers": {
           "gendoc": {
               "command": "python",
               "args": ["-m", "gendoc.mcp.server"],
               "cwd": "C:/gendoc",
               "env": {
                   "PYTHONPATH": "C:/gendoc/src"
               }
           }
       }
   }
   ```

   Remplacer `C:/gendoc` par le chemin reel du projet sur le poste (utiliser des `/` ou `\\\\`).

3. Verification : ouvrir Claude CLI dans le dossier du projet. Les outils `gendoc` doivent apparaitre dans les outils MCP disponibles (12 outils).

---

## 5. Test de generation

Ouvrir Claude CLI dans le dossier du projet, puis tester :

1. **Recherche de reference** :
   > Cherche la reference PM-D-H-75

2. **Liste des familles** :
   > Liste les familles de produits

3. **Generation de fiches** :
   > Genere les fiches pour le devis [chemin_vers_un_devis.pdf]

Resultat attendu : un dossier `output/` cree dans le repertoire courant avec :
- Le fichier PowerPoint des fiches techniques
- Le fichier `LOG.md` de suivi d'execution

---

## 6. Depannage

| Erreur | Cause | Solution |
|--------|-------|----------|
| `Config file not found` | Fichier gendoc.json absent | Creer gendoc.json (voir section 3) |
| `network_share_path does not exist` | Chemin reseau inaccessible | Verifier le chemin, verifier que le lecteur reseau est mappe |
| `Required subdirectory 'references/' not found` | Le chemin pointe vers le mauvais dossier | Corriger network_share_path pour pointer vers le dossier Delagrave contenant references/ |
| `Required template file not found` | Template PowerPoint manquant | Verifier que `Modele fiche technique vide - Ind J.potm` est present dans `Modele fiches - Powerpoint/` |
| `Operation reservee a l'administrateur` | Mode utilisateur (admin=false) | Normal : les modifications du catalogue sont reservees a l'administrateur |
| Les outils MCP n'apparaissent pas | Configuration MCP incorrecte | Verifier .mcp.json, verifier PYTHONPATH, relancer Claude CLI |

---

## 7. Structure du dossier partage

Le dossier Delagrave sur le reseau doit contenir :

```
Delagrave/
  references/                              <- Fichiers MD des produits
    _index.md                              <- Index des familles
    _parametrage.md                        <- Parametrage des familles
    paillasse.md                           <- 11 familles de produits
    sorbonne.md
    hotte.md
    armoire-sous-paillasse.md
    armoire-haute.md
    armoire-securite.md
    enceinte-ventilee.md
    accessoire.md
    bac-laver.md
    meuble-de-rangement.md
    complement.md
  images/                                  <- Images produits par famille
    paillasse/
    sorbonne/
    hotte/
    armoire-sous-paillasse/
    armoire-haute/
    armoire-securite/
    enceinte-ventilee/
    accessoire/
    bac-laver/
    meuble-de-rangement/
    complement/
  Modele fiches - Powerpoint/
    Modele fiche technique vide - Ind J.potm  <- Template PowerPoint
```

---

*Guide de deploiement v1.6 — Generateur de Fiches Techniques Delagrave*
