from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem, 
                             QMessageBox, QComboBox, QGroupBox, QDialog, QSpinBox, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
import os


class AssessmentConfigForm(QWidget):
    """Formulaire pour éditer une configuration d'évaluation."""
    
    def __init__(self, config_loader, parent=None):
        super().__init__(parent)
        self.current_config = None
        self.config_loader = config_loader
        self.init_ui()
        self.modified = False  # Flag pour suivre les modifications
    
    def init_ui(self):
        """Initialiser l'interface utilisateur."""
        layout = QVBoxLayout()
        
        # Informations de base
        basic_group = QGroupBox("Informations de base")
        basic_layout = QFormLayout()
        
        self.id_edit = QLineEdit()
        self.id_edit.setReadOnly(True)  # L'ID ne peut pas être modifié
        basic_layout.addRow("Identifiant :", self.id_edit)
        
        self.name_edit = QLineEdit()
        basic_layout.addRow("Nom :", self.name_edit)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # Exercices inclus
        exercises_group = QGroupBox("Exercices inclus")
        exercises_layout = QVBoxLayout()
        
        # Utiliser une classe personnalisée pour la liste d'exercices
        self.exercises_list = ExerciseListWidget(self)
        self.exercises_list.pointsChanged.connect(self.update_total_points)
        exercises_layout.addWidget(self.exercises_list)
        
        exercises_buttons = QHBoxLayout()
        self.add_exercise_button = QPushButton("Ajouter")
        self.add_exercise_button.clicked.connect(self.on_add_exercise)
        exercises_buttons.addWidget(self.add_exercise_button)
        
        self.delete_exercise_button = QPushButton("Supprimer")
        self.delete_exercise_button.clicked.connect(self.on_delete_exercise)
        exercises_buttons.addWidget(self.delete_exercise_button)
        
        exercises_layout.addLayout(exercises_buttons)
        exercises_group.setLayout(exercises_layout)
        layout.addWidget(exercises_group)
        
        # Total des points
        points_group = QGroupBox("Points")
        points_layout = QFormLayout()
        
        self.total_points_label = QLabel("0")
        # Définir une taille de police valide
        font = self.total_points_label.font()
        font.setPointSize(12)  # Utiliser setPointSize au lieu de setPixelSize
        self.total_points_label.setFont(font)
        points_layout.addRow("Total des points :", self.total_points_label)
        
        points_group.setLayout(points_layout)
        layout.addWidget(points_group)
        
        # Bouton de sauvegarde
        self.save_button = QPushButton("Enregistrer")
        self.save_button.clicked.connect(self.save_config)
        layout.addWidget(self.save_button)
        
        self.setLayout(layout)
        self.clear()
    
    def clear(self):
        """Effacer le formulaire."""
        self.current_config = None
        
        self.id_edit.clear()
        self.name_edit.clear()
        self.exercises_list.clear()
        self.total_points_label.setText("0")
        
        self.save_button.setEnabled(False)
    
    def update_exercise_list(self):
        """Mettre à jour la liste des exercices disponibles."""
        # Cette méthode est appelée quand la liste des exercices change
        if self.current_config:
            self.load_config(self.current_config)
    
    def load_config(self, config):
        """Charger une configuration dans le formulaire."""
        self.current_config = config
        
        # Informations de base
        self.id_edit.setText(config.id)
        self.name_edit.setText(config.name)
        
        # Exercices inclus
        self.exercises_list.clear()
        for exercise in config.exercises:
            self.exercises_list.add_exercise(exercise, self.config_loader)
        
        # Total des points
        self.update_total_points(save=False)
        
        self.save_button.setEnabled(True)
        self.modified = False
    
    def update_total_points(self, save=True):
        """Mettre à jour l'affichage du total des points."""
        if self.current_config:
            # Récupérer les exercices directement depuis la liste d'interface
            exercises = self.exercises_list.get_all_exercises()
            
            # Calculer le nouveau total
            total = sum(exercise.get('maxPoints', 0) for exercise in exercises)
            print(f"Total calculé: {total}")
            
            # Mettre à jour l'interface
            self.total_points_label.setText(str(total))
            
            # Mettre à jour l'objet de configuration
            self.current_config.exercises = exercises
            self.current_config.total_max_points = total
            
            # Marquer comme modifié
            self.modified = True
            
            # Sauvegarder si demandé
            if save:
                self.save_config(show_confirmation=False)
    
    def on_add_exercise(self):
        """Ajouter un exercice à l'évaluation."""
        # Récupérer la liste des exercices disponibles
        exercise_configs = self.config_loader.get_all_exercise_configs()
        if not exercise_configs:
            QMessageBox.warning(self, "Aucun exercice", 
                              "Aucun exercice n'est disponible. Veuillez d'abord créer des exercices.")
            return
        
        # Liste des exercices déjà inclus
        included_ids = self.exercises_list.get_included_exercise_ids()
        
        # Créer un dialogue de sélection
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter un exercice")
        layout = QVBoxLayout()
        
        label = QLabel("Sélectionnez un exercice :")
        layout.addWidget(label)
        
        combo = QComboBox()
        for exercise_id, config in exercise_configs.items():
            if exercise_id not in included_ids:
                combo.addItem(f"{config.name} ({exercise_id})", exercise_id)
        
        if combo.count() == 0:
            QMessageBox.warning(self, "Tous les exercices inclus", 
                              "Tous les exercices disponibles sont déjà inclus dans cette évaluation.")
            return
        
        layout.addWidget(combo)
        
        points_layout = QFormLayout()
        points_spin = QSpinBox()
        points_spin.setMinimum(0)
        points_spin.setMaximum(100)
        points_spin.setValue(5)  # Valeur par défaut
        points_layout.addRow("Points :", points_spin)
        
        layout.addLayout(points_layout)
        
        buttons = QHBoxLayout()
        ok_button = QPushButton("Ajouter")
        cancel_button = QPushButton("Annuler")
        
        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)
        
        layout.addLayout(buttons)
        dialog.setLayout(layout)
        
        # Connecter les boutons
        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        
        # Afficher le dialogue
        if dialog.exec_() == QDialog.Accepted:
            # Récupérer les valeurs
            exercise_id = combo.currentData()
            max_points = points_spin.value()
            
            # Créer l'exercice
            exercise = {
                'exerciseId': exercise_id,
                'maxPoints': max_points
            }
            
            # Ajouter à la liste
            self.exercises_list.add_exercise(exercise, self.config_loader)
            
            # Mettre à jour le total des points
            if self.current_config:
                self.current_config.exercises.append(exercise)
                self.update_total_points()
    
    def on_delete_exercise(self):
        """Supprimer l'exercice sélectionné."""
        current_item = self.exercises_list.currentItem()
        if not current_item:
            return
        
        # Supprimer de la liste
        self.exercises_list.remove_current_exercise()
        
        # Mettre à jour le total des points
        self.update_total_points()
    
    def save_config(self, show_confirmation=True):
        """Sauvegarder la configuration."""
        if not self.current_config or not self.modified:
            return
        
        try:
            # Mise à jour des informations de base
            self.current_config.name = self.name_edit.text()
            
            # Récupérer les exercices directement depuis la liste d'interface
            self.current_config.exercises = []
            for i in range(self.exercises_list.count()):
                exercise = self.exercises_list.item(i).data(Qt.UserRole)
                self.current_config.exercises.append(exercise)
            
            # Calculer le total des points directement à partir de la liste d'exercices
            total = sum(exercise.get('maxPoints', 0) for exercise in self.current_config.exercises)
            print(f"Total à la sauvegarde: {total}")
            self.current_config.total_max_points = total
            
            # Mettre à jour l'affichage avant sauvegarde
            self.total_points_label.setText(str(total))
            
            # Sauvegarder la configuration
            success = self.config_loader.save_assessment_config(self.current_config)
            
            if success:
                self.modified = False
                if show_confirmation:
                    QMessageBox.information(self, "Sauvegarde", 
                                         f"Configuration '{self.current_config.id}' sauvegardée avec succès.")
            else:
                QMessageBox.warning(self, "Erreur", 
                                  f"Erreur lors de la sauvegarde de la configuration '{self.current_config.id}'")
        except Exception as e:
            QMessageBox.critical(self, "Erreur critique", 
                               f"Erreur lors de la sauvegarde : {str(e)}")
    
    def closeEvent(self, event):
        """Gérer la fermeture du widget."""
        if self.modified:
            reply = QMessageBox.question(self, "Modifications non sauvegardées",
                                       "Voulez-vous sauvegarder les modifications avant de fermer ?",
                                       QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            
            if reply == QMessageBox.Yes:
                self.save_config()
                event.accept()
            elif reply == QMessageBox.No:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


# Classe personnalisée pour la liste d'exercices avec spinners intégrés
class ExerciseListWidget(QListWidget):
    """Liste d'exercices personnalisée avec spinners intégrés pour modifier les points."""
    
    pointsChanged = pyqtSignal()  # Signal émis quand les points changent
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.itemWidgets = {}  # Pour stocker les widgets associés à chaque item
        self.next_id = 0  # Compteur pour générer des identifiants uniques
    
    def add_exercise(self, exercise, config_loader):
        """Ajouter un exercice à la liste avec son spinner intégré."""
        exercise_id = exercise.get('exerciseId', '')
        max_points = exercise.get('maxPoints', 0)
        
        # Récupérer le nom de l'exercice s'il existe
        exercise_config = config_loader.get_exercise_config(exercise_id)
        exercise_name = exercise_config.name if exercise_config else exercise_id
        
        # Créer l'item de liste
        item = QListWidgetItem()
        self.addItem(item)
        
        # Créer le widget personnalisé
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        
        # Label pour le nom de l'exercice
        label = QLabel(f"{exercise_name} ({exercise_id})")
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(label)
        
        # Spinner pour les points
        spinner = QSpinBox()
        spinner.setMinimum(0)
        spinner.setMaximum(100)
        spinner.setValue(max_points)
        spinner.valueChanged.connect(lambda value, e=exercise, i=item, id=self.next_id: self.on_points_changed(value, e, i, id))
        layout.addWidget(spinner)
        
        # Configurer l'item
        self.setItemWidget(item, widget)
        item.setData(Qt.UserRole, exercise)
        item.setData(Qt.UserRole + 1, self.next_id)  # Stocker l'ID unique avec l'item
        item.setSizeHint(widget.sizeHint())
        
        # Stocker le widget avec un ID unique comme clé
        self.itemWidgets[self.next_id] = {
            'widget': widget,
            'spinner': spinner,
            'label': label,
            'item': item
        }
        
        # Incrémenter l'ID pour le prochain exercice
        self.next_id += 1
    
    def on_points_changed(self, value, exercise, item, item_id):
        """Gérer le changement de points via le spinner."""
        exercise['maxPoints'] = value
        item.setData(Qt.UserRole, exercise)
        self.pointsChanged.emit()
    
    def get_all_exercises(self):
        """Récupérer tous les exercices de la liste."""
        exercises = []
        for i in range(self.count()):
            exercise = self.item(i).data(Qt.UserRole)
            exercises.append(exercise)
            print(f"Exercice: {exercise.get('exerciseId', 'unknown')} - Points: {exercise.get('maxPoints', 0)}")
        return exercises
    
    def get_included_exercise_ids(self):
        """Récupérer les IDs des exercices déjà inclus."""
        included_ids = set()
        for i in range(self.count()):
            exercise = self.item(i).data(Qt.UserRole)
            included_ids.add(exercise.get('exerciseId', ''))
        return included_ids
    
    def remove_current_exercise(self):
        """Supprimer l'exercice sélectionné et son widget associé."""
        current_item = self.currentItem()
        if not current_item:
            return
        
        # Récupérer l'ID unique de l'item
        item_id = current_item.data(Qt.UserRole + 1)
        
        # Supprimer le widget de notre dictionnaire
        if item_id in self.itemWidgets:
            del self.itemWidgets[item_id]
        
        # Supprimer l'item de la liste
        row = self.row(current_item)
        self.takeItem(row) 