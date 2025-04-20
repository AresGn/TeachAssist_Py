/**
 * Programme qui affiche des séquences numériques avec quelques erreurs
 */
public class SequenceNumeriqueAvecErreur {
    
    public static void main(String[] args) {
        // Appeler les méthodes pour afficher les séquences
        System.out.println("Affichage en ligne:");
        afficherLigne();
        
        System.out.println("\nAffichage en triangle:");
        afficherTriangle();
    }
    
    /**
     * Affiche les valeurs de 1 à 9 en ligne - avec erreur (i > 9 au lieu de i <= 9)
     */
    public static void afficherLigne() {
        for (int i = 1; i > 9; i++) {  // ERREUR: condition incorrecte i > 9 (ne sera jamais exécuté)
            System.out.print(i);
        }
        // ERREUR: oubli du saut de ligne
    }
    
    /**
     * Affiche les valeurs de 1 à 9 en forme de triangle
     */
    public static void afficherTriangle() {
        // Utilisation de while au lieu de for (non conforme aux règles)
        int i = 1;
        while (i <= 9) {
            for (int j = 1; j <= i; j++) {
                System.out.print(j);
            }
            System.out.println();
            i++;
        }
    }
}
