import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QStatusBar, QMessageBox, 
                             QSplitter, QProgressDialog, QApplication, QTabWidget,
                             QComboBox, QToolBar, QToolButton, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, QTimer, QSize, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QIcon

from teach_assit.gui.file_selector import FileSelector
from teach_assit.gui.results_display import SubmissionTreeWidget
from teach_assit.gui.config_editor import ConfigEditorWidget
from teach_assit.gui.dashboard_widget import DashboardWidget
from teach_assit.gui.results_widget import ResultsWidget
from teach_assit.gui.about_widget import AboutWidget
from teach_assit.utils.file_utils import SubmissionManager
from teach_assit.core.analysis.config_loader import ConfigLoader
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
        
        self.nav_extract = QPushButton("  Extraction")
        self.nav_extract.setIcon(QIcon("icons/download.svg"))
        self.nav_extract.setIconSize(QSize(24, 24))
        self.nav_extract.setCheckable(True)
        self.nav_extract.clicked.connect(lambda: self.switch_page(1))
        
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
        
        self.nav_config = QPushButton("  Configuration")
        self.nav_config.setIcon(QIcon("icons/settings.svg"))
        self.nav_config.setIconSize(QSize(24, 24))
        self.nav_config.setCheckable(True)
        self.nav_config.clicked.connect(lambda: self.switch_page(4))
        
        self.nav_about = QPushButton("  À propos")
        self.nav_about.setIcon(QIcon("icons/info.svg"))
        self.nav_about.setIconSize(QSize(20, 20))
        self.nav_about.setObjectName("about-button")
        self.nav_about.setCheckable(True)
        self.nav_about.clicked.connect(lambda: self.switch_page(5))
        
        sidebar_layout.addWidget(self.nav_dashboard)
        sidebar_layout.addWidget(self.nav_extract)
        sidebar_layout.addWidget(self.nav_analyze)
        sidebar_layout.addWidget(self.nav_results)
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
        
        # Onglet d'extraction
        self.extract_tab = QWidget()
        self.setup_extract_tab()
        self.tab_widget.addTab(self.extract_tab, "Extraction")
        
        # Onglet d'analyse
        self.analyze_tab = QWidget()
        self.setup_analyze_tab()
        self.tab_widget.addTab(self.analyze_tab, "Analyse")
        
        # Onglet de résultats
        self.results_tab = ResultsWidget()
        self.tab_widget.addTab(self.results_tab, "Résultats")
        
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
        """Configurer l'onglet d'extraction."""
        layout = QVBoxLayout(self.extract_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # En-tête
        title_label = QLabel("Extraction des Soumissions")
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
        """)
        layout.addWidget(title_label)
        
        # Sélecteur de fichiers
        self.file_selector = FileSelector()
        self.file_selector.folder_selected.connect(self.on_folder_selected)
        layout.addWidget(self.file_selector)
        
        # Bouton d'extraction
        self.extract_button = QPushButton("Extraire les fichiers ZIP")
        self.extract_button.setIcon(QIcon("icons/download.svg"))
        self.extract_button.setIconSize(QSize(24, 24))
        self.extract_button.setEnabled(False)
        self.extract_button.clicked.connect(self.extract_zip_files)
        layout.addWidget(self.extract_button)
        
        # Liste des fichiers extraits
        self.results_widget = SubmissionTreeWidget()
        layout.addWidget(self.results_widget)
    
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
        analyze_button_layout.addWidget(self.analyze_button)
        
        main_content_layout.addWidget(analyze_button_container)
        
        # Ajouter le main_content au layout principal
        layout.addWidget(main_content, 1)  # Le 1 indique qu'il prendra tout l'espace disponible
    
    def switch_page(self, index):
        """Changer d'onglet et mettre à jour l'interface."""
        self.tab_widget.setCurrentIndex(index)
        
        # Si on passe à l'onglet d'analyse, mettre à jour le tableau des soumissions
        if index == 2:
            self.update_submission_table()
        
        # Désélectionner tous les boutons et sélectionner le bon
        for button in [self.nav_dashboard, self.nav_extract, self.nav_analyze, 
                      self.nav_results, self.nav_config, self.nav_about]:
            button.setChecked(False)
        
        if index == 0:
            self.nav_dashboard.setChecked(True)
            self.animate_button(self.nav_dashboard)
        elif index == 1:
            self.nav_extract.setChecked(True)
            self.animate_button(self.nav_extract)
        elif index == 2:
            self.nav_analyze.setChecked(True)
            self.animate_button(self.nav_analyze)
        elif index == 3:
            self.nav_results.setChecked(True)
            self.animate_button(self.nav_results)
        elif index == 4:
            self.nav_config.setChecked(True)
            self.animate_button(self.nav_config)
        elif index == 5:
            self.nav_about.setChecked(True)
            self.animate_button(self.nav_about)
            
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
        self.switch_page(5)  # L'index de l'onglet À propos
    
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
        
        if not student_folders:
            self.submission_table.setRowCount(0)
            self.submission_table.setHidden(True)
            return
        
        # Afficher le tableau
        self.submission_table.setHidden(False)
        
        # Configurer le tableau avec les données
        self.submission_table.setRowCount(len(student_folders))
        
        # Remplir le tableau avec les données des étudiants et leurs fichiers
        for row, (student_name, info) in enumerate(student_folders.items()):
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
            java_files_count = len(student_folders[list(student_folders.keys())[row]].get('java_files', []))
            # Hauteur plus grande pour chaque fichier
            row_height = max(70, 50 + java_files_count * 45)
            self.submission_table.setRowHeight(row, row_height)
        
        # Mise à jour du statut
        has_submissions = len(student_folders) > 0
        assessment_id = self.assessment_combo.currentData()
        self.analyze_button.setEnabled(has_submissions and assessment_id is not None) 