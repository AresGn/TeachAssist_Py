"""
Fournisseur de connexion à la base de données.
Centralise la création et la gestion des connexions à la base de données.
"""

import sqlite3

class ConnectionProvider:
    """Fournisseur de connexion à la base de données SQLite."""
    
    def __init__(self, db_path):
        """
        Initialise le fournisseur de connexion.
        
        Args:
            db_path (str): Chemin vers le fichier de base de données SQLite
        """
        self.db_path = db_path
    
    def get_connection(self):
        """
        Fournit une connexion à la base de données.
        
        Returns:
            sqlite3.Connection: Connexion à la base de données
        """
        return sqlite3.connect(self.db_path) 