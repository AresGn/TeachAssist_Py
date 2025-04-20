"""
Fonctions pour la génération et le formatage des rapports détaillés.
"""

from teach_assit.gui.results_widget.utils import fix_encoding, SYMBOL_OK, SYMBOL_FAIL, SYMBOL_WARNING

def format_detailed_report(result, exercise_config):
    """Formater un rapport détaillé pour l'affichage.
    
    Args:
        result: Dictionnaire contenant les résultats d'analyse
        exercise_config: Configuration de l'exercice
        
    Returns:
        str: Rapport formaté sous forme de texte
    """
    details = ""
    
    # Vérification de la syntaxe
    syntax_ok = not result.get('syntax_errors', []) and 'error' not in result
    syntax_symbol = SYMBOL_OK if syntax_ok else SYMBOL_FAIL
    details += f"{syntax_symbol} SYNTAXE: " + ("Code valide" if syntax_ok else "Code invalide") + "\n"
    
    if 'error' in result:
        error_msg = fix_encoding(result['error'])
        details += f"  {SYMBOL_FAIL} Erreur d'analyse: {error_msg}\n"
    elif result.get('syntax_errors', []):
        for error in result['syntax_errors']:
            error_msg = fix_encoding(error.get('message', 'Erreur inconnue'))
            details += f"  {SYMBOL_FAIL} Ligne {error.get('line', 'inconnue')}: {error_msg}\n"
    
    # Vérification des méthodes
    methods_ok = not result.get('missing_methods', [])
    methods_symbol = SYMBOL_OK if methods_ok else SYMBOL_WARNING
    details += f"\n{methods_symbol} MÉTHODES REQUISES: "
    
    if methods_ok:
        details += "Toutes les méthodes requises sont présentes\n"
    else:
        details += "Méthodes manquantes ou incorrectes\n"
        for m in result.get('missing_methods', []):
            method_name = m.get('name', '')
            method_params = m.get('expected_params', [])
            method_return = m.get('expected_return', 'void')
            details += f"  {SYMBOL_FAIL} {method_return} {method_name}({', '.join(method_params)})\n"
    
    # Méthodes trouvées
    if 'analysis_details' in result and 'found_methods' in result['analysis_details'] and result['analysis_details']['found_methods']:
        details += f"\n{SYMBOL_OK} MÉTHODES TROUVÉES:\n"
        for method_name, method_list in result['analysis_details']['found_methods'].items():
            for method in method_list:
                params = method.get('params', [])
                return_type = method.get('return', 'void')
                details += f"  {SYMBOL_OK} {return_type} {method_name}({', '.join(params)})\n"
    
    # Structures de contrôle
    if 'analysis_details' in result and 'control_structures' in result['analysis_details']:
        control_structures = result['analysis_details']['control_structures']
        found_structures = control_structures.get('found', [])
        missing_structures = control_structures.get('missing', [])
        
        control_symbol = SYMBOL_OK if not missing_structures else SYMBOL_FAIL
        details += f"\n{control_symbol} STRUCTURES DE CONTRÔLE:\n"
        
        if found_structures:
            details += f"  {SYMBOL_OK} Structures trouvées: {', '.join(found_structures)}\n"
        
        if missing_structures:
            details += f"  {SYMBOL_FAIL} Structures manquantes: {', '.join(missing_structures)}\n"
    
    # Conventions de nommage
    if 'analysis_details' in result and 'naming_conventions' in result['analysis_details']:
        naming_errors = result['analysis_details']['naming_conventions'].get('errors', [])
        naming_symbol = SYMBOL_OK if not naming_errors else SYMBOL_FAIL
        
        details += f"\n{naming_symbol} CONVENTIONS DE NOMMAGE:\n"
        
        if naming_errors:
            for error in naming_errors:
                message = fix_encoding(error.get('message', ''))
                details += f"  {SYMBOL_FAIL} {message}\n"
        else:
            details += f"  {SYMBOL_OK} Toutes les conventions de nommage sont respectées.\n"
    
    # Portée des variables
    if 'analysis_details' in result and 'variable_scopes' in result['analysis_details']:
        scope_errors = result['analysis_details']['variable_scopes'].get('errors', [])
        scope_symbol = SYMBOL_OK if not scope_errors else SYMBOL_FAIL
        
        details += f"\n{scope_symbol} PORTÉE DES VARIABLES:\n"
        
        if scope_errors:
            for error in scope_errors:
                message = fix_encoding(error.get('message', ''))
                details += f"  {SYMBOL_FAIL} {message}\n"
        else:
            details += f"  {SYMBOL_OK} Aucun problème de portée de variables détecté.\n"
    
    # Opérateurs non autorisés
    if 'analysis_details' in result and 'disallowed_operators' in result['analysis_details']:
        disallowed_operators = result['analysis_details']['disallowed_operators']
        operators_symbol = SYMBOL_OK if not disallowed_operators else SYMBOL_FAIL
        
        if disallowed_operators:
            details += f"\n{operators_symbol} OPÉRATEURS NON AUTORISÉS:\n"
            for op_info in disallowed_operators:
                message = fix_encoding(op_info.get('message', ''))
                details += f"  {SYMBOL_FAIL} {message}\n"
        else:
            details += f"\n{operators_symbol} OPÉRATEURS: Tous les opérateurs utilisés sont autorisés.\n"
    
    # Patterns requis
    if 'analysis_details' in result and 'missing_patterns' in result['analysis_details']:
        missing_patterns = result['analysis_details']['missing_patterns']
        patterns_ok = not missing_patterns
        patterns_symbol = SYMBOL_OK if patterns_ok else SYMBOL_WARNING
        
        details += f"\n{patterns_symbol} PATTERNS REQUIS:\n"
        
        # Si nous avons un exercise_config, vérifier tous les patterns
        if exercise_config:
            custom_patterns = exercise_config.get_custom_patterns()
            for pattern_info in custom_patterns:
                pattern_desc = fix_encoding(pattern_info.get('description', 'Pattern sans description'))
                required = pattern_info.get('required', False)
                
                if not required:
                    continue
                
                # Vérifier si le pattern est manquant
                is_missing = False
                error_msg = ""
                for missing_pattern in missing_patterns:
                    missing_desc = fix_encoding(missing_pattern.get('description', ''))
                    if missing_desc == pattern_desc:
                        is_missing = True
                        error_msg = fix_encoding(missing_pattern.get('errorMessage', ''))
                        break
                
                pattern_status = SYMBOL_FAIL if is_missing else SYMBOL_OK
                details += f"  {pattern_status} {pattern_desc}\n"
                
                if is_missing and error_msg:
                    details += f"      {SYMBOL_WARNING} {error_msg}\n"
        else:
            # Sans config, juste lister les patterns manquants
            if patterns_ok:
                details += f"  {SYMBOL_OK} Tous les patterns requis sont présents\n"
            else:
                for pattern in missing_patterns:
                    pattern_desc = fix_encoding(pattern.get('description', ''))
                    error_msg = fix_encoding(pattern.get('errorMessage', ''))
                    details += f"  {SYMBOL_FAIL} {pattern_desc}\n"
                    if error_msg:
                        details += f"      {SYMBOL_WARNING} {error_msg}\n"
    
    # Suggestions
    if 'analysis_details' in result and 'suggestions' in result['analysis_details'] and result['analysis_details']['suggestions']:
        details += f"\n{SYMBOL_WARNING} SUGGESTIONS D'AMÉLIORATION:\n"
        for suggestion in result['analysis_details']['suggestions']:
            details += f"  {SYMBOL_WARNING} {fix_encoding(suggestion)}\n"
    
    # Calcul du résumé
    if exercise_config and 'analysis_details' in result:
        # Vérifier le statut de chaque critère
        syntax_ok = not result.get('syntax_errors', []) and 'error' not in result
        methods_ok = not result.get('missing_methods', [])
        patterns_ok = not (result.get('analysis_details', {}).get('missing_patterns', []))
        
        # Opérateurs
        operators_ok = True
        if 'disallowed_operators' in result['analysis_details']:
            operators_ok = not result['analysis_details']['disallowed_operators']
        
        # Structures de contrôle
        control_structures_ok = True
        if 'control_structures' in result['analysis_details']:
            control_structures_ok = not result['analysis_details']['control_structures'].get('missing', [])
        
        # Conventions de nommage
        naming_ok = True
        if 'naming_conventions' in result['analysis_details']:
            naming_ok = not result['analysis_details']['naming_conventions'].get('errors', [])
        
        # Portée des variables
        scope_ok = True
        if 'variable_scopes' in result['analysis_details']:
            scope_ok = not result['analysis_details']['variable_scopes'].get('errors', [])
        
        # Compter le nombre de vérifications réussies
        total_checks = 7  # syntaxe, méthodes, patterns, opérateurs, structures, nommage, portée
        passed_checks = sum([syntax_ok, methods_ok, patterns_ok, operators_ok, control_structures_ok, naming_ok, scope_ok])
        
        # Note estimée (10 par défaut si non spécifié)
        max_points = exercise_config.max_points if hasattr(exercise_config, 'max_points') else 10
        estimated_score = round((passed_checks / total_checks) * max_points, 1)
        
        # Ajouter le résumé
        details += f"\n{'='*30}\nRÉSUMÉ GLOBAL: {passed_checks}/{total_checks} vérifications réussies\n"
        details += f"NOTE ESTIMÉE: {estimated_score}/{max_points} points\n"
        
        # Résultat global
        all_ok = syntax_ok and methods_ok and patterns_ok and operators_ok and control_structures_ok and naming_ok and scope_ok
        if all_ok:
            details += f"\n{SYMBOL_OK} RÉSULTAT GLOBAL: SUCCÈS"
        else:
            details += f"\n{SYMBOL_FAIL} RÉSULTAT GLOBAL: DES PROBLÈMES ONT ÉTÉ DÉTECTÉS\n  Détail des problèmes:"
            
            if not syntax_ok:
                details += f"\n    {SYMBOL_FAIL} Problèmes de syntaxe"
            if not methods_ok:
                details += f"\n    {SYMBOL_FAIL} Méthodes manquantes ou incorrectes"
            if not patterns_ok:
                details += f"\n    {SYMBOL_FAIL} Patterns requis manquants"
            if not operators_ok:
                details += f"\n    {SYMBOL_FAIL} Utilisation d'opérateurs non autorisés"
            if not control_structures_ok:
                details += f"\n    {SYMBOL_FAIL} Structures de contrôle manquantes"
            if not naming_ok:
                details += f"\n    {SYMBOL_FAIL} Conventions de nommage non respectées"
            if not scope_ok:
                details += f"\n    {SYMBOL_FAIL} Problèmes de portée des variables"
    
    return details 