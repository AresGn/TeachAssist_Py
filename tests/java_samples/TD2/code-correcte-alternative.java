public class CalculMoyenne {
    /**
     * Calcule la moyenne de trois entiers
     * @param a premier entier
     * @param b deuxième entier
     * @param c troisième entier
     * @return la moyenne des trois entiers sous forme de double
     */
    public static double calculerMoyenne(int a, int b, int c) {
        int somme = a + b + c;
        double moyenne = (double) somme / 3.0;
        return moyenne;
    }
    
    public static void main(String[] args) {
        // Test de la méthode
        double resultat = calculerMoyenne(15, 25, 35);
        System.out.println("La moyenne est : " + resultat);
    }
}
