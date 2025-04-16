"""
Styles centralisés pour l'interface utilisateur de TeachAssist.
"""

SIDEBAR_STYLE = """
QWidget#sidebar {
    background-color: #1a237e;
    padding: 20px 0;
}

QWidget#sidebar.expanded {
    min-width: 250px;
    max-width: 250px;
}

QWidget#sidebar.collapsed {
    min-width: 80px;
    max-width: 80px;
}

QWidget#sidebar QLabel#logo {
    color: white;
    font-size: 24px;
    font-weight: bold;
    padding: 20px;
    margin-bottom: 20px;
}

QWidget#sidebar.collapsed QLabel#logo {
    font-size: 0px;
}

QWidget#sidebar QPushButton {
    background-color: transparent;
    border: none;
    border-radius: 0;
    color: #b3e5fc;
    font-size: 16px;
    text-align: left;
    padding: 15px 20px;
    margin: 5px 0;
}

QWidget#sidebar.collapsed QPushButton {
    font-size: 0px;
    padding: 15px;
}

QWidget#sidebar QPushButton:hover {
    background-color: #283593;
}

QWidget#sidebar QPushButton:checked {
    background-color: #3949ab;
    color: white;
    border-left: 4px solid #64b5f6;
}

QWidget#sidebar QPushButton:disabled {
    color: #9fa8da;
}

QWidget#sidebar QLabel#version {
    color: #9fa8da;
    font-size: 14px;
    padding: 10px 20px;
}

QWidget#sidebar.collapsed QLabel#version {
    font-size: 0px;
}

QWidget#sidebar #toggle-button {
    background-color: transparent;
    border: none;
    border-radius: 0;
    color: #b3e5fc;
    font-size: 16px;
    padding: 15px;
    margin: 5px 0;
}

QWidget#sidebar #toggle-button:hover {
    background-color: #283593;
}
"""

MAIN_STYLE = """
QMainWindow {
    background-color: #f5f6fa;
}

QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
}

QPushButton {
    background-color: #1a237e;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-size: 16px;
    min-width: 120px;
}

QPushButton:hover {
    background-color: #283593;
}

QPushButton:pressed {
    background-color: #3949ab;
}

QLineEdit, QTextEdit, QComboBox {
    border: 2px solid #dcdde1;
    border-radius: 8px;
    padding: 10px;
    background-color: white;
    selection-background-color: #1a237e;
    font-size: 14px;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border: 2px solid #1a237e;
}

QComboBox {
    min-width: 200px;
}

QComboBox::drop-down {
    border: none;
    width: 40px;
}

QComboBox::down-arrow {
    image: url(icons/chevron-down.svg);
    width: 16px;
    height: 16px;
}

QLabel {
    color: #2f3542;
    font-size: 16px;
}

QGroupBox {
    border: 2px solid #dcdde1;
    border-radius: 8px;
    margin-top: 1em;
    padding-top: 15px;
    font-size: 16px;
}

QGroupBox::title {
    color: #2f3542;
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 8px;
    font-weight: bold;
}

/* Style pour la barre de statut */
QStatusBar {
    background-color: #f5f6fa;
    color: #2f3542;
    font-size: 14px;
    padding: 8px;
}

/* Style pour les messages de succès */
.success {
    color: #2ecc71;
    font-weight: bold;
}

/* Style pour les messages d'erreur */
.error {
    color: #e74c3c;
    font-weight: bold;
}

/* Style pour les messages d'attente */
.pending {
    color: #f1c40f;
    font-weight: bold;
}
"""

TOOLBAR_STYLE = """
QToolBar {
    background-color: white;
    border-bottom: 1px solid #dcdde1;
    spacing: 15px;
    padding: 8px;
}

QToolButton {
    border: none;
    border-radius: 6px;
    padding: 8px;
    min-width: 40px;
    min-height: 40px;
}

QToolButton:hover {
    background-color: #f1f2f6;
}

QToolButton:pressed {
    background-color: #dcdde1;
}
"""

MENU_STYLE = """
QMenuBar {
    background-color: white;
    border-bottom: 1px solid #dcdde1;
}

QMenuBar::item {
    padding: 12px 16px;
    font-size: 14px;
}

QMenuBar::item:selected {
    background-color: #f1f2f6;
}

QMenu {
    background-color: white;
    border: 1px solid #dcdde1;
}

QMenu::item {
    padding: 12px 24px;
    font-size: 14px;
}

QMenu::item:selected {
    background-color: #f1f2f6;
}
""" 