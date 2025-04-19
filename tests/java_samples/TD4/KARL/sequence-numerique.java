/**
 * Programme qui affiche des séquences numériques selon différents modèles.
 */
public class SequenceNumerique {
    
    public static void main(String[] args) {
        // Appeler les méthodes pour afficher les séquences
        System.out.println("Affichage en ligne:");
        afficherLigne();
        
        System.out.println("\nAffichage en triangle:");
        afficherTriangle();
    }
    
    /**
     * Affiche les valeurs de 1 à 9 en ligne
     */
    public static void afficherLigne() {
        for (int i = 1; i <= 9; i++) {
            System.out.print(i);
        }
        System.out.println(); // Ajoute une nouvelle ligne à la fin
    }
    
    /**
     * Affiche les valeurs de 1 à 9 en forme de triangle
     */
    public static void afficherTriangle() {
        for (int i = 1; i <= 9; i++) {
            for (int j = 1; j <= i; j++) {
                System.out.print(j);
            }
            System.out.println();
        }
    }
}
