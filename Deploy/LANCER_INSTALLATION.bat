@echo off
title GENDOC - Installation automatique
echo.
echo  ============================================================
echo   GENDOC - Generateur de Fiches Techniques Delagrave
echo   Lancement de l'installation...
echo  ============================================================
echo.

:: Lancer le script PowerShell avec les bonnes permissions
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"
