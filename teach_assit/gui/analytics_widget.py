"""
Module contenant les composants pour l'analyse des données et les statistiques.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QTabWidget, QFrame, QComboBox, QPushButton,
                            QGridLayout, QTableWidget, QTableWidgetItem,
                            QHeaderView, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QColor


class AnalyticsWidget(QWidget):
    """Widget pour l'affichage des graphiques et statistiques."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialiser l'interface utilisateur de l'onglet analytique."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # En-tête 
        header = QLabel("Statistiques et analyses")
        header.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
        """)
        main_layout.addWidget(header)
        
        # Contrôles de filtrage
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
        
        period_label = QLabel("Période :")
        period_label.setStyleSheet("font-weight: bold;")
        filter_layout.addWidget(period_label)
        
        period_combo = QComboBox()
        period_combo.addItems(["Dernier mois", "Derniers 3 mois", "Derniers 6 mois", "Dernière année", "Tout"])
        filter_layout.addWidget(period_combo)
        
        group_label = QLabel("Groupe :")
        group_label.setStyleSheet("font-weight: bold;")
        filter_layout.addWidget(group_label)
        
        group_combo = QComboBox()
        group_combo.addItems(["Tous les groupes", "Licence Informatique", "Master Informatique", "DUT Informatique"])
        filter_layout.addWidget(group_combo)
        
        filter_layout.addStretch()
        
        update_button = QPushButton("Mettre à jour")
        update_button.setIcon(QIcon("icons/refresh.svg"))
        update_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        filter_layout.addWidget(update_button)
        
        main_layout.addWidget(filter_frame)
        
        # Onglets pour les différentes vues d'analyse
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #dfe6e9;
                border-radius: 5px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                border: 1px solid #dfe6e9;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 15px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
            }
        """)
        
        # Onglet Vue d'ensemble
        overview_tab = QWidget()
        overview_layout = QVBoxLayout(overview_tab)
        
        # Résumé en grille
        summary_grid = QGridLayout()
        summary_grid.setSpacing(15)
        
        def create_metric_widget(title, value, icon_name=None, color="#3498db"):
            frame = QFrame()
            frame.setFrameShape(QFrame.StyledPanel)
            frame.setStyleSheet(f"""
                QFrame {{
                    border-radius: 8px;
                    background-color: white;
                    border: 1px solid #dfe6e9;
                    padding: 10px;
                }}
                QLabel#value {{
                    color: {color};
                    font-size: 24px;
                    font-weight: bold;
                }}
                QLabel#title {{
                    color: #7f8c8d;
                    font-size: 14px;
                }}
            """)
            
            layout = QVBoxLayout(frame)
            layout.setSpacing(5)
            
            title_label = QLabel(title)
            title_label.setObjectName("title")
            layout.addWidget(title_label)
            
            value_label = QLabel(value)
            value_label.setObjectName("value")
            layout.addWidget(value_label)
            
            return frame
        
        summary_grid.addWidget(create_metric_widget("Soumissions totales", "1,245"), 0, 0)
        summary_grid.addWidget(create_metric_widget("Moyenne générale", "14,7/20", color="#2ecc71"), 0, 1)
        summary_grid.addWidget(create_metric_widget("Taux de réussite", "76%", color="#2ecc71"), 0, 2)
        summary_grid.addWidget(create_metric_widget("Temps moyen par exercice", "45 min", color="#e67e22"), 1, 0)
        summary_grid.addWidget(create_metric_widget("Exercices créés", "27"), 1, 1)
        summary_grid.addWidget(create_metric_widget("Étudiants actifs", "183"), 1, 2)
        
        overview_layout.addLayout(summary_grid)
        
        # Message indiquant que les graphiques seraient ici
        chart_placeholder = QLabel("Les graphiques analytiques seraient affichés ici.\nCette section utiliserait matplotlib ou une autre bibliothèque de graphiques.")
        chart_placeholder.setAlignment(Qt.AlignCenter)
        chart_placeholder.setStyleSheet("""
            border: 2px dashed #dfe6e9;
            border-radius: 8px;
            padding: 40px;
            color: #7f8c8d;
            font-size: 16px;
        """)
        overview_layout.addWidget(chart_placeholder)
        
        # Onglet Analyse de performance
        performance_tab = QWidget()
        performance_layout = QVBoxLayout(performance_tab)
        
        performance_message = QLabel("Les analyses de performance détaillées seraient affichées ici.")
        performance_message.setAlignment(Qt.AlignCenter)
        performance_message.setStyleSheet("""
            border: 2px dashed #dfe6e9;
            border-radius: 8px;
            padding: 40px;
            color: #7f8c8d;
            font-size: 16px;
        """)
        performance_layout.addWidget(performance_message)
        
        # Onglet Progression
        progression_tab = QWidget()
        progression_layout = QVBoxLayout(progression_tab)
        
        progression_message = QLabel("Les graphiques et données de progression seraient affichés ici.")
        progression_message.setAlignment(Qt.AlignCenter)
        progression_message.setStyleSheet("""
            border: 2px dashed #dfe6e9;
            border-radius: 8px;
            padding: 40px;
            color: #7f8c8d;
            font-size: 16px;
        """)
        progression_layout.addWidget(progression_message)
        
        # Onglet Rapport
        report_tab = QWidget()
        report_layout = QVBoxLayout(report_tab)
        
        # Contrôles de rapport
        report_controls = QHBoxLayout()
        
        report_type_label = QLabel("Type de rapport:")
        report_type_label.setStyleSheet("font-weight: bold;")
        report_controls.addWidget(report_type_label)
        
        report_type_combo = QComboBox()
        report_type_combo.addItems(["Synthèse globale", "Rapport par groupe", "Rapport par exercice"])
        report_controls.addWidget(report_type_combo)
        
        report_controls.addStretch()
        
        export_button = QPushButton("Exporter")
        export_button.setIcon(QIcon("icons/download.svg"))
        export_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        report_controls.addWidget(export_button)
        
        report_layout.addLayout(report_controls)
        
        # Exemple de tableau de rapport
        report_table = QTableWidget()
        report_table.setColumnCount(5)
        report_table.setHorizontalHeaderLabels([
            "Catégorie", "Nb. Exercices", "Nb. Soumissions", "Taux Réussite", "Note Moyenne"
        ])
        
        report_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #dfe6e9;
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
        
        # Configurer l'en-tête de table
        header = report_table.horizontalHeader()
        for i in range(report_table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        # Ajouter des données d'exemple
        sample_data = [
            ("Fondamentaux Programmation", "8", "450", "82%", "15,3/20"),
            ("Structures de Données", "6", "320", "74%", "14,1/20"),
            ("Algorithmes", "5", "275", "68%", "13,5/20"),
            ("POO", "4", "200", "79%", "15,8/20"),
            ("Web", "4", "150", "85%", "16,2/20")
        ]
        
        report_table.setRowCount(len(sample_data))
        for row, (cat, ex, sub, rate, avg) in enumerate(sample_data):
            report_table.setItem(row, 0, QTableWidgetItem(cat))
            report_table.setItem(row, 1, QTableWidgetItem(ex))
            report_table.setItem(row, 2, QTableWidgetItem(sub))
            report_table.setItem(row, 3, QTableWidgetItem(rate))
            report_table.setItem(row, 4, QTableWidgetItem(avg))
        
        report_layout.addWidget(report_table)
        
        # Ajouter tous les onglets
        tabs.addTab(overview_tab, "Vue d'ensemble")
        tabs.addTab(performance_tab, "Performance")
        tabs.addTab(progression_tab, "Progression")
        tabs.addTab(report_tab, "Rapports")
        
        main_layout.addWidget(tabs) 