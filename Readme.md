Absolument ! Voici une proposition de plan de développement itératif détaillé pour votre application `TeachAssit`, incluant la structure du projet, les bibliothèques suggérées, et une stratégie de test.

**Vision Générale du Projet**

`TeachAssit` est une application de bureau (initialement ciblée pour Windows, mais la logique Python peut être multiplateforme) qui analyse statiquement le code Java soumis par des étudiants en fonction de règles définies par l'enseignant dans des fichiers JSON. Elle vise à automatiser une partie du processus de correction, fournir des points de données structurés ("constats") pour une évaluation ultérieure (potentiellement par IA ou barème), et organiser les soumissions.

**Technologies Principales Suggérées**

1.  **Langage :** Python 3.x
2.  **Interface Graphique (GUI) :**
    * **Option 1 (Simple, Intégré) :** `tkinter` - Fait partie de la bibliothèque standard Python, suffisant pour une interface fonctionnelle avec des boutons, des listes, des zones de texte.
    * **Option 2 (Web Tech dans une App Desktop) :** `PyWebView` ou `Eel` - Permet de créer l'interface avec HTML/CSS/JavaScript (comme votre exemple) et de la piloter avec Python. C'est une bonne option si vous préférez le développement web pour l'interface.
    * **Option 3 (Plus Complexe, Puissant) :** `PyQt` ou `PySide` - Frameworks très complets pour des interfaces riches, mais avec une courbe d'apprentissage plus raide.
    * *Recommandation :* Commençons avec `tkinter` pour la simplicité ou `PyWebView` si l'exemple HTML est représentatif de l'interface souhaitée.
3.  **Manipulation de Fichiers ZIP :** Module `zipfile` (intégré à Python).
4.  **Manipulation du Système de Fichiers :** Modules `os` et `pathlib` (intégrés).
5.  **Manipulation JSON :** Module `json` (intégré).
6.  **Analyse Statique du Code Java :**
    * **Bibliothèque Clé :** `javalang` - Une bibliothèque Python pure pour parser le code source Java en un Arbre Syntaxique Abstrait (AST). C'est l'outil le plus adapté pour une analyse structurelle et sémantique fiable, bien plus robuste que les expressions régulières pour ce cas d'usage.
7.  **Expressions Régulières (pour `customPatterns`) :** Module `re` (intégré).
8.  **Tests :** `pytest` - Un framework de test populaire et puissant pour Python.

**Structure de Projet Robuste Proposée**

```
TeachAssit/
├── teach_assit/                 # Package principal du code source de l'application
│   ├── __init__.py
│   ├── main.py                  # Point d'entrée de l'application, initialise la GUI
│   ├── gui/                     # Modules liés à l'interface graphique
│   │   ├── __init__.py
│   │   ├── main_window.py       # Fenêtre principale de l'application
│   │   ├── file_selector.py     # Widgets pour la sélection de fichiers/dossiers
│   │   └── results_display.py   # Widgets pour afficher les résultats de l'analyse
│   ├── core/                    # Logique métier principale
│   │   ├── __init__.py
│   │   ├── submission_handler.py # Gère l'extraction et l'organisation (Phase 1)
│   │   └── analysis/              # Modules pour l'analyse statique (Phase 2)
│   │       ├── __init__.py
│   │       ├── models.py          # Définition des structures de données (Config, Constat, etc.)
│   │       ├── config_loader.py   # Charge et valide les fichiers JSON de configuration
│   │       ├── java_parser.py     # Utilise javalang pour parser le code Java en AST
│   │       ├── rule_engine.py     # Applique les règles de config sur l'AST
│   │       └── static_analyzer.py # Orchestre le processus d'analyse pour une soumission
│   ├── utils/                   # Fonctions utilitaires générales
│   │   ├── __init__.py
│   │   └── file_utils.py        # Utilitaires liés aux fichiers/dossiers
│
├── tests/                       # Répertoire pour tous les tests
│   ├── __init__.py
│   ├── core/
│   │   └── test_submission_handler.py
│   │   └── analysis/
│   │       ├── test_config_loader.py
│   │       ├── test_java_parser.py
│   │       ├── test_rule_engine.py
│   │       └── test_static_analyzer.py
│   ├── utils/
│   │   └── test_file_utils.py
│   └── fixtures/                # Fichiers de test (ex: .java, .zip, .json)
│       ├── sample_submissions/
│       ├── sample_configs/
│       └── sample_assessments/
│
├── configs/                     # Fichiers de configuration des exercices (.json) - Gérés par l'enseignant
│   ├── 04-calcul-moyenne.json
│   └── 06-validation-age.json
│   └── ...
│
├── assessments/                 # Fichiers de configuration des évaluations (.json) - Gérés par l'enseignant
│   └── examen-s1.json
│   └── ...
│
├── data/                        # Données générées par l'application (ex: extractions) - *À ignorer par Git*
│   └── extracted_submissions/
│
├── requirements.txt             # Liste des dépendances Python
├── README.md                    # Documentation du projet
└── .gitignore                   # Fichiers et dossiers à ignorer par Git (ex: data/, __pycache__/, *.pyc)
```

**Plan de Développement Itératif**

Nous allons diviser le projet en itérations (ou Sprints) gérables.

---

**Itération 0 : Configuration de l'Environnement et Socle de l'Application**

* **Objectif :** Mettre en place la structure du projet, l'environnement virtuel, et une coquille d'application minimale.
* **Tâches :**
    1.  Créer la structure de dossiers ci-dessus.
    2.  Initialiser un environnement virtuel Python (`python -m venv venv`).
    3.  Créer `requirements.txt` (initialement vide ou avec `pytest`).
    4.  Créer `.gitignore`.
    5.  Implémenter une fenêtre GUI de base (`main.py`, `gui/main_window.py`) qui s'ouvre (avec `tkinter` ou une page HTML simple si `PyWebView`).
    6.  Configurer `pytest`.
* **Bibliothèques à Installer :** `pytest`, `tkinter` (généralement inclus) ou `pywebview`.
* **Tests :**
    * Vérifier que l'application se lance sans erreur.
    * Écrire un test simple avec `pytest` pour s'assurer que la configuration des tests fonctionne.
* **Livrable :** Une application vide qui s'exécute, structure de projet prête.

---

**Itération 1 : Phase 1 - Extraction et Organisation des Fichiers**

* **Objectif :** Implémenter la fonctionnalité d'extraction des soumissions ZIP.
* **Tâches :**
    1.  Ajouter un bouton "Sélectionner Dossier des ZIPs" à l'interface (`gui/file_selector.py`).
    2.  Implémenter la logique dans `core/submission_handler.py` pour :
        * Parcourir le dossier sélectionné et lister les fichiers `.zip`.
        * Extraire chaque fichier ZIP dans un sous-dossier nommé d'après l'étudiant (en supposant que le nom est dans le nom du ZIP) dans `data/extracted_submissions/`. Gérer les erreurs potentielles (ZIP corrompu, etc.).
        * Identifier les fichiers `.java` dans chaque dossier extrait.
    3.  Afficher dans l'interface (`gui/main_window.py` ou `gui/results_display.py`) :
        * Le nombre de soumissions détectées/extraites.
        * Une liste organisée des soumissions extraites et des fichiers `.java` trouvés pour chacune.
* **Bibliothèques à Installer :** (Aucune nouvelle, utilise `zipfile`, `os`, `pathlib`).
* **Tests (`tests/core/test_submission_handler.py`, `tests/utils/test_file_utils.py`):**
    * Unitaires : Tester la fonction d'extraction avec des fichiers ZIP valides, vides, contenant des structures différentes, et des noms variés. Tester l'identification des fichiers Java.
    * Manuels : Vérifier le fonctionnement via l'interface graphique.
* **Livrable :** Fonctionnalité permettant de sélectionner un dossier de ZIPs, de les extraire correctement, et d'afficher la liste des fichiers Java.

---

**Itération 2 : Phase 2 (Partie A) - Chargement des Configurations et Parsing Java de Base**

* **Objectif :** Charger les configurations d'évaluation/exercice et parser les fichiers Java en AST.
* **Tâches :**
    1.  Implémenter `core/analysis/models.py` pour définir les classes Python représentant `ExerciseConfig`, `AssessmentConfig`, et potentiellement `Submission`, `AnalysisResult`, `Constat`.
    2.  Implémenter `core/analysis/config_loader.py` pour :
        * Charger un fichier `AssessmentConfig` (.json).
        * Charger les `ExerciseConfig` (.json) correspondants listés dans l'assessment.
        * Valider basiquement la structure des JSON chargés.
    3.  Ajouter un sélecteur (dropdown/liste) dans la GUI (`gui/main_window.py`) pour choisir une évaluation (`AssessmentConfig`) disponible dans le dossier `assessments/`.
    4.  Implémenter `core/analysis/java_parser.py` utilisant `javalang` :
        * Prendre un chemin de fichier `.java` en entrée.
        * Retourner l'AST `javalang` correspondant.
        * Gérer les erreurs de syntaxe Java pendant le parsing et les capturer.
    5.  Connecter : Lorsque l'extraction est faite (fin Itération 1), et qu'une évaluation est sélectionnée, tenter de parser les fichiers `.java` concernés. Afficher un statut simple (ex: "Parse OK", "Syntax Error") pour chaque fichier.
* **Bibliothèques à Installer :** `javalang`.
* **Tests (`tests/core/analysis/test_config_loader.py`, `tests/core/analysis/test_java_parser.py`):**
    * Unitaires : Tester le chargement de JSON valides/invalides. Tester le parsing de fichiers Java simples, complexes, et avec des erreurs de syntaxe. Vérifier la structure de l'AST retourné pour des cas simples.
    * Manuels : Vérifier la sélection d'assessment et le statut de parsing dans la GUI.
* **Livrable :** Capacité de charger les configurations et de parser les fichiers Java soumis en AST (ou de rapporter les erreurs de syntaxe).

---

**Itération 3 : Phase 2 (Partie B) - Moteur de Règles et Vérifications Simples**

* **Objectif :** Mettre en place le moteur d'analyse et implémenter les premières règles de vérification basées sur l'AST.
* **Tâches :**
    1.  Finaliser la structure du `Constat` dans `core/analysis/models.py` (ex: `rule_id`, `status` ('passed'/'failed'/'warning'), `message`, `details`, `location` (ligne/colonne si possible)).
    2.  Implémenter `core/analysis/rule_engine.py` :
        * Prendre un AST `javalang` et un `ExerciseConfig` en entrée.
        * Contenir des méthodes pour chaque type de règle (ex: `check_required_methods`, `check_allowed_operators`).
        * Chaque méthode de vérification retournera une liste de `Constat`.
    3.  Implémenter les premières règles *simples* dans `rule_engine.py` :
        * `requiredMethods` : Vérifier la présence, les types de paramètres, et le type de retour. Utiliser l'AST pour trouver les déclarations de méthodes.
        * `requiredClasses` (si ajouté à la config) : Vérifier la présence de classes spécifiques.
    4.  Implémenter `core/analysis/static_analyzer.py` qui orchestre :
        * Prend l'AST et la config.
        * Appelle les différentes méthodes de vérification du `rule_engine`.
        * Collecte tous les `Constat` générés.
    5.  Connecter : Ajouter un bouton "Analyser l'Évaluation Sélectionnée" dans la GUI. Lorsque cliqué, pour chaque soumission extraite et l'évaluation choisie :
        * Parser les fichiers Java.
        * Pour chaque fichier/exercice pertinent, exécuter le `static_analyzer`.
        * Stocker les résultats (liste de `Constat` par fichier/étudiant).
    6.  Afficher les résultats de manière *basique* dans la GUI (ex: simple liste textuelle des constats).
* **Bibliothèques à Installer :** (Aucune nouvelle).
* **Tests (`tests/core/analysis/test_rule_engine.py` - focus sur les règles implémentées, `tests/core/analysis/test_static_analyzer.py`):**
    * Unitaires : Tester les fonctions de vérification (`check_required_methods`, etc.) avec des ASTs créés manuellement ou parsés depuis des fichiers de test (fixtures) contenant des cas corrects et incorrects. Vérifier que les bons `Constat` sont générés.
    * Intégration : Tester l'orchestration par `static_analyzer`.
    * Manuels : Vérifier le flux complet depuis la GUI : sélection évaluation -> analyse -> affichage basique des résultats.
* **Livrable :** L'application peut analyser le code Java pour la présence de méthodes/classes requises et afficher les constats générés.

---

**Itération 4 : Phase 2 (Partie C) - Règles d'Opérateurs, Structures de Contrôle et Portée**

* **Objectif :** Étendre le moteur de règles avec des vérifications plus complexes.
* **Tâches :** Implémenter les règles suivantes dans `core/analysis/rule_engine.py` en parcourant l'AST :
    1.  `allowedOperators` / `disallowedElements` : Identifier les opérateurs utilisés dans les expressions. Nécessite de parcourir les nœuds d'expression de l'AST.
    2.  `requiredControlStructures` : Identifier les structures comme `IfStatement`, `ForStatement`, `WhileStatement`, `SwitchStatement` dans l'AST.
    3.  `checkVariableScope` (si `true`) : Analyse plus complexe. Il faudra suivre les déclarations de variables (`VariableDeclarator`) et leur portée (blocs de code `{}`). `javalang` peut aider à identifier les déclarations, mais suivre la portée exacte peut être délicat sans analyse de flux de données complète. Commencer par vérifier si les variables utilisées sont déclarées dans le même bloc ou un bloc parent. Enregistrer un constat si une variable semble non déclarée localement (peut avoir des faux positifs avec les champs de classe).
    4.  `checkNamingConventions` (ex: `camelCase`) : Vérifier les noms de méthodes, variables, classes trouvés dans l'AST par rapport aux conventions spécifiées (via regex simple sur les noms extraits).
* **Bibliothèques à Installer :** (Aucune nouvelle, potentiellement `re` pour les conventions de nommage).
* **Tests (`tests/core/analysis/test_rule_engine.py`):**
    * Unitaires : Ajouter des tests spécifiques pour chaque nouvelle règle avec divers exemples de code Java (corrects, incorrects, cas limites) dans les fixtures.
    * Manuels : Tester avec des exercices utilisant ces contraintes.
* **Livrable :** Moteur d'analyse capable de vérifier les opérateurs, les structures de contrôle, la portée basique des variables, et les conventions de nommage.

---

**Itération 5 : Phase 2 (Partie D) - Patterns Personnalisés et Règles Avancées**

* **Objectif :** Implémenter les vérifications basées sur les patterns personnalisés et d'autres règles avancées.
* **Tâches :** Implémenter les règles suivantes dans `core/analysis/rule_engine.py` :
    1.  `customPatterns`:
        * Option A (Regex) : Extraire le code source de l'AST (ou du fichier original) et appliquer les regex fournies. Moins robuste mais plus simple à implémenter.
        * Option B (AST Matching) : Tenter de traduire le pattern en une structure AST spécifique à rechercher. Plus complexe mais plus fiable.
        * Implémenter la logique pour vérifier `required`, `description`, `errorMessage`.
    2.  Règles OOP (`oopConcepts` - si ajouté à la config) : Vérifier l'héritage (`extends`), l'implémentation d'interfaces (`implements`), l'utilisation de modificateurs (`public`, `private`, `static`), l'instanciation (`ClassCreator`), etc., en se basant sur les nœuds AST.
    3.  Gestion des Exceptions (`exceptionHandling` - si ajouté à la config) : Rechercher les blocs `TryStatement`, `CatchClause`, `ThrowStatement` dans l'AST. Vérifier si des types spécifiques d'exceptions sont capturés ou lancés.
    4.  Améliorer la gestion des erreurs de syntaxe de `java_parser` pour les intégrer proprement comme des `Constat` spécifiques (`syntaxError`).
    5.  Robustesse : Assurer que l'analyseur ne plante pas sur du code très mal formé ou incomplet (au-delà des erreurs de syntaxe gérées par `javalang`).
* **Bibliothèques à Installer :** `re` (si utilisé pour `customPatterns`).
* **Tests (`tests/core/analysis/test_rule_engine.py`):**
    * Unitaires : Tests pour `customPatterns` (avec regex et/ou AST), tests pour les concepts OOP, tests pour la gestion des exceptions. Tester avec du code incomplet ou étrange.
    * Manuels : Tester avec des exercices nécessitant ces vérifications avancées.
* **Livrable :** Moteur d'analyse complet couvrant toutes les règles spécifiées dans la description de la Phase 2.

---

**Itération 6 : Amélioration de l'Interface et Affichage des Résultats**

* **Objectif :** Présenter les résultats de l'analyse de manière claire et utilisable dans l'interface graphique.
* **Tâches :**
    1.  Concevoir et implémenter une vue détaillée des résultats dans `gui/results_display.py`.
        * Afficher les résultats par étudiant / par fichier / par exercice.
        * Regrouper les `Constat` par règle ou par type (erreur, avertissement, succès).
        * Afficher les messages d'erreur/feedback associés à chaque constat.
        * Idéalement, permettre de cliquer sur un constat pour voir la ligne de code concernée (peut nécessiter de stocker les numéros de ligne lors de l'analyse).
    2.  Implémenter la fonctionnalité de sélection d'évaluation (`assessmentType` dropdown) et le déclenchement de l'analyse (`analyzeAssessment` command) comme dans l'exemple HTML/JS fourni (adapter pour `tkinter` ou `PyWebView`).
    3.  Affiner l'interface globale pour une meilleure ergonomie.
* **Bibliothèques à Installer :** (Aucune nouvelle, dépend du choix de GUI).
* **Tests :**
    * Manuels : Tester intensivement l'affichage des résultats avec différents types de constats et différents volumes de données. Vérifier la clarté et l'utilité de l'affichage. Tester la sélection d'assessment.
    * (Optionnel) : Tests GUI automatisés si le framework le permet facilement (peut être complexe).
* **Livrable :** Une application fonctionnelle avec une interface utilisateur permettant de sélectionner les soumissions, choisir une évaluation, lancer l'analyse, et visualiser les constats détaillés de manière structurée.

---

**Stratégie de Test Globale**

* **Tests Unitaires (`pytest`) :** Essentiels pour chaque fonction/méthode critique, surtout dans `core/analysis`. Utiliser des fichiers `.java` et des ASTs mockés/pré-générés comme `fixtures` pour isoler les composants. Tester les cas nominaux, les cas limites, et les cas d'erreur.
* **Tests d'Intégration :** Vérifier que les composants majeurs fonctionnent ensemble (ex: `submission_handler` -> `static_analyzer` -> `results_display`). Peuvent être plus difficiles à écrire mais sont très utiles.
* **Tests Fonctionnels/Acceptation (Manuels) :** Simuler l'utilisation par un enseignant. Utiliser de vrais (ou réalistes) exemples de soumissions étudiantes et de fichiers de configuration. Vérifier que l'application répond aux objectifs fonctionnels et est facile à utiliser.
* **Couverture de Code :** Utiliser `pytest-cov` pour mesurer quelle proportion du code est exécutée par les tests unitaires et d'intégration. Viser une couverture élevée (>80-90%) pour le module `core/analysis`.

**Prochaines Étapes Possibles (Après ces Itérations)**

1.  **Phase 3 & 4 (Évaluation et Feedback) :**
    * Implémenter un système de notation basé sur les `Constat` générés (ex: attribuer des points/pénalités selon les `status` 'passed'/'failed').
    * Intégrer une composante IA (ex: un LLM comme Gemini ou GPT via API) pour générer des commentaires de feedback plus nuancés et personnalisés en se basant sur les `Constat` et le code source.
2.  **Phase 5 (Analyse de Cohorte) :**
    * Agréger les résultats d'analyse de plusieurs étudiants pour une évaluation donnée.
    * Générer des statistiques : taux de réussite par règle/exercice, erreurs fréquentes, etc.
    * Visualiser ces données (graphiques, tableaux).
3.  **Compilation et Exécution :** Ajouter la capacité de compiler (avec `javac`) et d'exécuter le code étudiant pour des tests dynamiques (vérifier la sortie, gérer les timeouts, etc.). C'est une extension significative qui ajoute de la complexité (besoin d'un JDK, gestion des processus enfants).
4.  **Empaquetage :** Créer un exécutable Windows autonome (avec `PyInstaller` ou similaire) pour faciliter la distribution aux enseignants.
5.  **Améliorations UI/UX :** Basées sur les retours des utilisateurs.

Ce plan fournit une base solide et itérative pour construire `TeachAssit`. N'hésitez pas si vous avez des questions ou si vous souhaitez ajuster certaines parties !



### Automatisation de l'évaluation des devoirs Java avec TeachAssit

**Points clés :**
- TeachAssit est une application Windows en Python qui semble bien adaptée pour automatiser l'évaluation des devoirs Java, réduire la charge des enseignants et fournir des retours personnalisés aux étudiants.
- Python est recommandé pour un développement rapide, utilisant des bibliothèques comme `javalang` pour l'analyse du code Java et `PyQt5` pour une interface graphique moderne.
- L'application peut gérer l'extraction de fichiers ZIP, l'analyse statique du code, l'exécution de code Java, et l'intégration d'une IA via une API pour la notation et les retours.
- Une structure de projet robuste et un plan itératif permettront de respecter les délais tout en assurant une application fonctionnelle.

**Pourquoi Python ?**
Python est idéal pour TeachAssit en raison de sa simplicité et de ses bibliothèques puissantes. Avec `javalang`, vous pouvez analyser le code Java pour vérifier les classes, méthodes et structures demandées. `PyQt5` offre une interface graphique professionnelle, et `subprocess` permet d'exécuter du code Java pour vérifier sa compilation et ses résultats. L'intégration d'une API d'IA est également facilitée avec `requests`.

**Plan de développement**
Un plan itératif en 10 étapes est proposé, commençant par la configuration du projet et une interface de base, puis progressant vers l'extraction de fichiers, l'analyse statique, l'exécution de code, et l'intégration de l'IA. Chaque étape inclut des tests pour garantir la fiabilité.

**Structure du projet**
Une structure organisée avec des dossiers pour les configurations, le code source, les tests et la documentation assurera la maintenabilité et l'évolutivité de l'application.

**Prochaines étapes**
Commencez par configurer l'environnement Python, installez les bibliothèques nécessaires, et prototypez l'interface graphique. Testez chaque composant au fur et à mesure pour respecter votre délai.

---

```python
import sys
import os
import zipfile
import json
import re
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QFileDialog, QComboBox, QLabel, QTreeWidget, 
                            QTreeWidgetItem, QMessageBox)
from PyQt5.QtCore import Qt
import javalang
import requests

class ExerciseConfig:
    def __init__(self, config_data):
        self.id = config_data.get('id')
        self.name = config_data.get('name')
        self.description = config_data.get('description')
        self.rules = config_data.get('rules', {})

class AssessmentConfig:
    def __init__(self, config_data):
        self.id = config_data.get('assessmentId')
        self.name = config_data.get('name')
        self.exercises = config_data.get('exercises', [])
        self.total_max_points = config_data.get('totalMaxPoints', 0)

class FileManager:
    def __init__(self):
        self.base_dir = ""
        self.student_folders = {}

    def set_base_directory(self, directory):
        self.base_dir = directory
        self.student_folders = {}

    def list_zip_files(self):
        if not self.base_dir:
            return []
        return [f for f in os.listdir(self.base_dir) if f.endswith('.zip')]

    def extract_zips(self):
        output_dir = os.path.join(self.base_dir, "extracted")
        os.makedirs(output_dir, exist_ok=True)
        for zip_file in self.list_zip_files():
            zip_path = os.path.join(self.base_dir, zip_file)
            student_name = os.path.splitext(zip_file)[0]
            student_dir = os.path.join(output_dir, student_name)
            os.makedirs(student_dir, exist_ok=True)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(student_dir)
            java_files = [f for f in os.listdir(student_dir) if f.endswith('.java')]
            self.student_folders[student_name] = {
                'path': student_dir,
                'java_files': java_files
            }
        return self.student_folders

class ConfigLoader:
    def __init__(self, config_dir):
        self.config_dir = config_dir
        self.exercise_configs = {}
        self.assessment_configs = {}

    def load_exercise_configs(self):
        exercise_dir = os.path.join(self.config_dir, 'exercises')
        if not os.path.exists(exercise_dir):
            return
        for config_file in os.listdir(exercise_dir):
            if config_file.endswith('.json'):
                with open(os.path.join(exercise_dir, config_file), 'r') as f:
                    config_data = json.load(f)
                    config = ExerciseConfig(config_data)
                    self.exercise_configs[config.id] = config

    def load_assessment_configs(self):
        assessment_dir = os.path.join(self.config_dir, 'assessments')
        if not os.path.exists(assessment_dir):
            return
        for config_file in os.listdir(assessment_dir):
            if config_file.endswith('.json'):
                with open(os.path.join(assessment_dir, config_file), 'r') as f:
                    config_data = json.load(f)
                    config = AssessmentConfig(config_data)
                    self.assessment_configs[config.id] = config

class StaticAnalyzer:
    def __init__(self, exercise_config):
        self.config = exercise_config
        self.findings = []

    def analyze_file(self, file_path):
        self.findings = []
        with open(file_path, 'r', encoding='utf-8') as file:
            code = file.read()
        try:
            tree = javalang.parse.parse(code)
            self.check_required_methods(tree)
            self.check_control_structures(tree)
            self.check_operators(tree)
            self.check_variable_scope(tree)
            self.check_naming_conventions(code)
            self.check_custom_patterns(code)
        except javalang.parser.JavaSyntaxError as e:
            self.findings.append({
                'check': 'syntax',
                'passed': False,
                'details': f"Erreur de syntaxe : {str(e)}"
            })
        return self.findings

    def check_required_methods(self, tree):
        required_methods = self.config.rules.get('requiredMethods', [])
        for req_method in required_methods:
            found = False
            for path, node in tree:
                if isinstance(node, javalang.tree.MethodDeclaration):
                    if (node.name == req_method['name'] and
                        node.return_type.name == req_method['returnType'] and
                        len(node.parameters) == len(req_method['params']) and
                        all(p.type.name == t for p, t in zip(node.parameters, req_method['params']))):
                        found = True
                        break
            self.findings.append({
                'check': f"requiredMethod_{req_method['name']}",
                'passed': found,
                'details': f"Méthode {req_method['name']} {'trouvée' if found else 'non trouvée'}"
            })

    def check_control_structures(self, tree):
        required_structures = self.config.rules.get('requiredControlStructures', [])
        found_structures = set()
        for path, node in tree:
            if isinstance(node, javalang.tree.IfStatement):
                found_structures.add('if')
            elif isinstance(node, javalang.tree.ForStatement):
                found_structures.add('for')
            elif isinstance(node, javalang.tree.WhileStatement):
                found_structures.add('while')
        for structure in required_structures:
            passed = structure in found_structures
            self.findings.append({
                'check': f"controlStructure_{structure}",
                'passed': passed,
                'details': f"Structure {structure} {'trouvée' if passed else 'non trouvée'}"
            })

    def check_operators(self, tree):
        allowed_operators = set(self.config.rules.get('allowedOperators', []))
        used_operators = set()
        for path, node in tree:
            if isinstance(node, javalang.tree.BinaryOperation):
                used_operators.add(node.operator)
        if not allowed_operators:
            return
        disallowed = used_operators - allowed_operators
        passed = not disallowed
        self.findings.append({
            'check': 'allowedOperators',
            'passed': passed,
            'details': f"Opérateurs utilisés : {', '.join(used_operators)}. {'Tous autorisés' if passed else f'Opérateurs non autorisés : {', '.join(disallowed)}'}"
        })

    def check_variable_scope(self, tree):
        if not self.config.rules.get('checkVariableScope', False):
            return
        for path, node in tree:
            if isinstance(node, javalang.tree.MethodDeclaration):
                declared_vars = set(p.name for p in node.parameters)
                local_decls = set()
                for _, subnode in node:
                    if isinstance(subnode, javalang.tree.LocalVariableDeclaration):
                        local_decls.update(v.declarator.name for v in subnode.declarators)
                declared_vars.update(local_decls)
                used_vars = set()
                for _, subnode in node:
                    if isinstance(subnode, javalang.tree.MemberReference):
                        used_vars.add(subnode.member)
                undeclared = used_vars - declared_vars
                passed = not undeclared
                self.findings.append({
                    'check': 'variableScope',
                    'passed': passed,
                    'details': f"{'Toutes les variables sont déclarées localement' if passed else f'Variables non déclarées : {', '.join(undeclared)}'}"
                })

    def check_naming_conventions(self, code):
        naming_conventions = self.config.rules.get('checkNamingConventions', [])
        if 'camelCase' not in naming_conventions:
            return
        identifiers = []
        for token in javalang.tokenizer.tokenize(code):
            if isinstance(token, javalang.tokenizer.Identifier):
                identifiers.append(token.value)
        non_camel_case = [id for id in identifiers if not re.match(r'^[a-z][a-zA-Z0-9]*$', id)]
        passed = not non_camel_case
        self.findings.append({
            'check': 'namingConventions',
            'passed': passed,
            'details': f"{'Tous les identifiants en camelCase' if passed else f'Identifiants non conformes : {', '.join(non_camel_case)}'}"
        })

    def check_custom_patterns(self, code):
        custom_patterns = self.config.rules.get('customPatterns', [])
        for pattern in custom_patterns:
            matches = re.search(pattern['pattern'], code)
            passed = bool(matches) if pattern.get('required', False) else True
            details = pattern.get('description', '')
            if not passed and 'errorMessage' in pattern:
                details += f" - {pattern['errorMessage']}"
            self.findings.append({
                'check': f"customPattern_{pattern['description']}",
                'passed': passed,
                'details': details
            })

class CodeExecutor:
    def compile_java(self, file_path):
        result = subprocess.run(['javac', file_path], capture_output=True, text=True)
        return result.returncode == 0, result.stderr

    def run_java(self, class_name, working_dir):
        result = subprocess.run(['java', '-cp', working_dir, class_name], 
                             capture_output=True, text=True)
        return result.stdout, result.stderr

class AIEvaluator:
    def __init__(self, api_key, api_url):
        self.api_key = api_key
        self.api_url = api_url

    def get_feedback(self, code, findings, prompt="Évaluez ce code Java pour un devoir d'étudiant"):
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{
                "role": "user",
                "content": f"{prompt}\nCode: {code}\nRésultats d'analyse: {json.dumps(findings)}"
            }]
        }
        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Erreur API : {str(e)}"

class TeachAssitWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TeachAssit - Évaluation des Devoirs Java")
        self.setGeometry(100, 100, 800, 600)
        self.file_manager = FileManager()
        self.config_loader = ConfigLoader('configs')
        self.code_executor = CodeExecutor()
        self.ai_evaluator = AIEvaluator("votre_cle_api", "https://api.openai.com/v1/chat/completions")
        self.init_ui()
        self.load_configs()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.select_dir_btn = QPushButton("Sélectionner le dossier des soumissions")
        self.select_dir_btn.clicked.connect(self.select_directory)
        layout.addWidget(self.select_dir_btn)

        self.extract_btn = QPushButton("Extraire les fichiers ZIP")
        self.extract_btn.clicked.connect(self.extract_zips)
        self.extract_btn.setEnabled(False)
        layout.addWidget(self.extract_btn)

        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["Étudiant", "Fichiers Java"])
        layout.addWidget(self.file_tree)

        self.assessment_combo = QComboBox()
        self.assessment_combo.addItem("Sélectionner une évaluation")
        self.assessment_combo.currentIndexChanged.connect(self.on_assessment_selected)
        layout.addWidget(self.assessment_combo)

        self.analyze_btn = QPushButton("Analyser l'évaluation")
        self.analyze_btn.clicked.connect(self.analyze_assessment)
        self.analyze_btn.setEnabled(False)
        layout.addWidget(self.analyze_btn)

        self.result_label = QLabel("Résultats de l'analyse ici")
        self.result_label.setWordWrap(True)
        layout.addWidget(self.result_label)

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Sélectionner le dossier des soumissions")
        if directory:
            self.file_manager.set_base_directory(directory)
            self.extract_btn.setEnabled(True)
            self.file_tree.clear()
            for zip_file in self.file_manager.list_zip_files():
                item = QTreeWidgetItem(self.file_tree, [zip_file, "Non extrait"])
            self.result_label.setText(f"Dossier sélectionné : {directory}")

    def extract_zips(self):
        self.file_tree.clear()
        student_folders = self.file_manager.extract_zips()
        for student, info in student_folders.items():
            student_item = QTreeWidgetItem(self.file_tree, [student, ""])
            for java_file in info['java_files']:
                QTreeWidgetItem(student_item, ["", java_file])
        self.result_label.setText(f"{len(student_folders)} dossiers extraits.")

    def load_configs(self):
        self.config_loader.load_exercise_configs()
        self.config_loader.load_assessment_configs()
        self.assessment_combo.clear()
        self.assessment_combo.addItem("Sélectionner une évaluation")
        for assessment_id, assessment in self.config_loader.assessment_configs.items():
            self.assessment_combo.addItem(assessment.name, assessment_id)

    def on_assessment_selected(self, index):
        self.analyze_btn.setEnabled(index > 0)

    def analyze_assessment(self):
        assessment_id = self.assessment_combo.currentData()
        if not assessment_id:
            return
        assessment = self.config_loader.assessment_configs.get(assessment_id)
        if not assessment:
            QMessageBox.critical(self, "Erreur", "Évaluation non trouvée.")
            return

        results = []
        for student, info in self.file_manager.student_folders.items():
            student_results = {'student': student, 'exercises': []}
            for exercise in assessment.exercises:
                exercise_id = exercise['exerciseId']
                exercise_config = self.config_loader.exercise_configs.get(exercise_id)
                if not exercise_config:
                    student_results['exercises'].append({
                        'exerciseId': exercise_id,
                        'error': "Configuration de l'exercice non trouvée"
                    })
                    continue
                java_file = f"{exercise_id}.java"
                file_path = os.path.join(info['path'], java_file)
                if not os.path.exists(file_path):
                    student_results['exercises'].append({
                        'exerciseId': exercise_id,
                        'error': "Fichier Java non trouvé"
                    })
                    continue
                analyzer = StaticAnalyzer(exercise_config)
                findings = analyzer.analyze_file(file_path)
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                success, compile_errors = self.code_executor.compile_java(file_path)
                execution_result = {}
                if success:
                    class_name = os.path.splitext(java_file)[0]
                    output, run_errors = self.code_executor.run_java(class_name, info['path'])
                    execution_result = {'output': output, 'errors': run_errors}
                else:
                    execution_result = {'errors': compile_errors}
                ai_feedback = self.ai_evaluator.get_feedback(code, findings)
                student_results['exercises'].append({
                    'exerciseId': exercise_id,
                    'findings': findings,
                    'execution': execution_result,
                    'ai_feedback': ai_feedback
                })
            results.append(student_results)

        result_text = f"Résultats pour {assessment.name}:\n"
        for student_result in results:
            result_text += f"\nÉtudiant: {student_result['student']}\n"
            for ex_result in student_result['exercises']:
                result_text += f"  Exercice {ex_result['exerciseId']}:\n"
                if 'error' in ex_result:
                    result_text += f"    Erreur: {ex_result['error']}\n"
                else:
                    for finding in ex_result['findings']:
                        status = "Réussi" if finding['passed'] else "Échoué"
                        result_text += f"    {finding['check']}: {status} - {finding['details']}\n"
                    if ex_result['execution']['errors']:
                        result_text += f"    Erreurs d'exécution: {ex_result['execution']['errors']}\n"
                    else:
                        result_text += f"    Sortie: {ex_result['execution']['output']}\n"
                    result_text += f"    Feedback IA: {ex_result['ai_feedback']}\n"
        self.result_label.setText(result_text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TeachAssitWindow()
    window.show()
    sys.exit(app.exec_())
```

### Rapport détaillé : Développement de TeachAssit

#### Contexte et objectifs
TeachAssit est une application Windows conçue pour automatiser l'évaluation des devoirs de programmation Java, répondant aux défis posés par la massification des effectifs dans les formations en informatique. Les méthodes traditionnelles de correction manuelle sont chronophages et peuvent entraîner des inégalités d'évaluation. TeachAssit vise à :
- **Automatiser l'évaluation** des exercices, travaux pratiques et examens Java.
- **Standardiser les critères** pour garantir l'équité.
- **Fournir des feedbacks détaillés** pour améliorer l'apprentissage.
- **Réduire la charge des enseignants**, leur permettant de se concentrer sur l'accompagnement pédagogique.
- **Analyser les performances** des cohortes pour identifier les concepts mal assimilés.

L'application fonctionne en quatre phases, mais seules les phases 1 (extraction et organisation des fichiers) et 2 (analyse statique du code) sont détaillées ici, avec des exigences supplémentaires pour l'exécution du code et l'intégration d'une IA.

#### Pourquoi Python ?
Python est recommandé pour sa rapidité de développement et ses bibliothèques adaptées :
- **[javalang](https://github.com/c2nes/javalang)** pour analyser le code Java.
- **[PyQt5](https://www.riverbankcomputing.com/static/Docs/PyQt5/)** pour une interface graphique moderne.
- **[requests](https://requests.readthedocs.io/en/latest/)** pour intégrer une API d'IA.
- **[subprocess](https://docs.python.org/3/library/subprocess.html)** pour compiler et exécuter le code Java.

Bien que Java soit une alternative robuste avec `JavaParser`, Python est plus rapide à prototyper, ce qui est crucial pour respecter votre délai.

#### Structure du projet
Une structure organisée garantit la maintenabilité et l'évolutivité :

| **Dossier/Fichier** | **Description** |
|---------------------|-----------------|
| `configs/exercises/` | Contient les fichiers JSON de configuration des exercices (ex. `06-validation-age.json`). |
| `configs/assessments/` | Contient les fichiers JSON de configuration des évaluations (ex. `examen-s1.json`). |
| `src/gui/` | Modules pour l'interface graphique (ex. `main_window.py`). |
| `src/file_manager.py` | Gère l'extraction des ZIP et l'organisation des fichiers. |
| `src/config_loader.py` | Charge les configurations JSON. |
| `src/static_analyzer.py` | Effectue l'analyse statique du code Java. |
| `src/code_executor.py` | Compile et exécute le code Java. |
| `src/ai_evaluator.py` | Intègre l'IA pour la notation et les feedbacks. |
| `tests/` | Contient les tests unitaires et d'intégration. |
| `requirements.txt` | Liste des dépendances Python. |
| `setup.py` | Script pour l'installation et le packaging. |
| `main.py` | Point d'entrée de l'application. |

#### Bibliothèques à installer
| **Bibliothèque** | **Commande** | **Utilité** |
|------------------|--------------|-------------|
| PyQt5 | `pip install PyQt5` | Interface graphique moderne. |
| javalang | `pip install javalang` | Analyse statique du code Java. |
| requests | `pip install requests` | Appels API pour l'IA. |
| pytest | `pip install pytest` | Tests unitaires et d'intégration. |
| PyInstaller | `pip install pyinstaller` | Création d'un exécutable Windows. |

#### Plan itératif de développement

##### Itération 1 : Configuration et interface de base
- **Tâches** :
  - Configurer l'environnement Python (3.8+).
  - Créer la structure du projet.
  - Installer les bibliothèques via `requirements.txt`.
  - Développer une interface de base avec PyQt5 : bouton pour sélectionner un dossier, liste des fichiers ZIP.
- **Tests** :
  - Vérifier que l'interface s'ouvre sans erreur.
  - Tester la sélection du dossier et l'affichage des fichiers ZIP.
- **Livrable** : Interface minimale fonctionnelle.

##### Itération 2 : Extraction et organisation des fichiers
- **Tâches** :
  - Implémenter l'extraction des fichiers ZIP dans des dossiers séparés (`file_manager.py`).
  - Lister les fichiers `.java` par étudiant dans une arborescence.
  - Intégrer cette liste dans l'interface (QTreeWidget).
- **Tests** :
  - Tester l'extraction avec des ZIP valides et invalides.
  - Vérifier que les fichiers `.java` sont correctement listés.
  - Tester avec un grand nombre de ZIP pour évaluer la performance.
- **Livrable** : Fonctionnalité d'extraction et affichage des fichiers.

##### Itération 3 : Chargement des configurations
- **Tâches** :
  - Créer des classes `ExerciseConfig` et `AssessmentConfig` (`config_loader.py`).
  - Charger les fichiers JSON des exercices et évaluations.
  - Ajouter un menu déroulant pour sélectionner les évaluations.
- **Tests** :
  - Tester le chargement de JSON valides et invalides.
  - Vérifier que les configurations sont correctement mappées.
  - Tester avec des configurations complexes (plusieurs exercices).
- **Livrable** : Gestion des configurations JSON.

##### Itération 4 : Analyse statique de base
- **Tâches** :
  - Implémenter l'analyse statique avec `javalang` (`static_analyzer.py`).
  - Vérifier les classes et méthodes requises selon les configurations.
  - Gérer les erreurs de syntaxe.
- **Tests** :
  - Tester l'analyse avec du code Java correct et incorrect.
  - Vérifier la détection des méthodes requises (ex. `estMajeur`).
  - Tester la gestion des erreurs de syntaxe.
- **Livrable** : Analyse statique des structures de base.

##### Itération 5 : Analyse statique avancée
- **Tâches** :
  - Ajouter des vérifications pour :
    - Structures de contrôle (if, for, etc.).
    - Opérateurs autorisés/interdits.
    - Portée des variables.
    - Conventions de nommage (camelCase).
    - Motifs personnalisés (regex).
  - Générer des constats structurés (JSON).
- **Tests** :
  - Tester chaque type de vérification avec des cas positifs et négatifs.
  - Vérifier la robustesse face à du code mal formé.
  - Tester les motifs personnalisés avec différents patterns.
- **Livrable** : Analyse statique complète.

##### Itération 6 : Compilation et exécution du code
- **Tâches** :
  - Implémenter la compilation et l'exécution du code Java (`code_executor.py`).
  - Capturer les erreurs de compilation et les sorties d'exécution.
- **Tests** :
  - Tester la compilation avec du code valide et invalide.
  - Vérifier l'exécution avec des programmes simples.
  - Tester la capture des erreurs d'exécution.
- **Livrable** : Exécution fonctionnelle du code Java.

##### Itération 7 : Intégration de l'IA
- **Tâches** :
  - Implémenter l'appel à une API d'IA pour la notation et les feedbacks (`ai_evaluator.py`).
  - Envoyer le code et les constats à l'API, récupérer les retours.
- **Tests** :
  - Tester l'intégration avec une API mock ou réelle.
  - Vérifier que les retours sont cohérents avec les constats.
  - Tester la gestion des erreurs API.
- **Livrable** : Feedbacks IA intégrés.

##### Itération 8 : Analyse des évaluations
- **Tâches** :
  - Coordonner l'analyse pour une évaluation complète (plusieurs exercices par étudiant).
  - Agréger les résultats et les afficher dans l'interface.
- **Tests** :
  - Tester avec une évaluation multi-exercices.
  - Vérifier l'agrégation des résultats par étudiant.
  - Tester les cas où des fichiers sont manquants.
- **Livrable** : Analyse complète des évaluations.

##### Itération 9 : Tests et optimisation
- **Tâches** :
  - Écrire des tests unitaires et d'intégration avec `pytest`.
  - Corriger les bogues identifiés.
  - Optimiser les performances pour les grandes cohortes.
- **Tests** :
  - Tests unitaires pour chaque module (file_manager, static_analyzer, etc.).
  - Tests d'intégration pour le flux complet.
  - Tests de charge avec 100+ étudiants.
- **Livrable** : Application robuste et testée.

##### Itération 10 : Packaging et documentation
- **Tâches** :
  - Utiliser `PyInstaller` pour créer un exécutable Windows.
  - Rédiger une