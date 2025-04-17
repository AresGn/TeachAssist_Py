/**
 * Classe de validation avec une erreur de syntaxe.
 */
public class ValidationSyntaxError {
    
    /**
     * Vérifie si une personne est majeure.
     * ERREUR: Point-virgule manquant
     */
    public boolean estMajeur(int age) {
        return age >= 18
    }
    
    /**
     * Méthode main pour tester.
     */
    public static void main(String[] args) {
        ValidationSyntaxError validator = new ValidationSyntaxError();
        System.out.println("18 ans: " + validator.estMajeur(18));
    }
} 