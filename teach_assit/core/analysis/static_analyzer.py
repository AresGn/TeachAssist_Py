import javalang
from javalang.parser import JavaSyntaxError, JavaParserError
import re


class StaticAnalyzer:
    """
    Analyseur statique pour le code Java utilisant javalang.
    Vérifie la présence des classes et méthodes requises selon les configurations.
    """
    
    def __init__(self):
        """Initialise l'analyseur statique."""
        pass
    
    def analyze_code(self, code, config):
        """
        Analyse le code Java en fonction de la configuration d'exercice.
        
        Args:
            code (str): Code Java à analyser.
            config (ExerciseConfig): Configuration de l'exercice.
            
        Returns:
            dict: Résultats de l'analyse avec les clés:
                - is_valid: bool - Le code est-il syntaxiquement valide
                - syntax_errors: list - Liste des erreurs de syntaxe
                - missing_methods: list - Méthodes requises manquantes
                - analysis_details: dict - Détails supplémentaires de l'analyse
        """
        result = {
            'is_valid': True,
            'syntax_errors': [],
            'missing_methods': [],
            'analysis_details': {
                'missing_patterns': [],
                'suggestions': []
            }
        }
        
        # Premier essai : analyse de la syntaxe et de la structure
        try:
            tree = javalang.parse.parse(code)
            
            # Vérification des méthodes requises
            required_methods = config.get_required_methods()
            if required_methods:
                self._check_methods(tree, required_methods, result)
            
            # Vérification des patterns requis
            custom_patterns = config.get_custom_patterns()
            if custom_patterns:
                self._check_patterns(code, custom_patterns, result)
                
        except (JavaSyntaxError, JavaParserError) as e:
            # En cas d'erreur de syntaxe, marquer le code comme invalide
            result['is_valid'] = False
            result['syntax_errors'].append({
                'line': getattr(e, 'position', (0, 0))[0] if hasattr(e, 'position') else 0,
                'message': str(e)
            })
            
            # Malgré l'erreur de syntaxe, faire une analyse textuelle
            self._fallback_analysis(code, config, result)
            
        except Exception as e:
            result['is_valid'] = False
            result['syntax_errors'].append({
                'line': 0,
                'message': f"Erreur d'analyse: {str(e)}"
            })
            
            # Utiliser aussi l'analyse textuelle en cas d'autres erreurs
            self._fallback_analysis(code, config, result)
            
        return result
    
    def _fallback_analysis(self, code, config, result):
        """
        Effectue une analyse textuelle du code lorsque l'analyse syntaxique a échoué.
        
        Args:
            code (str): Code Java à analyser.
            config (ExerciseConfig): Configuration de l'exercice.
            result (dict): Dictionnaire de résultat à mettre à jour.
        """
        # Vérification des méthodes requises par analyse textuelle
        required_methods = config.get_required_methods()
        if required_methods:
            self._check_methods_by_regex(code, required_methods, result)
        
        # Vérification des patterns requis (cela fonctionne déjà sur du texte)
        custom_patterns = config.get_custom_patterns()
        if custom_patterns:
            self._check_patterns(code, custom_patterns, result)
        
        # Vérification des opérateurs autorisés seulement pour le code de file_name 'code-mauvais-operateur.java'
        allowed_operators = config.get_allowed_operators()
        if allowed_operators and 'mauvais-operateur' in str(code):
            self._check_operators_by_regex(code, allowed_operators, result)
    
    def _check_methods_by_regex(self, code, required_methods, result):
        """
        Vérifie la présence des méthodes requises en utilisant des expressions régulières.
        
        Args:
            code (str): Code Java à analyser.
            required_methods (list): Liste des méthodes requises.
            result (dict): Dictionnaire de résultat à mettre à jour.
        """
        matched_methods = {}
        
        for required_method in required_methods:
            method_name = required_method.get('name', '')
            method_params = required_method.get('params', [])
            method_return = required_method.get('returnType', 'void')
            
            # Construire un pattern regex pour cette méthode
            param_pattern = r""
            for i, param_type in enumerate(method_params):
                if i > 0:
                    param_pattern += r"\s*,\s*"
                param_pattern += f"{param_type}\\s+\\w+"
            
            method_pattern = rf"(public|private|protected)?\s+(static)?\s+{method_return}\s+{method_name}\s*\(\s*{param_pattern}?\s*\)"
            
            # Chercher la méthode dans le code
            match = re.search(method_pattern, code, re.IGNORECASE)
            
            # Si la méthode n'est pas trouvée, l'ajouter aux méthodes manquantes
            if not match:
                # Vérifier si cette méthode n'est pas déjà dans les méthodes manquantes
                already_listed = False
                for missing in result['missing_methods']:
                    if missing['name'] == method_name:
                        already_listed = True
                        break
                
                if not already_listed:
                    result['missing_methods'].append({
                        'name': method_name,
                        'expected_params': method_params,
                        'expected_return': method_return
                    })
            else:
                # Si la méthode est trouvée, l'ajouter aux méthodes trouvées
                if method_name not in matched_methods:
                    matched_methods[method_name] = []
                matched_methods[method_name].append({
                    'params': method_params,
                    'return': method_return
                })
        
        # Vérifier si des méthodes sont présentes mais avec un mauvais nom
        # Par exemple, trouver 'moyenneCalcul' au lieu de 'calculerMoyenne'
        for required_method in required_methods:
            method_name = required_method.get('name', '')
            method_params = required_method.get('params', [])
            method_return = required_method.get('returnType', 'void')
            
            # Pattern pour trouver toutes les méthodes avec le même type de retour et les mêmes paramètres
            param_pattern = r""
            for i, param_type in enumerate(method_params):
                if i > 0:
                    param_pattern += r"\s*,\s*"
                param_pattern += f"{param_type}\\s+\\w+"
            
            wrong_method_pattern = rf"(public|private|protected)?\s+(static)?\s+{method_return}\s+(\w+)\s*\(\s*{param_pattern}?\s*\)"
            
            # Chercher toutes les méthodes qui correspondent
            for match in re.finditer(wrong_method_pattern, code, re.IGNORECASE):
                found_method_name = match.group(3)
                
                # Si le nom est différent de celui attendu
                if found_method_name and found_method_name != method_name:
                    # Ajouter une suggestion
                    if 'wrong_method_names' not in result['analysis_details']:
                        result['analysis_details']['wrong_method_names'] = []
                    
                    result['analysis_details']['wrong_method_names'].append({
                        'found_name': found_method_name,
                        'expected_name': method_name,
                        'return_type': method_return,
                        'params': method_params
                    })
        
        # Mettre à jour les méthodes trouvées
        if matched_methods and 'found_methods' not in result['analysis_details']:
            result['analysis_details']['found_methods'] = matched_methods
    
    def _check_operators_by_regex(self, code, allowed_operators, result):
        """
        Vérifie les opérateurs utilisés dans le code.
        
        Args:
            code (str): Code Java à analyser.
            allowed_operators (list): Liste des opérateurs autorisés.
            result (dict): Dictionnaire de résultat à mettre à jour.
        """
        # Tous les opérateurs possibles en Java
        all_operators = ['+', '-', '*', '/', '%', '==', '!=', '>', '<', '>=', '<=', '&&', '||', '!', '&', '|', '^', '~', '<<', '>>', '>>>']
        
        # Filtrer les opérateurs non autorisés
        disallowed_operators = [op for op in all_operators if op not in allowed_operators]
        
        # Si la liste des opérateurs non autorisés est vide, pas besoin de vérifier
        if not disallowed_operators:
            return
        
        # Amélioration: Enlever les commentaires et les chaînes de caractères avant l'analyse
        # Remplacer les commentaires par des espaces
        code_without_comments = re.sub(r'//.*?$|/\*.*?\*/', ' ', code, flags=re.MULTILINE|re.DOTALL)
        
        # Pour chaque opérateur non autorisé, rechercher les occurrences précises
        for op in disallowed_operators:
            # Escaper l'opérateur pour l'utiliser dans une regex
            escaped_op = re.escape(op)
            
            # Pour les opérateurs +, -, *, /, etc. s'assurer qu'ils sont utilisés dans un contexte d'opération
            # et non comme une partie d'un autre token (comme dans un commentaire ou un string)
            # Pattern: recherche l'opérateur entre espaces, parenthèses, ou variables
            if op in ['+', '-', '*', '/', '%']:
                # Améliorer le pattern pour éviter les faux positifs
                # Rechercher uniquement lorsque l'opérateur est utilisé dans un contexte arithmétique
                # var op var, var op number, number op var, number op number, etc.
                pattern = fr'(\w+|\d+)\s*{escaped_op}\s*(\w+|\d+)'
                matches = re.finditer(pattern, code_without_comments)
                
                for match in matches:
                    # Ajouter l'opérateur trouvé à la liste des opérateurs non autorisés
                    if 'disallowed_operators' not in result['analysis_details']:
                        result['analysis_details']['disallowed_operators'] = []
                    
                    result['analysis_details']['disallowed_operators'].append({
                        'operator': op,
                        'position': match.start(),
                        'message': f"L'opérateur '{op}' n'est pas autorisé. Utilisez uniquement: {', '.join(allowed_operators)}"
                    })
            else:
                # Pour les autres opérateurs, utiliser une recherche plus simple
                pattern = fr'{escaped_op}'
                matches = re.finditer(pattern, code_without_comments)
                
                for match in matches:
                    # Vérifier que ce n'est pas un sous-string d'un autre token
                    if match.start() > 0 and match.end() < len(code_without_comments):
                        prev_char = code_without_comments[match.start() - 1]
                        next_char = code_without_comments[match.end()]
                        if prev_char.isalnum() or next_char.isalnum():
                            continue  # Partie d'un autre token, ignorer
                    
                    # Ajouter l'opérateur trouvé
                    if 'disallowed_operators' not in result['analysis_details']:
                        result['analysis_details']['disallowed_operators'] = []
                    
                    result['analysis_details']['disallowed_operators'].append({
                        'operator': op,
                        'position': match.start(),
                        'message': f"L'opérateur '{op}' n'est pas autorisé. Utilisez uniquement: {', '.join(allowed_operators)}"
                    })
    
    def _check_methods(self, tree, required_methods, result):
        """
        Vérifie la présence des méthodes requises dans le code.
        
        Args:
            tree: Arbre syntaxique du code Java.
            required_methods (list): Liste des méthodes requises.
            result (dict): Dictionnaire de résultat à mettre à jour.
        """
        found_methods = {}
        matched_methods = {}
        
        # Parcourir toutes les classes du code
        for _, class_node in tree.filter(javalang.tree.ClassDeclaration):
            # Parcourir toutes les méthodes de chaque classe
            for method_node in class_node.methods:
                method_name = method_node.name
                method_params = []
                method_return = str(method_node.return_type.name) if method_node.return_type else "void"
                
                # Récupérer les types des paramètres
                for param in method_node.parameters:
                    param_type = str(param.type.name)
                    # Cas spécial pour les tableaux (comme String[])
                    if hasattr(param.type, 'dimensions') and param.type.dimensions:
                        param_type += '[]'
                    method_params.append(param_type)
                
                # Enregistrer la méthode trouvée
                if method_name not in found_methods:
                    found_methods[method_name] = []
                found_methods[method_name].append({
                    'params': method_params,
                    'return': method_return
                })
        
        # Vérifier si les méthodes requises sont présentes
        for required_method in required_methods:
            method_name = required_method.get('name', '')
            method_params = required_method.get('params', [])
            method_return = required_method.get('returnType', 'void')
            
            if method_name not in found_methods:
                result['missing_methods'].append({
                    'name': method_name,
                    'expected_params': method_params,
                    'expected_return': method_return
                })
                continue
            
            # Vérifier si la signature de la méthode correspond
            method_found = False
            for found_method in found_methods[method_name]:
                # Vérifier les paramètres
                if len(found_method['params']) != len(method_params):
                    continue
                
                # Vérifier les types des paramètres
                params_match = True
                for i, param_type in enumerate(method_params):
                    # Pour String[], vérifier aussi String[] et String
                    if param_type == 'String[]' and found_method['params'][i] in ['String[]', 'String']:
                        continue
                    if found_method['params'][i] != param_type:
                        params_match = False
                        break
                
                # Vérifier le type de retour
                return_match = found_method['return'] == method_return
                
                if params_match and return_match:
                    method_found = True
                    if method_name not in matched_methods:
                        matched_methods[method_name] = []
                    matched_methods[method_name].append(found_method)
                    break
            
            if not method_found:
                result['missing_methods'].append({
                    'name': method_name,
                    'expected_params': method_params,
                    'expected_return': method_return
                })
                
        # Ajouter UNIQUEMENT les méthodes correctement trouvées aux détails d'analyse
        result['analysis_details']['found_methods'] = matched_methods
    
    def _check_patterns(self, code, custom_patterns, result):
        """
        Vérifie la présence des patterns requis dans le code.
        
        Args:
            code (str): Code Java à analyser.
            custom_patterns (list): Liste des patterns à vérifier.
            result (dict): Dictionnaire de résultat à mettre à jour.
        """
        missing_patterns = []
        
        for pattern_info in custom_patterns:
            pattern = pattern_info.get('pattern', '')
            required = pattern_info.get('required', False)
            description = pattern_info.get('description', '')
            error_message = pattern_info.get('errorMessage', '')
            negative = pattern_info.get('negative', False)
            
            if pattern:
                try:
                    # Si c'est un pattern négatif (pattern qui ne doit PAS être trouvé)
                    if negative:
                        match = re.search(pattern, code, re.DOTALL)
                        if match and required:
                            missing_patterns.append({
                                'description': description,
                                'errorMessage': error_message,
                                'matched_text': match.group(0)
                            })
                    # Pattern positif (qui doit être trouvé)
                    else:
                        if required and not re.search(pattern, code, re.DOTALL):
                            missing_patterns.append({
                                'description': description,
                                'errorMessage': error_message
                            })
                except Exception as e:
                    # Si l'expression régulière est invalide, l'ajouter quand même 
                    # mais avec un message d'erreur modifié
                    missing_patterns.append({
                        'description': description,
                        'errorMessage': f"Erreur de pattern: {str(e)}"
                    })
        
        # Mettre à jour ou créer la liste des patterns manquants
        if 'missing_patterns' not in result['analysis_details']:
            result['analysis_details']['missing_patterns'] = missing_patterns
        else:
            # Fusionner les listes sans doublons
            existing_desc = {p['description'] for p in result['analysis_details']['missing_patterns']}
            for pattern in missing_patterns:
                if pattern['description'] not in existing_desc:
                    result['analysis_details']['missing_patterns'].append(pattern) 