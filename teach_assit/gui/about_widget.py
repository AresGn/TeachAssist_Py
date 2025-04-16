"""
Module pour afficher la section "À propos  ".
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QTabWidget)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QFont, QIcon


class AboutWidget(QWidget):
    """Widget pour afficher les informations sur l'application."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialiser l'interface utilisateur du widget."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # En-tête avec logo et titre
        header_layout = QHBoxLayout()
        
        # Logo (à remplacer par le vrai logo)
        logo_label = QLabel()
        logo_label.setPixmap(QIcon("icons/book.svg").pixmap(QSize(64, 64)))
        header_layout.addWidget(logo_label)
        
        # Titre et version
        title_layout = QVBoxLayout()
        
        app_name = QLabel("TeachAssit")
        app_name.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        title_layout.addWidget(app_name)
        
        version = QLabel("Version 2.1.0")
        version.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        title_layout.addWidget(version)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        # Séparateur
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #dfe6e9;")
        main_layout.addWidget(separator)
        
        # Tabs pour l'information
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #dfe6e9;
                border-radius: 5px;
                padding: 10px;
            }
            QTabBar::tab {
                background-color: #f1f2f6;
                padding: 8px 16px;
                margin-right: 4px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border: 1px solid #dfe6e9;
                border-bottom: none;
            }
        """)
        
        # Onglet "À propos"
        about_tab = QWidget()
        about_layout = QVBoxLayout(about_tab)
        
        about_text = QLabel(
            "<p><b>TeachAssit</b> est une application de bureau qui analyse statiquement "
            "le code Java soumis par des étudiants en fonction de règles définies par l'enseignant "
            "dans des fichiers JSON.</p>"
            "<p>Elle vise à automatiser une partie du processus de correction, fournir des "
            "points de données structurés (\"constats\") pour une évaluation ultérieure "
            "(potentiellement par IA ou barème), et organiser les soumissions.</p>"
            "<p>L'application fonctionne en quatre phases essentielles :</p>"
            "<ol>"
            "<li>Extraction et organisation des fichiers soumis</li>"
            "<li>Analyse statique du code Java</li>"
            "<li>Évaluation et génération de feedback</li>"
            "<li>Reporting et exportation des résultats</li>"
            "</ol>"
            "<p>TeachAssit accélère le processus d'évaluation tout en assurant "
            "une évaluation cohérente et objective.</p>"
        )
        about_text.setWordWrap(True)
        about_layout.addWidget(about_text)
        
        tab_widget.addTab(about_tab, "À propos")
        
        # Onglet "Fonctionnalités"
        features_tab = QWidget()
        features_layout = QVBoxLayout(features_tab)
        
        features_text = QLabel(
            "<p><b>Principales fonctionnalités :</b></p>"
            "<ul>"
            "<li>Extraction automatique des fichiers ZIP de soumission</li>"
            "<li>Analyse statique du code source Java</li>"
            "<li>Vérification de conformité avec des critères prédéfinis</li>"
            "<li>Configuration flexible des règles d'évaluation</li>"
            "<li>Génération de rapports détaillés</li>"
            "<li>Interface utilisateur intuitive et moderne</li>"
            "<li>Gestion des évaluations et des exercices</li>"
            "<li>Export des résultats en différents formats</li>"
            "</ul>"
        )
        features_text.setWordWrap(True)
        features_layout.addWidget(features_text)
        
        tab_widget.addTab(features_tab, "Fonctionnalités")
        
        # Onglet "Technologies"
        tech_tab = QWidget()
        tech_layout = QVBoxLayout(tech_tab)
        
        tech_text = QLabel(
            "<p><b>Technologies utilisées :</b></p>"
            "<ul>"
            "<li><b>Langage :</b> Python 3.x</li>"
            "<li><b>Interface Graphique :</b> PyQt5</li>"
            "<li><b>Analyse Java :</b> javalang</li>"
            "<li><b>Manipulation de fichiers :</b> os, pathlib, zipfile</li>"
            "<li><b>Gestion des configurations :</b> json</li>"
            "<li><b>Tests :</b> pytest</li>"
            "</ul>"
            "<p><b>Structure du projet :</b></p>"
            "<ul>"
            "<li>Interface graphique : modules GUI pour interaction utilisateur</li>"
            "<li>Logique métier : extraction, analyse, évaluation</li>"
            "<li>Configuration : formats JSON pour exercices et évaluations</li>"
            "<li>Utilitaires : gestion de fichiers et outils divers</li>"
            "</ul>"
        )
        tech_text.setWordWrap(True)
        tech_layout.addWidget(tech_text)
        
        tab_widget.addTab(tech_tab, "Technologies")
        
        # Onglet "Crédits"
        credits_tab = QWidget()
        credits_layout = QVBoxLayout(credits_tab)
        
        credits_text = QLabel(
            "<p><b>Développé par :</b></p>"
            "<p>Équipe TeachAssit</p>"
            "<p><b>Icônes :</b> Feather Icons (https://feathericons.com/)</p>"
        )
        credits_text.setWordWrap(True)
        credits_layout.addWidget(credits_text)
        
        tab_widget.addTab(credits_tab, "Crédits")
        
        main_layout.addWidget(tab_widget) 