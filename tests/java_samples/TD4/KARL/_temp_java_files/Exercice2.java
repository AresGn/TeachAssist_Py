import java.util.Scanner;

public class Exercice2 {
    static void printSpaces(int count) {
        for (int i = 0; i < count; i++) {
            System.out.print(" ");
        }
    }
    
    static void printStars(int count) {
        for (int i = 0; i < count; i++) {
            System.out.print("*");
        }
    }
    
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        System.out.print("Entrez n: ");
        int n = sc.nextInt();
        
        for (int i = 1; i <= n; i++) {
            printSpaces(n - i);
            printStars(2 * i - 1);
            System.out.println();
        }
    }
}