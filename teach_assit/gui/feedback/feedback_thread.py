"""
Thread pour générer du feedback avec l'API Gemini sans bloquer l'interface.
"""

import json
import re
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
                
                # Ajouter les critères de notation spécifiques à cet exercice avec insistance
                grading_criteria = config.get('grading_criteria', []) if config else []
                if grading_criteria:
                    for criterion in grading_criteria:
                        points = criterion.get('points', 0)
                        title = criterion.get('title', '')
                        description = criterion.get('description', '')
                        exercise_details += f"- {title} ({points} pts): {description}\n"
                        
                        subcriteria = criterion.get('subcriteria', [])
                        for subcriterion in subcriteria:
                            exercise_details += f"  * {subcriterion.get('text', '')}\n"
                
                    # Indiquer clairement que ces critères doivent être utilisés pour la notation
                    exercise_details += "\n** IMPORTANT: Tu DOIS évaluer cet exercice en utilisant précisément ces critères et attribuer les points en fonction. **\n"
                else:
                    exercise_details += "Aucun critère d'évaluation spécifié pour cet exercice.\n"
                    
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
            
            IMPORTANT: Ta réponse DOIT être formatée en Markdown bien structuré avec:
            
            # Évaluation de TD: {self.student_name}
            
            ## Évaluation Globale
            
            *Brève description de la performance générale sur le TD*
            
            ## Exercice 1: [Nom du premier exercice]
            
            ### Points forts
            - Liste des points forts
            
            ### Points à améliorer
            - Liste des points à améliorer avec recommandations
            
            ### Note: X/10
            
            ## Exercice 2: [Nom du deuxième exercice]
            
            *Même structure que l'exercice 1*
            
            ## Note Globale pour le TD : X/20
            
            ## Recommandations générales
            
            - Liste de recommandations pour progresser
            
            RAPPEL: Respecte SCRUPULEUSEMENT les notes déjà attribuées indiquées dans "NOTES EXISTANTES".
            """
            
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