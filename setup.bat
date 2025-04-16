@echo off
echo Initialisation du projet TeachAssit...

REM Création de la structure de répertoires
mkdir teach_assit
mkdir teach_assit\gui
mkdir teach_assit\core
mkdir teach_assit\core\analysis
mkdir teach_assit\utils
mkdir tests
mkdir tests\core
mkdir tests\core\analysis
mkdir tests\utils
mkdir tests\fixtures
mkdir tests\fixtures\sample_submissions
mkdir tests\fixtures\sample_configs
mkdir tests\fixtures\sample_assessments
mkdir configs
mkdir assessments
mkdir data
mkdir data\extracted_submissions

REM Création des fichiers Python initiaux
echo # TeachAssit Package > teach_assit\__init__.py
echo # Main Application > teach_assit\main.py
echo # GUI Package > teach_assit\gui\__init__.py
echo # Core Package > teach_assit\core\__init__.py
echo # Analysis Package > teach_assit\core\analysis\__init__.py
echo # Utils Package > teach_assit\utils\__init__.py
echo # Tests Package > tests\__init__.py
echo # Core Tests > tests\core\__init__.py
echo # Analysis Tests > tests\core\analysis\__init__.py
echo # Utils Tests > tests\utils\__init__.py

REM Création du fichier .gitignore
echo # Byte-compiled / optimized / DLL files > .gitignore
echo __pycache__/ >> .gitignore
echo *.py[cod] >> .gitignore
echo *$py.class >> .gitignore
echo # Distribution / packaging >> .gitignore
echo dist/ >> .gitignore
echo build/ >> .gitignore
echo *.egg-info/ >> .gitignore
echo # Unit test / coverage reports >> .gitignore
echo htmlcov/ >> .gitignore
echo .tox/ >> .gitignore
echo .coverage >> .gitignore
echo .coverage.* >> .gitignore
echo .pytest_cache/ >> .gitignore
echo # Environments >> .gitignore
echo venv/ >> .gitignore
echo env/ >> .gitignore
echo ENV/ >> .gitignore
echo # Project specific >> .gitignore
echo data/ >> .gitignore

REM Création du fichier requirements.txt
echo PyQt5 > requirements.txt
echo javalang >> requirements.txt
echo requests >> requirements.txt
echo pytest >> requirements.txt
echo PyInstaller >> requirements.txt

REM Création d'un environnement virtuel
echo Création de l'environnement virtuel...
python -m venv venv

REM Activation de l'environnement virtuel et installation des packages
echo Activation de l'environnement virtuel et installation des packages...
call venv\Scripts\activate.bat
pip install -r requirements.txt

echo.
echo Initialisation du projet TeachAssit terminée!
echo L'environnement virtuel a été créé et les packages nécessaires ont été installés.
echo.
echo Pour activer l'environnement virtuel, exécutez: venv\Scripts\activate.bat
echo Pour désactiver l'environnement virtuel, exécutez: deactivate
echo.
pause 