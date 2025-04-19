/**
 * Programme qui affiche des séquences numériques selon différents modèles.
 * Cette version utilise des boucles do-while et des opérateurs non autorisés.
 */
public class SequenceNumeriqueDoWhile {
    
    public static void main(String[] args) {
        // Appeler les méthodes pour afficher les séquences
        System.out.println("Affichage en ligne:");
        afficherLigne();
        
        System.out.println("\nAffichage en triangle:");
        afficherTriangle();
    }
    
    /**
     * Affiche les valeurs de 1 à 9 en ligne
     * ERREUR: utilise do-while au lieu de for et l'opérateur >= non autorisé
     */
    public static void afficherLigne() {
        int nombre = 1;
        do {
            System.out.print(nombre);
            nombre++; // Incrémentation
        } while (nombre >= 1 && nombre <= 9); // ERREUR: utilise l'opérateur >= non autorisé
    }
    
    /**
     * Affiche les valeurs de 1 à 9 en forme de triangle
     * ERREUR: utilise do-while au lieu de for et les opérateurs >= et != non autorisés
     */
    public static void afficherTriangle() {
        int ligne = 1;
        
        do {
            int colonne = 1;
            
            do {
                // ERREUR: utilise l'opérateur != non autorisé
                if (colonne != 10) {
                    System.out.print(colonne);
                }
                colonne++;
            } while (colonne <= ligne);
            
            System.out.println();
            ligne++;
        } while (ligne <= 9);
    }
}
