import java.util.Scanner;

public class Exercice2 {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        System.out.print("Entrez n: ");
        int n = sc.nextInt();
        
        for (int i = 1; i <= n; i++) {
            // Espaces
            for (int j = 1; j <= n - i; j++) {
                System.out.print(" ");
            }
            // Etoiles
            for (int k = 1; k <= 2 * i - 1; k++) {
                System.out.print("*");
            }
            System.out.println();
        }
    }
}