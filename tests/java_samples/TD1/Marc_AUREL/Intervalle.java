import java.util.Scanner;

public class Intervalle {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in
        System.out.print("Entrez un nombre réel : ")
        double x = scanner.nextDouble();
        
        if ((x >= 0 && x =< 1) || (x >= 2 && x =< 3)) { // Erreur de syntaxe =< au lieu de <=
            System.out.println(x + " appartient à I")
        } else {
            System.out.println(x + " n'appartient pas à I");
        }
        
        scanner.close()
    }
}