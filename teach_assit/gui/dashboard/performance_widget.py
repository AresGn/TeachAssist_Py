"""
Widget pour afficher les performances des étudiants avec un graphique.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QFrame, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont

import os
import json
import math
from collections import defaultdict

# Essayer d'importer matplotlib
try:
    import matplotlib
    matplotlib.use('Qt5Agg')
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class PerformanceWidget(QWidget):
    """Widget pour afficher les performances des étudiants avec un graphique."""
    
    def __init__(self, submission_manager=None, db_manager=None, parent=None):
        super().__init__(parent)
        self.submission_manager = submission_manager
        self.db_manager = db_manager
        self.student_performances = {}
        self.assessment_names = []
        
        # Définir une taille minimale pour garantir un bon affichage
        self.setMinimumSize(800, 600)
        
        self.init_ui()
        self.update_data()
    
    def init_ui(self):
        """Initialiser l'interface utilisateur du widget de performances."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # En-tête
        header = QLabel("Performances des étudiants")
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
        filter_layout.addWidget(self.assessment_combo)
        
        view_label = QLabel("Vue :")
        view_label.setStyleSheet("font-weight: bold;")
        filter_layout.addWidget(view_label)
        
        self.view_combo = QComboBox()
        self.view_combo.addItems(["Graphique en barres", "Graphique linéaire", "Camembert"])
        filter_layout.addWidget(self.view_combo)
        
        self.view_combo.currentIndexChanged.connect(self.update_chart)
        
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
        
        # Zone du graphique
        self.chart_frame = QFrame()
        self.chart_frame.setFrameShape(QFrame.StyledPanel)
        self.chart_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #dfe6e9;
                padding: 15px;
            }
        """)
        
        self.chart_layout = QVBoxLayout(self.chart_frame)
        
        # Message en l'absence de matplotlib
        if not MATPLOTLIB_AVAILABLE:
            message = QLabel("La bibliothèque matplotlib n'est pas disponible.\nVeuillez l'installer pour afficher les graphiques.")
            message.setAlignment(Qt.AlignCenter)
            message.setStyleSheet("font-size: 16px; color: #7f8c8d;")
            self.chart_layout.addWidget(message)
        else:
            # Créer la figure matplotlib
            self.figure = Figure(figsize=(8, 6), dpi=100)
            self.canvas = FigureCanvas(self.figure)
            self.chart_layout.addWidget(self.canvas)
        
        main_layout.addWidget(self.chart_frame)
    
    def update_data(self):
        """Mettre à jour les données de performances depuis la base de données."""
        self.student_performances = {}
        self.assessment_names = []
        
        try:
            # Chercher les fichiers d'évaluation (assessments)
            assessments_dir = os.path.join(os.getcwd(), "assessments")
            if os.path.exists(assessments_dir):
                assessment_files = [f for f in os.listdir(assessments_dir) if f.endswith('.json')]
                
                # Ajouter les noms des évaluations à la liste déroulante
                current_text = self.assessment_combo.currentText()
                self.assessment_combo.clear()
                self.assessment_combo.addItem("Toutes les évaluations")
                
                assessment_names = []
                for assessment_file in assessment_files:
                    assessment_id = os.path.splitext(assessment_file)[0]
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
                    self.assessment_names.append(assessment_id)
                
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
                                        import re
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
                            assessment_type = None
                            assessment_id = None
                            for line in content.split('\n'):
                                for assessment_name in self.assessment_names:
                                    if assessment_name in line:
                                        assessment_id = assessment_name
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
            
            # Mettre à jour le graphique
            self.update_chart()
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour des données de performances: {str(e)}")
            QMessageBox.warning(self, "Erreur", f"Impossible de mettre à jour les données : {str(e)}")
    
    def update_chart(self):
        """Mettre à jour le graphique en fonction des données et du type sélectionné."""
        if not MATPLOTLIB_AVAILABLE or not self.student_performances:
            return
        
        try:
            # Effacer la figure actuelle
            self.figure.clear()
            
            # Récupérer le type de graphique sélectionné
            chart_type = self.view_combo.currentText()
            
            # Récupérer l'évaluation sélectionnée
            selected_assessment = None
            if self.assessment_combo.currentText() != "Toutes les évaluations":
                selected_assessment = self.assessment_combo.currentData()
            
            # Filtrer les données en fonction de l'évaluation sélectionnée
            filtered_data = {}
            if selected_assessment:
                for student, assessments in self.student_performances.items():
                    if selected_assessment in assessments:
                        filtered_data[student] = {selected_assessment: assessments[selected_assessment]}
            else:
                filtered_data = self.student_performances
            
            # Créer un nouvel axe
            ax = self.figure.add_subplot(111)
            
            if chart_type == "Graphique en barres":
                self._create_bar_chart(ax, filtered_data, selected_assessment)
            elif chart_type == "Graphique linéaire":
                self._create_line_chart(ax, filtered_data, selected_assessment)
            elif chart_type == "Camembert":
                self._create_pie_chart(ax, filtered_data, selected_assessment)
            
            # Ajuster la mise en page
            self.figure.tight_layout()
            
            # Redessiner le canevas
            self.canvas.draw()
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour du graphique: {str(e)}")
    
    def _create_bar_chart(self, ax, data, selected_assessment):
        """Créer un graphique en barres des performances."""
        if not data:
            ax.set_title("Aucune donnée disponible")
            return
        
        # Préparer les données
        if selected_assessment:
            # Un seul type d'évaluation - barres simples
            students = []
            notes = []
            for student, assessments in data.items():
                if selected_assessment in assessments:
                    students.append(student)
                    notes.append(assessments[selected_assessment])
            
            # Trier par notes décroissantes
            sorted_data = sorted(zip(students, notes), key=lambda x: x[1], reverse=True)
            students = [s for s, _ in sorted_data]
            notes = [n for _, n in sorted_data]
            
            # Créer le graphique
            bars = ax.bar(students, notes, color='#3498db')
            
            # Ajouter les valeurs sur les barres
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{height:.1f}', ha='center', va='bottom')
            
            # Définir le titre et les axes
            ax.set_title(f"Notes des étudiants - {selected_assessment}")
            ax.set_ylabel("Note")
            ax.set_ylim(0, 20)  # Échelle de notes de 0 à 20
            
            # Rotation des étiquettes d'étudiants si nombreuses
            if len(students) > 8:
                plt = ax.get_figure().canvas.manager.plt if hasattr(ax.get_figure().canvas.manager, 'plt') else matplotlib.pyplot
                plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        
        else:
            # Plusieurs types d'évaluation - barres groupées
            # Trop complexe pour cette implémentation simple
            ax.set_title("Sélectionnez une évaluation spécifique pour voir le graphique en barres")
    
    def _create_line_chart(self, ax, data, selected_assessment):
        """Créer un graphique linéaire des performances."""
        if not data:
            ax.set_title("Aucune donnée disponible")
            return
        
        if selected_assessment:
            # Un seul type d'évaluation - ligne simple
            students = []
            notes = []
            for student, assessments in data.items():
                if selected_assessment in assessments:
                    students.append(student)
                    notes.append(assessments[selected_assessment])
            
            # Trier par notes décroissantes
            sorted_data = sorted(zip(students, notes), key=lambda x: x[1], reverse=True)
            students = [s for s, _ in sorted_data]
            notes = [n for _, n in sorted_data]
            
            # Créer le graphique
            ax.plot(students, notes, 'o-', color='#3498db', linewidth=2, markersize=8)
            
            # Ajouter les valeurs sur les points
            for i, note in enumerate(notes):
                ax.text(i, note + 0.3, f'{note:.1f}', ha='center')
            
            # Définir le titre et les axes
            ax.set_title(f"Progression des notes - {selected_assessment}")
            ax.set_ylabel("Note")
            ax.set_ylim(0, 20)  # Échelle de notes de 0 à 20
            
            # Rotation des étiquettes d'étudiants si nombreuses
            if len(students) > 8:
                plt = ax.get_figure().canvas.manager.plt if hasattr(ax.get_figure().canvas.manager, 'plt') else matplotlib.pyplot
                plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        
        else:
            # Pour chaque étudiant, tracer sa progression sur les différentes évaluations
            # Sélectionner les 5 premiers étudiants pour la lisibilité
            top_students = list(data.keys())[:5]
            
            # Récupérer tous les types d'évaluation présents
            all_assessments = set()
            for student, assessments in data.items():
                all_assessments.update(assessments.keys())
            
            assessment_list = sorted(list(all_assessments))
            
            # Tracer une ligne pour chaque étudiant
            colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6']
            
            for i, student in enumerate(top_students):
                if student in data:
                    # Récupérer les notes pour cet étudiant
                    x_values = []
                    y_values = []
                    
                    for assessment in assessment_list:
                        if assessment in data[student]:
                            x_values.append(assessment)
                            y_values.append(data[student][assessment])
                    
                    if x_values:
                        color = colors[i % len(colors)]
                        ax.plot(x_values, y_values, 'o-', color=color, linewidth=2, 
                                markersize=8, label=student)
            
            # Définir le titre et les axes
            ax.set_title("Progression des notes par étudiant")
            ax.set_ylabel("Note")
            ax.set_ylim(0, 20)  # Échelle de notes de 0 à 20
            
            # Rotation des étiquettes d'évaluations
            plt = ax.get_figure().canvas.manager.plt if hasattr(ax.get_figure().canvas.manager, 'plt') else matplotlib.pyplot
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
            
            # Ajouter une légende
            ax.legend()
    
    def _create_pie_chart(self, ax, data, selected_assessment):
        """Créer un graphique en camembert des performances."""
        if not data:
            ax.set_title("Aucune donnée disponible")
            return
        
        # Définir des tranches de notes
        ranges = [
            (0, 8, "Insuffisant"),
            (8, 12, "Passable"),
            (12, 14, "Assez bien"),
            (14, 16, "Bien"),
            (16, 20, "Très bien")
        ]
        
        # Compter le nombre d'étudiants dans chaque tranche
        counts = [0] * len(ranges)
        
        if selected_assessment:
            # Pour un type d'évaluation spécifique
            for student, assessments in data.items():
                if selected_assessment in assessments:
                    note = assessments[selected_assessment]
                    for i, (min_val, max_val, _) in enumerate(ranges):
                        if min_val <= note < max_val or (i == len(ranges) - 1 and note == max_val):
                            counts[i] += 1
                            break
        else:
            # Pour toutes les évaluations, prendre la moyenne par étudiant
            for student, assessments in data.items():
                if assessments:
                    avg_note = sum(assessments.values()) / len(assessments)
                    for i, (min_val, max_val, _) in enumerate(ranges):
                        if min_val <= avg_note < max_val or (i == len(ranges) - 1 and avg_note == max_val):
                            counts[i] += 1
                            break
        
        # Ne pas afficher les tranches vides
        labels = [label for (_, _, label), count in zip(ranges, counts) if count > 0]
        sizes = [count for count in counts if count > 0]
        
        if not sizes:
            ax.set_title("Aucune donnée disponible")
            return
        
        # Couleurs pour chaque tranche
        colors = ['#e74c3c', '#f39c12', '#f1c40f', '#2ecc71', '#3498db']
        colors = [color for color, count in zip(colors, counts) if count > 0]
        
        # Créer le camembert
        wedges, texts, autotexts = ax.pie(
            sizes, 
            labels=labels, 
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            shadow=False,
            wedgeprops={'edgecolor': 'white', 'linewidth': 1}
        )
        
        # Personnaliser le texte
        for text in texts:
            text.set_fontsize(12)
        for autotext in autotexts:
            autotext.set_fontsize(10)
            autotext.set_color('white')
        
        # Égaliser les axes pour un cercle parfait
        ax.axis('equal')
        
        # Titre
        title = f"Répartition des notes - {selected_assessment}" if selected_assessment else "Répartition des notes moyennes"
        ax.set_title(title) 