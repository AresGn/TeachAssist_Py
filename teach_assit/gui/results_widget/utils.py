"""
Fonctions et constantes utilitaires pour le module de résultats.
"""

# Symboles pour l'UI
SYMBOL_OK = "✅"
SYMBOL_FAIL = "❌"
SYMBOL_WARNING = "⚠️"

def fix_encoding(text):
    """Corriger l'encodage des caractères accentués"""
    if not text:
        return text
    
    # Tentatives de correction d'encodage
    try:
        # Si déjà en UTF-8 mais mal interprété
        return text.encode('latin1').decode('utf-8')
    except:
        try:
            # Si encodé en latin1
            return text.encode('latin1').decode('latin1')
        except:
            pass
    return text 