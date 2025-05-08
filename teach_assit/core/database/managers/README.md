# Module de gestion de la base de données

Ce package contient les différents gestionnaires spécialisés pour la base de données SQLite de TeachAssist.

## Structure

- `connection_provider.py` : Gestionnaire de connexion à la base de données
- `schema_manager.py` : Gestionnaire du schéma de la base de données
- `zip_manager.py` : Gestionnaire des fichiers ZIP et des dossiers extraits
- `exercise_manager.py` : Gestionnaire des configurations d'exercices
- `assessment_manager.py` : Gestionnaire des configurations d'évaluations
- `settings_manager.py` : Gestionnaire des paramètres de l'application
- `feedback_manager.py` : Gestionnaire des feedbacks stockés

## Architecture

L'architecture a été conçue selon le principe de responsabilité unique (SRP) pour faciliter la maintenance :

- Chaque gestionnaire est spécialisé dans un type d'entité spécifique
- Les dépendances sont clairement définies (tous les gestionnaires dépendent de ConnectionProvider)
- Le DatabaseManager principal délègue les opérations aux gestionnaires spécialisés

## Utilisation

Le module principal `DatabaseManager` continue d'offrir une interface unifiée pour accéder aux différentes fonctionnalités :

```python
from teach_assit.core.database.db_manager import DatabaseManager

# Initialiser le gestionnaire de base de données
db_manager = DatabaseManager()

# Utiliser les fonctionnalités comme avant
db_manager.add_exercise_config(config)
db_manager.get_all_zip_files()
db_manager.save_setting("theme", "dark")
```

## Avantages

Cette architecture modulaire offre plusieurs avantages :

1. **Maintenabilité** : Des fichiers plus courts, plus faciles à comprendre et à maintenir
2. **Testabilité** : Possibilité de tester chaque gestionnaire indépendamment
3. **Découplage** : Les modifications d'un gestionnaire n'affectent pas les autres
4. **Extensibilité** : Facilité pour ajouter de nouveaux gestionnaires