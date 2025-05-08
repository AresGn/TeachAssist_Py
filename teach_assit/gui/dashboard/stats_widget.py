"""
Widget pour afficher les statistiques principales du tableau de bord.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QGridLayout, QFrame, QPushButton, QSizePolicy)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont

import os
import sqlite3


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
        # Initialiser le dictionnaire des labels de valeurs une seule fois
        self.value_labels = {}
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
        
        # Ne pas réinitialiser self.value_labels ici
        value_label = QLabel(value)
        value_label.setStyleSheet("color: white; font-size: 28px; font-weight: bold;")
        info_layout.addWidget(value_label)
        # Stocker la référence au label dans le dictionnaire
        self.value_labels[title.lower()] = value_label
        
        layout.addLayout(info_layout)
        layout.setStretch(0, 1)
        layout.setStretch(1, 4)
        
        return frame
    
    def update_stats(self):
        """Mettre à jour les statistiques à partir de la base de données."""
        if self.submission_manager and self.db_manager:
            try:
                print("Débogage - Mise à jour des statistiques...")
                
                # Nombre d'étudiants (depuis les fichiers ZIP)
                if hasattr(self.submission_manager, 'get_all_zip_files_from_db'):
                    zip_files = self.submission_manager.get_all_zip_files_from_db()
                    print(f"Débogage - Fichiers ZIP trouvés: {len(zip_files)}")
                    # Utilisation d'un ensemble pour éviter les doublons
                    student_names = set()
                    for zip_file in zip_files:
                        filename = zip_file[1]  # Le nom du fichier dans le tuple
                        student_name = os.path.splitext(filename)[0]
                        student_names.add(student_name)
                    self.stats['students'] = len(student_names)
                    print(f"Débogage - Nombre d'étudiants: {self.stats['students']}")
                
                # Nombre de soumissions (fichiers ZIP)
                if hasattr(self.submission_manager, 'get_all_zip_files_from_db'):
                    zip_files = self.submission_manager.get_all_zip_files_from_db()
                    self.stats['submissions'] = len(zip_files)
                    print(f"Débogage - Nombre de soumissions: {self.stats['submissions']}")
                
                # Nombre d'évaluations (assessment configs)
                if hasattr(self.db_manager, 'get_all_assessment_configs'):
                    assessment_configs = self.db_manager.get_all_assessment_configs()
                    self.stats['assessments'] = len(assessment_configs)
                    print(f"Débogage - Nombre d'évaluations: {self.stats['assessments']}")
                
                # Nombre d'exercices (exercise configs)
                if hasattr(self.db_manager, 'get_all_exercise_configs'):
                    exercise_configs = self.db_manager.get_all_exercise_configs()
                    self.stats['exercises'] = len(exercise_configs)
                    print(f"Débogage - Nombre d'exercices: {self.stats['exercises']}")
                
                # Nombre de feedbacks
                feedback_count = 0
                
                # Utiliser directement get_all_feedbacks si disponible
                if hasattr(self.db_manager, 'get_all_feedbacks'):
                    feedbacks = self.db_manager.get_all_feedbacks()
                    feedback_count = len(feedbacks)
                    print(f"Débogage - Nombre de feedbacks depuis get_all_feedbacks: {feedback_count}")
                else:
                    # Fallback pour la compatibilité avec les anciennes versions
                    try:
                        conn = sqlite3.connect(self.db_manager.db_path)
                        cursor = conn.cursor()
                        cursor.execute('SELECT COUNT(*) FROM feedbacks')
                        result = cursor.fetchone()
                        if result and result[0]:
                            feedback_count = result[0]
                        conn.close()
                        print(f"Débogage - Nombre de feedbacks depuis la base de données: {feedback_count}")
                    except Exception as e:
                        print(f"Erreur lors du comptage des feedbacks: {str(e)}")
                        # Fallback: vérifier les fichiers dans le dossier feedback
                        feedback_dir = os.path.join(os.getcwd(), "data", "feedback")
                        if os.path.exists(feedback_dir):
                            feedback_files = [f for f in os.listdir(feedback_dir) 
                                             if f.endswith('.txt') or f.endswith('.md')]
                            feedback_count = len(feedback_files)
                            print(f"Débogage - Nombre de feedbacks depuis les fichiers: {feedback_count}")
                    
                self.stats['feedback_count'] = feedback_count
                print(f"Débogage - Nombre total de feedbacks: {self.stats['feedback_count']}")
                
                # Mettre à jour les labels avec les nouvelles valeurs
                self._update_value_labels()
                print("Débogage - Labels mis à jour")
                # Vérifier les valeurs des labels après mise à jour
                for key, label in self.value_labels.items():
                    print(f"Débogage - Label '{key}': {label.text()}")
            except Exception as e:
                print(f"Erreur lors de la mise à jour des statistiques: {str(e)}")
                import traceback
                traceback.print_exc()
    
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