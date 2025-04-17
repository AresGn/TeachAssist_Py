@echo off
echo Lancement de la démo d'analyse statique...
echo.

REM Activer l'environnement virtuel s'il existe
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Environnement virtuel non trouvé, utilisation de Python système...
)

REM Exécuter le script de démo
python teach_assit\static_analysis_demo.py

REM Désactiver l'environnement virtuel si activé
if exist venv\Scripts\deactivate.bat (
    call venv\Scripts\deactivate.bat
)

echo.
echo Appuyez sur une touche pour fermer cette fenêtre...
pause > nul 