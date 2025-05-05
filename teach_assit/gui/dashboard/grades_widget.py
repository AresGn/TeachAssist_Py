"""
Widget pour afficher le relevé de notes de tous les étudiants.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QTableWidget, QTableWidgetItem, QHeaderView, 
                           QFrame, QPushButton, QLineEdit, QComboBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QColor, QBrush

import os
import json
import re
from collections import defaultdict


class GradesWidget(QWidget):
    """Widget pour afficher le relevé de notes de tous les étudiants."""
    
    def __init__(self, submission_manager=None, db_manager=None, parent=None):
        super().__init__(parent)
        self.submission_manager = submission_manager
        self.db_manager = db_manager
        self.student_data = {}  # {student_name: {assessment_id: note}}
        self.assessment_data = {}  # {assessment_id: {name, type}}
        
        # Définir une taille minimale pour garantir un bon affichage
        self.setMinimumSize(800, 600)
        
        self.init_ui()
        self.update_data()
    
    def init_ui(self):
        """Initialiser l'interface utilisateur du widget de relevé de notes."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # En-tête
        header = QLabel("Relevé de notes")
        header.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        """)
        main_layout.addWidget(header)
        
        # Contrôles de recherche et filtrage
        search_frame = QFrame()
        search_frame.setFrameShape(QFrame.StyledPanel)
        search_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #dfe6e9;
                padding: 10px;
            }
        """)
        
        search_layout = QHBoxLayout(search_frame)
        
        search_label = QLabel("Rechercher :")
        search_label.setStyleSheet("font-weight: bold;")
        search_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nom de l'étudiant...")
        self.search_input.textChanged.connect(self.filter_table)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #dfe6e9;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
            }
        """)
        search_layout.addWidget(self.search_input)
        
        filter_label = QLabel("Type :")
        filter_label.setStyleSheet("font-weight: bold;")
        search_layout.addWidget(filter_label)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Tous", "TD", "Devoir", "Examen"])
        self.filter_combo.currentIndexChanged.connect(self.filter_table)
        search_layout.addWidget(self.filter_combo)
        
        search_layout.addStretch()
        
        export_button = QPushButton(" Exporter")
        export_button.setIcon(QIcon("icons/download.svg"))
        export_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        search_layout.addWidget(export_button)
        
        refresh_button = QPushButton(" Actualiser")
        refresh_button.setIcon(QIcon("icons/refresh-cw.svg"))
        refresh_button.setStyleSheet("""
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
        refresh_button.clicked.connect(self.update_data)
        search_layout.addWidget(refresh_button)
        
        main_layout.addWidget(search_frame)
        
        # Tableau de relevé de notes
        grades_frame = QFrame()
        grades_frame.setFrameShape(QFrame.StyledPanel)
        grades_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #dfe6e9;
                padding: 15px;
            }
        """)
        
        grades_layout = QVBoxLayout(grades_frame)
        
        self.grades_table = QTableWidget()
        self.grades_table.setAlternatingRowColors(True)
        self.grades_table.verticalHeader().setDefaultSectionSize(50)  # Hauteur de ligne augmentée
        self.grades_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: none;
                gridline-color: #cccccc;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 15px 10px;
                border: none;
                border-right: 1px solid #cccccc;
                border-bottom: 1px solid #cccccc;
                font-weight: bold;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #cccccc;
            }
        """)
        
        grades_layout.addWidget(self.grades_table)
        
        main_layout.addWidget(grades_frame)
    
    def update_data(self):
        """Mettre à jour les données du relevé de notes."""
        self.student_data = defaultdict(dict)
        self.assessment_data = {}
        
        try:
            # 1. Charger les informations sur les évaluations (TD, Devoir, Examen)
            assessments_dir = os.path.join(os.getcwd(), "assessments")
            if os.path.exists(assessments_dir):
                assessment_files = [f for f in os.listdir(assessments_dir) if f.endswith('.json')]
                
                for assessment_file in assessment_files:
                    assessment_id = os.path.splitext(assessment_file)[0]
                    try:
                        with open(os.path.join(assessments_dir, assessment_file), 'r', encoding='utf-8') as f:
                            assessment_data = json.load(f)
                            assessment_name = assessment_data.get('name', assessment_id)
                            
                            # Déterminer le type d'évaluation (TD, Devoir, Examen)
                            assessment_type = "TD"  # Type par défaut
                            if "devoir" in assessment_name.lower() or "homework" in assessment_name.lower():
                                assessment_type = "Devoir"
                            elif "examen" in assessment_name.lower() or "exam" in assessment_name.lower():
                                assessment_type = "Examen"
                            
                            self.assessment_data[assessment_id] = {
                                'name': assessment_name,
                                'type': assessment_type
                            }
                    except:
                        self.assessment_data[assessment_id] = {
                            'name': assessment_id,
                            'type': "TD"  # Type par défaut
                        }
            
            # 2. Récupérer les notes des étudiants
            feedback_dir = os.path.join(os.getcwd(), "data", "feedback")
            if os.path.exists(feedback_dir):
                for feedback_file in os.listdir(feedback_dir):
                    if feedback_file.endswith('.txt') or feedback_file.endswith('.md'):
                        # Extraire le nom de l'étudiant à partir du nom du fichier
                        student_name = feedback_file.split('_')[0] if '_' in feedback_file else os.path.splitext(feedback_file)[0]
                        
                        # Lire le contenu du fichier
                        with open(os.path.join(feedback_dir, feedback_file), 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                            # Analyser le contenu pour trouver la note globale
                            note_globale = None
                            for line in content.split('\n'):
                                if "NOTE GLOBALE" in line or "Note globale" in line or "Note finale" in line:
                                    parts = line.split(':')
                                    if len(parts) > 1:
                                        # Essayer de trouver un nombre dans la partie après le ":"
                                        note_text = parts[1].strip()
                                        # Chercher un format de note comme "15/20" ou "15.5/20"
                                        note_match = re.search(r'(\d+(\.\d+)?)/\d+', note_text)
                                        if note_match:
                                            try:
                                                note_globale = float(note_match.group(1))
                                            except ValueError:
                                                pass
                                        else:
                                            # Chercher juste un nombre
                                            note_match = re.search(r'(\d+(\.\d+)?)', note_text)
                                            if note_match:
                                                try:
                                                    note_globale = float(note_match.group(1))
                                                except ValueError:
                                                    pass
                            
                            # Chercher l'identifiant de l'évaluation
                            assessment_id = None
                            for aid in self.assessment_data.keys():
                                if aid in content:
                                    assessment_id = aid
                                    break
                            
                            # Si on a une note et un type d'évaluation
                            if note_globale is not None and assessment_id:
                                self.student_data[student_name][assessment_id] = note_globale
            
            # Si aucun étudiant n'est trouvé, ajouter quelques exemples pour démonstration
            if not self.student_data and not self.assessment_data:
                # Exemples d'évaluations
                self.assessment_data = {
                    'TD1': {'name': 'TD1 - Introduction', 'type': 'TD'},
                    'TD2': {'name': 'TD2 - Structures de données', 'type': 'TD'},
                    'TD3': {'name': 'TD3 - Algorithmes', 'type': 'TD'},
                    'Devoir1': {'name': 'Devoir 1', 'type': 'Devoir'},
                    'Examen': {'name': 'Examen final', 'type': 'Examen'}
                }
                
                # Exemples d'étudiants
                self.student_data = {
                    'Alice': {'TD1': 18.5, 'TD2': 17.0, 'TD3': 19.0, 'Devoir1': 16.5, 'Examen': 18.0},
                    'Bob': {'TD1': 14.0, 'TD2': 15.0, 'TD3': 13.5, 'Devoir1': 14.0, 'Examen': 15.5},
                    'Charlie': {'TD1': 11.0, 'TD2': 12.5, 'TD3': 13.0, 'Devoir1': 11.5, 'Examen': 12.0},
                    'David': {'TD1': 8.5, 'TD2': 9.0, 'TD3': 10.0, 'Devoir1': 9.5, 'Examen': 10.5},
                    'Eva': {'TD1': 16.0, 'TD2': 17.5, 'TD3': 16.0, 'Devoir1': 15.0, 'Examen': 16.5}
                }
            
            # 3. Mettre à jour le tableau
            self.update_table()
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour des données du relevé de notes: {str(e)}")
    
    def update_table(self):
        """Mettre à jour le tableau du relevé de notes."""
        # Trier les évaluations par type (TD, Devoir, Examen) puis par nom
        sorted_assessments = sorted(
            self.assessment_data.items(),
            key=lambda x: (
                0 if x[1]['type'] == 'TD' else 1 if x[1]['type'] == 'Devoir' else 2,
                x[1]['name']
            )
        )
        
        # Créer les colonnes
        col_count = 1 + len(sorted_assessments)  # Étudiant + colonnes pour chaque évaluation
        self.grades_table.setColumnCount(col_count)
        
        # En-têtes
        headers = ["Étudiant"]
        for assessment_id, assessment in sorted_assessments:
            headers.append(f"{assessment['name']} ({assessment['type']})")
        
        self.grades_table.setHorizontalHeaderLabels(headers)
        
        # Configurer les en-têtes
        self.grades_table.horizontalHeader().setFixedHeight(70)  # Hauteur fixe des en-têtes
        self.grades_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, col_count):
            self.grades_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
        # Trier les étudiants par ordre alphabétique
        sorted_students = sorted(self.student_data.keys())
        
        # Remplir les lignes
        self.grades_table.setRowCount(len(sorted_students))
        for row, student in enumerate(sorted_students):
            # Nom de l'étudiant
            name_item = QTableWidgetItem(student)
            name_item.setFont(QFont("Arial", 9, QFont.Bold))
            self.grades_table.setItem(row, 0, name_item)
            
            # Notes pour chaque évaluation
            for col, (assessment_id, _) in enumerate(sorted_assessments, start=1):
                if assessment_id in self.student_data[student]:
                    note = self.student_data[student][assessment_id]
                    note_item = QTableWidgetItem(f"{note:.1f}/20")
                    note_item.setTextAlignment(Qt.AlignCenter)
                    note_item.setFont(QFont("Arial", 10, QFont.Bold))
                    
                    # Coloration selon la note
                    if note >= 16:
                        note_item.setForeground(QBrush(QColor('#27ae60')))  # Vert - Très bien
                    elif note >= 14:
                        note_item.setForeground(QBrush(QColor('#2980b9')))  # Bleu - Bien
                    elif note >= 12:
                        note_item.setForeground(QBrush(QColor('#f39c12')))  # Orange - Assez bien
                    elif note >= 10:
                        note_item.setForeground(QBrush(QColor('#e67e22')))  # Orange foncé - Passable
                    else:
                        note_item.setForeground(QBrush(QColor('#e74c3c')))  # Rouge - Insuffisant
                    
                    self.grades_table.setItem(row, col, note_item)
                else:
                    # Pas de note
                    note_item = QTableWidgetItem("N/A")
                    note_item.setTextAlignment(Qt.AlignCenter)
                    note_item.setFont(QFont("Arial", 10, QFont.Bold))
                    note_item.setForeground(QBrush(QColor('#7f8c8d')))  # Gris
                    self.grades_table.setItem(row, col, note_item)
    
    def filter_table(self):
        """Filtrer le tableau en fonction des critères de recherche."""
        search_text = self.search_input.text().lower()
        filter_type = self.filter_combo.currentText()
        
        # Parcourir chaque ligne et déterminer si elle doit être affichée
        for row in range(self.grades_table.rowCount()):
            student_item = self.grades_table.item(row, 0)
            if not student_item:
                continue
            
            student_name = student_item.text().lower()
            show_row = search_text in student_name
            
            # Si un type de filtre est sélectionné, vérifier si les colonnes correspondent
            if filter_type != "Tous" and show_row:
                show_row = False
                for col in range(1, self.grades_table.columnCount()):
                    header = self.grades_table.horizontalHeaderItem(col)
                    if header and filter_type in header.text():
                        show_row = True
                        break
            
            # Afficher ou masquer la ligne
            self.grades_table.setRowHidden(row, not show_row) 