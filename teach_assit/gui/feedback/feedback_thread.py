"""
Thread pour générer du feedback avec l'API Gemini sans bloquer l'interface.
"""

import json
import re
import os
from PyQt5.QtCore import QThread, pyqtSignal
from google import genai

class FeedbackThread(QThread):
    """Thread pour générer du feedback avec l'API Gemini sans bloquer l'interface."""
    feedback_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    progress_changed = pyqtSignal(int)
    
    def __init__(self, api_key, student_name, exercises_data):
        super().__init__()
        self.api_key = api_key
        self.student_name = student_name
        self.exercises_data = exercises_data  # Liste de dictionnaires contenant les données de chaque exercice
        
    def run(self):
        try:
            # Émettre un signal de progression initiale
            self.progress_changed.emit(10)
            
            # Vérifier si nous avons des données d'exercices valides
            if not self.exercises_data:
                self.error_occurred.emit("Aucune donnée d'exercice fournie. Veuillez vérifier que les fichiers d'exercices sont correctement chargés.")
                return
            
            # Compter les exercices avec du code valide
            valid_exercises = 0
            for exercise in self.exercises_data:
                # Si le code est manquant ou trop court, essayer de le charger à partir du chemin de fichier
                if (not exercise.get('code') or len(exercise.get('code', '').strip()) < 100) and exercise.get('file_path'):
                    try:
                        file_path = exercise.get('file_path')
                        print(f"Tentative de chargement du code depuis le fichier: {file_path}")
                        with open(file_path, 'r', encoding='utf-8') as f:
                            exercise['code'] = f.read()
                        print(f"Code chargé depuis {file_path}: {len(exercise['code'])} caractères")
                    except Exception as e:
                        print(f"Erreur lors de la lecture du fichier {file_path}: {str(e)}")
                
                # Vérifier à nouveau si nous avons du code valide après la tentative de chargement
                if exercise.get('code') and len(exercise.get('code', '').strip()) > 100:
                    valid_exercises += 1
            
            if valid_exercises == 0:
                self.error_occurred.emit("Aucun exercice avec du code valide n'a été trouvé. Veuillez vérifier les fichiers source et les chemins.")
                return
            
            print(f"Démarrage du thread de feedback pour {self.student_name} avec {len(self.exercises_data)} exercices (dont {valid_exercises} valides)")
            
            # Configurer l'API Gemini en utilisant le nouvel API Client
            try:
                client = genai.Client(api_key=self.api_key)
            except Exception as e:
                error_msg = f"Erreur lors de l'initialisation du client Gemini: {str(e)}"
                print(error_msg)
                self.error_occurred.emit(error_msg)
                return
            
            # Émettre un signal de progression
            self.progress_changed.emit(20)
            
            # Préparer les informations sur tous les exercices et leurs critères
            exercise_details = ""
            total_exercises = len(self.exercises_data)
            existing_scores = {}
            assessment_info = {}  # Pour stocker les informations sur le TD actuel
            
            # Récupérer l'ID du TD actuel à partir du premier exercice
            if self.exercises_data and 'config' in self.exercises_data[0]:
                assessment_id = self.exercises_data[0].get('assessment_id', '')
                if assessment_id:
                    # Essayer de charger le fichier du TD pour obtenir les points max par exercice
                    assessments_dir = os.path.join(os.getcwd(), "assessments")
                    assessment_file = os.path.join(assessments_dir, f"{assessment_id}.json")
                    if os.path.exists(assessment_file):
                        try:
                            with open(assessment_file, 'r', encoding='utf-8') as f:
                                assessment_info = json.load(f)
                                print(f"Informations du TD chargées: {assessment_id}")
                        except Exception as e:
                            print(f"Erreur lors du chargement du fichier TD {assessment_file}: {str(e)}")
            
            # Informations sur le TD à utiliser dans le prompt
            td_name = assessment_info.get('name', 'Travaux Dirigés')
            td_max_points = assessment_info.get('totalMaxPoints', 20)  # Par défaut 20 points
            exercise_max_points = {}
            
            # Extraire les points maximum pour chaque exercice du fichier TD
            for ex in assessment_info.get('exercises', []):
                ex_id = ex.get('exerciseId', '')
                if ex_id and 'maxPoints' in ex:
                    exercise_max_points[ex_id] = ex.get('maxPoints')
                    print(f"Points maximum pour {ex_id}: {exercise_max_points[ex_id]}")
            
            for i, exercise in enumerate(self.exercises_data):
                # Mettre à jour la progression (entre 20 et 50)
                progress = 20 + int((i / total_exercises) * 30)
                self.progress_changed.emit(progress)
                
                exercise_id = exercise.get('id', '')
                code = exercise.get('code', '')
                analysis = exercise.get('analysis', '')
                execution = exercise.get('execution', '')
                config = exercise.get('config', {})
                
                # Récupérer le statut et le résultat depuis le tableau des exercices
                status = exercise.get('status', 'Non évalué')
                result = exercise.get('result', 'Pas de résultat disponible')
                
                # Extraire la note existante si disponible - priorité aux notes attribuées
                # Recherche plus aggressive des notes existantes
                score_patterns = [
                    r'Noté:\s*(\d+(?:\.\d+)?)/(\d+)(?:\s*pt)?',  # Format: Noté: X/Y pt
                    r'(\d+(?:\.\d+)?)/(\d+)(?:\s*pt)?',          # Format: X/Y pt
                    r'Note:\s*(\d+(?:\.\d+)?)/(\d+)',            # Format: Note: X/Y
                    r'Score:\s*(\d+(?:\.\d+)?)',                 # Format: Score: X
                ]
                
                # Chercher d'abord dans le statut
                for pattern in score_patterns:
                    score_match = re.search(pattern, status)
                    if score_match:
                        score_value = float(score_match.group(1))
                        max_score = float(score_match.group(2)) if len(score_match.groups()) > 1 else 20.0
                        existing_scores[exercise_id] = {
                            'score': score_value,
                            'max': max_score
                        }
                        print(f"Note existante trouvée dans le statut pour {exercise_id}: {score_value}/{max_score}")
                        break
                
                # Ensuite chercher dans le résultat si aucune note n'a été trouvée
                if exercise_id not in existing_scores:
                    for pattern in score_patterns:
                        score_match = re.search(pattern, result)
                        if score_match:
                            score_value = float(score_match.group(1))
                            max_score = float(score_match.group(2)) if len(score_match.groups()) > 1 else 20.0
                            existing_scores[exercise_id] = {
                                'score': score_value,
                                'max': max_score
                            }
                            print(f"Note existante trouvée dans le résultat pour {exercise_id}: {score_value}/{max_score}")
                            break
                
                # Ajouter les détails de cet exercice
                exercise_details += f"""
                ===== EXERCICE: {exercise_id} =====
                DESCRIPTION: {config.get('description', 'Pas de description disponible') if config else 'Pas de description disponible'}
                
                STATUT: {status}
                RÉSULTAT: {result}
                
                CODE SOURCE:
                ```java
                {code}
                ```
                
                RÉSULTATS D'ANALYSE:
                {analysis}
                
                RÉSULTATS D'EXÉCUTION:
                {execution}
                
                CRITÈRES D'ÉVALUATION:
                """
                
                # Calculer le nombre de points maximum pour cet exercice
                max_points = exercise_max_points.get(exercise_id, 20)  # Par défaut 20 points si non spécifié
                
                # Ajouter les critères de notation spécifiques à cet exercice avec insistance
                grading_criteria = config.get('grading_criteria', []) if config else []
                total_criteria_points = 0
                
                if grading_criteria:
                    exercise_details += f"TOTAL: {max_points} points répartis comme suit:\n\n"
                    
                    for criterion in grading_criteria:
                        points = criterion.get('points', 0)
                        total_criteria_points += points
                        title = criterion.get('title', '')
                        description = criterion.get('description', '')
                        exercise_details += f"- {title} ({points} pts): {description}\n"
                        
                        subcriteria = criterion.get('subcriteria', [])
                        for subcriterion in subcriteria:
                            exercise_details += f"  * {subcriterion.get('text', '')}\n"
                
                    # Vérifier si les points des critères correspondent au total
                    if total_criteria_points != max_points:
                        exercise_details += f"\n** ATTENTION: Les points des critères ({total_criteria_points}) ne correspondent pas au total de l'exercice ({max_points}). "
                        exercise_details += f"Tu dois ajuster la répartition pour que le total soit {max_points} points. **\n"
                    
                    # Indiquer clairement que ces critères doivent être utilisés pour la notation
                    exercise_details += f"\n** IMPORTANT: Tu DOIS évaluer cet exercice en utilisant précisément ces critères et attribuer les points en fonction, pour un total de {max_points} points. **\n"
                else:
                    exercise_details += f"Pas de critères spécifiques. Évaluer sur {max_points} points au total.\n"
                    
                # Si des résultats d'analyse/exécution existent, extraire les critères satisfaits
                criteres_satisfaits = []
                criteres_non_satisfaits = []
                
                # Analyser les résultats d'analyse pour extraire les critères satisfaits
                if "Syntaxe" in analysis and "✅" in analysis:
                    criteres_satisfaits.append("Syntaxe correcte")
                elif "Syntaxe" in analysis:
                    criteres_non_satisfaits.append("Problèmes de syntaxe détectés")
                    
                if "Méthodes" in analysis and "✅" in analysis:
                    criteres_satisfaits.append("Toutes les méthodes requises sont présentes")
                elif "Méthodes" in analysis:
                    criteres_non_satisfaits.append("Méthodes manquantes ou incorrectes")
                    
                # Vérifier les patterns/structures
                if "Structures" in analysis and "✅" in analysis:
                    criteres_satisfaits.append("Structures de code appropriées")
                elif "Structures" in analysis:
                    criteres_non_satisfaits.append("Utilisation incorrecte des structures de code")
                    
                # Si des critères ont été identifiés, les ajouter au détail
                if criteres_satisfaits or criteres_non_satisfaits:
                    exercise_details += "\nCRITÈRES SATISFAITS AUTOMATIQUEMENT:\n"
                    for critere in criteres_satisfaits:
                        exercise_details += f"+ {critere}\n"
                    
                    if criteres_non_satisfaits:
                        exercise_details += "\nCRITÈRES NON SATISFAITS:\n"
                        for critere in criteres_non_satisfaits:
                            exercise_details += f"- {critere}\n"
                
                # Ajouter des notes/directives spécifiques selon le type d'exercice
                if "fonction-racine" in exercise_id.lower() or "09-" in exercise_id.lower():
                    exercise_details += """
                    DIRECTIVES SPÉCIFIQUES:
                    - Vérifier si la fonction calcule correctement la racine carrée
                    - Vérifier la gestion des cas particuliers (nombres négatifs, zéro)
                    - Évaluer l'efficacité et l'optimisation de l'algorithme
                    """
                elif "comptage-mots" in exercise_id.lower() or "10-" in exercise_id.lower():
                    exercise_details += """
                    DIRECTIVES SPÉCIFIQUES:
                    - Vérifier si la fonction compte correctement les mots
                    - Évaluer la gestion des cas particuliers (texte vide, espaces multiples)
                    - Vérifier le traitement des séparateurs
                    """
                
                exercise_details += "\n"
            
            # Émettre un signal de progression
            self.progress_changed.emit(50)
            
            # Préparer le prompt pour l'évaluation globale du TD
            prompt = f"""
            Tu es un assistant pédagogique spécialisé dans l'évaluation de code Java pour des étudiants.
            Analyse l'ensemble des exercices du TD pour l'étudiant {self.student_name} et fournis une évaluation complète.
            
            TD: {td_name}
            NOTE TOTALE MAXIMALE DU TD: {td_max_points} points
            
            {exercise_details}
            
            NOTES EXISTANTES (TRÈS IMPORTANT - TU DOIS RESPECTER CES NOTES):
            """
            
            # Ajouter les notes existantes au prompt avec forte insistance
            if existing_scores:
                for ex_id, score_info in existing_scores.items():
                    prompt += f"- {ex_id}: {score_info['score']}/{score_info['max']} points\n"
                prompt += "\nTu DOIS ABSOLUMENT respecter ces notes existantes dans ton évaluation. Ne les modifie JAMAIS.\n"
                prompt += "Ces notes ont déjà été attribuées manuellement par un enseignant et doivent rester inchangées.\n"
            
            prompt += """
            DIRECTIVES D'ÉVALUATION:
            
            1. Évalue CHAQUE exercice selon ses critères spécifiques indiqués ci-dessus.
            2. Pour chaque critère, attribue les points de manière précise:
               - Points complets si toutes les vérifications sont correctes et le code passe tous les tests
               - Points partiels si erreurs mineures ou code fonctionnel mais mal structuré
               - 0 point en cas d'erreurs majeures ou non-respect des consignes
            3. Lorsqu'une note existante est déjà spécifiée, TU DOIS LA RESPECTER ABSOLUMENT. Ne la modifie pas.
            4. Pour les exercices sans note existante:
               - Évalue de façon rigoureuse en utilisant les critères fournis
               - Attribue les points en fonction des critères précis définis pour chaque exercice
            5. IMPORTANT: La note totale du TD est sur un maximum de %s points, et NON PAS la somme des points maximums de chaque exercice.
            
            IMPORTANT: Ta réponse DOIT être formatée en Markdown bien structuré avec:
            
            # Évaluation de TD: {self.student_name}
            
            ## Évaluation Globale
            
            *Brève description de la performance générale sur le TD*
            
            ## Exercice 1: [Nom du premier exercice]
            
            ### Points forts
            - Liste des points forts
            
            ### Points à améliorer
            - Liste des points à améliorer avec recommandations
            
            ### Note: X/Y
            * Détail des points par critère:
              - Critère 1: A/B points
              - Critère 2: C/D points
              - etc.
            
            ## Exercice 2: [Nom du deuxième exercice]
            
            *Même structure que l'exercice 1*
            
            ## Note Globale pour le TD : X/%s
            
            ## Recommandations générales
            
            - Liste de recommandations pour progresser
            
            RAPPEL: Respecte SCRUPULEUSEMENT les notes déjà attribuées indiquées dans "NOTES EXISTANTES".
            """ % (td_max_points, td_max_points)
            
            # Émettre un signal de progression
            self.progress_changed.emit(80)
            
            # Générer le feedback en utilisant la nouvelle syntaxe
            try:
                print("Envoi de la requête à l'API Gemini...")
                response = client.models.generate_content(
                    model="gemini-2.0-flash", 
                    contents=prompt
                )
                feedback = response.text
                print(f"Réponse reçue de l'API Gemini: {len(feedback)} caractères")
                
                # Vérifier que la réponse est valide
                if not feedback or len(feedback) < 100:
                    error_msg = "La réponse de l'API Gemini est vide ou trop courte. Veuillez réessayer."
                    print(error_msg)
                    self.error_occurred.emit(error_msg)
                    return
            except Exception as e:
                error_msg = f"Erreur lors de la communication avec l'API Gemini: {str(e)}"
                print(error_msg)
                self.error_occurred.emit(error_msg)
                return
            
            # Émettre un signal de progression
            self.progress_changed.emit(95)
            
            # Émettre le signal avec le feedback
            self.feedback_ready.emit(feedback)
            
            # Finaliser la progression
            self.progress_changed.emit(100)
            
        except Exception as e:
            error_msg = f"Erreur inattendue dans le thread de feedback: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            self.error_occurred.emit(error_msg)
            # Réinitialiser la progression en cas d'erreur
            self.progress_changed.emit(0) 