# ============================================================================
#  GENDOC - Script d'installation automatique
#  Generateur de Fiches Techniques Delagrave
# ============================================================================
#
#  Usage : clic droit sur install.ps1 > "Executer avec PowerShell"
#     ou : powershell -ExecutionPolicy Bypass -File install.ps1
#
# ============================================================================

param(
    [string]$InstallDir = "C:\gendoc",
    [string]$NetworkShare = ""
)

$ErrorActionPreference = "Stop"

# --- Couleurs et affichage ---------------------------------------------------

function Write-Banner($text) {
    Write-Host ""
    Write-Host ("=" * 60) -ForegroundColor Cyan
    Write-Host "  $text" -ForegroundColor Cyan
    Write-Host ("=" * 60) -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step($num, $text) {
    Write-Host "  [$num] $text" -ForegroundColor Yellow
}

function Write-OK($text) {
    Write-Host "   OK  $text" -ForegroundColor Green
}

function Write-Warn($text) {
    Write-Host "  !!  $text" -ForegroundColor Red
}

function Write-Info($text) {
    Write-Host "      $text" -ForegroundColor Gray
}

function Refresh-Path {
    $machinePath = [System.Environment]::GetEnvironmentVariable("Path", [System.EnvironmentVariableTarget]::Machine)
    $userPath = [System.Environment]::GetEnvironmentVariable("Path", [System.EnvironmentVariableTarget]::User)
    $env:Path = $machinePath + ";" + $userPath
}

# --- Dossier d'installation ---------------------------------------------------

Write-Banner "GENDOC - Installation automatique"

Write-Host "  Ou souhaitez-vous installer gendoc ?" -ForegroundColor Yellow
Write-Host "  (par defaut : $InstallDir)" -ForegroundColor Gray
Write-Host ""
$userDir = Read-Host "  Dossier d'installation (Entree = $InstallDir)"
if ($userDir -ne "") {
    $InstallDir = $userDir
}
Write-Host ""
Write-OK "Dossier d'installation : $InstallDir"
Write-Host ""

# --- Etape 1 : Verification Python -------------------------------------------

Write-Step 1 "Verification de Python..."

$pythonOK = $false
try {
    $pyVersion = python --version 2>&1
    if ($pyVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$Matches[1]
        $minor = [int]$Matches[2]
        if ($major -ge 3 -and $minor -ge 10) {
            Write-OK "Python $major.$minor detecte"
            $pythonOK = $true
        } else {
            Write-Warn "Python $major.$minor detecte - version 3.10+ requise"
        }
    }
} catch {
    Write-Warn "Python non trouve"
}

if (-not $pythonOK) {
    Write-Host ""
    Write-Host "  Python 3.10+ est requis. Options d'installation :" -ForegroundColor Yellow
    Write-Host ""

    # Detecter si winget est disponible
    $hasWinget = $false
    try { winget --version 2>&1 | Out-Null; $hasWinget = $true } catch {}

    if ($hasWinget) {
        Write-Host "  [A] Installer via winget (recommande)" -ForegroundColor White
        Write-Host "  [B] Telecharger l'installeur Python" -ForegroundColor White
        Write-Host "  [S] Passer (Python deja installe ailleurs)" -ForegroundColor White
        $choix = Read-Host "  Choix (A/B/S)"

        if ($choix -eq "A" -or $choix -eq "a") {
            Write-Info "Installation de Python via winget..."
            winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements
            Refresh-Path
            Write-OK "Python installe via winget"
            $pythonOK = $true
        }
        elseif ($choix -eq "B" -or $choix -eq "b") {
            $pyUrl = "https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe"
            $pyInstaller = "$env:TEMP\python-3.12.8-amd64.exe"
            Write-Info "Telechargement de Python 3.12.8..."
            Invoke-WebRequest -Uri $pyUrl -OutFile $pyInstaller -UseBasicParsing
            Write-Info "Lancement de l'installeur Python..."
            Write-Host "  IMPORTANT : cocher 'Add Python to PATH' dans l'installeur !" -ForegroundColor Red
            Start-Process -FilePath $pyInstaller -Wait
            Refresh-Path
            $pythonOK = $true
        }
    } else {
        Write-Host "  [T] Telecharger l'installeur Python" -ForegroundColor White
        Write-Host "  [S] Passer (Python deja installe ailleurs)" -ForegroundColor White
        $choix = Read-Host "  Choix (T/S)"

        if ($choix -eq "T" -or $choix -eq "t") {
            $pyUrl = "https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe"
            $pyInstaller = "$env:TEMP\python-3.12.8-amd64.exe"
            Write-Info "Telechargement de Python 3.12.8..."
            Invoke-WebRequest -Uri $pyUrl -OutFile $pyInstaller -UseBasicParsing
            Write-Info "Lancement de l'installeur Python..."
            Write-Host "  IMPORTANT : cocher 'Add Python to PATH' dans l'installeur !" -ForegroundColor Red
            Start-Process -FilePath $pyInstaller -Wait
            Refresh-Path
            $pythonOK = $true
        }
    }

    if (-not $pythonOK -and $choix -ne "S" -and $choix -ne "s") {
        Write-Warn "Python est requis pour continuer."
        Write-Host "  Installez Python 3.10+ puis relancez ce script." -ForegroundColor Gray
        Read-Host "  Appuyez sur Entree pour quitter"
        exit 1
    }
}

# --- Etape 2 : Verification Node.js (pour Claude CLI) ------------------------

Write-Step 2 "Verification de Node.js (requis pour Claude CLI)..."

$nodeOK = $false
try {
    $nodeVersion = node --version 2>&1
    if ($nodeVersion -match "v(\d+)") {
        $nodeMajor = [int]$Matches[1]
        if ($nodeMajor -ge 18) {
            Write-OK "Node.js $nodeVersion detecte"
            $nodeOK = $true
        } else {
            Write-Warn "Node.js $nodeVersion detecte - version 18+ requise"
        }
    }
} catch {
    Write-Warn "Node.js non trouve"
}

if (-not $nodeOK) {
    Write-Host ""
    Write-Host "  Node.js 18+ est requis pour Claude CLI." -ForegroundColor Yellow

    $hasWinget = $false
    try { winget --version 2>&1 | Out-Null; $hasWinget = $true } catch {}

    if ($hasWinget) {
        Write-Host "  [A] Installer via winget (recommande)" -ForegroundColor White
        Write-Host "  [T] Telecharger l'installeur Node.js" -ForegroundColor White
        Write-Host "  [S] Passer" -ForegroundColor White
        $choix = Read-Host "  Choix (A/T/S)"

        if ($choix -eq "A" -or $choix -eq "a") {
            Write-Info "Installation de Node.js via winget..."
            winget install OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements
            Refresh-Path
            Write-OK "Node.js installe via winget"
            $nodeOK = $true
        }
        elseif ($choix -eq "T" -or $choix -eq "t") {
            $nodeUrl = "https://nodejs.org/dist/v22.12.0/node-v22.12.0-x64.msi"
            $nodeInstaller = "$env:TEMP\node-v22.12.0-x64.msi"
            Write-Info "Telechargement de Node.js 22 LTS..."
            Invoke-WebRequest -Uri $nodeUrl -OutFile $nodeInstaller -UseBasicParsing
            Write-Info "Lancement de l'installeur Node.js..."
            Start-Process -FilePath "msiexec.exe" -ArgumentList "/i `"$nodeInstaller`" /passive" -Wait
            Refresh-Path
            $nodeOK = $true
        }
    } else {
        Write-Host "  [T] Telecharger l'installeur Node.js" -ForegroundColor White
        Write-Host "  [S] Passer" -ForegroundColor White
        $choix = Read-Host "  Choix (T/S)"

        if ($choix -eq "T" -or $choix -eq "t") {
            $nodeUrl = "https://nodejs.org/dist/v22.12.0/node-v22.12.0-x64.msi"
            $nodeInstaller = "$env:TEMP\node-v22.12.0-x64.msi"
            Write-Info "Telechargement de Node.js 22 LTS..."
            Invoke-WebRequest -Uri $nodeUrl -OutFile $nodeInstaller -UseBasicParsing
            Start-Process -FilePath "msiexec.exe" -ArgumentList "/i `"$nodeInstaller`" /passive" -Wait
            Refresh-Path
            $nodeOK = $true
        }
    }
}

# --- Etape 3 : Installation Claude CLI ---------------------------------------

Write-Step 3 "Verification de Claude CLI..."

$claudeOK = $false
try {
    $claudeVersion = claude --version 2>&1
    Write-OK "Claude CLI detecte : $claudeVersion"
    $claudeOK = $true
} catch {
    Write-Warn "Claude CLI non trouve"
}

if (-not $claudeOK -and $nodeOK) {
    Write-Host "  [I] Installer Claude CLI via npm" -ForegroundColor White
    Write-Host "  [S] Passer" -ForegroundColor White
    $choix = Read-Host "  Choix (I/S)"

    if ($choix -eq "I" -or $choix -eq "i") {
        Write-Info "Installation de Claude CLI..."
        npm install -g @anthropic-ai/claude-code
        Refresh-Path
        Write-OK "Claude CLI installe"
        $claudeOK = $true
    }
}

# --- Etape 4 : Copie du projet -----------------------------------------------

Write-Step 4 "Installation du package gendoc..."

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$sourceDir = $null

# Chercher pyproject.toml : parent (Deploy/ layout), meme dossier, ou dossier courant
if (Test-Path (Join-Path (Split-Path -Parent $scriptDir) "pyproject.toml")) {
    $sourceDir = Split-Path -Parent $scriptDir
} elseif (Test-Path (Join-Path $scriptDir "pyproject.toml")) {
    $sourceDir = $scriptDir
} elseif (Test-Path (Join-Path (Get-Location) "pyproject.toml")) {
    $sourceDir = (Get-Location).Path
}

if ($null -eq $sourceDir) {
    Write-Warn "pyproject.toml non trouve."
    Write-Info "Le script cherche dans : dossier parent, dossier du script, dossier courant."
    Write-Info "Assurez-vous que install.ps1 est dans le dossier Deploy/ du projet,"
    Write-Info "ou que pyproject.toml est present a cote du script."
    Read-Host "  Appuyez sur Entree pour quitter"
    exit 1
}

Write-Info "Projet source detecte : $sourceDir"

if ($InstallDir -ne $sourceDir) {
    Write-Info "Copie du projet vers $InstallDir..."

    if (Test-Path $InstallDir) {
        Write-Host "  Le dossier $InstallDir existe deja." -ForegroundColor Yellow
        Write-Host "  [E] Ecraser" -ForegroundColor White
        Write-Host "  [C] Continuer sans copier" -ForegroundColor White
        $choix = Read-Host "  Choix (E/C)"

        if ($choix -eq "E" -or $choix -eq "e") {
            Remove-Item -Recurse -Force $InstallDir
        } else {
            Write-Info "Conservation du dossier existant."
        }
    }

    if (-not (Test-Path $InstallDir)) {
        # Copier uniquement les fichiers necessaires
        New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
        $toCopy = @(
            "src",
            "Delagrave",
            "Deploy",
            "pyproject.toml",
            "CLAUDE.md"
        )
        foreach ($item in $toCopy) {
            $src = Join-Path $sourceDir $item
            $dst = Join-Path $InstallDir $item
            if (Test-Path $src) {
                if ((Get-Item $src).PSIsContainer) {
                    Copy-Item -Recurse -Force $src $dst
                } else {
                    Copy-Item -Force $src $dst
                }
            }
        }
        Write-OK "Projet copie dans $InstallDir"
    }
} else {
    Write-Info "Le script tourne deja depuis le projet - pas de copie necessaire."
    $InstallDir = $sourceDir
}

# pip install
Write-Info "Installation des dependances Python..."
Push-Location $InstallDir
try {
    pip install -e . 2>&1 | Out-Null
    Write-OK "Package gendoc installe (pip install -e .)"
} catch {
    Write-Warn "Erreur pip install : $_"
}
Pop-Location

# --- Etape 5 : Configuration gendoc.json -------------------------------------

Write-Step 5 "Configuration de gendoc.json..."

$configPath = Join-Path $InstallDir "gendoc.json"

if (Test-Path $configPath) {
    Write-OK "gendoc.json existe deja"
    $content = Get-Content $configPath -Raw | ConvertFrom-Json
    Write-Info "network_share_path = $($content.network_share_path)"
    Write-Info "admin = $($content.admin)"
} else {
    if ($NetworkShare -eq "") {
        Write-Host ""
        Write-Host "  Entrez le chemin du dossier Delagrave partage sur le reseau :" -ForegroundColor Yellow
        Write-Host "  Exemples : S:\Delagrave  ou  \\serveur\partage\Delagrave" -ForegroundColor Gray
        $NetworkShare = Read-Host "  Chemin"
    }

    if ($NetworkShare -ne "") {
        # Echapper les backslashes pour JSON
        $jsonPath = $NetworkShare.Replace("\", "\\")
        $jsonText = '{ "network_share_path": "' + $jsonPath + '", "admin": false }'
        Set-Content -Path $configPath -Value $jsonText -Encoding UTF8
        Write-OK "gendoc.json cree dans $InstallDir"
        Write-Info "network_share_path = $NetworkShare"
        Write-Info "admin = false (mode utilisateur)"
    } else {
        Write-Warn "Aucun chemin fourni - gendoc.json non cree"
        Write-Info "Copiez gendoc.json.example vers gendoc.json et editez-le manuellement."
    }
}

# --- Etape 6 : Configuration .mcp.json ---------------------------------------

Write-Step 6 "Configuration de .mcp.json (enregistrement Claude CLI)..."

$mcpPath = Join-Path $InstallDir ".mcp.json"

if (Test-Path $mcpPath) {
    Write-OK ".mcp.json existe deja"
} else {
    $installDirForward = $InstallDir.Replace("\", "/")
    $mcpJson = @{
        mcpServers = @{
            gendoc = @{
                command = "python"
                args = @("-m", "gendoc.mcp.server")
                cwd = $installDirForward
                env = @{
                    PYTHONPATH = "$installDirForward/src"
                }
            }
        }
    }
    $mcpJson | ConvertTo-Json -Depth 4 | Set-Content -Path $mcpPath -Encoding UTF8
    Write-OK ".mcp.json cree avec les chemins du poste"
}

# --- Etape 7 : Verification finale -------------------------------------------

Write-Step 7 "Verification finale..."

$allOK = $true

# Python
try {
    python -c "from gendoc.mcp.server import main; print('OK')" 2>&1 | Out-Null
    Write-OK "Module gendoc.mcp.server importable"
} catch {
    Write-Warn "Module gendoc.mcp.server non importable"
    $allOK = $false
}

# Dependencies
try {
    python -c "import openpyxl; import fastmcp; import pdfplumber; import pptx; print('OK')" 2>&1 | Out-Null
    Write-OK "Toutes les dependances Python installees"
} catch {
    Write-Warn "Dependances Python manquantes"
    $allOK = $false
}

# Config
$configExists = Test-Path (Join-Path $InstallDir "gendoc.json")
if ($configExists) {
    Write-OK "gendoc.json present"
} else {
    Write-Warn "gendoc.json manquant - a creer manuellement"
    $allOK = $false
}

# MCP config
$mcpExists = Test-Path (Join-Path $InstallDir ".mcp.json")
if ($mcpExists) {
    Write-OK ".mcp.json present"
} else {
    Write-Warn ".mcp.json manquant"
    $allOK = $false
}

# --- Etape 8 : Masquer les fichiers techniques --------------------------------

Write-Step 8 "Masquage des fichiers techniques..."

$filesToHide = @("pyproject.toml", "CLAUDE.md", ".mcp.json", "gendoc.json")
foreach ($f in $filesToHide) {
    $fp = Join-Path $InstallDir $f
    if (Test-Path $fp) {
        attrib +h $fp
    }
}
Write-OK "Fichiers techniques masques dans l'explorateur"

# --- Resume -------------------------------------------------------------------

Write-Host ""
Write-Host ("=" * 60) -ForegroundColor Cyan

if ($allOK) {
    Write-Host "  INSTALLATION TERMINEE AVEC SUCCES" -ForegroundColor Green
    Write-Host ("=" * 60) -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Pour utiliser gendoc :" -ForegroundColor White
    Write-Host "    1. Ouvrir un terminal dans $InstallDir" -ForegroundColor Gray
    Write-Host "    2. Lancer : claude" -ForegroundColor Gray
    Write-Host "    3. Tester : 'Cherche la reference PM-D-H-75'" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "  INSTALLATION PARTIELLE - voir les avertissements ci-dessus" -ForegroundColor Yellow
    Write-Host ("=" * 60) -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Consultez DEPLOY.md pour le guide de depannage." -ForegroundColor Gray
    Write-Host ""
}

Read-Host "Appuyez sur Entree pour fermer"
