from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QMessageBox, QScrollArea
from PyQt5.QtCore import Qt
import os

from teach_assit.core.analysis.config_loader import ConfigLoader
from teach_assit.gui.exercise_form.basic_info_panel import BasicInfoPanel
from teach_assit.gui.exercise_form.methods_panel import MethodsPanel
from teach_assit.gui.exercise_form.operators_control_panel import OperatorsControlPanel
from teach_assit.gui.exercise_form.options_panel import OptionsPanel
from teach_assit.gui.exercise_form.patterns_panel import PatternsPanel
from teach_assit.gui.exercise_form.domain_checks_panel import DomainChecksPanel
from teach_assit.gui.exercise_form.exceptions_panel import ExceptionsPanel
from teach_assit.gui.exercise_form.math_functions_panel import MathFunctionsPanel
from teach_assit.gui.exercise_form.grading_criteria_panel import GradingCriteriaPanel
from teach_assit.gui.exercise_form.test_inputs_panel import TestInputsPanel

class ExerciseConfigForm(QWidget):
    """Formulaire pour éditer une configuration d'exercice."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_config = None
        self.config_loader = ConfigLoader(os.getcwd())
        self.init_ui()
    
    def init_ui(self):
        """Initialiser l'interface utilisateur."""
        main_layout = QVBoxLayout()
        
        # Utiliser un widget de défilement pour gérer les grands formulaires
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # Widget conteneur pour le formulaire
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        
        # Ajouter les panneaux
        self.basic_info_panel = BasicInfoPanel()
        form_layout.addWidget(self.basic_info_panel)
        
        # Panneau des règles
        self.methods_panel = MethodsPanel()
        form_layout.addWidget(self.methods_panel)
        
        self.operators_control_panel = OperatorsControlPanel()
        form_layout.addWidget(self.operators_control_panel)
        
        self.options_panel = OptionsPanel()
        form_layout.addWidget(self.options_panel)
        
        self.patterns_panel = PatternsPanel()
        form_layout.addWidget(self.patterns_panel)
        
        self.domain_checks_panel = DomainChecksPanel()
        form_layout.addWidget(self.domain_checks_panel)
        
        self.math_functions_panel = MathFunctionsPanel()
        form_layout.addWidget(self.math_functions_panel)
        
        self.exceptions_panel = ExceptionsPanel()
        form_layout.addWidget(self.exceptions_panel)
        
        self.grading_criteria_panel = GradingCriteriaPanel()
        form_layout.addWidget(self.grading_criteria_panel)
        
        self.test_inputs_panel = TestInputsPanel()
        form_layout.addWidget(self.test_inputs_panel)

        # Bouton de sauvegarde
        self.save_button = QPushButton("Enregistrer")
        self.save_button.clicked.connect(self.save_config)
        form_layout.addWidget(self.save_button)
        
        # Configurer le scroll area
        scroll_area.setWidget(form_container)
        main_layout.addWidget(scroll_area)
        
        self.setLayout(main_layout)
        self.resize(800, 600)  # Taille initiale
        self.clear()
    
    def clear(self):
        """Effacer le formulaire."""
        self.current_config = None
        
        # Effacer tous les panneaux
        self.basic_info_panel.load_data(None)
        self.methods_panel.load_data(None)
        self.operators_control_panel.load_data(None)
        self.options_panel.load_data(None)
        self.patterns_panel.load_data(None)
        self.domain_checks_panel.load_data(None)
        self.math_functions_panel.load_data(None)
        self.exceptions_panel.load_data(None)
        self.grading_criteria_panel.load_data(None)
        self.test_inputs_panel.load_data(None)
        
        self.save_button.setEnabled(False)
    
    def load_config(self, config):
        """Charger une configuration dans le formulaire."""
        self.current_config = config
        
        # Charger les données dans les panneaux
        self.basic_info_panel.load_data(config)
        self.methods_panel.load_data(config)
        self.operators_control_panel.load_data(config)
        self.options_panel.load_data(config)
        self.patterns_panel.load_data(config)
        self.domain_checks_panel.load_data(config)
        self.math_functions_panel.load_data(config)
        self.exceptions_panel.load_data(config)
        self.grading_criteria_panel.load_data(config)
        self.test_inputs_panel.load_data(config)
        
        self.save_button.setEnabled(True)
    
    def save_config(self):
        """Sauvegarder la configuration."""
        if not self.current_config:
            return
        
        # Mettre à jour les données depuis les panneaux
        self.basic_info_panel.save_data(self.current_config)
        self.methods_panel.save_data(self.current_config)
        self.operators_control_panel.save_data(self.current_config)
        self.options_panel.save_data(self.current_config)
        self.patterns_panel.save_data(self.current_config)
        self.domain_checks_panel.save_data(self.current_config)
        self.math_functions_panel.save_data(self.current_config)
        self.exceptions_panel.save_data(self.current_config)
        self.grading_criteria_panel.save_data(self.current_config)
        self.test_inputs_panel.save_data(self.current_config)
        
        # Sauvegarde de la configuration
        if self.config_loader.save_exercise_config(self.current_config):
            QMessageBox.information(self, "Sauvegarde", 
                                  f"Configuration '{self.current_config.id}' sauvegardée avec succès.")
        else:
            QMessageBox.warning(self, "Erreur", 
                              f"Erreur lors de la sauvegarde de la configuration '{self.current_config.id}'.") 