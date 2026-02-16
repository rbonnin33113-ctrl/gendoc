# Requirements: Generateur de Fiches Techniques Delagrave

**Defined:** 2026-02-16
**Core Value:** Un utilisateur soumet un devis PDF et obtient automatiquement un dossier PowerPoint complet de fiches techniques — sans intervention manuelle.

## v1.6 Requirements

Requirements pour le deploiement multi-postes. Chaque requirement mappe a une phase du roadmap.

### Configuration

- [ ] **CFG-01**: Le systeme lit un fichier `gendoc.json` local pour connaitre le chemin du dossier partage reseau
- [ ] **CFG-02**: Si le fichier config n'existe pas au demarrage, le serveur MCP signale une erreur claire avec instructions
- [ ] **CFG-03**: Le systeme valide au demarrage que le dossier partage est accessible et contient les donnees attendues (references/, images/, template)

### Output

- [ ] **OUT-01**: Chaque generation de devis cree un sous-dossier dedie dans `./output/{numero_devis}/`
- [ ] **OUT-02**: Le fichier PowerPoint genere est ecrit dans le sous-dossier du devis
- [ ] **OUT-03**: Le LOG.md de l'execution est ecrit dans le sous-dossier du devis
- [ ] **OUT-04**: Le SP selector HTML et le JSON d'export sont ecrits dans le sous-dossier du devis

### Controle d'acces

- [ ] **ACL-01**: Le fichier config contient un flag `admin` (true/false)
- [ ] **ACL-02**: Les outils CRUD (add_reference, update_reference, delete_reference) sont desactives quand admin=false
- [ ] **ACL-03**: Un message d'erreur clair est retourne si un utilisateur non-admin tente une operation CRUD

### Deploiement

- [ ] **DEP-01**: Le package Python peut etre installe/execute depuis un dossier copie localement
- [ ] **DEP-02**: La configuration MCP pour Claude CLI est documentee et reproductible
- [ ] **DEP-03**: Un script ou guide de deploiement permet de configurer un nouveau poste

### Non-regression

- [ ] **REG-01**: Tous les 123 tests existants passent apres la refactorisation des chemins
- [ ] **REG-02**: Tests specifiques pour la resolution des chemins depuis la config
- [ ] **REG-03**: Tests pour le mode admin vs utilisateur

## Future Requirements

Differes des milestones precedents, hors scope v1.6.

- **GEN-01**: Modes de generation CHI/DOE/FTI
- **GEN-02**: Integration des fiches-existantes (.pptx pre-existants)
- **SYNC-01**: Synchronisation automatique Excel -> MD

## Out of Scope

| Feature | Reason |
|---------|--------|
| Installation via pip/registry | Deploiement par copie locale suffit pour le nombre de postes |
| Interface web d'administration | L'admin utilise Claude CLI comme les autres |
| Gestion des permissions Windows (ACL filesystem) | Le flag admin dans la config suffit |
| Mise a jour automatique du code | Copie manuelle ou script de deploiement |
| Multi-tenancy (plusieurs catalogues) | Un seul catalogue partage par tous |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| CFG-01 | — | Pending |
| CFG-02 | — | Pending |
| CFG-03 | — | Pending |
| OUT-01 | — | Pending |
| OUT-02 | — | Pending |
| OUT-03 | — | Pending |
| OUT-04 | — | Pending |
| ACL-01 | — | Pending |
| ACL-02 | — | Pending |
| ACL-03 | — | Pending |
| DEP-01 | — | Pending |
| DEP-02 | — | Pending |
| DEP-03 | — | Pending |
| REG-01 | — | Pending |
| REG-02 | — | Pending |
| REG-03 | — | Pending |

**Coverage:**
- v1.6 requirements: 16 total
- Mapped to phases: 0
- Unmapped: 16

---
*Requirements defined: 2026-02-16*
*Last updated: 2026-02-16 after initial definition*
