# Main Application 

import sys
from PyQt5.QtWidgets import QApplication
from teach_assit.gui.main_window import MainWindow


def main():
    """Point d'entrée principal de l'application TeachAssit."""
    app = QApplication(sys.argv)
    
    # Création et affichage de la fenêtre principale
    window = MainWindow()
    window.show()
    
    # Exécution de la boucle d'événements
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 