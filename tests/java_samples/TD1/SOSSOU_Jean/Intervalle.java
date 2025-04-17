import java.util.Scanner;

public class Intervalle {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        System.out.print("Entrez un nombre réel : ");
        double x = scanner.nextDouble();
        
        // Utilisation uniquement des opérateurs < et == comme spécifié
        boolean dansIntervalle1 = !(x < 0) && !(x > 1); // équivalent à x >= 0 && x <= 1
        boolean dansIntervalle2 = !(x < 2) && !(x > 3); // équivalent à x >= 2 && x <= 3
        
        if (dansIntervalle1 || dansIntervalle2) {
            System.out.println(x + " appartient à I");
        } else {
            System.out.println(x + " n'appartient pas à I");
        }
        
        scanner.close();
    }
}