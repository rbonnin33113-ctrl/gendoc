# Phase 3: Analyse de Devis - Context

**Gathered:** 2026-02-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Parser un devis PDF Delagrave pour extraire les references produit presentes, les associer a leurs familles, detecter les revetements, et signaler les references inconnues. L'utilisateur appelle `/gendoc-analyze` avec un PDF et obtient un rapport structure.

</domain>

<decisions>
## Implementation Decisions

### Quantites
- **PAS de quantites** — extraire seulement les references uniques (1 de chaque code article)
- Un meme code present dans plusieurs sections du devis = 1 seule occurrence dans le resultat

### Format du resultat
- Code article + famille associee (Paillasse, Sorbonne, Meuble, etc.)
- Pas de donnees detaillees (titre, texte, dimensions) — juste code + famille

### Revetements
- Garder le code complet tel quel dans le resultat (ex: PM-D-H-75-GE)
- ET noter le revetement detecte comme information supplementaire (ex: revetement = GE)
- Produire une liste dedupliquee des fiches revetement a generer (ex: GE - Glace emaillee, GR - Gres)

### References inconnues
- Lister les codes non trouves dans les fichiers MD en fin de rapport
- Pas de fuzzy match ni de suggestions — simple liste
- Ne pas bloquer l'analyse — continuer et signaler

### Forfaits
- Les forfaits (FPORT, FORPOSE1J, etc.) ne sont pas des produits
- Les lister dans une section separee "Forfaits ignores" pour transparence
- Ne pas les inclure dans les references produit

### En-tete du devis
- Extraire numero de devis, date, nom du client depuis la page de garde
- Ces infos seront utiles pour nommer le fichier PowerPoint genere en Phase 4

### Claude's Discretion
- Choix de la librairie de parsing PDF
- Structure interne des modules (parser vs analyzer)
- Gestion des cas limites (PDF mal formate, pages vides)
- Detection des sorbonnes autoportantes necessitant un revetement

</decisions>

<specifics>
## Specific Ideas

- Le resultat doit etre exploitable directement par la Phase 4 (generation PowerPoint) — la liste des codes + familles + revetements est l'input du generateur
- Les forfaits listes separement permettent a l'utilisateur de verifier que rien d'important n'a ete ignore

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 03-analyse-de-devis*
*Context gathered: 2026-02-10*
