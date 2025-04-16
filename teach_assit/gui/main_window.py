import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QStatusBar, QMessageBox, 
                             QSplitter, QProgressDialog, QApplication, QTabWidget,
                             QComboBox)
from PyQt5.QtCore import Qt, QTimer

from teach_assit.gui.file_selector import FileSelector
from teach_assit.gui.results_display import SubmissionTreeWidget
from teach_assit.gui.config_editor import ConfigEditorWidget
from teach_assit.utils.file_utils import SubmissionManager
from teach_assit.core.analysis.config_loader import ConfigLoader


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application TeachAssit."""
    
    def __init__(self):
        super().__init__()
        self.submission_manager = SubmissionManager()
        self.config_loader = ConfigLoader(os.getcwd())
        self.init_ui()
        
    def init_ui(self):
        """Initialiser l'interface utilisateur de la fenêtre principale."""
        # Configuration de la fenêtre
        self.setWindowTitle("TeachAssit - Évaluation des Devoirs Java")
        self.setGeometry(100, 100, 1000, 700)
        
        # Widget central avec onglets
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # Onglet principal : extraction et analyse
        self.main_tab = QWidget()
        main_layout = QVBoxLayout(self.main_tab)
        
        # Titre de l'application
        title_label = QLabel("TeachAssit - Analyse des Soumissions Java")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # Sélecteur d'évaluation
        assessment_layout = QHBoxLayout()
        assessment_layout.addWidget(QLabel("Sélectionner une évaluation :"))
        
        self.assessment_combo = QComboBox()
        self.assessment_combo.currentIndexChanged.connect(self.on_assessment_selected)
        assessment_layout.addWidget(self.assessment_combo)
        
        self.reload_assessments_button = QPushButton("Recharger")
        self.reload_assessments_button.clicked.connect(self.load_assessments)
        assessment_layout.addWidget(self.reload_assessments_button)
        
        main_layout.addLayout(assessment_layout)
        
        # Description
        self.description_label = QLabel("Sélectionnez un dossier contenant les fichiers ZIP des soumissions.")
        self.description_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.description_label)
        
        # Splitter pour diviser la partie sélection de fichiers et résultats
        splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(splitter)
        
        # Partie supérieure : sélection de fichiers
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        
        self.file_selector = FileSelector()
        self.file_selector.folder_selected.connect(self.on_folder_selected)
        top_layout.addWidget(self.file_selector)
        
        # Boutons d'action
        button_layout = QHBoxLayout()
        
        self.extract_button = QPushButton("Extraire les fichiers ZIP")
        self.extract_button.setEnabled(False)
        self.extract_button.clicked.connect(self.extract_zip_files)
        button_layout.addWidget(self.extract_button)
        
        self.analyze_button = QPushButton("Analyser les soumissions")
        self.analyze_button.setEnabled(False)
        button_layout.addWidget(self.analyze_button)
        
        top_layout.addLayout(button_layout)
        
        splitter.addWidget(top_widget)
        
        # Partie inférieure : résultats d'extraction
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        
        self.results_widget = SubmissionTreeWidget()
        bottom_layout.addWidget(self.results_widget)
        
        splitter.addWidget(bottom_widget)
        
        # Définir les tailles relatives du splitter (30% en haut, 70% en bas)
        splitter.setSizes([300, 700])
        
        # Ajouter l'onglet principal
        self.tab_widget.addTab(self.main_tab, "Extraction et Analyse")
        
        # Onglet de configuration
        self.config_editor = ConfigEditorWidget()
        self.tab_widget.addTab(self.config_editor, "Configuration")
        
        # Barre de statut
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Prêt")
        
        # Charger les évaluations disponibles
        self.load_assessments()
    
    def load_assessments(self):
        """Charger les évaluations disponibles."""
        self.config_loader.load_all_configs()
        
        self.assessment_combo.clear()
        self.assessment_combo.addItem("Sélectionner une évaluation...", None)
        
        for assessment_id, config in self.config_loader.get_all_assessment_configs().items():
            self.assessment_combo.addItem(f"{config.name} ({assessment_id})", assessment_id)
        
        self.statusBar.showMessage(f"{len(self.config_loader.get_all_assessment_configs())} évaluation(s) chargée(s)")
    
    def on_assessment_selected(self, index):
        """Appelé quand une évaluation est sélectionnée dans le combo."""
        assessment_id = self.assessment_combo.currentData()
        
        if not assessment_id:
            self.description_label.setText("Sélectionnez un dossier contenant les fichiers ZIP des soumissions.")
            self.analyze_button.setEnabled(False)
            return
        
        assessment = self.config_loader.get_assessment_config(assessment_id)
        if assessment:
            exercises = [f"{ex['exerciseId']} ({self.config_loader.get_exercise_config(ex['exerciseId']).name})" 
                        for ex in assessment.exercises 
                        if self.config_loader.get_exercise_config(ex['exerciseId'])]
            
            exercises_str = ", ".join(exercises)
            self.description_label.setText(f"Évaluation : {assessment.name}\nExercices : {exercises_str}")
            
            # Activer le bouton d'analyse seulement si on a des soumissions extraites
            has_submissions = len(self.submission_manager.get_student_folders()) > 0
            self.analyze_button.setEnabled(has_submissions)
    
    def on_folder_selected(self, folder_path):
        """Appelé lorsqu'un dossier est sélectionné."""
        self.submission_manager.set_base_directory(folder_path)
        zip_files = self.submission_manager.list_zip_files()
        
        self.extract_button.setEnabled(len(zip_files) > 0)
        self.statusBar.showMessage(f"Dossier sélectionné : {folder_path} - {len(zip_files)} fichier(s) ZIP trouvé(s)")
    
    def extract_zip_files(self):
        """Extraire les fichiers ZIP avec gestion de la progression."""
        zip_files = self.submission_manager.list_zip_files()
        if not zip_files:
            QMessageBox.warning(self, "Aucun fichier ZIP", 
                               "Aucun fichier ZIP n'a été trouvé dans le dossier sélectionné.")
            return
        
        # Créer une boîte de dialogue de progression
        progress = QProgressDialog("Extraction des fichiers ZIP...", "Annuler", 0, len(zip_files), self)
        progress.setWindowTitle("Extraction en cours")
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        
        # Dictionnaire pour stocker les résultats
        extraction_results = {}
        
        # Extraire chaque fichier ZIP individuellement
        for i, zip_file in enumerate(zip_files):
            if progress.wasCanceled():
                break
                
            progress.setValue(i)
            progress.setLabelText(f"Extraction de {zip_file}...")
            
            # Mise à jour de l'interface
            QApplication.processEvents()
            
            # Extraction du fichier
            success, message = self.submission_manager.extract_zip_file(zip_file)
            extraction_results[zip_file] = (success, message)
            
            # Pause courte pour donner le temps à l'interface de se mettre à jour
            QTimer.singleShot(100, lambda: None)
        
        # Fermer la boîte de dialogue de progression
        progress.setValue(len(zip_files))
        
        # Mettre à jour l'arborescence des résultats
        student_folders = self.submission_manager.get_student_folders()
        self.results_widget.update_tree(student_folders, extraction_results)
        
        # Afficher un résumé dans la barre d'état
        success_count = sum(1 for result in extraction_results.values() if result[0])
        self.statusBar.showMessage(f"Extraction terminée : {success_count}/{len(extraction_results)} fichier(s) extrait(s) avec succès")
        
        # Afficher un message récapitulatif
        QMessageBox.information(self, "Extraction terminée", 
                              f"{success_count} fichier(s) sur {len(extraction_results)} ont été extraits avec succès.")
        
        # Activer le bouton d'analyse si une évaluation est sélectionnée
        assessment_id = self.assessment_combo.currentData()
        if assessment_id:
            self.analyze_button.setEnabled(True)
    
    def closeEvent(self, event):
        """Nettoyer les ressources avant de fermer l'application."""
        reply = QMessageBox.question(self, "Confirmation", 
                                    "Voulez-vous supprimer les fichiers extraits avant de quitter ?",
                                     QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        
        if reply == QMessageBox.Cancel:
            event.ignore()
            return
            
        if reply == QMessageBox.Yes:
            success, message = self.submission_manager.clean_extraction_directory()
            if not success:
                QMessageBox.warning(self, "Nettoyage", message)
        
        event.accept() 