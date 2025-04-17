public class CalculMoyenne {
    /**
     * Calcule la moyenne de trois entiers
     * @param a premier entier
     * @param b deuxième entier
     * @param c troisième entier
     * @return la moyenne des trois entiers sous forme de double
     */
    public static double calculerMoyenne(int a, int b, int c) {
        double somme = a + b + c;
        return somme / 3.0;
    }
    
    public static void main(String[] args) {
        // Test de la méthode
        double resultat = calculerMoyenne(10, 20, 30);
        System.out.println("La moyenne est : " + resultat);
    }
}
