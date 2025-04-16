from PyQt5.QtWidgets import (QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, 
                             QFormLayout, QLabel, QLineEdit, QTextEdit, 
                             QPushButton, QListWidget, QListWidgetItem, 
                             QMessageBox, QComboBox, QCheckBox, QSpinBox,
                             QGroupBox, QScrollArea, QInputDialog, QDialog)
from PyQt5.QtCore import Qt, QSize
import json
import os

from teach_assit.core.analysis.models import ExerciseConfig, AssessmentConfig
from teach_assit.core.analysis.config_loader import ConfigLoader


class ConfigEditorWidget(QWidget):
    """Widget permettant d'éditer les configurations JSON."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_loader = ConfigLoader(os.getcwd())
        self.init_ui()
        self.load_configs()
    
    def init_ui(self):
        """Initialiser l'interface utilisateur."""
        layout = QVBoxLayout()
        
        # Onglets pour les exercices et les évaluations
        self.tab_widget = QTabWidget()
        self.exercise_tab = self.create_exercise_tab()
        self.assessment_tab = self.create_assessment_tab()
        
        self.tab_widget.addTab(self.exercise_tab, "Exercices")
        self.tab_widget.addTab(self.assessment_tab, "Évaluations")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
    
    def create_exercise_tab(self):
        """Créer l'onglet pour les exercices."""
        tab = QWidget()
        layout = QHBoxLayout()
        
        # Panneau de gauche : liste des exercices
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        self.exercise_list = QListWidget()
        self.exercise_list.setMinimumWidth(250)
        self.exercise_list.currentItemChanged.connect(self.on_exercise_selected)
        
        left_layout.addWidget(QLabel("Exercices disponibles :"))
        left_layout.addWidget(self.exercise_list)
        
        button_layout = QHBoxLayout()
        
        self.add_exercise_button = QPushButton("Nouveau")
        self.add_exercise_button.clicked.connect(self.on_add_exercise)
        button_layout.addWidget(self.add_exercise_button)
        
        self.delete_exercise_button = QPushButton("Supprimer")
        self.delete_exercise_button.clicked.connect(self.on_delete_exercise)
        self.delete_exercise_button.setEnabled(False)
        button_layout.addWidget(self.delete_exercise_button)
        
        left_layout.addLayout(button_layout)
        left_panel.setLayout(left_layout)
        
        # Panneau de droite : formulaire d'édition
        right_panel = QScrollArea()
        right_panel.setWidgetResizable(True)
        
        self.exercise_form = ExerciseConfigForm()
        right_panel.setWidget(self.exercise_form)
        
        # Ajout des panneaux au layout principal
        layout.addWidget(left_panel)
        layout.addWidget(right_panel, 1)  # Le panneau de droite prend plus de place
        
        tab.setLayout(layout)
        return tab
    
    def create_assessment_tab(self):
        """Créer l'onglet pour les évaluations."""
        tab = QWidget()
        layout = QHBoxLayout()
        
        # Panneau de gauche : liste des évaluations
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        self.assessment_list = QListWidget()
        self.assessment_list.setMinimumWidth(250)
        self.assessment_list.currentItemChanged.connect(self.on_assessment_selected)
        
        left_layout.addWidget(QLabel("Évaluations disponibles :"))
        left_layout.addWidget(self.assessment_list)
        
        button_layout = QHBoxLayout()
        
        self.add_assessment_button = QPushButton("Nouveau")
        self.add_assessment_button.clicked.connect(self.on_add_assessment)
        button_layout.addWidget(self.add_assessment_button)
        
        self.delete_assessment_button = QPushButton("Supprimer")
        self.delete_assessment_button.clicked.connect(self.on_delete_assessment)
        self.delete_assessment_button.setEnabled(False)
        button_layout.addWidget(self.delete_assessment_button)
        
        left_layout.addLayout(button_layout)
        left_panel.setLayout(left_layout)
        
        # Panneau de droite : formulaire d'édition
        right_panel = QScrollArea()
        right_panel.setWidgetResizable(True)
        
        self.assessment_form = AssessmentConfigForm(self.config_loader)
        right_panel.setWidget(self.assessment_form)
        
        # Ajout des panneaux au layout principal
        layout.addWidget(left_panel)
        layout.addWidget(right_panel, 1)  # Le panneau de droite prend plus de place
        
        tab.setLayout(layout)
        return tab
    
    def load_configs(self):
        """Charger les configurations existantes."""
        exercise_count, assessment_count = self.config_loader.load_all_configs()
        
        # Charger les exercices
        self.exercise_list.clear()
        for exercise_id, config in self.config_loader.get_all_exercise_configs().items():
            item = QListWidgetItem(f"{config.name} ({exercise_id})")
            item.setData(Qt.UserRole, exercise_id)
            self.exercise_list.addItem(item)
        
        # Charger les évaluations
        self.assessment_list.clear()
        for assessment_id, config in self.config_loader.get_all_assessment_configs().items():
            item = QListWidgetItem(f"{config.name} ({assessment_id})")
            item.setData(Qt.UserRole, assessment_id)
            self.assessment_list.addItem(item)
        
        # Mettre à jour le formulaire d'évaluation avec la liste des exercices
        self.assessment_form.update_exercise_list()
    
    def on_exercise_selected(self, item):
        """Appelé quand un exercice est sélectionné dans la liste."""
        self.delete_exercise_button.setEnabled(item is not None)
        
        if item is None:
            self.exercise_form.clear()
            return
        
        exercise_id = item.data(Qt.UserRole)
        config = self.config_loader.get_exercise_config(exercise_id)
        if config:
            self.exercise_form.load_config(config)
    
    def on_assessment_selected(self, item):
        """Appelé quand une évaluation est sélectionnée dans la liste."""
        self.delete_assessment_button.setEnabled(item is not None)
        
        if item is None:
            self.assessment_form.clear()
            return
        
        assessment_id = item.data(Qt.UserRole)
        config = self.config_loader.get_assessment_config(assessment_id)
        if config:
            self.assessment_form.load_config(config)
    
    def on_add_exercise(self):
        """Ajouter un nouvel exercice."""
        # Demander l'ID de l'exercice
        exercise_id, ok = QInputDialog.getText(self, "Nouvel exercice", 
                                             "Identifiant de l'exercice :")
        if not ok or not exercise_id:
            return
        
        # Vérifier si l'ID existe déjà
        if exercise_id in self.config_loader.get_all_exercise_configs():
            QMessageBox.warning(self, "Erreur", 
                              f"Un exercice avec l'identifiant '{exercise_id}' existe déjà.")
            return
        
        # Créer une nouvelle configuration
        config = ExerciseConfig()
        config.id = exercise_id
        config.name = f"Nouvel exercice {exercise_id}"
        
        # Sauvegarder et charger
        if self.config_loader.save_exercise_config(config):
            self.load_configs()
            
            # Sélectionner le nouvel exercice dans la liste
            for i in range(self.exercise_list.count()):
                item = self.exercise_list.item(i)
                if item.data(Qt.UserRole) == exercise_id:
                    self.exercise_list.setCurrentItem(item)
                    break
    
    def on_delete_exercise(self):
        """Supprimer l'exercice sélectionné."""
        item = self.exercise_list.currentItem()
        if not item:
            return
        
        exercise_id = item.data(Qt.UserRole)
        
        # Confirmation
        reply = QMessageBox.question(self, "Confirmation", 
                                    f"Êtes-vous sûr de vouloir supprimer l'exercice '{exercise_id}' ?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        
        # Supprimer la configuration
        if self.config_loader.delete_exercise_config(exercise_id):
            self.load_configs()
            self.exercise_form.clear()
    
    def on_add_assessment(self):
        """Ajouter une nouvelle évaluation."""
        # Demander l'ID de l'évaluation
        assessment_id, ok = QInputDialog.getText(self, "Nouvelle évaluation", 
                                               "Identifiant de l'évaluation :")
        if not ok or not assessment_id:
            return
        
        # Vérifier si l'ID existe déjà
        if assessment_id in self.config_loader.get_all_assessment_configs():
            QMessageBox.warning(self, "Erreur", 
                              f"Une évaluation avec l'identifiant '{assessment_id}' existe déjà.")
            return
        
        # Créer une nouvelle configuration
        config = AssessmentConfig()
        config.id = assessment_id
        config.name = f"Nouvelle évaluation {assessment_id}"
        
        # Sauvegarder et charger
        if self.config_loader.save_assessment_config(config):
            self.load_configs()
            
            # Sélectionner la nouvelle évaluation dans la liste
            for i in range(self.assessment_list.count()):
                item = self.assessment_list.item(i)
                if item.data(Qt.UserRole) == assessment_id:
                    self.assessment_list.setCurrentItem(item)
                    break
    
    def on_delete_assessment(self):
        """Supprimer l'évaluation sélectionnée."""
        item = self.assessment_list.currentItem()
        if not item:
            return
        
        assessment_id = item.data(Qt.UserRole)
        
        # Confirmation
        reply = QMessageBox.question(self, "Confirmation", 
                                    f"Êtes-vous sûr de vouloir supprimer l'évaluation '{assessment_id}' ?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        
        # Supprimer la configuration
        if self.config_loader.delete_assessment_config(assessment_id):
            self.load_configs()
            self.assessment_form.clear()


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
        for method in config.get_required_methods():
            params_str = ", ".join(method.get('params', []))
            return_type = method.get('returnType', 'void')
            display_name = f"{method.get('name', '')}({params_str}) -> {return_type}"
            
            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, method)
            self.methods_list.addItem(item)
        
        # Opérateurs autorisés
        self.operators_edit.setText(", ".join(config.get_allowed_operators()))
        
        # Structures de contrôle requises
        self.control_edit.setText(", ".join(config.get_required_control_structures()))
        
        # Options diverses
        self.check_scope.setChecked(config.should_check_variable_scope())
        self.naming_edit.setText(", ".join(config.get_naming_conventions()))
        
        # Motifs personnalisés
        self.patterns_list.clear()
        for pattern in config.get_custom_patterns():
            display_name = pattern.get('description', 'Pattern sans description')
            
            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, pattern)
            self.patterns_list.addItem(item)
        
        # Vérifications de domaine
        self.domain_checks_list.clear()
        for domain_check in config.get_domain_checks():
            display_name = domain_check.get('description', 'Vérification sans description')
            
            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, domain_check)
            self.domain_checks_list.addItem(item)
        
        # Fonctions mathématiques
        self.math_functions_list.clear()
        for math_function in config.get_math_functions():
            display_name = math_function.get('description', 'Fonction mathématique sans description')
            
            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, math_function)
            self.math_functions_list.addItem(item)
        
        # Gestion des exceptions
        self.try_catch_checkbox.setChecked(config.should_use_try_catch())
        self.specific_exceptions_edit.setText(", ".join(config.get_specific_exceptions()))
        
        self.save_button.setEnabled(True)
    
    def save_config(self):
        """Sauvegarder la configuration."""
        if not self.current_config:
            return
        
        # Mise à jour des informations de base
        self.current_config.name = self.name_edit.text()
        self.current_config.description = self.description_edit.toPlainText()
        
        # Mise à jour des règles
        rules = {}
        
        # Méthodes requises
        methods = []
        for i in range(self.methods_list.count()):
            method = self.methods_list.item(i).data(Qt.UserRole)
            methods.append(method)
        rules['requiredMethods'] = methods
        
        # Opérateurs autorisés
        operators = [op.strip() for op in self.operators_edit.text().split(',') if op.strip()]
        if operators:
            rules['allowedOperators'] = operators
        
        # Structures de contrôle requises
        control_structures = [cs.strip() for cs in self.control_edit.text().split(',') if cs.strip()]
        if control_structures:
            rules['requiredControlStructures'] = control_structures
        
        # Options diverses
        if self.check_scope.isChecked():
            rules['checkVariableScope'] = True
        
        naming_conventions = [nc.strip() for nc in self.naming_edit.text().split(',') if nc.strip()]
        if naming_conventions:
            rules['checkNamingConventions'] = naming_conventions
        
        # Motifs personnalisés
        patterns = []
        for i in range(self.patterns_list.count()):
            pattern = self.patterns_list.item(i).data(Qt.UserRole)
            patterns.append(pattern)
        if patterns:
            rules['customPatterns'] = patterns
        
        # Vérifications de domaine
        domain_checks = []
        for i in range(self.domain_checks_list.count()):
            domain_check = self.domain_checks_list.item(i).data(Qt.UserRole)
            domain_checks.append(domain_check)
        if domain_checks:
            rules['requiredDomainChecks'] = domain_checks
        
        # Fonctions mathématiques
        math_functions = []
        for i in range(self.math_functions_list.count()):
            math_function = self.math_functions_list.item(i).data(Qt.UserRole)
            math_functions.append(math_function)
        if math_functions:
            rules['mathFunctions'] = math_functions
        
        # Gestion des exceptions
        exception_handling = {}
        if self.try_catch_checkbox.isChecked():
            exception_handling['requiredTryCatch'] = True
        
        specific_exceptions = [ex.strip() for ex in self.specific_exceptions_edit.text().split(',') if ex.strip()]
        if specific_exceptions:
            exception_handling['specificExceptions'] = specific_exceptions
        
        if exception_handling:
            rules['exceptionHandling'] = exception_handling
        
        self.current_config.rules = rules
        
        # Sauvegarde de la configuration
        if self.config_loader.save_exercise_config(self.current_config):
            QMessageBox.information(self, "Sauvegarde", 
                                  f"Configuration '{self.current_config.id}' sauvegardée avec succès.")
        else:
            QMessageBox.warning(self, "Erreur", 
                              f"Erreur lors de la sauvegarde de la configuration '{self.current_config.id}'.")
    
    def on_add_method(self):
        """Ajouter une méthode requise avec un dialogue."""
        # Créer un dialogue pour saisir les informations de la méthode
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter une méthode requise")
        layout = QVBoxLayout()
        
        # Formulaire pour les informations de la méthode
        form_layout = QFormLayout()
        
        # Nom de la méthode
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Ex: calculerSomme")
        form_layout.addRow("Nom de la méthode :", name_edit)
        
        # Type de retour
        return_type_edit = QLineEdit()
        return_type_edit.setPlaceholderText("Ex: int, boolean, String, void")
        form_layout.addRow("Type de retour :", return_type_edit)
        
        # Paramètres
        params_layout = QVBoxLayout()
        params_layout.addWidget(QLabel("Paramètres :"))
        
        params_list = QListWidget()
        params_list.setMinimumHeight(100)
        params_layout.addWidget(params_list)
        
        params_buttons = QHBoxLayout()
        
        # Bouton pour ajouter un paramètre
        add_param_button = QPushButton("Ajouter paramètre")
        
        # Bouton pour supprimer un paramètre
        delete_param_button = QPushButton("Supprimer paramètre")
        delete_param_button.setEnabled(False)
        
        params_buttons.addWidget(add_param_button)
        params_buttons.addWidget(delete_param_button)
        params_layout.addLayout(params_buttons)
        
        # Fonction pour ajouter un paramètre
        def add_parameter():
            param_type, ok = QInputDialog.getText(dialog, "Type de paramètre", 
                                                "Entrez le type du paramètre (ex: int, String, double) :")
            if ok and param_type:
                params_list.addItem(param_type)
        
        # Fonction pour supprimer un paramètre
        def delete_parameter():
            selected_items = params_list.selectedItems()
            if selected_items:
                for item in selected_items:
                    params_list.takeItem(params_list.row(item))
            delete_param_button.setEnabled(params_list.currentItem() is not None)
        
        # Connecter les boutons
        add_param_button.clicked.connect(add_parameter)
        delete_param_button.clicked.connect(delete_parameter)
        params_list.itemSelectionChanged.connect(
            lambda: delete_param_button.setEnabled(params_list.currentItem() is not None)
        )
        
        layout.addLayout(form_layout)
        layout.addLayout(params_layout)
        
        # Boutons OK/Annuler
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
        
        # Exécuter le dialogue
        if dialog.exec_() == QDialog.Accepted:
            # Récupérer les informations saisies
            method_name = name_edit.text().strip()
            return_type = return_type_edit.text().strip()
            
            # Vérifier que le nom et le type de retour sont renseignés
            if not method_name or not return_type:
                QMessageBox.warning(self, "Information manquante", 
                                  "Le nom de la méthode et le type de retour sont obligatoires.")
                return
            
            # Récupérer les paramètres
            params = []
            for i in range(params_list.count()):
                params.append(params_list.item(i).text())
            
            # Créer la méthode
            method = {
                'name': method_name,
                'params': params,
                'returnType': return_type
            }
            
            # Ajouter la méthode à la liste
            display_name = f"{method['name']}({', '.join(method['params'])}) -> {method['returnType']}"
            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, method)
            self.methods_list.addItem(item)
    
    def on_delete_method(self):
        """Supprimer la méthode sélectionnée."""
        item = self.methods_list.currentItem()
        if item:
            self.methods_list.takeItem(self.methods_list.row(item))
    
    def on_add_pattern(self):
        """Ajouter un motif personnalisé avec un dialogue."""
        # Créer un dialogue pour saisir les informations du motif
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter un motif personnalisé")
        layout = QVBoxLayout()
        
        # Formulaire pour les informations du motif
        form_layout = QFormLayout()
        
        # Expression régulière du motif
        pattern_edit = QTextEdit()
        pattern_edit.setPlaceholderText("Ex: if\\s*\\(.*\\)")
        pattern_edit.setMaximumHeight(100)
        form_layout.addRow("Expression régulière :", pattern_edit)
        
        # Description du motif
        description_edit = QLineEdit()
        description_edit.setPlaceholderText("Ex: Utilisation de la structure if")
        form_layout.addRow("Description :", description_edit)
        
        # Message d'erreur (optionnel)
        error_message_edit = QLineEdit()
        error_message_edit.setPlaceholderText("Message affiché si le motif n'est pas trouvé")
        form_layout.addRow("Message d'erreur (optionnel) :", error_message_edit)
        
        # Requis ou non
        required_checkbox = QCheckBox("Ce motif est requis")
        form_layout.addRow("", required_checkbox)
        
        layout.addLayout(form_layout)
        
        # Boutons OK/Annuler
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
        
        # Exécuter le dialogue
        if dialog.exec_() == QDialog.Accepted:
            # Récupérer les informations saisies
            pattern_regex = pattern_edit.toPlainText().strip()
            description = description_edit.text().strip()
            error_message = error_message_edit.text().strip()
            required = required_checkbox.isChecked()
            
            # Vérifier que le pattern et la description sont renseignés
            if not pattern_regex or not description:
                QMessageBox.warning(self, "Information manquante", 
                                  "L'expression régulière et la description sont obligatoires.")
                return
            
            # Créer le motif
            pattern = {
                'pattern': pattern_regex,
                'description': description,
                'required': required
            }
            
            # Ajouter le message d'erreur s'il est renseigné
            if error_message:
                pattern['errorMessage'] = error_message
            
            # Ajouter le motif à la liste
            item = QListWidgetItem(description)
            item.setData(Qt.UserRole, pattern)
            self.patterns_list.addItem(item)
    
    def on_delete_pattern(self):
        """Supprimer le motif sélectionné."""
        item = self.patterns_list.currentItem()
        if item:
            self.patterns_list.takeItem(self.patterns_list.row(item))
    
    def on_add_domain_check(self):
        """Ajouter une vérification de domaine avec un dialogue."""
        # Créer un dialogue pour saisir les informations de la vérification
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter une vérification de domaine")
        layout = QVBoxLayout()
        
        # Formulaire pour les informations de la vérification
        form_layout = QFormLayout()
        
        # Expression régulière de la vérification
        expression_edit = QLineEdit()
        expression_edit.setPlaceholderText("Ex: x > 0")
        form_layout.addRow("Expression régulière :", expression_edit)
        
        # Description de la vérification
        description_edit = QLineEdit()
        description_edit.setPlaceholderText("Ex: Vérifier que x est positif")
        form_layout.addRow("Description :", description_edit)
        
        # Message d'erreur (optionnel)
        error_message_edit = QLineEdit()
        error_message_edit.setPlaceholderText("Message affiché si la vérification échoue")
        form_layout.addRow("Message d'erreur (optionnel) :", error_message_edit)
        
        # Requis ou non
        required_checkbox = QCheckBox("Cette vérification est requise")
        form_layout.addRow("", required_checkbox)
        
        layout.addLayout(form_layout)
        
        # Boutons OK/Annuler
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
        
        # Exécuter le dialogue
        if dialog.exec_() == QDialog.Accepted:
            # Récupérer les informations saisies
            expression = expression_edit.text().strip()
            description = description_edit.text().strip()
            error_message = error_message_edit.text().strip()
            required = required_checkbox.isChecked()
            
            # Vérifier que l'expression et la description sont renseignés
            if not expression or not description:
                QMessageBox.warning(self, "Information manquante", 
                                  "L'expression et la description sont obligatoires.")
                return
            
            # Créer la vérification
            domain_check = {
                'expression': expression,
                'description': description,
                'required': required
            }
            
            # Ajouter la vérification à la liste
            item = QListWidgetItem(description)
            item.setData(Qt.UserRole, domain_check)
            self.domain_checks_list.addItem(item)
    
    def on_delete_domain_check(self):
        """Supprimer la vérification sélectionnée."""
        item = self.domain_checks_list.currentItem()
        if item:
            self.domain_checks_list.takeItem(self.domain_checks_list.row(item))
    
    def on_add_math_function(self):
        """Ajouter une fonction mathématique avec un dialogue."""
        # Créer un dialogue pour saisir les informations de la fonction
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter une fonction mathématique")
        layout = QVBoxLayout()
        
        # Formulaire pour les informations de la fonction
        form_layout = QFormLayout()
        
        # Nom de la fonction
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Ex: calculerSomme")
        form_layout.addRow("Nom de la fonction :", name_edit)
        
        # Description de la fonction
        description_edit = QLineEdit()
        description_edit.setPlaceholderText("Ex: Fonction pour calculer la somme de deux nombres")
        form_layout.addRow("Description :", description_edit)
        
        # Expression régulière de la fonction
        expression_edit = QTextEdit()
        expression_edit.setPlaceholderText("Ex: x + y")
        expression_edit.setMaximumHeight(100)
        form_layout.addRow("Expression régulière :", expression_edit)
        
        layout.addLayout(form_layout)
        
        # Boutons OK/Annuler
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
        
        # Exécuter le dialogue
        if dialog.exec_() == QDialog.Accepted:
            # Récupérer les informations saisies
            name = name_edit.text().strip()
            description = description_edit.text().strip()
            expression = expression_edit.toPlainText().strip()
            
            # Vérifier que le nom, la description et l'expression sont renseignés
            if not name or not description or not expression:
                QMessageBox.warning(self, "Information manquante", 
                                  "Le nom, la description et l'expression sont obligatoires.")
                return
            
            # Créer la fonction
            math_function = {
                'name': name,
                'description': description,
                'expression': expression
            }
            
            # Ajouter la fonction à la liste
            item = QListWidgetItem(description)
            item.setData(Qt.UserRole, math_function)
            self.math_functions_list.addItem(item)
    
    def on_delete_math_function(self):
        """Supprimer la fonction sélectionnée."""
        item = self.math_functions_list.currentItem()
        if item:
            self.math_functions_list.takeItem(self.math_functions_list.row(item))


class AssessmentConfigForm(QWidget):
    """Formulaire pour éditer une configuration d'évaluation."""
    
    def __init__(self, config_loader, parent=None):
        super().__init__(parent)
        self.current_config = None
        self.config_loader = config_loader
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
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # Exercices inclus
        exercises_group = QGroupBox("Exercices inclus")
        exercises_layout = QVBoxLayout()
        
        self.exercises_list = QListWidget()
        exercises_layout.addWidget(self.exercises_list)
        
        exercises_buttons = QHBoxLayout()
        self.add_exercise_button = QPushButton("Ajouter")
        self.add_exercise_button.clicked.connect(self.on_add_exercise)
        exercises_buttons.addWidget(self.add_exercise_button)
        
        self.delete_exercise_button = QPushButton("Supprimer")
        self.delete_exercise_button.clicked.connect(self.on_delete_exercise)
        exercises_buttons.addWidget(self.delete_exercise_button)
        
        exercises_layout.addLayout(exercises_buttons)
        exercises_group.setLayout(exercises_layout)
        layout.addWidget(exercises_group)
        
        # Total des points
        points_group = QGroupBox("Points")
        points_layout = QFormLayout()
        
        self.total_points_label = QLabel("0")
        points_layout.addRow("Total des points :", self.total_points_label)
        
        points_group.setLayout(points_layout)
        layout.addWidget(points_group)
        
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
        self.exercises_list.clear()
        self.total_points_label.setText("0")
        
        self.save_button.setEnabled(False)
    
    def update_exercise_list(self):
        """Mettre à jour la liste des exercices disponibles."""
        # Cette méthode est appelée quand la liste des exercices change
        if self.current_config:
            self.load_config(self.current_config)
    
    def load_config(self, config):
        """Charger une configuration dans le formulaire."""
        self.current_config = config
        
        # Informations de base
        self.id_edit.setText(config.id)
        self.name_edit.setText(config.name)
        
        # Exercices inclus
        self.exercises_list.clear()
        for exercise in config.exercises:
            exercise_id = exercise.get('exerciseId', '')
            max_points = exercise.get('maxPoints', 0)
            
            # Récupérer le nom de l'exercice s'il existe
            exercise_config = self.config_loader.get_exercise_config(exercise_id)
            exercise_name = exercise_config.name if exercise_config else exercise_id
            
            display_name = f"{exercise_name} ({exercise_id}) - {max_points} points"
            
            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, exercise)
            self.exercises_list.addItem(item)
        
        # Total des points
        self.total_points_label.setText(str(config.total_max_points))
        
        self.save_button.setEnabled(True)
    
    def save_config(self):
        """Sauvegarder la configuration."""
        if not self.current_config:
            return
        
        # Mise à jour des informations de base
        self.current_config.name = self.name_edit.text()
        
        # Mise à jour des exercices
        self.current_config.exercises = []
        for i in range(self.exercises_list.count()):
            exercise = self.exercises_list.item(i).data(Qt.UserRole)
            self.current_config.exercises.append(exercise)
        
        # Mise à jour du total des points
        self.current_config.update_max_points()
        
        # Sauvegarde de la configuration
        if self.config_loader.save_assessment_config(self.current_config):
            self.total_points_label.setText(str(self.current_config.total_max_points))
            QMessageBox.information(self, "Sauvegarde", 
                                  f"Configuration '{self.current_config.id}' sauvegardée avec succès.")
        else:
            QMessageBox.warning(self, "Erreur", 
                              f"Erreur lors de la sauvegarde de la configuration '{self.current_config.id}'.")
    
    def on_add_exercise(self):
        """Ajouter un exercice à l'évaluation."""
        # Récupérer la liste des exercices disponibles
        exercise_configs = self.config_loader.get_all_exercise_configs()
        if not exercise_configs:
            QMessageBox.warning(self, "Aucun exercice", 
                              "Aucun exercice n'est disponible. Veuillez d'abord créer des exercices.")
            return
        
        # Liste des exercices déjà inclus
        included_ids = set()
        for i in range(self.exercises_list.count()):
            exercise = self.exercises_list.item(i).data(Qt.UserRole)
            included_ids.add(exercise.get('exerciseId', ''))
        
        # Créer un dialogue de sélection
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter un exercice")
        layout = QVBoxLayout()
        
        label = QLabel("Sélectionnez un exercice :")
        layout.addWidget(label)
        
        combo = QComboBox()
        for exercise_id, config in exercise_configs.items():
            if exercise_id not in included_ids:
                combo.addItem(f"{config.name} ({exercise_id})", exercise_id)
        
        if combo.count() == 0:
            QMessageBox.warning(self, "Tous les exercices inclus", 
                              "Tous les exercices disponibles sont déjà inclus dans cette évaluation.")
            return
        
        layout.addWidget(combo)
        
        points_layout = QFormLayout()
        points_spin = QSpinBox()
        points_spin.setMinimum(0)
        points_spin.setMaximum(100)
        points_spin.setValue(5)  # Valeur par défaut
        points_layout.addRow("Points :", points_spin)
        
        layout.addLayout(points_layout)
        
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
            exercise_id = combo.currentData()
            max_points = points_spin.value()
            
            exercise = {
                'exerciseId': exercise_id,
                'maxPoints': max_points
            }
            
            # Récupérer le nom de l'exercice
            exercise_config = self.config_loader.get_exercise_config(exercise_id)
            exercise_name = exercise_config.name if exercise_config else exercise_id
            
            display_name = f"{exercise_name} ({exercise_id}) - {max_points} points"
            
            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, exercise)
            self.exercises_list.addItem(item)
    
    def on_delete_exercise(self):
        """Supprimer l'exercice sélectionné."""
        item = self.exercises_list.currentItem()
        if item:
            self.exercises_list.takeItem(self.exercises_list.row(item)) 