from PyQt5.QtWidgets import (QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QListWidget, QListWidgetItem, 
                             QMessageBox, QScrollArea, QDialog, QComboBox, QInputDialog,
                             QFrame, QToolButton)
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QIcon, QColor, QPalette, QFont
import os

from teach_assit.core.analysis.config_loader import ConfigLoader
from teach_assit.gui.config.exercise_form import ExerciseConfigForm
from teach_assit.gui.config.assessment_form import AssessmentConfigForm


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
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Onglets pour les exercices et les évaluations avec style moderne
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: white;
            }
            QTabBar::tab {
                padding: 12px 20px;
                margin-right: 5px;
                border: none;
                background: #f1f2f6;
                color: #2c3e50;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #4a69bd;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background: #dcdde1;
            }
        """)
        
        self.exercise_tab = self.create_exercise_tab()
        self.assessment_tab = self.create_assessment_tab()
        
        self.tab_widget.addTab(self.exercise_tab, QIcon("icons/book.svg"), "Exercices")
        self.tab_widget.addTab(self.assessment_tab, QIcon("icons/clipboard.svg"), "Évaluations")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
    
    def create_exercise_tab(self):
        """Créer l'onglet pour les exercices."""
        tab = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Panneau de gauche : liste des exercices
        left_panel = QFrame()
        left_panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 2px solid #dcdde1;
            }
        """)
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(10)
        
        # En-tête avec icône
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 10)
        
        icon_label = QLabel()
        icon_label.setPixmap(QIcon("icons/book-open.svg").pixmap(24, 24))
        header_layout.addWidget(icon_label)
        
        title_label = QLabel("Exercices disponibles")
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        left_layout.addWidget(header)
        
        # Liste des exercices avec style
        self.exercise_list = QListWidget()
        self.exercise_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #dcdde1;
                border-radius: 6px;
                background-color: white;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f1f2f6;
            }
            QListWidget::item:selected {
                background-color: #f1f2f6;
                color: #2c3e50;
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
            }
        """)
        self.exercise_list.setMinimumWidth(300)
        self.exercise_list.currentItemChanged.connect(self.on_exercise_selected)
        self.exercise_list.setAlternatingRowColors(True)
        left_layout.addWidget(self.exercise_list)
        
        # Boutons d'action
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.add_exercise_button = QPushButton("Nouveau")
        self.add_exercise_button.setIcon(QIcon("icons/plus-circle.svg"))
        self.add_exercise_button.clicked.connect(self.on_add_exercise)
        button_layout.addWidget(self.add_exercise_button)
        
        self.delete_exercise_button = QPushButton("Supprimer")
        self.delete_exercise_button.setIcon(QIcon("icons/trash-2.svg"))
        self.delete_exercise_button.clicked.connect(self.on_delete_exercise)
        self.delete_exercise_button.setEnabled(False)
        button_layout.addWidget(self.delete_exercise_button)
        
        left_layout.addLayout(button_layout)
        left_panel.setLayout(left_layout)
        
        # Panneau de droite : formulaire d'édition
        right_panel = QScrollArea()
        right_panel.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f2f6;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #dcdde1;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        right_panel.setWidgetResizable(True)
        
        self.exercise_form = ExerciseConfigForm()
        right_panel.setWidget(self.exercise_form)
        
        # Ajout des panneaux au layout principal
        layout.addWidget(left_panel)
        layout.addWidget(right_panel, 1)
        
        tab.setLayout(layout)
        return tab
    
    def create_assessment_tab(self):
        """Créer l'onglet pour les évaluations."""
        tab = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Panneau de gauche : liste des évaluations
        left_panel = QFrame()
        left_panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 2px solid #dcdde1;
            }
        """)
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(10)
        
        # En-tête avec icône
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 10)
        
        icon_label = QLabel()
        icon_label.setPixmap(QIcon("icons/clipboard.svg").pixmap(24, 24))
        header_layout.addWidget(icon_label)
        
        title_label = QLabel("Évaluations disponibles")
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        left_layout.addWidget(header)
        
        # Liste des évaluations avec style
        self.assessment_list = QListWidget()
        self.assessment_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #dcdde1;
                border-radius: 6px;
                background-color: white;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f1f2f6;
            }
            QListWidget::item:selected {
                background-color: #f1f2f6;
                color: #2c3e50;
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
            }
        """)
        self.assessment_list.setMinimumWidth(300)
        self.assessment_list.currentItemChanged.connect(self.on_assessment_selected)
        self.assessment_list.setAlternatingRowColors(True)
        left_layout.addWidget(self.assessment_list)
        
        # Boutons d'action
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.add_assessment_button = QPushButton("Nouveau")
        self.add_assessment_button.setIcon(QIcon("icons/plus-circle.svg"))
        self.add_assessment_button.clicked.connect(self.on_add_assessment)
        button_layout.addWidget(self.add_assessment_button)
        
        self.delete_assessment_button = QPushButton("Supprimer")
        self.delete_assessment_button.setIcon(QIcon("icons/trash-2.svg"))
        self.delete_assessment_button.clicked.connect(self.on_delete_assessment)
        self.delete_assessment_button.setEnabled(False)
        button_layout.addWidget(self.delete_assessment_button)
        
        self.save_button = QPushButton("Sauvegarder tout")
        self.save_button.setIcon(QIcon("icons/save.svg"))
        self.save_button.clicked.connect(self.on_save_all)
        button_layout.addWidget(self.save_button)
        
        left_layout.addLayout(button_layout)
        left_panel.setLayout(left_layout)
        
        # Panneau de droite : formulaire d'édition
        right_panel = QScrollArea()
        right_panel.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f2f6;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #dcdde1;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        right_panel.setWidgetResizable(True)
        
        self.assessment_form = AssessmentConfigForm(self.config_loader)
        right_panel.setWidget(self.assessment_form)
        
        # Ajout des panneaux au layout principal
        layout.addWidget(left_panel)
        layout.addWidget(right_panel, 1)
        
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
        # Demander un ID pour le nouvel exercice
        exercise_id, ok = QInputDialog.getText(
            self, "Nouvel exercice", 
            "Entrez l'ID de l'exercice (ex: 01-variables):"
        )
        
        if not ok or not exercise_id:
            return
        
        # Vérifier si l'ID existe déjà
        if self.config_loader.get_exercise_config(exercise_id):
            QMessageBox.warning(
                self, "ID déjà utilisé", 
                f"Un exercice avec l'ID '{exercise_id}' existe déjà."
            )
            return
        
        # Créer une nouvelle configuration d'exercice
        config = self.config_loader.create_empty_exercise_config(exercise_id)
        
        # Mettre à jour l'interface
        item = QListWidgetItem(f"{config.name} ({exercise_id})")
        item.setData(Qt.UserRole, exercise_id)
        self.exercise_list.addItem(item)
        self.exercise_list.setCurrentItem(item)
        
        # Recharger la liste des exercices dans le formulaire d'évaluation
        self.assessment_form.update_exercise_list()
    
    def on_delete_exercise(self):
        """Supprimer l'exercice sélectionné."""
        item = self.exercise_list.currentItem()
        if not item:
            return
        
        exercise_id = item.data(Qt.UserRole)
        
        # Demander confirmation
        reply = QMessageBox.question(
            self, "Confirmer la suppression", 
            f"Êtes-vous sûr de vouloir supprimer l'exercice '{exercise_id}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Supprimer l'exercice
            self.config_loader.delete_exercise_config(exercise_id)
            
            # Mettre à jour l'interface
            row = self.exercise_list.row(item)
            self.exercise_list.takeItem(row)
            
            # Effacer le formulaire
            self.exercise_form.clear()
            
            # Recharger la liste des exercices dans le formulaire d'évaluation
            self.assessment_form.update_exercise_list()
    
    def on_add_assessment(self):
        """Ajouter une nouvelle évaluation."""
        # Demander un ID pour la nouvelle évaluation
        assessment_id, ok = QInputDialog.getText(
            self, "Nouvelle évaluation", 
            "Entrez l'ID de l'évaluation (ex: exam-s1):"
        )
        
        if not ok or not assessment_id:
            return
        
        # Vérifier si l'ID existe déjà
        if self.config_loader.get_assessment_config(assessment_id):
            QMessageBox.warning(
                self, "ID déjà utilisé", 
                f"Une évaluation avec l'ID '{assessment_id}' existe déjà."
            )
            return
        
        # Créer une nouvelle configuration d'évaluation
        config = self.config_loader.create_empty_assessment_config(assessment_id)
        
        # Mettre à jour l'interface
        item = QListWidgetItem(f"{config.name} ({assessment_id})")
        item.setData(Qt.UserRole, assessment_id)
        self.assessment_list.addItem(item)
        self.assessment_list.setCurrentItem(item)
    
    def on_delete_assessment(self):
        """Supprimer l'évaluation sélectionnée."""
        item = self.assessment_list.currentItem()
        if not item:
            return
        
        assessment_id = item.data(Qt.UserRole)
        
        # Demander confirmation
        reply = QMessageBox.question(
            self, "Confirmer la suppression", 
            f"Êtes-vous sûr de vouloir supprimer l'évaluation '{assessment_id}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Supprimer l'évaluation
            self.config_loader.delete_assessment_config(assessment_id)
            
            # Mettre à jour l'interface
            row = self.assessment_list.row(item)
            self.assessment_list.takeItem(row)
            
            # Effacer le formulaire
            self.assessment_form.clear()
    
    def on_save_all(self):
        """Sauvegarder toutes les configurations ouvertes explicitement."""
        # Sauvegarder l'exercice en cours
        if self.exercise_form.current_config:
            self.exercise_form.save_config()
        
        # Sauvegarder l'évaluation en cours
        if self.assessment_form.current_config:
            self.assessment_form.save_config()
        
        QMessageBox.information(self, "Sauvegarde", 
                             f"Toutes les configurations ont été sauvegardées.\n\nDossier de sauvegarde: {os.path.join(os.getcwd(), 'assessments')}")
    
    def save_all_configs(self):
        """Sauvegarde toutes les configurations ouvertes à la fermeture."""
        # Sauvegarder l'exercice en cours
        if self.exercise_form.current_config:
            self.exercise_form.save_config()
        
        # Sauvegarder l'évaluation en cours
        if self.assessment_form.current_config:
            self.assessment_form.save_config() 