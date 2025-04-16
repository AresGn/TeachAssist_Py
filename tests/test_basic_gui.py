import sys
import pytest
from PyQt5.QtWidgets import QApplication
from teach_assit.gui.main_window import MainWindow
from teach_assit.gui.file_selector import FileSelector


@pytest.fixture
def app():
    """Fixture pour créer une instance QApplication."""
    app = QApplication(sys.argv)
    yield app


def test_main_window_creation(app):
    """Vérifier que la fenêtre principale peut être créée sans erreur."""
    window = MainWindow()
    assert window is not None
    assert window.windowTitle() == "TeachAssit - Évaluation des Devoirs Java"
    assert window.extract_button.isEnabled() == False


def test_file_selector_creation(app):
    """Vérifier que le sélecteur de fichiers peut être créé sans erreur."""
    selector = FileSelector()
    assert selector is not None
    assert selector.file_list is not None 