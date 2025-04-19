import java.util.Scanner;

public class Exercice2 {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        System.out.print("Entrez n: ");
        int n = sc.nextInt();
        
        // Erreur: i commence à 0 au lieu de 1
        for (int i = 0; i < n; i++) {
            // Erreur: condition j < n - i au lieu de j <= n - i
            for (int j = 1; j < n - i; j++) {
                System.out.print(" ");
            }
            // Erreur: 2 * i + 2 au lieu de 2 * i - 1
            for (int k = 1; k <= 2 * i + 2; k++) {
                System.out.print("*");
            }
            System.out.println();
        }
    }
}