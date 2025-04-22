"""
Utilitaires divers pour le module de feedback.
"""

import re
import os
import glob

def extract_note_from_feedback(feedback):
    """
    Extrait la note globale d'un feedback formaté en markdown.
    
    Args:
        feedback (str): Le feedback complet au format markdown
        
    Returns:
        str: La note au format "X/Y" ou "--/20" si non trouvée
    """
    # Chercher d'abord le format standard "Note Globale pour le TD : XX/20"
    note_globale_match = re.search(r'Note\s+Globale\s+pour\s+le\s+TD\s*:\s*(\d+(\.\d+)?)/(\d+)', feedback, re.IGNORECASE)
    if note_globale_match:
        note_value = note_globale_match.group(1)
        note_total = note_globale_match.group(3)
        return f"{note_value}/{note_total}"
    
    # Essayer un format alternatif si le premier n'a pas fonctionné
    note_match = re.search(r'(\d+(\.\d+)?)/(\d+)', feedback)
    if note_match:
        return note_match.group(0)
    
    # Aucune note trouvée
    return "--/20"

def extract_exercise_notes(feedback, exercise_ids):
    """
    Extrait les notes individuelles pour chaque exercice.
    
    Args:
        feedback (str): Le feedback complet au format markdown
        exercise_ids (list): Liste des identifiants d'exercices
        
    Returns:
        dict: Dictionnaire avec les ID d'exercices comme clés et les notes comme valeurs
    """
    exercise_notes = {}
    
    # Chercher les patterns comme "Note : 8/10" ou "Note: 7.1/10"
    for exercise_id in exercise_ids:
        # Construction d'un pattern qui cherche le nom de l'exercice suivi d'une note
        # ou simplement une note associée à un exercice spécifique
        pattern = rf"{re.escape(exercise_id)}.*?Note\s*:\s*(\d+(\.\d+)?)/(\d+)|Note\s*pour\s*{re.escape(exercise_id)}\s*:\s*(\d+(\.\d+)?)/(\d+)"
        match = re.search(pattern, feedback, re.IGNORECASE | re.DOTALL)
        
        if match:
            # Extraire la note trouvée (elle peut être dans le groupe 1 ou 4 selon le pattern qui a matché)
            note_value = match.group(1) if match.group(1) else match.group(4)
            note_total = match.group(3) if match.group(3) else match.group(6)
            exercise_notes[exercise_id] = f"{note_value}/{note_total}"
    
    return exercise_notes

def test_api_connection(api_key):
    """
    Teste la connexion à l'API Gemini.
    
    Args:
        api_key (str): Clé API Gemini à tester
        
    Returns:
        tuple: (success, message) indiquant si la connexion est réussie et un message
    """
    if not api_key:
        return False, "Veuillez entrer une clé API"
    
    try:
        from google import genai
        
        # Configurer l'API avec le nouvel API Client
        client = genai.Client(api_key=api_key)
        
        # Vérifier si l'API fonctionne avec une requête simple
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents="Réponds simplement par 'OK' pour tester la connexion."
        )
        
        if response.text:
            return True, "Connexion à l'API Gemini réussie!"
        else:
            return False, "Échec de connexion: pas de réponse"
            
    except Exception as e:
        return False, f"Échec de connexion: {str(e)}"

def save_feedback_to_file(feedback, student_name, filename=None):
    """
    Sauvegarde le feedback dans un fichier.
    
    Args:
        feedback (str): Le contenu du feedback à sauvegarder
        student_name (str): Nom de l'étudiant (pour générer un nom de fichier par défaut)
        filename (str, optional): Chemin du fichier où sauvegarder
        
    Returns:
        tuple: (success, message) indiquant si l'opération est réussie et un message
    """
    if not filename:
        # Si aucun nom de fichier n'est fourni, générer un par défaut
        filename = f"{student_name}_feedback.md"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(feedback)
        return True, f"Feedback enregistré dans {filename}"
    except Exception as e:
        return False, f"Erreur lors de l'enregistrement: {str(e)}" 