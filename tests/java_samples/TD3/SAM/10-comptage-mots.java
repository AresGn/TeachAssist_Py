/**
 * Classe implémentant une méthode de comptage de mots dans une chaîne de caractères.
 */
public class CompteurMots {
    
    /**
     * Compte le nombre de mots dans une chaîne de caractères.
     * Les mots sont séparés par des espaces, tabulations, ou retours à la ligne.
     * 
     * @param texte La chaîne à analyser
     * @return Le nombre de mots, 0 si la chaîne est vide ou null
     */
    public static int compterMots(String texte) {
        // Vérification que la chaîne n'est pas null ou vide
        if (texte == null || texte.isEmpty()) {
            return 0;
        }
        
        // Supprimer les espaces en début et fin de chaîne
        String texteTrim = texte.trim();
        
        // Si après le trim la chaîne est vide, elle ne contenait que des espaces
        if (texteTrim.length() == 0) {
            return 0;
        }
        
        // Découper la chaîne en utilisant les espaces, tabulations, retours à la ligne
        String[] mots = texteTrim.split("\\s+");
        
        // Retourner le nombre de mots
        return mots.length;
    }
    
    /**
     * Méthode principale pour tester la fonction.
     */
    public static void main(String[] args) {
        String[] exemples = {
            "Bonjour le monde",
            "   Espaces   en   trop   ",
            "",
            null,
            "Un\tMot\tPar\tTabulation",
            "Sauts\nDe\nLigne"
        };
        
        for (String exemple : exemples) {
            if (exemple == null) {
                System.out.println("La chaîne null contient 0 mots: " + compterMots(exemple));
            } else {
                System.out.println("La chaîne \"" + exemple + "\" contient " + compterMots(exemple) + " mots.");
            }
        }
    }
} 