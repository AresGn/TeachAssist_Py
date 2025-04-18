/**
 * Implémentation incorrecte de l'exercice de comptage de mots.
 */
public class CompteurMots {
    
    /**
     * Méthode incorrecte qui compte les mots sans vérifier la chaîne null
     * et sans utiliser split.
     */
    public static int compterMots(String texte) {
        // Pas de vérification si texte est null ou vide
        
        int compteur = 0;
        boolean estDansUnMot = false;
        
        // Utilisation d'un algorithme manuel au lieu de split
        for (int i = 0; i < texte.length(); i++) {
            char c = texte.charAt(i);
            
            // Si c'est un espace, tabulation ou retour à la ligne
            if (c == ' ' || c == '\t' || c == '\n') {
                estDansUnMot = false;
            } 
            // Si c'est un caractère non-espace et qu'on n'est pas actuellement dans un mot
            else if (!estDansUnMot) {
                estDansUnMot = true;
                compteur++;
            }
        }
        
        return compteur;
    }
    
    /**
     * Méthode principale pour tester la fonction.
     */
    public static void main(String[] args) {
        // Tests - La méthode va planter avec null
        System.out.println(compterMots("Bonjour le monde"));
        System.out.println(compterMots("   Espaces   en   trop   "));
        System.out.println(compterMots(""));
        // System.out.println(compterMots(null)); // NullPointerException
    }
} 