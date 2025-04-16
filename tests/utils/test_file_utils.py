import os
import pytest
import tempfile
import zipfile
import shutil
from teach_assit.utils.file_utils import SubmissionManager


class TestSubmissionManager:
    """Tests pour le gestionnaire de soumissions."""
    
    @pytest.fixture
    def setup_temp_directory(self):
        """Créer un répertoire temporaire pour les tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Nettoyage
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def create_test_zip(self, setup_temp_directory):
        """Créer un fichier ZIP de test avec des fichiers Java."""
        temp_dir = setup_temp_directory
        
        # Créer un ZIP avec deux fichiers Java
        student_zip_path = os.path.join(temp_dir, "Dupont_Jean.zip")
        
        with zipfile.ZipFile(student_zip_path, 'w') as zip_file:
            # Premier fichier Java
            zip_file.writestr("Main.java", """
            public class Main {
                public static void main(String[] args) {
                    System.out.println("Hello, World!");
                }
            }
            """)
            
            # Second fichier Java dans un sous-dossier
            zip_file.writestr("utils/Helper.java", """
            package utils;
            
            public class Helper {
                public void help() {
                    System.out.println("Helping...");
                }
            }
            """)
            
            # Fichier non-Java
            zip_file.writestr("README.txt", "Ceci est un exercice.")
        
        # Créer un ZIP invalide
        invalid_zip_path = os.path.join(temp_dir, "Invalid.zip")
        with open(invalid_zip_path, 'w') as f:
            f.write("Ceci n'est pas un fichier ZIP valide")
        
        return temp_dir
    
    def test_list_zip_files(self, create_test_zip):
        """Tester la fonction list_zip_files."""
        temp_dir = create_test_zip
        manager = SubmissionManager()
        manager.set_base_directory(temp_dir)
        
        zip_files = manager.list_zip_files()
        assert len(zip_files) == 2
        assert "Dupont_Jean.zip" in zip_files
        assert "Invalid.zip" in zip_files
    
    def test_extract_valid_zip(self, create_test_zip):
        """Tester l'extraction d'un fichier ZIP valide."""
        temp_dir = create_test_zip
        manager = SubmissionManager()
        manager.set_base_directory(temp_dir)
        
        success, message = manager.extract_zip_file("Dupont_Jean.zip")
        assert success is True
        assert "2 fichier(s) Java trouvé(s)" in message
        
        # Vérifier que les fichiers ont bien été extraits
        student_folders = manager.get_student_folders()
        assert "Dupont_Jean" in student_folders
        
        java_files = student_folders["Dupont_Jean"]["java_files"]
        assert len(java_files) == 2
        assert "Main.java" in java_files
        assert os.path.join("utils", "Helper.java").replace("\\", "/") in [f.replace("\\", "/") for f in java_files]
    
    def test_extract_invalid_zip(self, create_test_zip):
        """Tester l'extraction d'un fichier ZIP invalide."""
        temp_dir = create_test_zip
        manager = SubmissionManager()
        manager.set_base_directory(temp_dir)
        
        success, message = manager.extract_zip_file("Invalid.zip")
        assert success is False
        assert "Fichier ZIP corrompu ou invalide" in message
    
    def test_extract_all_zip_files(self, create_test_zip):
        """Tester l'extraction de tous les fichiers ZIP."""
        temp_dir = create_test_zip
        manager = SubmissionManager()
        manager.set_base_directory(temp_dir)
        
        results = manager.extract_all_zip_files()
        assert len(results) == 2
        
        # Vérifier les résultats pour chaque fichier
        assert results["Dupont_Jean.zip"][0] is True  # Succès
        assert results["Invalid.zip"][0] is False  # Échec
    
    def test_clean_extraction_directory(self, create_test_zip):
        """Tester le nettoyage du répertoire d'extraction."""
        temp_dir = create_test_zip
        manager = SubmissionManager()
        manager.set_base_directory(temp_dir)
        
        # Extraire d'abord un fichier
        manager.extract_zip_file("Dupont_Jean.zip")
        
        # Vérifier que le répertoire d'extraction existe
        assert os.path.exists(manager.extraction_dir)
        
        # Nettoyer
        success, message = manager.clean_extraction_directory()
        assert success is True
        assert "supprimé avec succès" in message
        
        # Vérifier que le répertoire a bien été supprimé
        assert not os.path.exists(manager.extraction_dir) 