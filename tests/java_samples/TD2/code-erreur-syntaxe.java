public class CalculMoyenne {
    /**
     * Calcule la moyenne de trois entiers
     * @param a premier entier
     * @param b deuxième entier
     * @param c troisième entier
     * @return la moyenne des trois entiers sous forme de double
     */
    public static double moyenneCalcul(int a, int b, int c) { // Nom de méthode incorrect (devrait être calculerMoyenne)
        double somme = a + b + c;
        return somme / 3.0
    } // Erreur de syntaxe : point-virgule manquant
    
    public static void main(String[] args) {
        // Test de la méthode
        double resultat = moyenneCalcul(10, 20, 30);
        System.out.println("La moyenne est : " + resultat);
    }
}
