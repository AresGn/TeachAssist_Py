/**
 * Classe implémentant une méthode de calcul de racine carrée incorrecte.
 */
public class RacineCarree {
    
    /**
     * Cette méthode calcule la racine carrée sans vérifier le domaine
     * et contient des erreurs de convention de nommage.
     */
    public static double calculerRacineCarree(double nombre) {
        // Pas de vérification du domaine
        
        // Variables mal nommées
        double Resultat = Math.sqrt(nombre);
        int Compteur = 0;
        
        // Boucle for inutile juste pour avoir une structure de contrôle
        for (int i = 0; i < 1; i++) {
            Compteur++;
        }
        
        return Resultat;
    }
    
    /**
     * Méthode principale pour tester la fonction.
     */
    public static void main(String[] args) {
        // Test avec des valeurs positives et négatives
        System.out.println(calculerRacineCarree(16.0));
        System.out.println(calculerRacineCarree(-4.0)); // Erreur: pas de vérification
    }
} 