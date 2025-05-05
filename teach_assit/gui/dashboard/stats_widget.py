"""
Widget pour afficher les statistiques principales du tableau de bord.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QGridLayout, QFrame, QPushButton, QSizePolicy)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont

import os


class StatsWidget(QWidget):
    """Widget pour afficher les statistiques principales du tableau de bord."""
    
    def __init__(self, submission_manager=None, db_manager=None, parent=None):
        super().__init__(parent)
        self.submission_manager = submission_manager
        self.db_manager = db_manager
        self.stats = {
            'students': 0,
            'submissions': 0,
            'assessments': 0,
            'exercises': 0,
            'feedback_count': 0
        }
        self.init_ui()
        self.update_stats()
    
    def init_ui(self):
        """Initialiser l'interface utilisateur des statistiques."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(15)
        
        # Section des statistiques
        stats_frame = QFrame()
        stats_frame.setFrameShape(QFrame.StyledPanel)
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #dfe6e9;
                padding: 15px;
            }
        """)
        
        stats_layout = QGridLayout(stats_frame)
        stats_layout.setSpacing(15)
        
        # Créer les widgets de statistiques
        self.student_widget = self._create_stat_widget(
            "Étudiants", "0", "users", "#2ecc71", 
            "Nombre total d'étudiants."
        )
        stats_layout.addWidget(self.student_widget, 0, 0)
        
        self.submission_widget = self._create_stat_widget(
            "Soumissions", "0", "file-text", "#3498db", 
            "Nombre total de soumissions."
        )
        stats_layout.addWidget(self.submission_widget, 0, 1)
        
        self.assessment_widget = self._create_stat_widget(
            "Évaluations", "0", "clipboard", "#9b59b6", 
            "Nombre total d'évaluations (TD, Devoirs, Examens)."
        )
        stats_layout.addWidget(self.assessment_widget, 0, 2)
        
        self.exercise_widget = self._create_stat_widget(
            "Exercices", "0", "code", "#e74c3c", 
            "Nombre total d'exercices."
        )
        stats_layout.addWidget(self.exercise_widget, 1, 0)
        
        self.feedback_widget = self._create_stat_widget(
            "Feedbacks", "0", "message-circle", "#f39c12", 
            "Nombre total de feedbacks générés."
        )
        stats_layout.addWidget(self.feedback_widget, 1, 1)
        
        # Bouton d'actualisation
        refresh_button = QPushButton(" Actualiser les statistiques")
        refresh_button.setIcon(QIcon("icons/refresh-cw.svg"))
        refresh_button.setIconSize(QSize(16, 16))
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #dfe6e9;
                border-radius: 4px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        refresh_button.clicked.connect(self.update_stats)
        stats_layout.addWidget(refresh_button, 1, 2)
        
        main_layout.addWidget(stats_frame)
    
    def _create_stat_widget(self, title, value, icon_name, color, tooltip):
        """Créer un widget de statistique."""
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        frame.setToolTip(tooltip)
        
        layout = QHBoxLayout(frame)
        
        icon_label = QLabel()
        icon_path = f"icons/{icon_name}.svg"
        if os.path.exists(icon_path):
            icon_label.setPixmap(QIcon(icon_path).pixmap(QSize(48, 48)))
        else:
            # Fallback si l'icône n'existe pas
            icon_label.setText("📊")
            icon_label.setStyleSheet("font-size: 24px; color: white;")
        layout.addWidget(icon_label)
        
        info_layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: white; font-size: 14px;")
        info_layout.addWidget(title_label)
        
        self.value_labels = {}
        value_label = QLabel(value)
        value_label.setStyleSheet("color: white; font-size: 28px; font-weight: bold;")
        info_layout.addWidget(value_label)
        self.value_labels[title.lower()] = value_label
        
        layout.addLayout(info_layout)
        layout.setStretch(0, 1)
        layout.setStretch(1, 4)
        
        return frame
    
    def update_stats(self):
        """Mettre à jour les statistiques à partir de la base de données."""
        if self.submission_manager and self.db_manager:
            try:
                # Nombre d'étudiants (depuis les fichiers ZIP)
                if hasattr(self.submission_manager, 'get_all_zip_files_from_db'):
                    zip_files = self.submission_manager.get_all_zip_files_from_db()
                    # Utilisation d'un ensemble pour éviter les doublons
                    student_names = set()
                    for zip_file in zip_files:
                        filename = zip_file[1]  # Le nom du fichier dans le tuple
                        student_name = os.path.splitext(filename)[0]
                        student_names.add(student_name)
                    self.stats['students'] = len(student_names)
                
                # Nombre de soumissions (fichiers ZIP)
                if hasattr(self.submission_manager, 'get_all_zip_files_from_db'):
                    zip_files = self.submission_manager.get_all_zip_files_from_db()
                    self.stats['submissions'] = len(zip_files)
                
                # Nombre d'évaluations, exercices et feedbacks
                # Note: ces informations peuvent nécessiter un accès à d'autres parties de la base de données
                # Pour l'instant, on utilise des données statiques ou calculées à partir d'autres sources
                
                # Rechercher les fichiers d'évaluation dans le répertoire assessments
                assessment_files = []
                assessments_dir = os.path.join(os.getcwd(), "assessments")
                if os.path.exists(assessments_dir):
                    assessment_files = [f for f in os.listdir(assessments_dir) 
                                      if f.endswith('.json')]
                self.stats['assessments'] = len(assessment_files)
                
                # Compter le nombre d'exercices à partir des fichiers d'évaluation
                exercise_count = 0
                import json
                for assessment_file in assessment_files:
                    try:
                        with open(os.path.join(assessments_dir, assessment_file), 'r', encoding='utf-8') as f:
                            assessment_data = json.load(f)
                            if 'exercises' in assessment_data:
                                exercise_count += len(assessment_data['exercises'])
                    except:
                        pass
                self.stats['exercises'] = exercise_count
                
                # Nombre de feedbacks générés
                # Rechercher les fichiers de feedback
                feedback_dir = os.path.join(os.getcwd(), "data", "feedback")
                feedback_count = 0
                if os.path.exists(feedback_dir):
                    feedback_files = [f for f in os.listdir(feedback_dir) 
                                     if f.endswith('.txt') or f.endswith('.md')]
                    feedback_count = len(feedback_files)
                self.stats['feedback_count'] = feedback_count
                
                # Mettre à jour les labels avec les nouvelles valeurs
                self._update_value_labels()
            except Exception as e:
                print(f"Erreur lors de la mise à jour des statistiques: {str(e)}")
    
    def _update_value_labels(self):
        """Mettre à jour les labels avec les nouvelles valeurs."""
        if 'étudiants' in self.value_labels:
            self.value_labels['étudiants'].setText(str(self.stats['students']))
        
        if 'soumissions' in self.value_labels:
            self.value_labels['soumissions'].setText(str(self.stats['submissions']))
        
        if 'évaluations' in self.value_labels:
            self.value_labels['évaluations'].setText(str(self.stats['assessments']))
            
        if 'exercices' in self.value_labels:
            self.value_labels['exercices'].setText(str(self.stats['exercises']))
            
        if 'feedbacks' in self.value_labels:
            self.value_labels['feedbacks'].setText(str(self.stats['feedback_count'])) 