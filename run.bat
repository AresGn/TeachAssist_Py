@echo off
echo Démarrage de TeachAssit...

REM Activation de l'environnement virtuel
call venv\Scripts\activate.bat

REM Définition du PYTHONPATH pour trouver les modules
set PYTHONPATH=%PYTHONPATH%;%CD%

REM Exécution de l'application
python teach_assit\main.py

REM Désactivation de l'environnement virtuel
call deactivate

pause 