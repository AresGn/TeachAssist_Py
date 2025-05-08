"""
Gestionnaire des fichiers ZIP dans la base de données.
"""

import sqlite3

class ZipManager:
    """Gestionnaire des fichiers ZIP et des dossiers/fichiers extraits."""
    
    def __init__(self, connection_provider):
        """
        Initialise le gestionnaire de fichiers ZIP.
        
        Args:
            connection_provider: Fournisseur de connexion à la base de données
        """
        self.connection_provider = connection_provider
    
    def add_zip_file(self, filename, filepath, file_size, md5_hash=None, description=None):
        """
        Ajoute un fichier ZIP à la base de données.
        
        Args:
            filename (str): Nom du fichier ZIP
            filepath (str): Chemin complet vers le fichier
            file_size (int): Taille du fichier en octets
            md5_hash (str, optional): Hash MD5 du fichier pour vérification
            description (str, optional): Description du contenu du ZIP
            
        Returns:
            int: ID du fichier ZIP dans la base de données
        """
        conn = self.connection_provider.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO zip_files (filename, filepath, file_size, md5_hash, description)
        VALUES (?, ?, ?, ?, ?)
        ''', (filename, filepath, file_size, md5_hash, description))
        
        zip_id = cursor.lastrowid
        conn.commit()
        
        return zip_id
    
    def add_extracted_folder(self, zip_id, folder_path):
        """
        Ajoute un dossier extrait à la base de données.
        
        Args:
            zip_id (int): ID du fichier ZIP d'origine
            folder_path (str): Chemin vers le dossier extrait
            
        Returns:
            int: ID du dossier extrait
        """
        conn = self.connection_provider.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO extracted_folders (zip_id, folder_path)
        VALUES (?, ?)
        ''', (zip_id, folder_path))
        
        folder_id = cursor.lastrowid
        conn.commit()
        
        return folder_id
    
    def add_extracted_file(self, folder_id, filepath, file_size, file_type=None):
        """
        Ajoute un fichier extrait à la base de données.
        
        Args:
            folder_id (int): ID du dossier contenant le fichier
            filepath (str): Chemin vers le fichier
            file_size (int): Taille du fichier en octets
            file_type (str, optional): Type du fichier (extension)
            
        Returns:
            int: ID du fichier extrait
        """
        conn = self.connection_provider.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO extracted_files (folder_id, filepath, file_size, file_type)
        VALUES (?, ?, ?, ?)
        ''', (folder_id, filepath, file_size, file_type))
        
        file_id = cursor.lastrowid
        conn.commit()
        
        return file_id
    
    def get_all_zip_files(self):
        """
        Récupère tous les fichiers ZIP stockés dans la base de données.
        
        Returns:
            list: Liste de tuples contenant les informations des fichiers ZIP
        """
        conn = self.connection_provider.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, filename, filepath, file_size, upload_date, md5_hash, description
        FROM zip_files
        ORDER BY upload_date DESC
        ''')
        
        result = cursor.fetchall()
        
        return result
    
    def get_extracted_folders_by_zip(self, zip_id):
        """
        Récupère tous les dossiers extraits pour un fichier ZIP donné.
        
        Args:
            zip_id (int): ID du fichier ZIP
            
        Returns:
            list: Liste de tuples contenant les informations des dossiers
        """
        conn = self.connection_provider.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, folder_path, extraction_date, status
        FROM extracted_folders
        WHERE zip_id = ?
        ORDER BY extraction_date DESC
        ''', (zip_id,))
        
        result = cursor.fetchall()
        
        return result
    
    def get_files_by_folder(self, folder_id):
        """
        Récupère tous les fichiers d'un dossier extrait.
        
        Args:
            folder_id (int): ID du dossier
            
        Returns:
            list: Liste de tuples contenant les informations des fichiers
        """
        conn = self.connection_provider.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, filepath, file_size, file_type
        FROM extracted_files
        WHERE folder_id = ?
        ''', (folder_id,))
        
        result = cursor.fetchall()
        
        return result
    
    def delete_zip_file(self, zip_id):
        """
        Supprime un fichier ZIP et tous ses dossiers/fichiers associés.
        
        Args:
            zip_id (int): ID du fichier ZIP à supprimer
            
        Returns:
            bool: True si la suppression a réussi
        """
        conn = self.connection_provider.get_connection()
        cursor = conn.cursor()
        
        try:
            # Récupère tous les dossiers extraits
            cursor.execute('SELECT id FROM extracted_folders WHERE zip_id = ?', (zip_id,))
            folder_ids = [row[0] for row in cursor.fetchall()]
            
            # Supprime les fichiers extraits
            for folder_id in folder_ids:
                cursor.execute('DELETE FROM extracted_files WHERE folder_id = ?', (folder_id,))
            
            # Supprime les dossiers extraits
            cursor.execute('DELETE FROM extracted_folders WHERE zip_id = ?', (zip_id,))
            
            # Supprime le fichier ZIP
            cursor.execute('DELETE FROM zip_files WHERE id = ?', (zip_id,))
            
            conn.commit()
            return True
        except sqlite3.Error:
            conn.rollback()
            return False
    
    def update_extracted_folder_status(self, folder_id, status):
        """
        Met à jour le statut d'un dossier extrait.
        
        Args:
            folder_id (int): ID du dossier
            status (str): Nouveau statut ('active', 'archived', etc.)
            
        Returns:
            bool: True si la mise à jour a réussi
        """
        conn = self.connection_provider.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            UPDATE extracted_folders
            SET status = ?
            WHERE id = ?
            ''', (status, folder_id))
            
            conn.commit()
            return True
        except sqlite3.Error:
            conn.rollback()
            return False 