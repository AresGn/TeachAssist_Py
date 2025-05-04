"""
Gestionnaire de données pour le module de feedback.
Gère le chargement des exercices, des configurations et l'analyse des fichiers.
"""

import os
import re
import json
import glob
import logging

from teach_assit.core.analysis.config_loader import ConfigLoader
from teach_assit.gui.feedback.assessment_loader import AssessmentLoader

class DataManager:
    """Gestionnaire de données pour le module de feedback."""
    
    def __init__(self, results_widget=None):
        """
        Initialise le gestionnaire de données.
        
        Args:
            results_widget: Référence vers le widget de résultats pour accéder aux données
        """
        self.results_widget = results_widget
        self.exercise_configs = {}
        self.exercise_file_paths = {}  # Cache des chemins de fichiers trouvés
        self.student_exercise_files = {}  # Nouveau cache pour stocker les chemins par étudiant et exercice
        self.exercise_data = {}  # Initialisation de l'attribut exercise_data manquant
        
        # Initialiser le chargeur d'évaluations dynamique
        self.assessment_loader = AssessmentLoader()
        
        # Charger les configurations depuis le chargeur d'évaluations
        self.load_exercise_configs()
    
    def load_exercise_configs(self):
        """Charge les configurations des exercices depuis les fichiers de configuration"""
        # Charger depuis ConfigLoader pour compatibilité avec le code existant
        config_loader = ConfigLoader(os.getcwd())
        config_loader.load_all_configs()
        
        for exercise_id, config in config_loader.get_all_exercise_configs().items():
            self.exercise_configs[exercise_id] = config.to_dict()
        
        # Charger également depuis AssessmentLoader pour avoir toutes les configurations
        for exercise_id, config in self.assessment_loader.get_all_exercise_configs().items():
            if exercise_id not in self.exercise_configs:
                self.exercise_configs[exercise_id] = config
        
        print(f"Nombre total de configurations d'exercices chargées: {len(self.exercise_configs)}")
    
    def get_students_from_results(self):
        """Récupère la liste des étudiants depuis l'onglet Results"""
        if self.results_widget:
            try:
                # Get the actual student list from the results widget
                return self.results_widget.get_student_list()
            except AttributeError:
                # If the method doesn't exist, use the sample data we have
                return ["ARES", "CARLOS", "KARL", "SARAH"]
        return []
    
    def get_exercises_for_student(self, student):
        """Récupère les exercices pour un étudiant donné depuis l'onglet Results"""
        if self.results_widget:
            try:
                # Get the actual exercises from the results widget
                return self.results_widget.get_exercises_for_student(student)
            except AttributeError:
                pass
                
        # Si on ne peut pas accéder directement au ResultsWidget, essayer de récupérer les données
        # depuis les fichiers logs ou le système de stockage temporaire
        try:
            # Essayer de trouver le répertoire des exercices soumis
            base_dirs = [
                os.path.join(os.getcwd(), "tests", "java_samples", "TD*"),
                os.path.join(os.getcwd(), "submissions", "*"),
                # Autres chemins possibles où les soumissions pourraient être stockées
            ]
            
            student_dirs = []
            for base in base_dirs:
                for td_dir in glob.glob(base):
                    student_dir = os.path.join(td_dir, student)
                    if os.path.exists(student_dir):
                        student_dirs.append(student_dir)
            
            if not student_dirs:
                # Aucun répertoire d'étudiant trouvé
                return self.get_default_exercises()
                
            # Récupérer tous les fichiers .java dans les répertoires de l'étudiant
            exercises = []
            for student_dir in student_dirs:
                java_files = glob.glob(os.path.join(student_dir, "*.java"))
                for file_path in java_files:
                    file_name = os.path.basename(file_path)
                    
                    # Déterminer l'ID de l'exercice à partir du nom du fichier
                    exercise_id = self.get_exercise_id_from_filename(file_name)
                    if exercise_id:
                        # Vérifier si on a une configuration pour cet ID d'exercice
                        if exercise_id in self.exercise_configs:
                            config = self.exercise_configs[exercise_id]
                            if isinstance(config, dict) and "name" in config:
                                display_name = config["name"]
                            else:
                                display_name = exercise_id
                        else:
                            display_name = exercise_id
                            
                        exercises.append({
                            'id': exercise_id,
                            'file': file_name,
                            'status': 'En attente',
                            'path': file_path,  # Stocker le chemin complet pour un accès facile
                            'display_name': display_name
                        })
                        
                        # Ajouter au cache des chemins
                        self.exercise_file_paths[exercise_id] = file_path
            
            return exercises if exercises else self.get_default_exercises()
            
        except Exception as e:
            logging.error(f"Erreur lors de la recherche des exercices: {str(e)}")
            return self.get_default_exercises()
    
    def get_exercise_id_from_filename(self, filename):
        """Détermine l'ID de l'exercice à partir du nom de fichier"""
        # Essayer d'identifier l'exercice en utilisant les configurations connues
        filename_lower = filename.lower()
        
        # Vérifier chaque configuration d'exercice pour voir si le nom de fichier correspond
        for exercise_id, config in self.exercise_configs.items():
            # Si la configuration contient un champ "name", l'utiliser comme autre identifiant
            ex_name = config.get("name", "").lower() if isinstance(config, dict) else ""
            
            if exercise_id.lower() in filename_lower or (ex_name and ex_name.replace(" ", "-") in filename_lower):
                return exercise_id
        
        # Si aucune correspondance directe, essayer de déterminer par des mots-clés
        if "fonction-racine" in filename_lower or "racine" in filename_lower:
            return "09-fonction-racine-carree"
        elif "comptage-mots" in filename_lower or "comptage" in filename_lower:
            return "10-comptage-mots"
        elif "sequence-numerique" in filename_lower or "sequence" in filename_lower:
            return "11-sequence-numerique"
        elif "triangle-isocele" in filename_lower or "triangle" in filename_lower:
            return "12-triangle-isocele"
        
        # Stratégie par défaut: extraire la partie avant le premier tiret ou point
        match = re.search(r'^([a-zA-Z0-9-]+)', filename)
        if match:
            return match.group(1)
            
        return None
    
    def get_default_exercises(self):
        """Retourne une liste d'exercices par défaut si aucun n'est trouvé"""
        # Chercher quels exercices ont des configurations
        default_exercises = []
        for exercise_id in self.exercise_configs:
            if isinstance(self.exercise_configs[exercise_id], dict) and "name" in self.exercise_configs[exercise_id]:
                display_name = self.exercise_configs[exercise_id]["name"]
            else:
                display_name = exercise_id
                
            default_exercises.append({
                'id': exercise_id,
                'file': f"{exercise_id}.java",
                'status': 'En attente',
                'display_name': display_name
            })
            
        # Limiter à quelques exercices pour ne pas surcharger l'interface
        return default_exercises[:5] if default_exercises else [
            {'id': 'sequence-numerique', 'file': 'sequence-numerique.java', 'status': 'En attente'},
            {'id': 'triangle-isocele', 'file': 'triangle-isocele.java', 'status': 'En attente'}
        ]
    
    def get_analysis_data(self, student, exercise_id):
        """Récupère les données d'analyse pour un étudiant et un exercice"""
        # Initialiser les variables de retour
        code = ""
        analysis_results = ""
        execution_results = ""
        
        print(f"Recherche des données pour {student}/{exercise_id}")
        
        # 1. D'abord chercher dans nos données mises en cache
        if student in self.exercise_data and exercise_id in self.exercise_data[student]:
            data = self.exercise_data[student][exercise_id]
            if 'code' in data and data['code']:
                code = data['code']
                print(f"Code récupéré depuis le cache pour {student}/{exercise_id}: {len(code)} caractères")
            if 'analysis' in data and data['analysis']:
                analysis_results = data['analysis']
            if 'execution' in data and data['execution']:
                execution_results = data['execution']
        
        # 2. Si le code n'est pas dans le cache, chercher dans le tableau de résultats
        if not code and self.results_widget:
            # Parcourir le tableau de résultats
            if hasattr(self.results_widget, 'results_table'):
                for i in range(self.results_widget.results_table.rowCount()):
                    student_item = self.results_widget.results_table.item(i, 0)
                    if student_item and student_item.text() == student:
                        # Obtenir le widget d'exercice
                        exercise_widget = self.results_widget.results_table.cellWidget(i, 1)
                        if exercise_widget:
                            # Vérifier si cet exercice correspond à celui que nous cherchons
                            try:
                                widget_exercise_name = exercise_widget.get_exercise_name()
                                widget_file_name = exercise_widget.get_file_name()
                                
                                # Vérifier la correspondance par nom ou par ID
                                if (exercise_id.lower() in widget_exercise_name.lower() or 
                                    exercise_id.lower() in widget_file_name.lower() or
                                    self._normalize_exercise_id(exercise_id) == self._normalize_exercise_id(widget_exercise_name)):
                                    
                                    print(f"Exercice trouvé dans le tableau: {widget_exercise_name} / {widget_file_name}")
                                    
                                    # Récupérer l'état et les résultats de l'analyse
                                    status_widget = self.results_widget.results_table.cellWidget(i, 2)
                                    if status_widget:
                                        try:
                                            if hasattr(status_widget, 'get_analysis_results'):
                                                analysis_results = status_widget.get_analysis_results()
                                                print(f"Résultats d'analyse récupérés de StatusWidget")
                                            if hasattr(status_widget, 'get_execution_results'):
                                                execution_results = status_widget.get_execution_results()
                                                print(f"Résultats d'exécution récupérés de StatusWidget")
                                        except Exception as e:
                                            print(f"Erreur lors de la récupération des résultats: {e}")
                                    
                                    # Récupérer le code source
                                    try:
                                        if hasattr(exercise_widget, 'get_code'):
                                            code = exercise_widget.get_code()
                                            print(f"Code récupéré depuis ExerciseWidget: {len(code)} caractères")
                                        # Essayer d'autres méthodes pour obtenir le code
                                        elif hasattr(self.results_widget, 'get_code_for_student'):
                                            code = self.results_widget.get_code_for_student(student, widget_exercise_name)
                                            print(f"Code récupéré via get_code_for_student: {len(code) if code else 0} caractères")
                                    except Exception as e:
                                        print(f"Erreur lors de la récupération du code: {e}")
                            except Exception as e:
                                print(f"Erreur lors de l'accès aux données de l'exercice: {e}")
        
        # 3. Si toujours pas de code, chercher dans le système de fichiers
        if not code:
            # Construire les chemins possibles
            possible_paths = []
            
            # 3.1 Chercher dans les dossiers de TD
            for td_dir in glob.glob(os.path.join(os.getcwd(), "tests", "java_samples", "*")):
                student_dir = os.path.join(td_dir, student)
                if os.path.exists(student_dir):
                    # Essayer avec le nom exact de l'exercice
                    java_file = os.path.join(student_dir, f"{exercise_id}.java")
                    if os.path.exists(java_file):
                        possible_paths.append(java_file)
                    
                    # Essayer avec des formes normalisées comme "FonctionRacineCarree.java" ou "Exercice09.java"
                    normalized_exercise = self._normalize_exercise_id(exercise_id)
                    alt_files = [
                        os.path.join(student_dir, f"{normalized_exercise}.java"),
                        os.path.join(student_dir, f"Exercice{normalized_exercise.replace('exercice', '')}.java"),
                        os.path.join(student_dir, f"E{normalized_exercise.replace('exercice', '')}.java")
                    ]
                    for alt_file in alt_files:
                        if os.path.exists(alt_file):
                            possible_paths.append(alt_file)
                    
                    # Chercher tous les fichiers Java qui pourraient correspondre
                    for java_file in glob.glob(os.path.join(student_dir, "*.java")):
                        file_name = os.path.basename(java_file).lower()
                        exercise_parts = exercise_id.lower().split('-')
                        # Chercher des correspondances partielles
                        for part in exercise_parts:
                            if part and len(part) > 2 and part in file_name:
                                possible_paths.append(java_file)
                                break
            
            # 3.2 Essayer de lire le premier fichier trouvé
            for file_path in possible_paths:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        code = f.read()
                        print(f"Code trouvé dans {file_path}: {len(code)} caractères")
                        
                        # Stocker dans le cache pour une utilisation future
                        if student not in self.exercise_data:
                            self.exercise_data[student] = {}
                        if exercise_id not in self.exercise_data[student]:
                            self.exercise_data[student][exercise_id] = {}
                        self.exercise_data[student][exercise_id]['code'] = code
                        
                        # Stocker également le chemin du fichier
                        self.exercise_file_paths[exercise_id] = file_path
                        break
                except Exception as e:
                    print(f"Erreur lors de la lecture du fichier {file_path}: {e}")
        
        # Si code toujours non trouvé, créer un squelette minimal
        if not code:
            print(f"Aucun code trouvé pour {student}/{exercise_id}. Utilisation du code depuis l'écran Résultats.")
            
            # Essayer d'accéder directement au code via le widget de résultats
            if self.results_widget:
                try:
                    # Essayer plusieurs méthodes pour obtenir le code
                    if hasattr(self.results_widget, 'get_editor_content'):
                        code = self.results_widget.get_editor_content()
                        print(f"Code récupéré via get_editor_content: {len(code) if code else 0} caractères")
                    elif hasattr(self.results_widget, 'get_current_code'):
                        code = self.results_widget.get_current_code()
                        print(f"Code récupéré via get_current_code: {len(code) if code else 0} caractères")
                except Exception as e:
                    print(f"Erreur lors de la récupération du code depuis l'éditeur: {e}")
        
        # Dernière tentative - créer un squelette si nécessaire
        if not code:
            print(f"Aucun code trouvé pour {student}/{exercise_id}. Création d'un squelette.")
            # Créer un squelette de code minimale avec l'ID de l'exercice
            code = f"""
/**
 * Exercice: {exercise_id}
 * Étudiant: {student}
 */
public class {self._normalize_exercise_id(exercise_id)} {{
    // Le code de l'exercice n'a pas été trouvé
    // Cette classe est un squelette généré automatiquement
}}
"""
        
        # Stocker les résultats d'analyse et d'exécution dans notre cache
        if student not in self.exercise_data:
            self.exercise_data[student] = {}
        if exercise_id not in self.exercise_data[student]:
            self.exercise_data[student][exercise_id] = {}
        
        # Mettre à jour le cache
        self.exercise_data[student][exercise_id]['code'] = code
        self.exercise_data[student][exercise_id]['analysis'] = analysis_results
        self.exercise_data[student][exercise_id]['execution'] = execution_results
        
        print(f"Données récupérées pour {student}/{exercise_id}: code={bool(code)}, analyse={bool(analysis_results)}, exécution={bool(execution_results)}")
        
        return code, analysis_results, execution_results
    
    def _normalize_exercise_id(self, exercise_id):
        """Normalise un ID d'exercice pour faciliter les comparaisons"""
        # Supprimer les caractères spéciaux
        normalized = re.sub(r'[^a-zA-Z0-9]', '', exercise_id)
        
        # Gérer les cas spéciaux "09-fonction-racine-carree" -> "FonctionRacineCarree"
        if "fonction-racine" in exercise_id.lower() or "09" in exercise_id:
            return "FonctionRacineCarree"
        elif "comptage-mots" in exercise_id.lower() or "10" in exercise_id:
            return "ComptageMots"
        
        # Première lettre en majuscule
        result = normalized[0].upper() + normalized[1:] if normalized else normalized
        return result
    
    def get_file_path_for_exercise(self, student, exercise_id):
        """Obtient le chemin complet vers le fichier de l'exercice"""
        # Parcourir les exercices pour trouver celui correspondant à l'ID
        exercises = self.get_exercises_for_student(student)
        for exercise in exercises:
            if exercise.get('id') == exercise_id:
                return exercise.get('path')  # Retourne le chemin complet s'il est disponible
        return None
    
    def get_analysis_results_from_logs(self, student, exercise_id):
        """Tente de récupérer les résultats d'analyse depuis les fichiers logs"""
        try:
            # Chercher dans les fichiers logs récents pour les résultats
            log_files = glob.glob(os.path.join(os.getcwd(), "logs", "*.log"))
            if not log_files:
                return "Pas de résultats d'analyse disponibles"
                
            # Trier par date de modification (le plus récent d'abord)
            log_files.sort(key=os.path.getmtime, reverse=True)
            
            # Rechercher des informations sur cet exercice dans les logs récents
            for log_file in log_files[:3]:  # Examiner seulement les 3 fichiers les plus récents
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Rechercher des mentions de l'étudiant et de l'exercice
                    pattern = rf"{re.escape(student)}.*?{re.escape(exercise_id)}.*?((Code valide)|(Méthodes manquantes)|(Erreurs de compilation))"
                    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
                    
                    if match:
                        # Extraire un fragment pertinent du log
                        start = max(0, match.start() - 100)
                        end = min(len(content), match.end() + 100)
                        return content[start:end]
            
            return "Analyse effectuée mais résultats non disponibles"
            
        except Exception as e:
            logging.error(f"Erreur lors de la recherche des résultats d'analyse: {str(e)}")
            return "Erreur lors de la récupération des résultats d'analyse"
    
    def get_execution_results_from_logs(self, student, exercise_id):
        """Tente de récupérer les résultats d'exécution depuis les fichiers logs"""
        try:
            # Chercher dans les fichiers logs récents pour les résultats
            log_files = glob.glob(os.path.join(os.getcwd(), "logs", "*.log"))
            if not log_files:
                return "Pas de résultats d'exécution disponibles"
                
            # Trier par date de modification (le plus récent d'abord)
            log_files.sort(key=os.path.getmtime, reverse=True)
            
            # Rechercher des informations sur cet exercice dans les logs récents
            for log_file in log_files[:3]:  # Examiner seulement les 3 fichiers les plus récents
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Rechercher des mentions de l'étudiant et de l'exercice
                    pattern = rf"{re.escape(student)}.*?{re.escape(exercise_id)}.*?((Test réussi)|(Échec de test)|(Exécution terminée))"
                    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
                    
                    if match:
                        # Extraire un fragment pertinent du log
                        start = max(0, match.start() - 100)
                        end = min(len(content), match.end() + 200)
                        return content[start:end]
            
            return "Pas de résultats d'exécution disponibles"
            
        except Exception as e:
            logging.error(f"Erreur lors de la recherche des résultats d'exécution: {str(e)}")
            return "Pas de résultats d'exécution disponibles"
    
    def get_exercise_status(self, student, exercise_id):
        """
        Récupère le statut d'un exercice pour un étudiant donné.
        
        Args:
            student (str): Nom de l'étudiant
            exercise_id (str): Identifiant de l'exercice
            
        Returns:
            str: Statut de l'exercice
        """
        # Essayer de récupérer le statut depuis les résultats
        if self.results_widget:
            try:
                # Parcourir le tableau de résultats pour trouver l'exercice correspondant
                for i in range(self.results_widget.results_table.rowCount()):
                    student_item = self.results_widget.results_table.item(i, 0)
                    if student_item and student_item.text() == student:
                        exercise_widget = self.results_widget.results_table.cellWidget(i, 1)
                        result_widget = self.results_widget.results_table.cellWidget(i, 3)
                        
                        if exercise_widget:
                            ex_name = exercise_widget.get_exercise_name().lower()
                            
                            # Vérifier la correspondance
                            if exercise_id.lower() in ex_name:
                                # Récupérer le statut
                                if result_widget:
                                    if hasattr(result_widget, 'get_score_text'):
                                        return f"Noté: {result_widget.get_score_text()}"
                                    else:
                                        return result_widget.text()
                                return "Vérifié"
            except Exception as e:
                logging.error(f"Erreur lors de la récupération du statut: {str(e)}")
        
        # Valeur par défaut
        return "En attente"
    
    def get_execution_analysis(self, student, exercise_id):
        """Récupère les résultats d'exécution et d'analyse pour un étudiant et un exercice spécifique"""
        analysis_results = ""
        execution_results = ""
        
        try:
            # Essayer de récupérer depuis le widget de résultats
            if self.results_widget:
                # Récupérer les résultats d'analyse
                if hasattr(self.results_widget, 'get_analysis_results'):
                    analysis_results = self.results_widget.get_analysis_results(student, exercise_id)
                elif hasattr(self.results_widget, 'get_analysis_for_student'):
                    analysis_results = self.results_widget.get_analysis_for_student(student, exercise_id)
                
                # Récupérer les résultats d'exécution
                if hasattr(self.results_widget, 'get_execution_results'):
                    execution_results = self.results_widget.get_execution_results(student, exercise_id)
                elif hasattr(self.results_widget, 'get_execution_for_student'):
                    execution_results = self.results_widget.get_execution_for_student(student, exercise_id)
        except Exception as e:
            print(f"Erreur lors de la récupération des résultats d'analyse/exécution: {e}")
        
        return execution_results, analysis_results
    
    def get_result_data(self, student, exercise_id):
        """Récupère les données de résultat pour un étudiant et un exercice spécifique"""
        result = "Non évalué"
        
        try:
            # Parcourir le tableau de résultats pour trouver l'exercice correspondant
            if self.results_widget and hasattr(self.results_widget, 'results_table'):
                for i in range(self.results_widget.results_table.rowCount()):
                    student_item = self.results_widget.results_table.item(i, 0)
                    if student_item and student_item.text() == student:
                        exercise_widget = self.results_widget.results_table.cellWidget(i, 1)
                        result_widget = self.results_widget.results_table.cellWidget(i, 3)
                        
                        if exercise_widget and result_widget:
                            ex_name = exercise_widget.get_exercise_name().lower()
                            ex_file = exercise_widget.get_file_name().lower()
                            
                            # Vérifier si l'exercice correspond
                            if ((exercise_id.lower() in ex_name) or (exercise_id.lower() in ex_file)):
                                # Extraire le résultat
                                try:
                                    if hasattr(result_widget, 'get_score_text'):
                                        result = result_widget.get_score_text()
                                    elif hasattr(result_widget, 'text'):  # Si c'est un QLabel ou similaire
                                        result = result_widget.text()
                                    elif hasattr(result_widget, 'toPlainText'):  # Si c'est un QTextEdit
                                        result = result_widget.toPlainText()
                                    else:
                                        # Fallback: convertir en chaîne
                                        result = str(result_widget)
                                    print(f"Résultat trouvé dans le tableau pour {exercise_id}: {result}")
                                    return result
                                except Exception as e:
                                    print(f"Erreur lors de l'extraction du résultat: {e}")
        except Exception as e:
            print(f"Erreur lors de la récupération des données de résultat: {e}")
        
        return result
    
    def store_exercise_file_path(self, student, exercise_id, file_path):
        """Stocke le chemin d'un fichier d'exercice pour un étudiant
        
        Args:
            student: Nom de l'étudiant
            exercise_id: ID de l'exercice
            file_path: Chemin du fichier
        """
        if student not in self.student_exercise_files:
            self.student_exercise_files[student] = {}
        
        self.student_exercise_files[student][exercise_id] = file_path
        print(f"Stocké: {student}/{exercise_id} -> {file_path}")
        
    def get_exercise_file_path(self, student, exercise_id):
        """Récupère le chemin d'un fichier d'exercice pour un étudiant
        
        Args:
            student: Nom de l'étudiant
            exercise_id: ID de l'exercice
            
        Returns:
            str: Chemin du fichier ou None si non trouvé
        """
        if student in self.student_exercise_files and exercise_id in self.student_exercise_files[student]:
            return self.student_exercise_files[student][exercise_id]
        
        return None
    
    def extract_file_paths_from_results(self, student):
        """Extrait directement les chemins de fichiers depuis l'écran Results.
        
        Parcourt le tableau des résultats pour trouver tous les fichiers de l'étudiant
        et les met en cache.
        
        Args:
            student: Nom de l'étudiant
        """
        if not self.results_widget or not hasattr(self.results_widget, 'results_table'):
            print("Impossible d'extraire les chemins des fichiers: widget de résultats non disponible")
            return {}
            
        extracted_paths = {}
        try:
            # Parcourir le tableau des résultats
            for i in range(self.results_widget.results_table.rowCount()):
                student_item = self.results_widget.results_table.item(i, 0)
                
                # Vérifier si c'est la ligne de l'étudiant recherché
                if student_item and student_item.text() == student:
                    # Obtenir le widget de l'exercice et le nom du fichier
                    exercise_widget = self.results_widget.results_table.cellWidget(i, 1)
                    
                    if exercise_widget:
                        exercise_id = None
                        file_name = None
                        
                        # Extraire l'ID de l'exercice et le nom du fichier
                        if hasattr(exercise_widget, 'get_exercise_name'):
                            exercise_id = exercise_widget.get_exercise_name()
                        if hasattr(exercise_widget, 'get_file_name'):
                            file_name = exercise_widget.get_file_name()
                            
                        # Si on a un nom de fichier, essayer de trouver le chemin complet
                        if exercise_id and file_name:
                            print(f"Extraction pour {student}: exercice={exercise_id}, fichier={file_name}")
                            
                            # Chercher le fichier depuis le chemin de base
                            # (peut être dans n'importe quel sous-dossier de tests/java_samples/)
                            file_found = False
                            
                            # 1. Chercher dans tous les dossiers TD*
                            for td_dir in glob.glob(os.path.join(os.getcwd(), "tests", "java_samples", "TD*")):
                                # Chercher directement dans le répertoire TD
                                full_path = os.path.join(td_dir, file_name)
                                if os.path.exists(full_path):
                                    extracted_paths[exercise_id] = full_path
                                    self.store_exercise_file_path(student, exercise_id, full_path)
                                    print(f"Fichier trouvé dans le TD: {full_path}")
                                    file_found = True
                                    break
                                    
                                # Chercher dans le répertoire étudiant/exercice
                                student_dir = os.path.join(td_dir, student)
                                if os.path.exists(student_dir):
                                    full_path = os.path.join(student_dir, file_name)
                                    if os.path.exists(full_path):
                                        extracted_paths[exercise_id] = full_path
                                        self.store_exercise_file_path(student, exercise_id, full_path)
                                        print(f"Fichier trouvé dans le répertoire étudiant: {full_path}")
                                        file_found = True
                                        break
                                        
                                    # Chercher dans des sous-dossiers (_temp_java_files, etc.)
                                    for subdir in glob.glob(os.path.join(student_dir, "*")):
                                        if os.path.isdir(subdir):
                                            full_path = os.path.join(subdir, file_name)
                                            if os.path.exists(full_path):
                                                extracted_paths[exercise_id] = full_path
                                                self.store_exercise_file_path(student, exercise_id, full_path)
                                                print(f"Fichier trouvé dans un sous-dossier: {full_path}")
                                                file_found = True
                                                break
                            
                            # 2. Chercher dans le répertoire _temp_files
                            if not file_found:
                                temp_dir = os.path.join(os.getcwd(), "temp_fixed_files")
                                if os.path.exists(temp_dir):
                                    full_path = os.path.join(temp_dir, file_name)
                                    if os.path.exists(full_path):
                                        extracted_paths[exercise_id] = full_path
                                        self.store_exercise_file_path(student, exercise_id, full_path)
                                        print(f"Fichier trouvé dans temp_fixed_files: {full_path}")
                                        file_found = True
            
            print(f"Extraction des chemins de fichiers pour {student}: {len(extracted_paths)} fichiers trouvés")
            return extracted_paths
            
        except Exception as e:
            print(f"Erreur lors de l'extraction des chemins de fichiers: {str(e)}")
            import traceback
            traceback.print_exc()
            return {} 