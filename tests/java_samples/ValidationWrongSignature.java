/**
 * Classe de validation avec la méthode estMajeur mais avec une signature incorrecte.
 */
public class ValidationWrongSignature {
    
    /**
     * Vérifie si une personne est majeure mais avec un type de retour incorrect.
     * ERREUR: Le type de retour devrait être boolean au lieu de void.
     */
    public void estMajeur(int age) {
        System.out.println("Est majeur: " + (age >= 18));
    }
    
    /**
     * Méthode main pour tester.
     */
    public static void main(String[] args) {
        ValidationWrongSignature validator = new ValidationWrongSignature();
        validator.estMajeur(18);
    }
} 