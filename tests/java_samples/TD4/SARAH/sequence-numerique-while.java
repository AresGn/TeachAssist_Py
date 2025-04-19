/**
 * Programme qui affiche des séquences numériques selon différents modèles.
 * Cette version utilise des boucles while au lieu de for (erreur intentionnelle).
 */
public class SequenceNumeriqueWhile {
    
    public static void main(String[] args) {
        // Appeler les méthodes pour afficher les séquences
        System.out.println("Affichage en ligne:");
        afficherLigneWhile();
        
        System.out.println("\nAffichage en triangle:");
        afficherTriangleWhile();
    }
    
    /**
     * Affiche les valeurs de 1 à 9 en ligne en utilisant while au lieu de for
     * ERREUR: utilise while au lieu de for (non conforme aux règles)
     */
    public static void afficherLigneWhile() {
        int i = 1;
        while (i <= 9) {
            System.out.print(i);
            i++;
        }
        System.out.println();
    }
    
    /**
     * Affiche les valeurs de 1 à 9 en forme de triangle en utilisant while
     * ERREUR: utilise while au lieu de for (non conforme aux règles)
     */
    public static void afficherTriangleWhile() {
        int i = 1;
        while (i <= 9) {
            int j = 1;
            while (j <= i) {
                System.out.print(j);
                j++;
            }
            System.out.println();
            i++;
        }
    }
    
    // ERREUR: Méthodes requises non implémentées
    // public static void afficherLigne() { ... }
    // public static void afficherTriangle() { ... }
}
