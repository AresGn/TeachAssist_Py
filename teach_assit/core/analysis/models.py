class ExerciseConfig:
    """Représente la configuration d'un exercice."""
    
    def __init__(self, config_dict):
        """
        Initialise une configuration d'exercice à partir d'un dictionnaire.
        
        Args:
            config_dict (dict): Dictionnaire de configuration de l'exercice.
        """
        self.id = config_dict.get('id', '')
        self.name = config_dict.get('name', '')
        self.description = config_dict.get('description', '')
        self.difficulty = config_dict.get('difficulty', 1)
        self.max_points = config_dict.get('maxPoints', 10)
        
        # Règles de vérification
        self.rules = config_dict.get('rules', {})
    
    def to_dict(self):
        """
        Convertit l'objet en dictionnaire.
        
        Returns:
            dict: Dictionnaire représentant la configuration.
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'rules': self.rules
        }
    
    def get_required_methods(self):
        """Retourne la liste des méthodes requises."""
        return self.rules.get('requiredMethods', [])
    
    def get_allowed_operators(self):
        """Retourne la liste des opérateurs autorisés."""
        return self.rules.get('allowedOperators', [])
    
    def get_required_control_structures(self):
        """Retourne la liste des structures de contrôle requises."""
        return self.rules.get('requiredControlStructures', [])
    
    def get_custom_patterns(self):
        """Retourne la liste des patterns personnalisés."""
        return self.rules.get('customPatterns', [])
    
    def should_check_variable_scope(self):
        """Indique si la portée des variables doit être vérifiée."""
        return self.rules.get('checkVariableScope', False)
    
    def get_naming_conventions(self):
        """Retourne la liste des conventions de nommage à respecter."""
        return self.rules.get('checkNamingConventions', [])
    
    def get_math_functions(self):
        """Retourne la liste des fonctions mathématiques attendues."""
        return self.rules.get('mathFunctions', [])
    
    def get_required_domain_checks(self):
        """Retourne la liste des vérifications de domaine requises."""
        return self.rules.get('requiredDomainChecks', [])
    
    def get_domain_checks(self):
        """Alias pour get_required_domain_checks pour compatibilité avec l'interface."""
        return self.rules.get('requiredDomainChecks', [])
    
    def get_exception_handling(self):
        """Retourne les paramètres de gestion des exceptions."""
        return self.rules.get('exceptionHandling', {})
    
    def should_use_try_catch(self):
        """Indique si le bloc try/catch est requis."""
        exception_handling = self.get_exception_handling()
        return exception_handling.get('requiredTryCatch', False)
    
    def get_specific_exceptions(self):
        """Retourne la liste des exceptions spécifiques à utiliser."""
        exception_handling = self.get_exception_handling()
        return exception_handling.get('specificExceptions', [])
    
    def set_math_functions(self, math_functions):
        """
        Définit la liste des fonctions mathématiques attendues.
        
        Args:
            math_functions (list): Liste des fonctions mathématiques.
        """
        if 'mathFunctions' not in self.rules:
            self.rules['mathFunctions'] = []
        self.rules['mathFunctions'] = math_functions
    
    def set_required_domain_checks(self, domain_checks):
        """
        Définit la liste des vérifications de domaine requises.
        
        Args:
            domain_checks (list): Liste des vérifications de domaine.
        """
        if 'requiredDomainChecks' not in self.rules:
            self.rules['requiredDomainChecks'] = []
        self.rules['requiredDomainChecks'] = domain_checks
    
    def set_domain_checks(self, domain_checks):
        """Alias pour set_required_domain_checks pour compatibilité avec l'interface."""
        self.set_required_domain_checks(domain_checks)
    
    def set_exception_handling(self, exception_handling):
        """
        Définit les paramètres de gestion des exceptions.
        
        Args:
            exception_handling (dict): Paramètres de gestion des exceptions.
        """
        self.rules['exceptionHandling'] = exception_handling


class AssessmentConfig:
    """Représente la configuration d'une évaluation."""
    
    def __init__(self, config_dict=None):
        """
        Initialise une configuration d'évaluation à partir d'un dictionnaire.
        
        Args:
            config_dict (dict): Dictionnaire contenant la configuration de l'évaluation.
        """
        if config_dict is None:
            config_dict = {}
            
        self.id = config_dict.get('assessmentId', '')
        self.name = config_dict.get('name', '')
        self.exercises = config_dict.get('exercises', [])
        self.total_max_points = config_dict.get('totalMaxPoints', 0)
    
    def to_dict(self):
        """
        Convertit l'objet en dictionnaire.
        
        Returns:
            dict: Dictionnaire représentant la configuration.
        """
        return {
            'assessmentId': self.id,
            'name': self.name,
            'exercises': self.exercises,
            'totalMaxPoints': self.total_max_points
        }
    
    def get_exercise_ids(self):
        """
        Retourne la liste des identifiants d'exercices.
        
        Returns:
            list: Liste d'identifiants d'exercices.
        """
        return [ex['exerciseId'] for ex in self.exercises]
    
    def get_exercise_max_points(self, exercise_id):
        """
        Retourne le nombre maximal de points pour un exercice.
        
        Args:
            exercise_id (str): Identifiant de l'exercice.
            
        Returns:
            int: Nombre maximal de points, 0 si l'exercice n'est pas trouvé.
        """
        for exercise in self.exercises:
            if exercise['exerciseId'] == exercise_id:
                return exercise.get('maxPoints', 0)
        return 0
    
    def add_exercise(self, exercise_id, max_points):
        """
        Ajoute un exercice à l'évaluation.
        
        Args:
            exercise_id (str): Identifiant de l'exercice.
            max_points (int): Nombre maximal de points.
        """
        self.exercises.append({
            'exerciseId': exercise_id,
            'maxPoints': max_points
        })
    
    def remove_exercise(self, exercise_id):
        """
        Supprime un exercice de l'évaluation.
        
        Args:
            exercise_id (str): Identifiant de l'exercice à supprimer.
            
        Returns:
            bool: True si l'exercice a été supprimé, False sinon.
        """
        for i, exercise in enumerate(self.exercises):
            if exercise['exerciseId'] == exercise_id:
                self.exercises.pop(i)
                return True
        return False
    
    def update_max_points(self):
        """Met à jour le nombre total de points maximum."""
        self.total_max_points = sum(ex.get('maxPoints', 0) for ex in self.exercises)
    
    def update_exercise_points(self, exercise_id, new_max_points):
        """
        Modifie le nombre maximum de points pour un exercice existant.
        
        Args:
            exercise_id (str): Identifiant de l'exercice à modifier.
            new_max_points (int): Nouveau nombre maximal de points.
            
        Returns:
            bool: True sii l'exercice a été modifié, False si l'exercice n'a pas été trouvé.
        """
        for exercise in self.exercises:
            if exercise['exerciseId'] == exercise_id:
                exercise['maxPoints'] = new_max_points
                self.update_max_points()  # Mettre à jour le total des points
                return True
        return False 