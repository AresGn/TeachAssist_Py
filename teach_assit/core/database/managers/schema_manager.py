"""
Gestionnaire du schéma de la base de données.
Gère la création et la mise à jour de la structure de la base de données.
"""

import sqlite3

class SchemaManager:
    """Gestionnaire du schéma de la base de données."""
    
    def __init__(self, connection_provider):
        """
        Initialise le gestionnaire de schéma.
        
        Args:
            connection_provider: Fournisseur de connexion à la base de données
        """
        self.connection_provider = connection_provider
    
    def initialize_database(self):
        """
        Initialise la structure de la base de données si elle n'existe pas.
        
        Returns:
            bool: True si l'initialisation a réussi
        """
        conn = self.connection_provider.get_connection()
        cursor = conn.cursor()
        
        try:
            # Table pour les fichiers ZIP
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS zip_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                md5_hash TEXT,
                description TEXT
            )
            ''')
            
            # Table pour les dossiers extraits
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS extracted_folders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                zip_id INTEGER NOT NULL,
                folder_path TEXT NOT NULL,
                extraction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (zip_id) REFERENCES zip_files (id)
            )
            ''')
            
            # Table pour les fichiers individuels dans les dossiers extraits
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS extracted_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                folder_id INTEGER NOT NULL,
                filepath TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                file_type TEXT,
                FOREIGN KEY (folder_id) REFERENCES extracted_folders (id)
            )
            ''')
            
            # Table pour les configurations d'exercices
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS exercise_configs (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                difficulty INTEGER DEFAULT 1,
                test_inputs TEXT,  -- Stockage JSON des entrées de test
                rules TEXT,        -- Stockage JSON des règles
                grading_criteria TEXT,  -- Stockage JSON des critères d'évaluation
                last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Table pour les configurations d'évaluations
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS assessment_configs (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                exercises TEXT,     -- Stockage JSON des exercices
                total_max_points INTEGER DEFAULT 0,
                last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Table pour les paramètres de l'application
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS application_settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                description TEXT,
                last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Table pour les feedbacks générés
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedbacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL,
                assessment_id TEXT,
                feedback_content TEXT NOT NULL,
                global_grade TEXT,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                hash_id TEXT UNIQUE,
                FOREIGN KEY (assessment_id) REFERENCES assessment_configs (id) ON DELETE SET NULL
            )
            ''')
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erreur lors de l'initialisation de la base de données: {e}")
            conn.rollback()
            return False 