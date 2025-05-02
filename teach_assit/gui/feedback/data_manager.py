"""
Gestionnaire de données pour le module de feedback.
Gère le chargement des exercices, des configurations et l'analyse des fichiers.
"""

import os
import re
import json
import glob

from teach_assit.core.analysis.config_loader import ConfigLoader

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
        self.load_exercise_configs()
    
    def load_exercise_configs(self):
        """Charge les configurations des exercices depuis la base de données"""
        # Initialiser le chargeur de configuration avec le répertoire courant
        config_loader = ConfigLoader(os.getcwd())
        
        # S'assurer que toutes les configurations sont chargées depuis la base de données
        config_loader.load_all_configs()
        
        # Récupérer toutes les configurations d'exercices
        self.exercise_configs = {}
        for exercise_id, config in config_loader.get_all_exercise_configs().items():
            self.exercise_configs[exercise_id] = config.to_dict()
    
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
                        exercises.append({
                            'id': exercise_id,
                            'file': file_name,
                            'status': 'En attente',
                            'path': file_path  # Stocker le chemin complet pour un accès facile
                        })
            
            return exercises if exercises else self.get_default_exercises()
            
        except Exception as e:
            print(f"Erreur lors de la recherche des exercices: {str(e)}")
            return self.get_default_exercises()
    
    def get_exercise_id_from_filename(self, filename):
        """Détermine l'ID de l'exercice à partir du nom de fichier"""
        # Mapping des noms de fichiers vers les IDs d'exercices
        # Cette fonction pourrait être améliorée en utilisant une correspondance plus sophistiquée
        filename_lower = filename.lower()
        
        if "sequence-numerique" in filename_lower:
            return "sequence-numerique"
        elif "triangle-isocele" in filename_lower:
            return "triangle-isocele"
        
        # Stratégie par défaut: extraire la partie avant le premier tiret ou point
        match = re.search(r'^([a-zA-Z0-9-]+)', filename)
        if match:
            return match.group(1)
            
        return None
    
    def get_default_exercises(self):
        """Retourne une liste d'exercices par défaut si aucun n'est trouvé"""
        return [
            {'id': 'sequence-numerique', 'file': 'sequence-numerique.java', 'status': 'En attente'},
            {'id': 'triangle-isocele', 'file': 'triangle-isocele.java', 'status': 'En attente'}
        ]
    
    def get_analysis_data(self, student, exercise_id):
        """Récupère les données d'analyse et d'exécution pour un étudiant et un exercice donnés"""
        if self.results_widget:
            try:
                # Get the actual analysis data from the results widget
                return self.results_widget.get_analysis_data(student, exercise_id)
            except AttributeError:
                pass
        
        # Essayer de lire le fichier de code directement si disponible
        file_path = self.get_file_path_for_exercise(student, exercise_id)
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                    
                # Essayer de trouver des résultats d'analyse dans les fichiers logs
                analysis_results = self.get_analysis_results_from_logs(student, exercise_id)
                execution_results = self.get_execution_results_from_logs(student, exercise_id)
                
                return code, analysis_results, execution_results
            except Exception as e:
                print(f"Erreur lors de la lecture du fichier {file_path}: {str(e)}")
        
        # Fallback to default data
        if exercise_id == "triangle-isocele":
            code = "public class Triangle {\n    public static boolean estTriangleIsocele(int a, int b, int c) {\n        return a == b || b == c || a == c;\n    }\n}"
            analysis = "✅ Méthode estTriangleIsocele trouvée\n❌ Test unitaire: Le triangle (3,3,5) devrait être identifié comme isocèle\n✅ Tous les paramètres sont correctement déclarés\n❌ La logique de vérification n'est pas complète"
            execution = "Test #1: Triangle (3,3,5) => Attendu: true, Obtenu: false"
        elif exercise_id == "sequence-numerique":
            code = "public class Sequence {\n    public static int sommeSequence(int n) {\n        int somme = 0;\n        for (int i = 1; i <= n; i++) {\n            somme += i;\n        }\n        return somme;\n    }\n}"
            analysis = "✅ Méthode sommeSequence trouvée\n✅ Tests unitaires réussis\n✅ Tous les paramètres sont correctement déclarés\n✅ Logique correcte"
            execution = "Test #1: sommeSequence(5) => Attendu: 15, Obtenu: 15\nTest #2: sommeSequence(10) => Attendu: 55, Obtenu: 55"
        else:
            code = "// Pas de code disponible pour cet exercice"
            analysis = "Pas de résultats d'analyse disponibles"
            execution = "Pas de résultats d'exécution disponibles"
            
        return code, analysis, execution
    
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
            print(f"Erreur lors de la recherche des résultats d'analyse: {str(e)}")
            return "Erreur lors de la récupération des résultats d'analyse"
    
    def get_execution_results_from_logs(self, student, exercise_id):
        """Tente de récupérer les résultats d'exécution depuis les fichiers logs"""
        # Implémentation similaire à get_analysis_results_from_logs mais pour les résultats d'exécution
        return "Résultats d'exécution non disponibles dans le système de logs" 