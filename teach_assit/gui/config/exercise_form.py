"""
Redirection vers le nouveau module exercise_form.
Ce fichier est maintenu pour compatibilité mais utilise la nouvelle implémentation modulaire.

NE PAS MODIFIER DIRECTEMENT CE FICHIER - il est maintenant décomposé en plusieurs modules
dans le package teach_assit.gui.exercise_form.
"""

from teach_assit.gui.exercise_form import ExerciseConfigForm

# Réexportation pour compatibilité
__all__ = ['ExerciseConfigForm'] 