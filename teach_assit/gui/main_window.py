import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QStatusBar, QMessageBox, 
                             QSplitter, QProgressDialog, QApplication, QTabWidget,
                             QComboBox, QToolBar, QToolButton, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, QTimer, QSize, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QIcon

from teach_assit.gui.results_display import SubmissionTreeWidget
from teach_assit.gui.config_editor import ConfigEditorWidget
from teach_assit.gui.dashboard_widget import DashboardWidget
from teach_assit.gui.results_widget import ResultsWidget
from teach_assit.gui.about_widget import AboutWidget
from teach_assit.gui.feedback import FeedbackWidget
from teach_assit.gui.db_file_manager import DatabaseFileManager
from teach_assit.utils.file_utils import SubmissionManager
from teach_assit.core.analysis.config_loader import ConfigLoader
from teach_assit.core.analysis.static_analyzer import StaticAnalyzer
from teach_assit.gui.styles import MAIN_STYLE, TOOLBAR_STYLE, MENU_STYLE, SIDEBAR_STYLE


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application TeachAssit."""
    
    def __init__(self):
        super().__init__()
        self.submission_manager = SubmissionManager()
        self.config_loader = ConfigLoader(os.getcwd())
        self.animations = []  # Pour stocker les animations en cours
        self.sidebar_expanded = False  # État initial de la barre latérale
        self.init_ui()
        
    def init_ui(self):
        """Initialiser l'interface utilisateur de la fenêtre principale."""
        # Configuration de la fenêtre
        self.setWindowTitle("TeachAssit - Évaluation des Devoirs Java")
        self.setGeometry(100, 100, 1400, 900)
        
        # Appliquer les styles
        self.setStyleSheet(MAIN_STYLE + TOOLBAR_STYLE + MENU_STYLE)
        
        # Widget central principal
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Barre de navigation latérale
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setStyleSheet(SIDEBAR_STYLE)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Logo et titre
        logo_label = QLabel("TeachAssit")
        logo_label.setObjectName("logo")
        sidebar_layout.addWidget(logo_label)
        
        # Bouton pour réduire/étendre la barre latérale
        self.toggle_button = QPushButton()
        self.toggle_button.setObjectName("toggle-button")
        self.toggle_button.setIcon(QIcon("icons/chevrons-left.svg"))
        self.toggle_button.setIconSize(QSize(24, 24))
        self.toggle_button.clicked.connect(self.toggle_sidebar)
        sidebar_layout.addWidget(self.toggle_button)
        
        # Boutons de navigation
        self.nav_dashboard = QPushButton("  Tableau de bord")
        self.nav_dashboard.setIcon(QIcon("icons/home.svg"))
        self.nav_dashboard.setIconSize(QSize(24, 24))
        self.nav_dashboard.setCheckable(True)
        self.nav_dashboard.setChecked(True)
        self.nav_dashboard.clicked.connect(lambda: self.switch_page(0))
        
        self.nav_files = QPushButton("  Fichiers")
        self.nav_files.setIcon(QIcon("icons/file-text.svg"))
        self.nav_files.setIconSize(QSize(24, 24))
        self.nav_files.setCheckable(True)
        self.nav_files.clicked.connect(lambda: self.switch_page(1))
        
        self.nav_analyze = QPushButton("  Analyse")
        self.nav_analyze.setIcon(QIcon("icons/activity.svg"))
        self.nav_analyze.setIconSize(QSize(24, 24))
        self.nav_analyze.setCheckable(True)
        self.nav_analyze.clicked.connect(lambda: self.switch_page(2))
        
        self.nav_results = QPushButton("  Résultats")
        self.nav_results.setIcon(QIcon("icons/bar-chart-2.svg"))
        self.nav_results.setIconSize(QSize(24, 24))
        self.nav_results.setCheckable(True)
        self.nav_results.clicked.connect(lambda: self.switch_page(3))
        
        self.nav_feedback = QPushButton("  Notes & Feedback")
        self.nav_feedback.setIcon(QIcon("icons/message-circle.svg"))
        self.nav_feedback.setIconSize(QSize(24, 24))
        self.nav_feedback.setCheckable(True)
        self.nav_feedback.clicked.connect(lambda: self.switch_page(4))
        
        self.nav_config = QPushButton("  Configuration")
        self.nav_config.setIcon(QIcon("icons/settings.svg"))
        self.nav_config.setIconSize(QSize(24, 24))
        self.nav_config.setCheckable(True)
        self.nav_config.clicked.connect(lambda: self.switch_page(5))
        
        self.nav_about = QPushButton("  À propos")
        self.nav_about.setIcon(QIcon("icons/info.svg"))
        self.nav_about.setIconSize(QSize(20, 20))
        self.nav_about.setObjectName("about-button")
        self.nav_about.setCheckable(True)
        self.nav_about.clicked.connect(lambda: self.switch_page(6))
        
        sidebar_layout.addWidget(self.nav_dashboard)
        sidebar_layout.addWidget(self.nav_files)
        sidebar_layout.addWidget(self.nav_analyze)
        sidebar_layout.addWidget(self.nav_results)
        sidebar_layout.addWidget(self.nav_feedback)
        sidebar_layout.addWidget(self.nav_config)
        sidebar_layout.addWidget(self.nav_about)
        sidebar_layout.addStretch()
        
        # Version et bouton About en bas de la barre latérale
        version_label = QLabel("Version 2.1.0")
        version_label.setObjectName("version")
        sidebar_layout.addWidget(version_label)
        
        # Ajouter la barre latérale au layout principal
        main_layout.addWidget(self.sidebar)
        
        # Contenu principal
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Widget central avec onglets (mais sans les tabs visibles)
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.tabBar().hide()
        content_layout.addWidget(self.tab_widget)
        
        # Onglet Tableau de bord
        self.dashboard_tab = DashboardWidget()
        self.tab_widget.addTab(self.dashboard_tab, "Tableau de bord")
        
        # Onglet Fichiers (remplace l'onglet d'extraction)
        self.files_tab = DatabaseFileManager(submission_manager=self.submission_manager)
        self.tab_widget.addTab(self.files_tab, "Fichiers")
        
        # Connecter le signal de sélection de dossier aux fonctions existantes
        self.files_tab.folder_selected.connect(self.on_folder_selected)
        
        # Onglet d'analyse
        self.analyze_tab = QWidget()
        self.setup_analyze_tab()
        self.tab_widget.addTab(self.analyze_tab, "Analyse")
        
        # Onglet de résultats
        self.results_tab = ResultsWidget()
        self.tab_widget.addTab(self.results_tab, "Résultats")
        
        # Onglet Notes & Feedback
        self.feedback_tab = FeedbackWidget()
        self.tab_widget.addTab(self.feedback_tab, "Notes & Feedback")
        
        # Connecter le widget de feedback au widget de résultats
        self.feedback_tab.set_results_widget(self.results_tab)
        
        # Onglet de configuration
        self.config_editor = ConfigEditorWidget()
        self.tab_widget.addTab(self.config_editor, "Configuration")
        
        # Onglet À propos
        self.about_tab = AboutWidget()
        self.tab_widget.addTab(self.about_tab, "À propos")
        
        # Ajouter le contenu au layout principal
        main_layout.addWidget(content_widget)
        
        self.setCentralWidget(central_widget)
        
        # Barre de statut avec style amélioré
        self.statusBar = QStatusBar()
        self.statusBar.setStyleSheet("""
            QStatusBar {
                background-color: #f8f9fa;
                border-top: 1px solid #dcdde1;
            }
        """)
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Prêt")
        
        # Initialiser la barre latérale en mode réduit
        self.sidebar.setProperty("class", "collapsed")
        self.sidebar.style().unpolish(self.sidebar)
        self.sidebar.style().polish(self.sidebar)
        
        # Charger les évaluations disponibles
        self.load_assessments()
    
    def toggle_sidebar(self):
        """Basculer l'état de la barre latérale entre réduit et étendu."""
        self.sidebar_expanded = not self.sidebar_expanded
        
        # Créer l'animation
        animation = QPropertyAnimation(self.sidebar, b"minimumWidth")
        animation.setDuration(300)
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        if self.sidebar_expanded:
            animation.setStartValue(80)
            animation.setEndValue(250)
            self.toggle_button.setIcon(QIcon("icons/chevrons-left.svg"))
            self.sidebar.setProperty("class", "expanded")
        else:
            animation.setStartValue(250)
            animation.setEndValue(80)
            self.toggle_button.setIcon(QIcon("icons/chevrons-right.svg"))
            self.sidebar.setProperty("class", "collapsed")
        
        # Mettre à jour le style
        self.sidebar.style().unpolish(self.sidebar)
        self.sidebar.style().polish(self.sidebar)
        
        animation.start()
        self.animations.append(animation)  # Garder une référence à l'animation
    
    def setup_extract_tab(self):
        """
        Cette fonction est conservée pour référence mais n'est plus utilisée.
        L'extraction est maintenant intégrée dans l'onglet Fichiers.
        """
        pass
    
    def setup_analyze_tab(self):
        """Configurer l'onglet d'analyse."""
        layout = QVBoxLayout(self.analyze_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # En-tête
        title_label = QLabel("Analyse des Soumissions")
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
        """)
        layout.addWidget(title_label)
        
        # Sélecteur d'évaluation
        assessment_widget = QWidget()
        assessment_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        assessment_layout = QHBoxLayout(assessment_widget)
        assessment_layout.setContentsMargins(15, 15, 15, 15)
        
        assessment_label = QLabel("Sélectionner une évaluation :")
        assessment_label.setStyleSheet("font-weight: bold;")
        assessment_layout.addWidget(assessment_label)
        
        self.assessment_combo = QComboBox()
        self.assessment_combo.setMinimumWidth(400)
        self.assessment_combo.currentIndexChanged.connect(self.on_assessment_selected)
        assessment_layout.addWidget(self.assessment_combo)
        
        self.reload_assessments_button = QPushButton()
        self.reload_assessments_button.setIcon(QIcon("icons/refresh-cw.svg"))
        self.reload_assessments_button.setToolTip("Recharger les évaluations")
        self.reload_assessments_button.clicked.connect(self.load_assessments)
        self.reload_assessments_button.setFixedSize(50, 50)
        assessment_layout.addWidget(self.reload_assessments_button)
        
        layout.addWidget(assessment_widget)
        
        # Description
        self.description_label = QLabel("Sélectionnez une évaluation pour commencer l'analyse.")
        self.description_label.setStyleSheet("""
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            color: #2c3e50;
            font-size: 16px;
        """)
        self.description_label.setWordWrap(True)
        self.description_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.description_label)
        
        # Créer un widget qui prendra toute la place disponible
        main_content = QWidget()
        main_content_layout = QVBoxLayout(main_content)
        main_content_layout.setContentsMargins(0, 0, 0, 0)
        main_content_layout.setSpacing(20)
        
        # Tableau des soumissions extraites - maintenant dans le main_content
        submissions_widget = QWidget()
        submissions_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
                border: 2px solid #dcdde1;
                padding: 15px;
            }
        """)
        submissions_layout = QVBoxLayout(submissions_widget)
        submissions_layout.setContentsMargins(15, 15, 15, 15)
        submissions_layout.setSpacing(15)
        
        # En-tête du tableau
        submissions_header = QWidget()
        header_layout = QHBoxLayout(submissions_header)
        header_layout.setContentsMargins(0, 0, 0, 15)
        
        icon_label = QLabel()
        icon_label.setPixmap(QIcon("icons/users.svg").pixmap(32, 32))
        header_layout.addWidget(icon_label)
        
        header_label = QLabel("Soumissions disponibles pour analyse")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(header_label)
        
        # Bouton de rafraîchissement pour les soumissions
        refresh_button = QPushButton()
        refresh_button.setIcon(QIcon("icons/refresh-cw.svg"))
        refresh_button.setIconSize(QSize(20, 20))
        refresh_button.setToolTip("Rafraîchir la liste des soumissions")
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #dcdde1;
                border-radius: 15px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        refresh_button.setFixedSize(30, 30)
        refresh_button.clicked.connect(self.update_submission_table)
        header_layout.addWidget(refresh_button)
        
        header_layout.addStretch()
        
        submissions_layout.addWidget(submissions_header)
        
        # Tableau des soumissions
        self.submission_table = QTableWidget()
        self.submission_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #dcdde1;
                border-radius: 6px;
                alternate-background-color: #f9f9f9;
                gridline-color: #ecf0f1;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QTableWidget::item:selected {
                background-color: #e6f2ff;
                color: #2c3e50;
            }
            QHeaderView::section {
                background-color: #f1f1f1;
                padding: 15px;
                border: none;
                border-bottom: 2px solid #dcdde1;
                border-right: 1px solid #dcdde1;
                color: #2c3e50;
                font-weight: bold;
                font-size: 16px;
                text-align: center;
            }
        """)
        self.submission_table.setColumnCount(3)
        self.submission_table.setHorizontalHeaderLabels(["#", "Étudiant", "Fichiers soumis"])
        self.submission_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.submission_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.submission_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.submission_table.setAlternatingRowColors(True)
        self.submission_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.submission_table.setSelectionMode(QTableWidget.SingleSelection)
        self.submission_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.submission_table.setIconSize(QSize(24, 24))
        self.submission_table.verticalHeader().setVisible(False)
        self.submission_table.setShowGrid(True)
        
        # Définir la hauteur de l'en-tête du tableau pour le rendre plus visible
        self.submission_table.horizontalHeader().setFixedHeight(50)
        self.submission_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #e9f2fd;
                color: #2c3e50;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-bottom: 2px solid #3498db;
            }
        """)
        
        # Masquer le tableau initialement (sera affiché quand des soumissions seront disponibles)
        self.submission_table.setHidden(True)
        
        submissions_layout.addWidget(self.submission_table)
        main_content_layout.addWidget(submissions_widget)
        
        # Bouton d'analyse désormais dans le main_content, tout en bas
        analyze_button_container = QWidget()
        analyze_button_layout = QHBoxLayout(analyze_button_container)
        analyze_button_layout.setContentsMargins(0, 10, 0, 0)
        
        self.analyze_button = QPushButton("Analyser les soumissions")
        self.analyze_button.setIcon(QIcon("icons/activity.svg"))
        self.analyze_button.setIconSize(QSize(24, 24))
        self.analyze_button.setEnabled(False)
        self.analyze_button.setMinimumHeight(50)
        self.analyze_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.analyze_button.clicked.connect(self.analyze_submissions)
        analyze_button_layout.addWidget(self.analyze_button)
        
        main_content_layout.addWidget(analyze_button_container)
        
        # Ajouter le main_content au layout principal
        layout.addWidget(main_content, 1)  # Le 1 indique qu'il prendra tout l'espace disponible
    
    def switch_page(self, index):
        """Changer d'onglet et mettre à jour l'apparence du bouton sélectionné."""
        self.tab_widget.setCurrentIndex(index)
        
        # Désélectionner tous les boutons
        for button in [self.nav_dashboard, self.nav_files, self.nav_analyze, 
                     self.nav_results, self.nav_feedback, self.nav_config, self.nav_about]:
            button.setChecked(False)
            button.setStyleSheet("")
        
        # Si on passe à l'onglet d'analyse, mettre à jour le tableau des soumissions
        if index == 2:  # Onglet Analyse
            self.update_submission_table()
        
        # Sélectionner le bouton actif
        if index == 0:
            self.nav_dashboard.setChecked(True)
            self.animate_button(self.nav_dashboard)
        elif index == 1:
            self.nav_files.setChecked(True)
            self.animate_button(self.nav_files)
        elif index == 2:
            self.nav_analyze.setChecked(True)
            self.animate_button(self.nav_analyze)
        elif index == 3:
            self.nav_results.setChecked(True)
            self.animate_button(self.nav_results)
        elif index == 4:
            self.nav_feedback.setChecked(True)
            self.animate_button(self.nav_feedback)
        elif index == 5:
            self.nav_config.setChecked(True)
            self.animate_button(self.nav_config)
        elif index == 6:
            self.nav_about.setChecked(True)
            self.animate_button(self.nav_about)
        
        # Mettre à jour le titre
        self.update_title_for_page(index)
    
    def animate_button(self, button):
        """Ajouter une animation au survol des boutons."""
        animation = QPropertyAnimation(button, b"pos")
        animation.setDuration(100)
        animation.setEasingCurve(QEasingCurve.OutBack)
        self.animations.append(animation)
        return animation
    
    def clean_files(self):
        """Nettoyer les fichiers extraits."""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous supprimer tous les fichiers extraits ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = self.submission_manager.clean_extraction_directory()
            if success:
                self.statusBar.showMessage("Nettoyage effectué avec succès")
                self.results_widget.clear()
                self.analyze_button.setEnabled(False)
            else:
                QMessageBox.warning(self, "Erreur", message)
    
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
            self.description_label.setText("Sélectionnez une évaluation pour voir les soumissions correspondantes.")
            self.analyze_button.setEnabled(False)
            # Vider et masquer le tableau quand aucune évaluation n'est sélectionnée
            self.submission_table.setRowCount(0)
            self.submission_table.setHidden(True)
            return
        
        assessment = self.config_loader.get_assessment_config(assessment_id)
        if assessment:
            exercises = [f"{ex['exerciseId']} ({self.config_loader.get_exercise_config(ex['exerciseId']).name})" 
                        for ex in assessment.exercises 
                        if self.config_loader.get_exercise_config(ex['exerciseId'])]
            
            exercises_str = ", ".join(exercises)
            self.description_label.setText(f"Évaluation : {assessment.name}\nExercices : {exercises_str}")
            
            # Mettre à jour le tableau des soumissions avec le nouveau filtre
            self.update_submission_table()
    
    def on_folder_selected(self, folder_path):
        """Appelé lorsqu'un dossier est sélectionné."""
        self.submission_manager.set_base_directory(folder_path)
        zip_files = self.submission_manager.list_zip_files()
        
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
        
        # Mettre à jour le tableau des soumissions dans l'onglet d'analyse
        self.update_submission_table()
        
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
    
    def show_about_tab(self):
        """Afficher l'onglet À propos."""
        self.switch_page(6)  # L'index de l'onglet À propos
    
    def closeEvent(self, event):
        """Nettoyer les ressources avant de fermer l'application."""
        # Sauvegarder les configurations
        self.config_editor.save_all_configs()
        
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
    
    def update_submission_table(self):
        """Mettre à jour le tableau des soumissions extraites dans l'onglet d'analyse."""
        # Récupérer les dossiers d'étudiants extraits
        student_folders = self.submission_manager.get_student_folders()
        
        # Récupérer l'évaluation sélectionnée
        assessment_id = self.assessment_combo.currentData()
        
        # Si aucune évaluation n'est sélectionnée, vider le tableau et le masquer
        if not assessment_id:
            self.submission_table.setRowCount(0)
            self.submission_table.setHidden(True)
            self.statusBar.showMessage("Veuillez sélectionner une évaluation pour voir les soumissions correspondantes")
            self.analyze_button.setEnabled(False)
            return
        
        # Si aucune soumission n'est disponible, vider le tableau et le masquer
        if not student_folders:
            self.submission_table.setRowCount(0)
            self.submission_table.setHidden(True)
            self.statusBar.showMessage("Aucune soumission disponible")
            self.analyze_button.setEnabled(False)
            return
        
        # Récupérer la configuration de l'évaluation sélectionnée
        assessment = self.config_loader.get_assessment_config(assessment_id)
        if not assessment:
            self.submission_table.setRowCount(0)
            self.submission_table.setHidden(True)
            self.statusBar.showMessage("Configuration de l'évaluation non trouvée")
            self.analyze_button.setEnabled(False)
            return
            
        # Créer un dictionnaire de correspondance entre mots-clés et exercices
        exercise_keywords = {}
        for ex in assessment.exercises:
            ex_id = ex.get('exerciseId', '')
            if ex_id:
                # Extraire des mots-clés de l'ID de l'exercice
                # Par exemple, '02-intervalle' donne 'intervalle'
                if '-' in ex_id:
                    keyword = ex_id.split('-', 1)[1].lower()
                else:
                    keyword = ex_id.lower()
                exercise_keywords[keyword] = ex_id
        
        # Filtrer les fichiers Java par exercice
        filtered_students = {}
        
        for student_name, info in student_folders.items():
            java_files = info.get('java_files', [])
            
            # Filtrer les fichiers par exercice
            filtered_files = []
            
            for java_file in java_files:
                java_file_lower = java_file.lower()
                
                # Vérifier si le fichier correspond à l'un des exercices de l'évaluation
                matches_exercise = False
                
                # Méthode 1: Correspondance directe avec l'ID d'exercice
                for ex in assessment.exercises:
                    ex_id = ex.get('exerciseId', '')
                    if ex_id and ex_id.lower() in java_file_lower:
                        matches_exercise = True
                        break
                
                # Méthode 2: Correspondance avec les mots-clés extraits
                if not matches_exercise:
                    for keyword in exercise_keywords:
                        if keyword in java_file_lower:
                            matches_exercise = True
                            break
                        
                        # Vérifier aussi le nom de base du fichier
                        base_name = os.path.splitext(os.path.basename(java_file_lower))[0]
                        if keyword in base_name:
                            matches_exercise = True
                            break
                
                # Méthode 3: Cas spéciaux
                if not matches_exercise:
                    if "intervalle" in java_file_lower and any("intervalle" in kw for kw in exercise_keywords):
                        matches_exercise = True
                    elif ("fonction" in java_file_lower or "log" in java_file_lower) and any(("fonction" in kw or "log" in kw) for kw in exercise_keywords):
                        matches_exercise = True
                
                # Si le fichier correspond à un exercice de l'évaluation, l'ajouter à la liste filtrée
                if matches_exercise:
                    filtered_files.append(java_file)
            
            # Si l'étudiant a des fichiers correspondant aux exercices, l'ajouter à la liste
            if filtered_files:
                filtered_info = info.copy()
                filtered_info['java_files'] = filtered_files
                filtered_students[student_name] = filtered_info
        
        # Si aucune soumission ne correspond à l'évaluation sélectionnée
        if not filtered_students:
            self.submission_table.setRowCount(0)
            self.submission_table.setHidden(True)
            self.statusBar.showMessage(f"Aucune soumission correspondant à l'évaluation {assessment.name}")
            self.analyze_button.setEnabled(False)
            return
        
        # Afficher le tableau
        self.submission_table.setHidden(False)
        
        # Configurer le tableau avec les données
        self.submission_table.setRowCount(len(filtered_students))
        
        # Remplir le tableau avec les données des étudiants et leurs fichiers
        for row, (student_name, info) in enumerate(filtered_students.items()):
            # Numéro de ligne
            num_item = QTableWidgetItem(str(row + 1))
            num_item.setTextAlignment(Qt.AlignCenter)
            font = num_item.font()
            font.setPointSize(14)  # Agrandir encore plus
            font.setBold(True)
            num_item.setFont(font)
            self.submission_table.setItem(row, 0, num_item)
            
            # Nom de l'étudiant avec icône
            student_item = QTableWidgetItem(" " + student_name)
            student_item.setIcon(QIcon("icons/user.svg"))
            font = student_item.font()
            font.setPointSize(14)  # Agrandir encore plus
            font.setBold(True)
            student_item.setFont(font)
            self.submission_table.setItem(row, 1, student_item)
            
            # Conteneur pour les fichiers Java
            files_widget = QWidget()
            files_layout = QVBoxLayout(files_widget)
            files_layout.setContentsMargins(10, 8, 10, 8)
            files_layout.setSpacing(10)
            files_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            
            # Ajouter chaque fichier Java avec son icône
            java_files = info.get('java_files', [])
            if java_files:
                for java_file in java_files:
                    file_container = QWidget()
                    file_container_layout = QHBoxLayout(file_container)
                    file_container_layout.setContentsMargins(0, 0, 0, 0)
                    file_container_layout.setSpacing(12)
                    
                    # Créer un label pour l'icône
                    file_icon = QLabel()
                    file_icon.setPixmap(QIcon("icons/file-text.svg").pixmap(QSize(24, 24)))
                    file_container_layout.addWidget(file_icon)
                    
                    # Créer un label pour le nom du fichier
                    file_path_parts = java_file.split('\\')
                    file_name = file_path_parts[-1] if len(file_path_parts) > 1 else java_file
                    
                    # Construire le chemin complet du fichier pour l'affichage
                    if len(file_path_parts) > 1:
                        display_path = student_name + "\\" + file_name
                    else:
                        display_path = file_name
                    
                    file_label = QLabel(display_path)
                    file_label.setStyleSheet("""
                        color: #e67e22;
                        font-size: 14px;
                        padding: 5px;
                        background-color: #f8f9fa;
                        border-radius: 4px;
                    """)
                    file_container_layout.addWidget(file_label)
                    file_container_layout.addStretch()
                    
                    files_layout.addWidget(file_container)
            else:
                no_files_label = QLabel("Aucun fichier Java")
                no_files_label.setStyleSheet("color: #7f8c8d; font-size: 14px;")
                files_layout.addWidget(no_files_label)
            
            files_layout.addStretch()
            
            # Ajouter le widget de fichiers au tableau
            self.submission_table.setCellWidget(row, 2, files_widget)
        
        # Ajuster la hauteur des lignes en fonction du nombre de fichiers
        for row in range(self.submission_table.rowCount()):
            student_name = list(filtered_students.keys())[row]
            java_files_count = len(filtered_students[student_name].get('java_files', []))
            # Hauteur plus grande pour chaque fichier
            row_height = max(70, 50 + java_files_count * 45)
            self.submission_table.setRowHeight(row, row_height)
        
        # Mettre à jour le statut
        self.analyze_button.setEnabled(len(filtered_students) > 0)
        
        # Afficher un message d'information dans la barre de statut
        self.statusBar.showMessage(f"{len(filtered_students)} soumission(s) correspondant à l'évaluation {assessment.name}")
    
    def analyze_submissions(self):
        """Analyser les soumissions d'étudiants avec l'analyseur statique."""
        # Récupérer l'évaluation sélectionnée
        assessment_id = self.assessment_combo.currentData()
        if not assessment_id:
            QMessageBox.warning(self, "Aucune évaluation", "Veuillez sélectionner une évaluation à analyser.")
            return
        
        # Récupérer la configuration de l'évaluation
        assessment = self.config_loader.get_assessment_config(assessment_id)
        if not assessment:
            QMessageBox.warning(self, "Erreur de configuration", "Configuration d'évaluation non trouvée.")
            return
        
        # Récupérer les dossiers d'étudiants
        all_student_folders = self.submission_manager.get_student_folders()
        if not all_student_folders:
            QMessageBox.warning(self, "Aucune soumission", "Aucune soumission extraite à analyser.")
            return
        
        # Créer un dictionnaire de correspondance entre mots-clés et exercices
        exercise_keywords = {}
        exercise_ids = []
        for ex in assessment.exercises:
            ex_id = ex.get('exerciseId', '')
            if ex_id:
                exercise_ids.append(ex_id)
                # Extraire des mots-clés de l'ID de l'exercice
                if '-' in ex_id:
                    keyword = ex_id.split('-', 1)[1].lower()
                else:
                    keyword = ex_id.lower()
                exercise_keywords[keyword] = ex_id
        
        # DEBUG: Afficher les IDs d'exercices pour cette évaluation
        print(f"\n======= DEBUG: Exercices de l'évaluation {assessment.name} ({assessment_id}) =======")
        print(f"IDs d'exercices: {exercise_ids}")
        print(f"Mots-clés: {list(exercise_keywords.keys())}")
        print("=====================================================================\n")
        
        # Filtrer les étudiants ayant des fichiers correspondant à l'évaluation sélectionnée
        filtered_students = {}
        for student_name, info in all_student_folders.items():
            java_files = info.get('java_files', [])
            
            # Filtrer les fichiers par exercice
            filtered_files = []
            
            for java_file in java_files:
                java_file_lower = java_file.lower()
                
                # Vérifier si le fichier correspond à l'un des exercices de l'évaluation
                matches_exercise = False
                matching_exercise_id = None
                
                # Méthode 1: Correspondance directe avec l'ID d'exercice
                for ex in assessment.exercises:
                    ex_id = ex.get('exerciseId', '')
                    if ex_id and ex_id.lower() in java_file_lower:
                        matches_exercise = True
                        matching_exercise_id = ex_id
                        break
                
                # Méthode 2: Correspondance avec les mots-clés extraits
                if not matches_exercise:
                    for keyword, ex_id in exercise_keywords.items():
                        if keyword in java_file_lower:
                            matches_exercise = True
                            matching_exercise_id = ex_id
                            break
                        
                        # Vérifier aussi le nom de base du fichier
                        base_name = os.path.splitext(os.path.basename(java_file_lower))[0]
                        if keyword in base_name:
                            matches_exercise = True
                            matching_exercise_id = ex_id
                            break
                
                # Méthode 3: Cas spéciaux
                if not matches_exercise:
                    if "intervalle" in java_file_lower and any("intervalle" in kw for kw in exercise_keywords):
                        matches_exercise = True
                        matching_exercise_id = next((ex_id for ex_id in exercise_ids if "intervalle" in ex_id), None)
                    elif ("fonction" in java_file_lower or "log" in java_file_lower) and any(("fonction" in kw or "log" in kw) for kw in exercise_keywords):
                        matches_exercise = True
                        matching_exercise_id = next((ex_id for ex_id in exercise_ids if "fonction" in ex_id or "log" in ex_id), None)
                
                # Si le fichier correspond à un exercice de l'évaluation, l'ajouter à la liste filtrée
                if matches_exercise:
                    # DEBUG: Afficher la correspondance trouvée
                    print(f"Fichier correspondant: {java_file} -> Exercice: {matching_exercise_id}")
                    filtered_files.append(java_file)
                else:
                    print(f"Fichier ignoré (pas de correspondance): {java_file}")
            
            # Si l'étudiant a des fichiers correspondant aux exercices, l'ajouter à la liste
            if filtered_files:
                filtered_info = info.copy()
                filtered_info['java_files'] = filtered_files
                filtered_students[student_name] = filtered_info
        
        if not filtered_students:
            QMessageBox.warning(self, "Aucune soumission correspondante", f"Aucune soumission ne correspond à l'évaluation {assessment.name}.")
            return
        
        # DEBUG: Résumé des étudiants et fichiers filtrés
        print(f"\n======= DEBUG: Résumé des étudiants filtrés pour {assessment.name} =======")
        for student, info in filtered_students.items():
            print(f"Étudiant: {student}, Fichiers: {info['java_files']}")
        print("=====================================================================\n")
        
        # Créer une boîte de dialogue de progression
        progress = QProgressDialog("Analyse des soumissions en cours...", "Annuler", 0, len(filtered_students), self)
        progress.setWindowTitle("Analyse en cours")
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        
        # Créer l'analyseur statique
        analyzer = StaticAnalyzer()
        
        # Dictionnaire pour stocker les résultats d'analyse
        analysis_results = {}
        
        # Préparer les configurations d'exercices pour l'analyse
        exercise_configs = {}
        for ex in assessment.exercises:
            ex_id = ex.get('exerciseId', '')
            config = self.config_loader.get_exercise_config(ex_id)
            if config:
                exercise_configs[ex_id] = config
        
        # Analyser chaque soumission d'étudiant
        student_count = 0
        for student_name, info in filtered_students.items():
            if progress.wasCanceled():
                break
            
            progress.setValue(student_count)
            progress.setLabelText(f"Analyse des soumissions de {student_name}...")
            
            # Mise à jour de l'interface
            QApplication.processEvents()
            
            # Récupérer les fichiers Java de l'étudiant (déjà filtrés)
            java_files = info.get('java_files', [])
            student_dir = info.get('path', '')
            student_results = {}
            
            # Analyser chaque fichier Java
            for java_file in java_files:
                file_path = os.path.join(student_dir, java_file)
                
                # Lire le contenu du fichier
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        code = f.read()
                    
                    # Déterminer l'exercice associé au fichier en utilisant les mots-clés
                    exercise_id = None
                    java_file_lower = java_file.lower()
                    
                    # Méthode 1: Correspondance directe avec l'ID d'exercice
                    for ex in assessment.exercises:
                        ex_id = ex.get('exerciseId', '')
                        if ex_id and ex_id in java_file_lower:
                            exercise_id = ex_id
                            break
                    
                    # Méthode 2: Correspondance avec les mots-clés extraits
                    if not exercise_id:
                        for keyword, ex_id in exercise_keywords.items():
                            if keyword in java_file_lower:
                                exercise_id = ex_id
                                break
                            # Vérifier aussi si le keyword est dans le nom de base du fichier sans extension
                            base_name = os.path.splitext(os.path.basename(java_file_lower))[0]
                            if keyword in base_name:
                                exercise_id = ex_id
                                break
                    
                    # Méthode 3: Correspondance approfondie pour des cas spécifiques
                    if not exercise_id:
                        if "intervalle" in java_file_lower:
                            for ex_id in exercise_keywords.values():
                                if "intervalle" in ex_id:
                                    exercise_id = ex_id
                                    break
                        elif "fonction" in java_file_lower or "log" in java_file_lower:
                            for ex_id in exercise_keywords.values():
                                if "fonction" in ex_id or "log" in ex_id:
                                    exercise_id = ex_id
                                    break
                    
                    # Si aucune correspondance, ignorer ce fichier
                    if not exercise_id:
                        print(f"ERREUR: {java_file} n'a pas d'exercice associé lors de l'analyse!")
                        continue
                    
                    # Obtenir la configuration de l'exercice
                    exercise_config = exercise_configs.get(exercise_id)
                    if not exercise_config:
                        print(f"ERREUR: Configuration introuvable pour l'exercice {exercise_id}")
                        continue  # Ignorer ce fichier si la configuration n'est pas trouvée
                    
                    # Analyser le code
                    result = analyzer.analyze_code(code, exercise_config)
                    
                    # Enrichir les résultats avec l'ID de l'exercice pour faciliter le filtrage ultérieur
                    result['exerciseId'] = exercise_id
                    student_results[java_file] = result
                    
                except Exception as e:
                    student_results[java_file] = {
                        'error': f"Erreur lors de l'analyse: {str(e)}",
                        'exerciseId': exercise_id  # Peut être None si non déterminé
                    }
            
            # Stocker les résultats pour cet étudiant uniquement s'il a des fichiers analysés
            if student_results:
                analysis_results[student_name] = student_results
            student_count += 1
        
        # Fermer la boîte de dialogue de progression
        progress.setValue(len(filtered_students))
        
        if not analysis_results:
            QMessageBox.warning(self, "Aucun résultat", f"Aucun fichier n'a pu être analysé pour l'évaluation {assessment.name}.")
            return
        
        # DEBUG: Vérifier ce qui va être envoyé à results_tab.update_analysis_results
        print(f"\n======= DEBUG: Résultats d'analyse avant envoi à ResultsWidget =======")
        for student, files in analysis_results.items():
            print(f"Étudiant: {student}")
            for file, result in files.items():
                exercise_id = result.get('exerciseId', 'NON SPÉCIFIÉ')
                print(f"  - Fichier: {file}, Exercice: {exercise_id}")
                if 'error' in result:
                    print(f"    Erreur: {result['error']}")
                else:
                    print(f"    Valide: {result.get('is_valid', False)}")
        print("=====================================================================\n")
        
        # Mettre à jour l'interface avec les résultats d'analyse
        self.update_analysis_results(analysis_results)
        
        # Mettre à jour l'onglet des résultats avec uniquement les résultats pertinents pour cette évaluation
        self.results_tab.update_analysis_results(analysis_results, assessment.name, exercise_configs)
        
        # Basculer vers l'onglet des résultats pour afficher les résultats détaillés
        self.switch_page(3)  # L'index de l'onglet Résultats
        
        # Message de confirmation
        self.statusBar.showMessage(f"Analyse terminée pour {len(analysis_results)} soumission(s) correspondant à l'évaluation {assessment.name}")
    
    def update_analysis_results(self, analysis_results):
        """Mettre à jour l'interface avec les résultats d'analyse."""
        print(f"Mise à jour des résultats d'analyse pour {len(analysis_results)} étudiants")
        
        # Pour chaque étudiant, mettre à jour la ligne correspondante dans le tableau
        for row in range(self.submission_table.rowCount()):
            student_item = self.submission_table.item(row, 1)
            if not student_item:
                continue
            
            student_name = student_item.text().strip()
            if student_name.startswith(" "):  # Supprimer l'espace ajouté pour l'icône
                student_name = student_name[1:]
            
            # Récupérer les résultats d'analyse pour cet étudiant
            student_results = analysis_results.get(student_name, {})
            if not student_results:
                print(f"Pas de résultats trouvés pour l'étudiant: {student_name}")
                continue
            else:
                print(f"Résultats trouvés pour {student_name}: {len(student_results)} fichiers")
            
            # Mettre à jour l'affichage des fichiers Java dans la cellule
            files_widget = self.submission_table.cellWidget(row, 2)
            if not files_widget:
                continue
            
            # Parcourir les containers de fichiers dans le widget principal
            for i in range(files_widget.layout().count()):
                file_container_item = files_widget.layout().itemAt(i)
                if not file_container_item or not file_container_item.widget():
                    continue
                
                # Container du fichier (QWidget)
                file_container = file_container_item.widget()
                if not isinstance(file_container, QWidget) or not file_container.layout():
                    continue
                
                # Trouver le QLabel du nom de fichier dans le container
                file_name_label = None
                file_icon_label = None
                
                # Parcourir les éléments du container (icône + nom de fichier)
                for j in range(file_container.layout().count()):
                    widget_item = file_container.layout().itemAt(j)
                    if not widget_item or not widget_item.widget():
                        continue
                    
                    widget = widget_item.widget()
                    if isinstance(widget, QLabel):
                        # Le premier QLabel est l'icône, le second est le nom de fichier
                        if file_icon_label is None:
                            file_icon_label = widget
                        else:
                            file_name_label = widget
                
                # Vérifier si nous avons trouvé le label du fichier
                if file_name_label and file_icon_label:
                    file_text = file_name_label.text().strip()
                    # Extraire juste le nom du fichier s'il contient un chemin
                    if "\\" in file_text:
                        file_text = file_text.split("\\")[-1]
                    
                    print(f"Vérification du fichier: {file_text}")
                    
                    # Vérifier si nous avons des résultats pour ce fichier
                    for file_path, result in student_results.items():
                        base_file_name = os.path.basename(file_path)
                        if base_file_name == file_text or file_path.endswith(file_text):
                            print(f"Correspondance trouvée: {file_path} → {file_text}")
                            
                            icon_name = "check-circle"
                            text_color = "#2ecc71"  # vert
                            tooltip = "Code valide"
                            
                            # Erreur d'analyse
                            if 'error' in result:
                                icon_name = "alert-triangle"
                                text_color = "#e74c3c"  # rouge
                                tooltip = result['error']
                                print(f"Erreur d'analyse: {tooltip}")
                            # Erreur de syntaxe
                            elif result.get('syntax_errors', []):
                                icon_name = "alert-circle"
                                text_color = "#e74c3c"  # rouge
                                errors = [f"Ligne {err['line']}: {err['message']}" for err in result['syntax_errors']]
                                tooltip = "Erreurs de syntaxe:\n" + "\n".join(errors)
                                print(f"Erreurs de syntaxe: {len(result['syntax_errors'])}")
                            # Méthodes manquantes ou incorrectes
                            elif result.get('missing_methods', []):
                                icon_name = "alert-triangle"
                                text_color = "#f39c12"  # orange
                                methods = [f"{m['expected_return']} {m['name']}({', '.join(m['expected_params'])})" 
                                          for m in result['missing_methods']]
                                tooltip = "Méthodes manquantes ou incorrectes:\n" + "\n".join(methods)
                                print(f"Méthodes manquantes: {len(result['missing_methods'])}")
                            else:
                                print("Code valide")
                            
                            # Mettre à jour l'icône
                            file_icon_label.setPixmap(QIcon(f"icons/{icon_name}.svg").pixmap(24, 24))
                            
                            # Mettre à jour le style et le tooltip du label du nom de fichier
                            file_name_label.setStyleSheet(f"color: {text_color}; font-size: 14px; padding: 5px; background-color: #f8f9fa; border-radius: 4px;")
                            file_name_label.setToolTip(tooltip)
                            break
        
        # Ajuster à nouveau la hauteur des lignes pour tenir compte des tooltips
        for row in range(self.submission_table.rowCount()):
            current_height = self.submission_table.rowHeight(row)
            self.submission_table.setRowHeight(row, current_height)
            
        # Message informant l'utilisateur que l'analyse est terminée
        QMessageBox.information(self, "Analyse terminée", 
                               f"L'analyse de {len(analysis_results)} soumissions est terminée.\n"
                               "✅ Vert: Code valide\n"
                               "⚠️ Orange: Méthodes manquantes ou incorrectes\n"
                               "❌ Rouge: Erreurs de syntaxe\n\n"
                               "Survolez les fichiers pour voir les détails.")
    
    def update_title_for_page(self, index):
        """Met à jour le titre de la fenêtre en fonction de la page active."""
        titles = [
            "TeachAssit - Tableau de bord",
            "TeachAssit - Gestion des fichiers",
            "TeachAssit - Analyse des soumissions",
            "TeachAssit - Résultats d'analyse",
            "TeachAssit - Notes et Feedback",
            "TeachAssit - Configuration",
            "TeachAssit - À propos"
        ]
        
        if 0 <= index < len(titles):
            self.setWindowTitle(titles[index]) 