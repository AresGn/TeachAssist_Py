/**
 * Classe de validation sans la méthode estMajeur requise.
 */
public class ValidationMissingMethod {
    
    /**
     * Vérifie si une personne est majeure mais avec un nom différent.
     */
    public boolean verifierAge(int age) {
        return age >= 18;
    }
    
    /**
     * Méthode main pour tester.
     */
    public static void main(String[] args) {
        ValidationMissingMethod validator = new ValidationMissingMethod();
        System.out.println("18 ans: " + validator.verifierAge(18));
    }
} 