import java.util.Scanner;

/**
 * Programme qui affiche un triangle isocèle composé d'étoiles,
 * dont le nombre de lignes est saisi par l'utilisateur.
 */
public class TriangleIsocele {
    
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        System.out.print("Entrez le nombre de lignes du triangle: ");
        int nombreLignes = scanner.nextInt();
        
        afficherTriangleIsocele(nombreLignes);
        
        scanner.close();
    }
    
    /**
     * Affiche un triangle isocèle formé d'étoiles.
     * @param nombreLignes Nombre de lignes du triangle
     */
    public static void afficherTriangleIsocele(int nombreLignes) {
        // ERREUR: déclaration de variable incorrecte en dehors de la boucle
        int nombreEtoiles;
        
        for (int ligne = 1; ligne <= nombreLignes; ligne++) {
            // Calculer le nombre d'espaces et d'étoiles pour chaque ligne
            int nombreEspaces = nombreLignes - ligne;
            nombreEtoiles = 2 * ligne - 1;  // Référence à la variable déclarée en dehors de la boucle
            
            // Afficher les espaces avant les étoiles
            for (int i = 1; i <= nombreEspaces; i++) {
                System.out.print(" ");
            }
            
            // Afficher les étoiles
            for (int i = 1; i <= nombreEtoiles; i++) {
                System.out.print("*");
            }
            
            // Passer à la ligne suivante
            System.out.println();
        }
    }
}
