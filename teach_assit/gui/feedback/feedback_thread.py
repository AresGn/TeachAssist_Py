"""
Thread pour générer du feedback avec l'API Gemini sans bloquer l'interface.
"""

import json
from PyQt5.QtCore import QThread, pyqtSignal
from google import genai

class FeedbackThread(QThread):
    """Thread pour générer du feedback avec l'API Gemini sans bloquer l'interface."""
    feedback_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, api_key, student_name, exercises_data):
        super().__init__()
        self.api_key = api_key
        self.student_name = student_name
        self.exercises_data = exercises_data  # Liste de dictionnaires contenant les données de chaque exercice
        
    def run(self):
        try:
            # Configurer l'API Gemini en utilisant le nouvel API Client
            client = genai.Client(api_key=self.api_key)
            
            # Préparer les informations sur tous les exercices et leurs critères
            exercise_details = ""
            for exercise in self.exercises_data:
                exercise_id = exercise.get('id', '')
                code = exercise.get('code', '')
                analysis = exercise.get('analysis', '')
                execution = exercise.get('execution', '')
                config = exercise.get('config', {})
                
                # Récupérer le statut et le résultat depuis le tableau des exercices
                status = exercise.get('status', 'Non évalué')
                result = exercise.get('result', 'Pas de résultat disponible')
                
                # Ajouter les détails de cet exercice
                exercise_details += f"""
                ===== EXERCICE: {exercise_id} =====
                DESCRIPTION: {config.get('description', 'Pas de description disponible')}
                
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
                
                # Ajouter les critères de notation spécifiques à cet exercice
                grading_criteria = config.get('grading_criteria', [])
                if grading_criteria:
                    for criterion in grading_criteria:
                        points = criterion.get('points', 0)
                        title = criterion.get('title', '')
                        description = criterion.get('description', '')
                        exercise_details += f"- {title} ({points} pts): {description}\n"
                        
                        subcriteria = criterion.get('subcriteria', [])
                        for subcriterion in subcriteria:
                            exercise_details += f"  * {subcriterion.get('text', '')}\n"
                else:
                    exercise_details += "Aucun critère d'évaluation spécifié pour cet exercice.\n"
                
                exercise_details += "\n"
            
            # Préparer le prompt pour l'évaluation globale du TD
            prompt = f"""
            Tu es un assistant pédagogique spécialisé dans l'évaluation de code Java pour des étudiants.
            Analyse l'ensemble des exercices du TD pour l'étudiant {self.student_name} et fournis une évaluation complète.
            
            {exercise_details}
            
            DIRECTIVES D'ÉVALUATION:
            
            1. Évalue CHAQUE exercice selon ses critères spécifiques indiqués ci-dessus.
            2. Pour chaque critère, attribue:
               - Points complets si toutes les vérifications sont correctes et le code passe tous les tests
               - Points partiels si erreurs mineures ou code fonctionnel mais mal structuré
               - 0 point en cas d'erreurs majeures ou non-respect des consignes
            3. Sois clément mais rigoureux:
               - Accorde 80% des points si l'étudiant a fait des efforts visibles malgré des erreurs mineures
               - 50% si le code est partiellement fonctionnel
               - 0% uniquement en cas d'échec total ou de non-respect des consignes
            
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
            
            Utilise un ton encourageant et pédagogique. Si la note est basse, souligne les aspects positifs et donne des conseils constructifs pour s'améliorer.
            """
            
            # Générer le feedback en utilisant la nouvelle syntaxe
            response = client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=prompt
            )
            feedback = response.text
            
            # Émettre le signal avec le feedback
            self.feedback_ready.emit(feedback)
            
        except Exception as e:
            self.error_occurred.emit(str(e)) 