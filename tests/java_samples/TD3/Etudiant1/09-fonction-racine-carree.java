/**
 * Classe implémentant une méthode de calcul de racine carrée avec vérification du domaine.
 */
public class RacineCarree {
    
    /**
     * Calcule la racine carrée d'un nombre en vérifiant qu'il est positif ou nul.
     * 
     * @param nombre Le nombre dont on veut la racine carrée
     * @return La racine carrée du nombre, ou Double.NaN si le nombre est négatif
     */
    public static double calculerRacineCarree(double nombre) {
        // Vérification que le nombre est positif ou nul
        if (nombre < 0) {
            System.out.println("Erreur: Le nombre doit être positif ou nul");
            return Double.NaN; // Not a Number pour les cas invalides
        }
        
        // Calcul de la racine carrée
        return Math.sqrt(nombre);
    }
    
    /**
     * Méthode principale pour tester la fonction.
     */
    public static void main(String[] args) {
        double[] valeurs = {16.0, 25.0, 0.0, -4.0};
        
        for (double valeur : valeurs) {
            double resultat = calculerRacineCarree(valeur);
            if (Double.isNaN(resultat)) {
                System.out.println("La racine carrée de " + valeur + " n'est pas définie.");
            } else {
                System.out.println("La racine carrée de " + valeur + " est " + resultat);
            }
        }
    }
} 