from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
                             QLabel, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont


class SubmissionTreeWidget(QWidget):
    """Widget pour afficher les soumissions extraites dans une arborescence."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialiser l'interface utilisateur."""
        layout = QVBoxLayout()
        
        # Étiquette d'information
        self.info_label = QLabel("Soumissions extraites :")
        layout.addWidget(self.info_label)
        
        # Arborescence des soumissions
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Soumission", "Statut"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        layout.addWidget(self.tree)
        
        self.setLayout(layout)
    
    def update_tree(self, student_folders, extraction_results=None):
        """Mettre à jour l'arborescence avec les dossiers d'étudiants extraits.
        
        Args:
            student_folders: Dictionnaire {nom_etudiant: {path: chemin, java_files: [liste_fichiers]}}
            extraction_results: Dictionnaire des résultats d'extraction {nom_zip: (succès, message)}
        """
        self.tree.clear()
        
        if not student_folders:
            self.info_label.setText("Aucune soumission extraite.")
            return
        
        self.info_label.setText(f"Soumissions extraites ({len(student_folders)}) :")
        
        # Création des éléments d'arborescence pour chaque étudiant
        for student_name, info in student_folders.items():
            # Création de l'élément parent (étudiant)
            status = ""
            if extraction_results and f"{student_name}.zip" in extraction_results:
                success, message = extraction_results[f"{student_name}.zip"]
                status = "Succès" if success else "Erreur"
            
            student_item = QTreeWidgetItem(self.tree, [student_name, status])
            student_item.setExpanded(True)  # Déplier par défaut
            
            # Ajout des fichiers Java comme enfants
            java_files = info.get('java_files', [])
            
            if not java_files:
                QTreeWidgetItem(student_item, ["Aucun fichier Java trouvé", ""])
            else:
                for java_file in java_files:
                    QTreeWidgetItem(student_item, [java_file, ""])
        
        # Ajustement automatique de la largeur des colonnes
        self.tree.resizeColumnToContents(0)
    
    def clear(self):
        """Effacer l'arborescence."""
        self.tree.clear()
        self.info_label.setText("Soumissions extraites :") 