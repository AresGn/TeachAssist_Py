from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QLabel, QLineEdit, QTextEdit, QPushButton, QListWidget, 
                             QListWidgetItem, QMessageBox, QComboBox, QCheckBox, 
                             QGroupBox, QInputDialog, QDialog)
from PyQt5.QtCore import Qt
import os
import json

from teach_assit.core.analysis.config_loader import ConfigLoader


class ExerciseConfigForm(QWidget):
    """Formulaire pour éditer une configuration d'exercice."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_config = None
        self.config_loader = ConfigLoader(os.getcwd())
        self.init_ui()
    
    def init_ui(self):
        """Initialiser l'interface utilisateur."""
        layout = QVBoxLayout()
        
        # Informations de base
        basic_group = QGroupBox("Informations de base")
        basic_layout = QFormLayout()
        
        self.id_edit = QLineEdit()
        self.id_edit.setReadOnly(True)  # L'ID ne peut pas être modifié
        basic_layout.addRow("Identifiant :", self.id_edit)
        
        self.name_edit = QLineEdit()
        basic_layout.addRow("Nom :", self.name_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMinimumHeight(100)
        basic_layout.addRow("Description :", self.description_edit)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # Règles
        rules_group = QGroupBox("Règles")
        rules_layout = QVBoxLayout()
        
        # Méthodes requises
        methods_group = QGroupBox("Méthodes requises")
        methods_layout = QVBoxLayout()
        
        self.methods_list = QListWidget()
        methods_layout.addWidget(self.methods_list)
        
        methods_buttons = QHBoxLayout()
        self.add_method_button = QPushButton("Ajouter")
        self.add_method_button.clicked.connect(self.on_add_method)
        methods_buttons.addWidget(self.add_method_button)
        
        self.delete_method_button = QPushButton("Supprimer")
        self.delete_method_button.clicked.connect(self.on_delete_method)
        methods_buttons.addWidget(self.delete_method_button)
        
        methods_layout.addLayout(methods_buttons)
        methods_group.setLayout(methods_layout)
        rules_layout.addWidget(methods_group)
        
        # Opérateurs autorisés
        operators_group = QGroupBox("Opérateurs autorisés")
        operators_layout = QFormLayout()
        
        self.operators_edit = QLineEdit()
        self.operators_edit.setPlaceholderText("Ex: +, -, *, /, ==, <=, >=")
        operators_layout.addRow("Liste (séparés par des virgules) :", self.operators_edit)
        
        operators_group.setLayout(operators_layout)
        rules_layout.addWidget(operators_group)
        
        # Structures de contrôle requises
        control_group = QGroupBox("Structures de contrôle requises")
        control_layout = QFormLayout()
        
        self.control_edit = QLineEdit()
        self.control_edit.setPlaceholderText("Ex: if, for, while, switch")
        control_layout.addRow("Liste (séparées par des virgules) :", self.control_edit)
        
        control_group.setLayout(control_layout)
        rules_layout.addWidget(control_group)
        
        # Options diverses
        options_group = QGroupBox("Options diverses")
        options_layout = QFormLayout()
        
        self.check_scope = QCheckBox("Vérifier la portée des variables")
        options_layout.addRow("", self.check_scope)
        
        self.naming_edit = QLineEdit()
        self.naming_edit.setPlaceholderText("Ex: camelCase, PascalCase")
        options_layout.addRow("Conventions de nommage :", self.naming_edit)
        
        options_group.setLayout(options_layout)
        rules_layout.addWidget(options_group)
        
        # Motifs personnalisés
        patterns_group = QGroupBox("Motifs personnalisés")
        patterns_layout = QVBoxLayout()
        
        self.patterns_list = QListWidget()
        patterns_layout.addWidget(self.patterns_list)
        
        patterns_buttons = QHBoxLayout()
        self.add_pattern_button = QPushButton("Ajouter")
        self.add_pattern_button.clicked.connect(self.on_add_pattern)
        patterns_buttons.addWidget(self.add_pattern_button)
        
        self.delete_pattern_button = QPushButton("Supprimer")
        self.delete_pattern_button.clicked.connect(self.on_delete_pattern)
        patterns_buttons.addWidget(self.delete_pattern_button)
        
        patterns_layout.addLayout(patterns_buttons)
        patterns_group.setLayout(patterns_layout)
        rules_layout.addWidget(patterns_group)
        
        # Vérifications de domaine
        domain_checks_group = QGroupBox("Vérifications de domaine")
        domain_checks_layout = QVBoxLayout()
        
        self.domain_checks_list = QListWidget()
        domain_checks_layout.addWidget(self.domain_checks_list)
        
        domain_checks_buttons = QHBoxLayout()
        self.add_domain_check_button = QPushButton("Ajouter")
        self.add_domain_check_button.clicked.connect(self.on_add_domain_check)
        domain_checks_buttons.addWidget(self.add_domain_check_button)
        
        self.delete_domain_check_button = QPushButton("Supprimer")
        self.delete_domain_check_button.clicked.connect(self.on_delete_domain_check)
        domain_checks_buttons.addWidget(self.delete_domain_check_button)
        
        domain_checks_layout.addLayout(domain_checks_buttons)
        domain_checks_group.setLayout(domain_checks_layout)
        rules_layout.addWidget(domain_checks_group)
        
        # Fonctions mathématiques
        math_functions_group = QGroupBox("Fonctions mathématiques")
        math_functions_layout = QVBoxLayout()
        
        self.math_functions_list = QListWidget()
        math_functions_layout.addWidget(self.math_functions_list)
        
        math_functions_buttons = QHBoxLayout()
        self.add_math_function_button = QPushButton("Ajouter")
        self.add_math_function_button.clicked.connect(self.on_add_math_function)
        math_functions_buttons.addWidget(self.add_math_function_button)
        
        self.delete_math_function_button = QPushButton("Supprimer")
        self.delete_math_function_button.clicked.connect(self.on_delete_math_function)
        math_functions_buttons.addWidget(self.delete_math_function_button)
        
        math_functions_layout.addLayout(math_functions_buttons)
        math_functions_group.setLayout(math_functions_layout)
        rules_layout.addWidget(math_functions_group)
        
        # Gestion des exceptions
        exceptions_group = QGroupBox("Gestion des exceptions")
        exceptions_layout = QFormLayout()
        
        self.try_catch_checkbox = QCheckBox("Bloc try/catch requis")
        exceptions_layout.addRow("", self.try_catch_checkbox)
        
        self.specific_exceptions_edit = QLineEdit()
        self.specific_exceptions_edit.setPlaceholderText("Ex: IllegalArgumentException, ArithmeticException")
        exceptions_layout.addRow("Exceptions spécifiques :", self.specific_exceptions_edit)
        
        exceptions_group.setLayout(exceptions_layout)
        rules_layout.addWidget(exceptions_group)
        
        rules_group.setLayout(rules_layout)
        layout.addWidget(rules_group)
        
        # Bouton de sauvegarde
        self.save_button = QPushButton("Enregistrer")
        self.save_button.clicked.connect(self.save_config)
        layout.addWidget(self.save_button)
        
        self.setLayout(layout)
        self.clear()
    
    def clear(self):
        """Effacer le formulaire."""
        self.current_config = None
        
        self.id_edit.clear()
        self.name_edit.clear()
        self.description_edit.clear()
        self.methods_list.clear()
        self.operators_edit.clear()
        self.control_edit.clear()
        self.check_scope.setChecked(False)
        self.naming_edit.clear()
        self.patterns_list.clear()
        self.domain_checks_list.clear()
        self.math_functions_list.clear()
        self.try_catch_checkbox.setChecked(False)
        self.specific_exceptions_edit.clear()
        
        self.save_button.setEnabled(False)
    
    def load_config(self, config):
        """Charger une configuration dans le formulaire."""
        self.current_config = config
        
        # Informations de base
        self.id_edit.setText(config.id)
        self.name_edit.setText(config.name)
        self.description_edit.setText(config.description)
        
        # Méthodes requises
        self.methods_list.clear()
        for method in config.rules.get('requiredMethods', []):
            params = ", ".join(method.get('params', []))
            display_name = f"{method['name']}({params}) -> {method['returnType']}"
            
            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, method)
            self.methods_list.addItem(item)
        
        # Opérateurs autorisés
        operators = config.rules.get('allowedOperators', [])
        self.operators_edit.setText(", ".join(operators))
        
        # Structures de contrôle requises
        control_structures = config.rules.get('requiredControlStructures', [])
        self.control_edit.setText(", ".join(control_structures))
        
        # Options diverses
        self.check_scope.setChecked(config.rules.get('checkVariableScope', False))
        
        naming_conventions = config.rules.get('checkNamingConventions', [])
        self.naming_edit.setText(", ".join(naming_conventions))
        
        # Motifs personnalisés
        self.patterns_list.clear()
        for pattern in config.rules.get('customPatterns', []):
            description = pattern.get('description', 'Sans description')
            required = pattern.get('required', False)
            display_name = f"{description} ({'Requis' if required else 'Optionnel'})"
            
            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, pattern)
            self.patterns_list.addItem(item)
        
        # Vérifications de domaine
        self.domain_checks_list.clear()
        domain_checks = config.get_domain_checks()
        for check in domain_checks:
            if 'pattern' in check:  # Nouveau format avec pattern
                display_name = f"Pattern: {check['pattern']}"
            else:  # Ancien format avec variable/operator/value
                display_name = f"{check.get('variable', '')} {check.get('operator', '')} {check.get('value', '')}"
            
            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, check)
            self.domain_checks_list.addItem(item)
            
        # Fonctions mathématiques
        self.math_functions_list.clear()
        for func in config.get_math_functions():
            # Gérer le cas où la fonction n'a pas de paramètres explicites
            params = func.get('params', [])
            if not params and 'domainCondition' in func:
                # Si pas de paramètres mais une condition de domaine, on suppose un paramètre
                params = ['x']
            
            display_name = f"{func['name']}({', '.join(params)})"
            
            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, func)
            self.math_functions_list.addItem(item)
        
        # Gestion des exceptions
        self.try_catch_checkbox.setChecked(config.rules.get('exceptionHandling', {}).get('required', False))
        
        specific_exceptions = config.rules.get('exceptionHandling', {}).get('specificExceptions', [])
        self.specific_exceptions_edit.setText(", ".join(specific_exceptions))
        
        self.save_button.setEnabled(True)
    
    def save_config(self):
        """Sauvegarder la configuration."""
        if not self.current_config:
            return
        
        # Mise à jour des informations de base
        self.current_config.name = self.name_edit.text()
        self.current_config.description = self.description_edit.toPlainText()
        
        # Mise à jour des règles
        self.current_config.rules = {
            # Méthodes requises
            'requiredMethods': [
                self.methods_list.item(i).data(Qt.UserRole)
                for i in range(self.methods_list.count())
            ],
            
            # Opérateurs autorisés
            'allowedOperators': [
                op.strip()
                for op in self.operators_edit.text().split(',')
                if op.strip()
            ],
            
            # Structures de contrôle requises
            'requiredControlStructures': [
                ctrl.strip()
                for ctrl in self.control_edit.text().split(',')
                if ctrl.strip()
            ],
            
            # Options diverses
            'checkVariableScope': self.check_scope.isChecked(),
            
            'checkNamingConventions': [
                conv.strip()
                for conv in self.naming_edit.text().split(',')
                if conv.strip()
            ],
            
            # Motifs personnalisés
            'customPatterns': [
                self.patterns_list.item(i).data(Qt.UserRole)
                for i in range(self.patterns_list.count())
            ]
        }
        
        # Vérifications de domaine
        domain_checks = [
            self.domain_checks_list.item(i).data(Qt.UserRole)
            for i in range(self.domain_checks_list.count())
        ]
        self.current_config.set_domain_checks(domain_checks)
        
        # Fonctions mathématiques
        math_functions = [
            self.math_functions_list.item(i).data(Qt.UserRole)
            for i in range(self.math_functions_list.count())
        ]
        self.current_config.set_math_functions(math_functions)
        
        # Gestion des exceptions
        exception_handling = {
            'required': self.try_catch_checkbox.isChecked(),
            'specificExceptions': [
                ex.strip()
                for ex in self.specific_exceptions_edit.text().split(',')
                if ex.strip()
            ]
        }
        
        if exception_handling['required'] or exception_handling['specificExceptions']:
            self.current_config.rules['exceptionHandling'] = exception_handling
        
        # Sauvegarde de la configuration
        if self.config_loader.save_exercise_config(self.current_config):
            QMessageBox.information(self, "Sauvegarde", 
                                  f"Configuration '{self.current_config.id}' sauvegardée avec succès.")
        else:
            QMessageBox.warning(self, "Erreur", 
                              f"Erreur lors de la sauvegarde de la configuration '{self.current_config.id}'.")
    
    def on_add_method(self):
        """Ajouter une méthode requise."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter une méthode requise")
        layout = QVBoxLayout()
        
        form = QFormLayout()
        
        name_edit = QLineEdit()
        form.addRow("Nom :", name_edit)
        
        return_type_edit = QLineEdit()
        return_type_edit.setText("void")  # Valeur par défaut
        form.addRow("Type de retour :", return_type_edit)
        
        params_list = QListWidget()
        form.addRow("Paramètres :", params_list)
        
        params_buttons = QHBoxLayout()
        add_param_button = QPushButton("Ajouter")
        delete_param_button = QPushButton("Supprimer")
        params_buttons.addWidget(add_param_button)
        params_buttons.addWidget(delete_param_button)
        
        def add_parameter():
            param_type, ok = QInputDialog.getText(
                dialog, "Type de paramètre", 
                "Entrez le type du paramètre (ex: int, String):"
            )
            if ok and param_type:
                item = QListWidgetItem(param_type)
                params_list.addItem(item)
        
        def delete_parameter():
            current_item = params_list.currentItem()
            if current_item:
                row = params_list.row(current_item)
                params_list.takeItem(row)
        
        add_param_button.clicked.connect(add_parameter)
        delete_param_button.clicked.connect(delete_parameter)
        
        layout.addLayout(form)
        layout.addLayout(params_buttons)
        
        buttons = QHBoxLayout()
        ok_button = QPushButton("Ajouter")
        cancel_button = QPushButton("Annuler")
        
        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)
        
        layout.addLayout(buttons)
        dialog.setLayout(layout)
        
        # Connecter les boutons
        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        
        # Afficher le dialogue
        if dialog.exec_() == QDialog.Accepted:
            # Récupérer les valeurs
            method_name = name_edit.text()
            return_type = return_type_edit.text()
            
            parameters = []
            for i in range(params_list.count()):
                parameters.append(params_list.item(i).text())
            
            if not method_name:
                QMessageBox.warning(self, "Erreur", "Le nom de la méthode est obligatoire.")
                return
            
            # Créer la méthode
            method = {
                'name': method_name,
                'returnType': return_type,
                'params': parameters
            }
            
            # Ajouter à la liste
            params_display = ", ".join(parameters)
            display_name = f"{method_name}({params_display}) -> {return_type}"
            
            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, method)
            self.methods_list.addItem(item)
    
    def on_delete_method(self):
        """Supprimer la méthode sélectionnée."""
        current_item = self.methods_list.currentItem()
        if current_item:
            row = self.methods_list.row(current_item)
            self.methods_list.takeItem(row)
    
    def on_add_pattern(self):
        """Ajouter un motif personnalisé."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter un motif personnalisé")
        layout = QVBoxLayout()
        
        form = QFormLayout()
        
        description_edit = QLineEdit()
        form.addRow("Description :", description_edit)
        
        pattern_edit = QTextEdit()
        pattern_edit.setPlaceholderText("Motif regex ou syntaxe Java")
        form.addRow("Motif :", pattern_edit)
        
        required_checkbox = QCheckBox("Motif requis")
        form.addRow("", required_checkbox)
        
        error_message_edit = QLineEdit()
        form.addRow("Message d'erreur :", error_message_edit)
        
        layout.addLayout(form)
        
        buttons = QHBoxLayout()
        ok_button = QPushButton("Ajouter")
        cancel_button = QPushButton("Annuler")
        
        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)
        
        layout.addLayout(buttons)
        dialog.setLayout(layout)
        
        # Connecter les boutons
        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        
        # Afficher le dialogue
        if dialog.exec_() == QDialog.Accepted:
            # Récupérer les valeurs
            description = description_edit.text()
            pattern = pattern_edit.toPlainText()
            required = required_checkbox.isChecked()
            error_message = error_message_edit.text()
            
            if not description or not pattern:
                QMessageBox.warning(self, "Erreur", "La description et le motif sont obligatoires.")
                return
            
            # Créer le motif
            custom_pattern = {
                'description': description,
                'pattern': pattern,
                'required': required
            }
            
            if error_message:
                custom_pattern['errorMessage'] = error_message
            
            # Ajouter à la liste
            display_name = f"{description} ({'Requis' if required else 'Optionnel'})"
            
            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, custom_pattern)
            self.patterns_list.addItem(item)
    
    def on_delete_pattern(self):
        """Supprimer le motif sélectionné."""
        current_item = self.patterns_list.currentItem()
        if current_item:
            row = self.patterns_list.row(current_item)
            self.patterns_list.takeItem(row)
    
    def on_add_domain_check(self):
        """Ajouter une vérification de domaine."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter une vérification de domaine")
        layout = QVBoxLayout()
        
        form = QFormLayout()
        
        variable_edit = QLineEdit()
        form.addRow("Variable :", variable_edit)
        
        operator_combo = QComboBox()
        operator_combo.addItems(["==", "!=", ">", ">=", "<", "<=", "in"])
        form.addRow("Opérateur :", operator_combo)
        
        value_edit = QLineEdit()
        form.addRow("Valeur :", value_edit)
        
        error_message_edit = QLineEdit()
        form.addRow("Message d'erreur :", error_message_edit)
        
        layout.addLayout(form)
        
        buttons = QHBoxLayout()
        ok_button = QPushButton("Ajouter")
        cancel_button = QPushButton("Annuler")
        
        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)
        
        layout.addLayout(buttons)
        dialog.setLayout(layout)
        
        # Connecter les boutons
        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        
        # Afficher le dialogue
        if dialog.exec_() == QDialog.Accepted:
            # Récupérer les valeurs
            variable = variable_edit.text()
            operator = operator_combo.currentText()
            value = value_edit.text()
            error_message = error_message_edit.text()
            
            if not variable or not value:
                QMessageBox.warning(self, "Erreur", "La variable et la valeur sont obligatoires.")
                return
            
            # Créer la vérification
            domain_check = {
                'variable': variable,
                'operator': operator,
                'value': value
            }
            
            if error_message:
                domain_check['errorMessage'] = error_message
            
            # Ajouter à la liste
            display_name = f"{variable} {operator} {value}"
            
            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, domain_check)
            self.domain_checks_list.addItem(item)
    
    def on_delete_domain_check(self):
        """Supprimer la vérification de domaine sélectionnée."""
        current_item = self.domain_checks_list.currentItem()
        if current_item:
            row = self.domain_checks_list.row(current_item)
            self.domain_checks_list.takeItem(row)
    
    def on_add_math_function(self):
        """Ajouter une fonction mathématique."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter une fonction mathématique")
        layout = QVBoxLayout()
        
        form = QFormLayout()
        
        name_edit = QLineEdit()
        form.addRow("Nom :", name_edit)
        
        params_edit = QLineEdit()
        params_edit.setPlaceholderText("Ex: x, y, z")
        form.addRow("Paramètres (séparés par des virgules) :", params_edit)
        
        expression_edit = QTextEdit()
        expression_edit.setPlaceholderText("Ex: Math.sqrt(x*x + y*y)")
        form.addRow("Expression :", expression_edit)
        
        error_message_edit = QLineEdit()
        form.addRow("Message d'erreur :", error_message_edit)
        
        layout.addLayout(form)
        
        buttons = QHBoxLayout()
        ok_button = QPushButton("Ajouter")
        cancel_button = QPushButton("Annuler")
        
        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)
        
        layout.addLayout(buttons)
        dialog.setLayout(layout)
        
        # Connecter les boutons
        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        
        # Afficher le dialogue
        if dialog.exec_() == QDialog.Accepted:
            # Récupérer les valeurs
            name = name_edit.text()
            params = [p.strip() for p in params_edit.text().split(',') if p.strip()]
            expression = expression_edit.toPlainText()
            error_message = error_message_edit.text()
            
            if not name or not expression:
                QMessageBox.warning(self, "Erreur", "Le nom et l'expression sont obligatoires.")
                return
            
            # Créer la fonction
            math_function = {
                'name': name,
                'params': params,
                'expression': expression
            }
            
            if error_message:
                math_function['errorMessage'] = error_message
            
            # Ajouter à la liste
            display_name = f"{name}({', '.join(params)})"
            
            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, math_function)
            self.math_functions_list.addItem(item)
    
    def on_delete_math_function(self):
        """Supprimer la fonction mathématique sélectionnée."""
        current_item = self.math_functions_list.currentItem()
        if current_item:
            row = self.math_functions_list.row(current_item)
            self.math_functions_list.takeItem(row) 