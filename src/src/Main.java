import java.util.*;


public class Main {
    public static String Spassword;
    private final int max_size = 7;
    private int worker_threads = 2;
    private final int length = 3;
    private ArrayList<Attempt> currentProcesses = new ArrayList<>();
    private Queue<Attempt> data_pipe = new LinkedList<>();

    private final char[] chars = {
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
            ')', '!', '@', '#', '$', '%', '^', '&', '*', '('
    };

    public static void main(String[] args){
        Spassword = "jbeee";
    }

}
