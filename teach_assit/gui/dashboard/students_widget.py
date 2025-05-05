"""
Widget pour afficher le classement des étudiants.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QTableWidget, QTableWidgetItem, QHeaderView,
                            QFrame, QPushButton, QSplitter, QComboBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QColor, QBrush

import os
import json
import re
from collections import defaultdict


class StudentsWidget(QWidget):
    """Widget pour afficher le classement des étudiants."""
    
    def __init__(self, submission_manager=None, db_manager=None, parent=None):
        super().__init__(parent)
        self.submission_manager = submission_manager
        self.db_manager = db_manager
        self.student_performances = {}
        
        # Définir une taille minimale pour garantir un bon affichage
        self.setMinimumSize(800, 600)
        
        self.init_ui()
        self.update_data()
    
    def init_ui(self):
        """Initialiser l'interface utilisateur du widget de classement des étudiants."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # En-tête
        header = QLabel("Classement des étudiants")
        header.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
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
        
        assessment_label = QLabel("Évaluation :")
        assessment_label.setStyleSheet("font-weight: bold;")
        filter_layout.addWidget(assessment_label)
        
        self.assessment_combo = QComboBox()
        self.assessment_combo.addItem("Toutes les évaluations")
        self.assessment_combo.currentIndexChanged.connect(self.update_tables)
        filter_layout.addWidget(self.assessment_combo)
        
        threshold_label = QLabel("Seuil d'excellence :")
        threshold_label.setStyleSheet("font-weight: bold;")
        filter_layout.addWidget(threshold_label)
        
        self.excellence_combo = QComboBox()
        self.excellence_combo.addItems(["14/20", "16/20", "18/20"])
        self.excellence_combo.setCurrentText("16/20")
        self.excellence_combo.currentIndexChanged.connect(self.update_tables)
        filter_layout.addWidget(self.excellence_combo)
        
        filter_layout.addStretch()
        
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
        filter_layout.addWidget(refresh_button)
        
        main_layout.addWidget(filter_frame)
        
        # Splitter pour les deux tableaux
        splitter = QSplitter(Qt.Horizontal)
        
        # 1. Tableau des étudiants performants
        top_frame = QFrame()
        top_frame.setFrameShape(QFrame.StyledPanel)
        top_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #dfe6e9;
                padding: 15px;
            }
        """)
        
        top_layout = QVBoxLayout(top_frame)
        
        top_label = QLabel("Étudiants performants")
        top_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2ecc71;
            margin-bottom: 10px;
        """)
        top_layout.addWidget(top_label)
        
        self.top_table = QTableWidget()
        self.top_table.setColumnCount(3)
        self.top_table.setHorizontalHeaderLabels(["Étudiant", "Note moyenne", "Évaluations"])
        self.top_table.horizontalHeader().setFixedHeight(70)  # Hauteur fixe des en-têtes
        self.top_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.top_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.top_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.top_table.setAlternatingRowColors(True)
        self.top_table.verticalHeader().setDefaultSectionSize(50)
        self.top_table.setStyleSheet("""
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
        top_layout.addWidget(self.top_table)
        
        splitter.addWidget(top_frame)
        
        # 2. Tableau des étudiants à améliorer
        bottom_frame = QFrame()
        bottom_frame.setFrameShape(QFrame.StyledPanel)
        bottom_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #dfe6e9;
                padding: 15px;
            }
        """)
        
        bottom_layout = QVBoxLayout(bottom_frame)
        
        bottom_label = QLabel("Étudiants à améliorer")
        bottom_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #e74c3c;
            margin-bottom: 10px;
        """)
        bottom_layout.addWidget(bottom_label)
        
        self.bottom_table = QTableWidget()
        self.bottom_table.setColumnCount(3)
        self.bottom_table.setHorizontalHeaderLabels(["Étudiant", "Note moyenne", "Évaluations"])
        self.bottom_table.horizontalHeader().setFixedHeight(70)  # Hauteur fixe des en-têtes
        self.bottom_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.bottom_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.bottom_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.bottom_table.setAlternatingRowColors(True)
        self.bottom_table.verticalHeader().setDefaultSectionSize(50)
        self.bottom_table.setStyleSheet("""
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
        bottom_layout.addWidget(self.bottom_table)
        
        splitter.addWidget(bottom_frame)
        
        # Égaliser la taille des colonnes du splitter
        splitter.setSizes([1000, 1000])
        
        main_layout.addWidget(splitter)
    
    def update_data(self):
        """Mettre à jour les données de performances des étudiants."""
        self.student_performances = {}
        
        try:
            # Chercher les fichiers d'évaluation (assessments)
            assessments_dir = os.path.join(os.getcwd(), "assessments")
            if os.path.exists(assessments_dir):
                assessment_files = [f for f in os.listdir(assessments_dir) if f.endswith('.json')]
                
                # Récupérer les noms des évaluations pour la liste déroulante
                current_text = self.assessment_combo.currentText()
                self.assessment_combo.clear()
                self.assessment_combo.addItem("Toutes les évaluations")
                
                assessment_names = []
                assessment_ids = []
                
                for assessment_file in assessment_files:
                    assessment_id = os.path.splitext(assessment_file)[0]
                    assessment_ids.append(assessment_id)
                    try:
                        with open(os.path.join(assessments_dir, assessment_file), 'r', encoding='utf-8') as f:
                            assessment_data = json.load(f)
                            assessment_name = assessment_data.get('name', assessment_id)
                            assessment_names.append((assessment_id, assessment_name))
                    except:
                        assessment_names.append((assessment_id, assessment_id))
                
                # Trier alphabétiquement les évaluations
                assessment_names.sort(key=lambda x: x[1])
                for assessment_id, assessment_name in assessment_names:
                    self.assessment_combo.addItem(assessment_name, assessment_id)
                
                # Restaurer la sélection précédente si possible
                if current_text and self.assessment_combo.findText(current_text) >= 0:
                    self.assessment_combo.setCurrentText(current_text)
            
            # Chercher les données de feedback pour extraire les performances
            feedback_dir = os.path.join(os.getcwd(), "data", "feedback")
            if os.path.exists(feedback_dir):
                # Dictionnaire pour stocker les performances par étudiant
                performances = defaultdict(dict)
                
                # Parcourir tous les fichiers de feedback
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
                            
                            # Chercher le type d'évaluation (TD, Devoir, Examen)
                            assessment_id = None
                            for line in content.split('\n'):
                                for aid in assessment_ids:
                                    if aid in line:
                                        assessment_id = aid
                                        break
                                if assessment_id:
                                    break
                            
                            # Si on a une note et un type d'évaluation
                            if note_globale is not None:
                                if assessment_id:
                                    performances[student_name][assessment_id] = note_globale
                                else:
                                    # Si on ne connaît pas le type, utiliser "Inconnu"
                                    performances[student_name]["Inconnu"] = note_globale
                
                # Mettre à jour les performances
                self.student_performances = dict(performances)
            
            # Mettre à jour les tableaux
            self.update_tables()
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour des données de classement: {str(e)}")
    
    def update_tables(self):
        """Mettre à jour les tableaux des étudiants performants et à améliorer."""
        # Récupérer les seuils
        excellence_text = self.excellence_combo.currentText()
        excellence_threshold = float(excellence_text.split('/')[0])
        mediocre_threshold = 10.0  # Seuil fixe pour les étudiants à améliorer
        
        # Récupérer l'évaluation sélectionnée
        selected_assessment = None
        if self.assessment_combo.currentText() != "Toutes les évaluations":
            selected_assessment = self.assessment_combo.currentData()
        
        # Calculer les moyennes pour chaque étudiant
        student_averages = {}
        for student, assessments in self.student_performances.items():
            if selected_assessment:
                # Utiliser uniquement l'évaluation sélectionnée
                if selected_assessment in assessments:
                    student_averages[student] = {
                        'score': assessments[selected_assessment],
                        'count': 1,
                        'assessments': [selected_assessment]
                    }
            else:
                # Utiliser toutes les évaluations
                total = sum(assessments.values())
                count = len(assessments)
                student_averages[student] = {
                    'score': total / count if count > 0 else 0,
                    'count': count,
                    'assessments': list(assessments.keys())
                }
        
        # 1. Étudiants performants (au-dessus du seuil d'excellence)
        top_students = [
            (student, data['score'], data['count'], data['assessments'])
            for student, data in student_averages.items()
            if data['score'] >= excellence_threshold
        ]
        top_students.sort(key=lambda x: x[1], reverse=True)  # Tri par note décroissante
        
        # 2. Étudiants à améliorer (en dessous du seuil de médiocrité)
        bottom_students = [
            (student, data['score'], data['count'], data['assessments'])
            for student, data in student_averages.items()
            if data['score'] < mediocre_threshold
        ]
        bottom_students.sort(key=lambda x: x[1])  # Tri par note croissante
        
        # Mettre à jour le tableau des étudiants performants
        self.top_table.setRowCount(len(top_students))
        for i, (student, score, count, assessments) in enumerate(top_students):
            # Nom de l'étudiant
            name_item = QTableWidgetItem(student)
            name_item.setForeground(QBrush(QColor('#2ecc71')))
            name_item.setFont(QFont("Arial", 10, QFont.Bold))
            self.top_table.setItem(i, 0, name_item)
            
            # Note moyenne
            score_item = QTableWidgetItem(f"{score:.1f}/20")
            score_item.setTextAlignment(Qt.AlignCenter)
            score_item.setFont(QFont("Arial", 10, QFont.Bold))
            self.top_table.setItem(i, 1, score_item)
            
            # Nombre d'évaluations
            evals_item = QTableWidgetItem(str(count))
            evals_item.setTextAlignment(Qt.AlignCenter)
            evals_item.setFont(QFont("Arial", 10, QFont.Bold))
            self.top_table.setItem(i, 2, evals_item)
        
        # Mettre à jour le tableau des étudiants à améliorer
        self.bottom_table.setRowCount(len(bottom_students))
        for i, (student, score, count, assessments) in enumerate(bottom_students):
            # Nom de l'étudiant
            name_item = QTableWidgetItem(student)
            name_item.setForeground(QBrush(QColor('#e74c3c')))
            name_item.setFont(QFont("Arial", 10, QFont.Bold))
            self.bottom_table.setItem(i, 0, name_item)
            
            # Note moyenne
            score_item = QTableWidgetItem(f"{score:.1f}/20")
            score_item.setTextAlignment(Qt.AlignCenter)
            score_item.setFont(QFont("Arial", 10, QFont.Bold))
            self.bottom_table.setItem(i, 1, score_item)
            
            # Nombre d'évaluations
            evals_item = QTableWidgetItem(str(count))
            evals_item.setTextAlignment(Qt.AlignCenter)
            evals_item.setFont(QFont("Arial", 10, QFont.Bold))
            self.bottom_table.setItem(i, 2, evals_item) 