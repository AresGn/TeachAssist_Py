/**
 * Classe de validation correcte avec la méthode estMajeur bien implémentée.
 */
public class ValidationCorrect {
    
    /**
     * Vérifie si une personne est majeure.
     * 
     * @param age L'âge de la personne
     * @return true si la personne est majeure (>= 18 ans), false sinon
     */
    public boolean estMajeur(int age) {
        // Vérification si l'âge est valide
        if (age < 0) {
            System.out.println("L'âge ne peut pas être négatif");
            return false;
        }
        
        // Vérification de la majorité
        return age >= 18;
    }
    
    /**
     * Méthode main pour tester manuellement.
     */
    public static void main(String[] args) {
        ValidationCorrect validator = new ValidationCorrect();
        
        System.out.println("17 ans: " + validator.estMajeur(17));
        System.out.println("18 ans: " + validator.estMajeur(18));
        System.out.println("21 ans: " + validator.estMajeur(21));
        System.out.println("-5 ans: " + validator.estMajeur(-5));
    }
} 