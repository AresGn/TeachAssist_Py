"""
Module pour l'affichage et l'analyse des résultats des étudiants.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QTableWidget, QTableWidgetItem, QComboBox, 
                            QPushButton, QLineEdit, QFrame, QHeaderView)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont


class ResultsWidget(QWidget):
    """Widget pour afficher et analyser les résultats des évaluations."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialiser l'interface utilisateur de l'onglet résultats."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # En-tête des résultats
        header = QLabel("Résultats des évaluations")
        header.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
        """)
        main_layout.addWidget(header)
        
        # Filtre et actions
        filter_frame = QFrame()
        filter_frame.setFrameShape(QFrame.StyledPanel)
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #dfe6e9;
                padding: 10px;
            }
        """)
        
        filter_layout = QHBoxLayout(filter_frame)
        
        # Recherche
        search_input = QLineEdit()
        search_input.setPlaceholderText("Rechercher...")
        search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #dfe6e9;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
        """)
        filter_layout.addWidget(search_input)
        
        # Filtre par exercice
        exercise_filter = QComboBox()
        exercise_filter.addItem("Tous les exercices")
        exercise_filter.setStyleSheet("""
            QComboBox {
                border: 1px solid #dfe6e9;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                min-width: 180px;
            }
        """)
        filter_layout.addWidget(exercise_filter)
        
        # Filtre par date
        date_filter = QComboBox()
        date_filter.addItem("Toutes les dates")
        date_filter.addItem("Aujourd'hui")
        date_filter.addItem("Cette semaine")
        date_filter.addItem("Ce mois")
        date_filter.setStyleSheet("""
            QComboBox {
                border: 1px solid #dfe6e9;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                min-width: 150px;
            }
        """)
        filter_layout.addWidget(date_filter)
        
        # Bouton exporter
        export_button = QPushButton("Exporter")
        export_button.setIcon(QIcon("icons/download.svg"))
        export_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                border-radius: 4px;
                padding: 8px 15px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        filter_layout.addWidget(export_button)
        
        main_layout.addWidget(filter_frame)
        
        # Tableau des résultats
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "Étudiant", "Exercice", "Date", "Score", "Temps", "Statut"
        ])
        
        # Style du tableau
        self.results_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #dfe6e9;
                border-radius: 8px;
                gridline-color: #f1f2f6;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 10px;
                border: none;
                border-right: 1px solid #dfe6e9;
                border-bottom: 1px solid #dfe6e9;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f1f2f6;
            }
        """)
        
        # Ajuster les en-têtes du tableau
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        # Ajouter quelques données d'exemple
        self.add_sample_data()
        
        main_layout.addWidget(self.results_table)
        
        # Statistiques de résumé
        stats_layout = QHBoxLayout()
        
        def create_stat_box(title, value):
            frame = QFrame()
            frame.setFrameShape(QFrame.StyledPanel)
            frame.setStyleSheet("""
                QFrame {
                    background-color: #f8f9fa;
                    border: 1px solid #dfe6e9;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            
            layout = QVBoxLayout(frame)
            
            title_label = QLabel(title)
            title_label.setStyleSheet("color: #7f8c8d; font-size: 14px;")
            layout.addWidget(title_label)
            
            value_label = QLabel(value)
            value_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
            layout.addWidget(value_label)
            
            return frame
        
        stats_layout.addWidget(create_stat_box("Score moyen", "0"))
        stats_layout.addWidget(create_stat_box("Taux de réussite", "0%"))
        stats_layout.addWidget(create_stat_box("Temps moyen", "0 min"))
        stats_layout.addWidget(create_stat_box("Soumissions totales", "0"))
        
        main_layout.addLayout(stats_layout)
    
    def add_sample_data(self):
        """Ajouter des données d'exemple au tableau de résultats."""
        # Cette méthode sera utilisée pour ajouter des données réelles plus tard
        # Pour l'instant, le tableau est vide
        self.results_table.setRowCount(0) 