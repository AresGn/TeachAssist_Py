"""
Gestionnaire des paramètres de l'application dans la base de données.
"""

import sqlite3

class SettingsManager:
    """Gestionnaire des paramètres de l'application."""
    
    def __init__(self, connection_provider):
        """
        Initialise le gestionnaire de paramètres.
        
        Args:
            connection_provider: Fournisseur de connexion à la base de données
        """
        self.connection_provider = connection_provider
    
    def save_setting(self, key, value, description=None):
        """
        Sauvegarde un paramètre dans la base de données.
        
        Args:
            key (str): Clé du paramètre
            value (str): Valeur du paramètre
            description (str, optional): Description du paramètre
            
        Returns:
            bool: True si l'opération a réussi
        """
        conn = self.connection_provider.get_connection()
        cursor = conn.cursor()
        
        try:
            # Vérifier si le paramètre existe déjà
            cursor.execute('SELECT key FROM application_settings WHERE key = ?', (key,))
            existing = cursor.fetchone()
            
            if existing:
                # Mise à jour
                cursor.execute('''
                UPDATE application_settings
                SET value = ?, description = ?,
                    last_modified = CURRENT_TIMESTAMP
                WHERE key = ?
                ''', (value, description, key))
            else:
                # Insertion
                cursor.execute('''
                INSERT INTO application_settings 
                (key, value, description)
                VALUES (?, ?, ?)
                ''', (key, value, description))
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de la sauvegarde du paramètre {key}: {e}")
            conn.rollback()
            return False
    
    def get_setting(self, key, default_value=None):
        """
        Récupère la valeur d'un paramètre.
        
        Args:
            key (str): Clé du paramètre
            default_value: Valeur par défaut si le paramètre n'existe pas
            
        Returns:
            str: Valeur du paramètre ou default_value si non trouvé
        """
        conn = self.connection_provider.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT value FROM application_settings
            WHERE key = ?
            ''', (key,))
            
            row = cursor.fetchone()
            
            if row:
                return row[0]
            return default_value
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de la récupération du paramètre {key}: {e}")
            return default_value
    
    def delete_setting(self, key):
        """
        Supprime un paramètre.
        
        Args:
            key (str): Clé du paramètre
            
        Returns:
            bool: True si l'opération a réussi
        """
        conn = self.connection_provider.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            DELETE FROM application_settings
            WHERE key = ?
            ''', (key,))
            
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de la suppression du paramètre {key}: {e}")
            conn.rollback()
            return False
    
    def get_all_settings(self):
        """
        Récupère tous les paramètres.
        
        Returns:
            dict: Dictionnaire {clé: valeur} de tous les paramètres
        """
        conn = self.connection_provider.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT key, value FROM application_settings
            ''')
            
            settings = {}
            for row in cursor.fetchall():
                settings[row[0]] = row[1]
            
            return settings
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de la récupération des paramètres: {e}")
            return {} 