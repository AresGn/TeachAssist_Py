@echo off
echo Exécution des tests TeachAssit...

REM Activation de l'environnement virtuel
call venv\Scripts\activate.bat

REM Définition du PYTHONPATH pour trouver les modules
set PYTHONPATH=%PYTHONPATH%;%CD%

REM Exécution des tests avec pytest
pytest -v tests\

REM Désactivation de l'environnement virtuel
call deactivate

echo.
echo Tests terminés.
pause 