import java.math.BigInteger;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

public class Hasher {
    private String hash = "";
    private String input;

    public Hasher(String input){
        this.input = input;
    }
    private void computeHash() throws NoSuchAlgorithmException {
        // CODE CREDIT GOES TO geeksforgeeks.com

        // Static getInstance method is called with hashing MD5
        MessageDigest md = MessageDigest.getInstance("SHA-256");

        // digest() method is called to calculate message digest
        //  of an input digest() return array of byte
        byte[] messageDigest = md.digest(input.getBytes());

        // Convert byte array into signum representation
        BigInteger no = new BigInteger(1, messageDigest);

        // Convert message digest into hex value
        StringBuilder hashtext = new StringBuilder(no.toString(16));
        while (hashtext.length() < 32) {
            hashtext.insert(0, "0");
        }
        this.hash = hashtext.toString();

    }
    public String getHash() throws NoSuchAlgorithmException {
        computeHash();
        return this.hash;
    }
    public void setInput(String input){
        this.input = input;
    }
}
