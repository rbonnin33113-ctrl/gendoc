# Requirements: Generateur de Fiches Techniques Delagrave

**Defined:** 2026-02-18
**Core Value:** Un utilisateur soumet un devis PDF et obtient automatiquement un dossier PowerPoint complet de fiches techniques — sans intervention manuelle.

## v1.7 Requirements

Requirements pour le systeme de mise a jour. Chaque requirement mappe a une phase du roadmap.

### Version & Detection

- [ ] **VER-01**: Le serveur MCP compare la version locale avec la version distante (GitHub) au demarrage
- [ ] **VER-02**: Le numero de version suit le format semver (pyproject.toml comme source de verite)

### Notification

- [ ] **NOTIF-01**: L'utilisateur recoit un message dans Claude au demarrage quand une MAJ est disponible (version + changelog resume)
- [ ] **NOTIF-02**: Si a jour, aucun message supplementaire (silencieux)

### Installation MAJ

- [ ] **MAJ-01**: L'utilisateur peut lancer la mise a jour via un outil MCP (un clic)
- [ ] **MAJ-02**: Le script de MAJ execute git pull + pip install -e . automatiquement
- [ ] **MAJ-03**: Le resultat (succes/echec + version installee) est retourne dans Claude

### Deploiement

- [ ] **DEP-01**: Le script d'installation (install.ps1) inclut l'installation de Git
- [ ] **DEP-02**: Le script configure le clone initial du repo GitHub prive
- [ ] **DEP-03**: L'authentification GitHub est configuree une seule fois a l'installation (token ou SSH)

## Future Requirements

Deferred a un milestone ulterieur.

### Modes de generation

- **GEN-01**: Modes de generation CHI/DOE en plus de FTI
- **GEN-02**: Integration des fiches-existantes (.pptx pre-existants)

### Synchronisation

- **SYNC-01**: Synchronisation automatique Excel -> MD

## Out of Scope

| Feature | Reason |
|---------|--------|
| Auto-update sans confirmation | L'utilisateur doit valider la MAJ (pas de surprise) |
| Rollback de version | Trop complexe pour v1.7, git revert suffit en admin |
| MAJ donnees via git | Les donnees sont sur le reseau partage, pas dans le repo |
| CI/CD pipeline | Pas de serveur de build, deploiement git direct |
| MAJ du serveur MCP a chaud | Necessite redemarrage de Claude, MAJ = redemarrage |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| VER-01 | TBD | Pending |
| VER-02 | TBD | Pending |
| NOTIF-01 | TBD | Pending |
| NOTIF-02 | TBD | Pending |
| MAJ-01 | TBD | Pending |
| MAJ-02 | TBD | Pending |
| MAJ-03 | TBD | Pending |
| DEP-01 | TBD | Pending |
| DEP-02 | TBD | Pending |
| DEP-03 | TBD | Pending |

**Coverage:**
- v1.7 requirements: 10 total
- Mapped to phases: 0
- Unmapped: 10

---
*Requirements defined: 2026-02-18*
*Last updated: 2026-02-18 after initial definition*
