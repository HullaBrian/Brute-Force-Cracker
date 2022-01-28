import java.util.*;


public class Main {
    public static String Spassword;
    private static final int max_size = 7;
    private static int worker_threads = 2;
    private static int length = 3;
    private static ArrayList<Attempt> currentProcesses = new ArrayList<>();
    private static ArrayList<Attempt> thread_queue = new ArrayList<>();
    private static Queue<Attempt> data_pipe = new LinkedList<>();

    private final char[] chars = {
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
            ')', '!', '@', '#', '$', '%', '^', '&', '*', '('
    };

    public static void main(String[] args) throws InterruptedException {
        Spassword = "jbeee";

        System.out.print("[MAIN]: Populating thread queue...");
        for(int x = length; x < max_size; x++){
            Attempt attempt = new Attempt(x, length);
            attempt.setDaemon(true);
            thread_queue.add(attempt);
            length++;
        }
        System.out.println("Done!");

        System.out.print("[MAIN]: Queuing initial threads...");
        for(int x = 0; x < worker_threads; x++){
            currentProcesses.add(thread_queue.get(0));
            thread_queue.remove(thread_queue.get(0));
            currentProcesses.get(currentProcesses.size() - 1).start();
        }
        System.out.println("Done!");

        System.out.println("[MAIN]: Brute forcing password with " + worker_threads + " threads...");
        while(currentProcesses.size() > 0){
            int processes1 = currentProcesses.size();
            killIdleThreads();
            int processes2 = currentProcesses.size();

            if (processes1 > processes2){
                for(int x = 0; x < processes1 - processes2; x++){
                    try{
                        System.out.println("[MAIN]: Started thread for length " + thread_queue.get(0).id);
                        currentProcesses.add(thread_queue.get(0));
                        thread_queue.remove(thread_queue.get(0));
                        currentProcesses.get(currentProcesses.size() - 1).start();
                    } catch(IndexOutOfBoundsException e){
                        for (Attempt attempt : currentProcesses){
                            attempt.join();
                        }
                        System.out.println("[MAIN]: Exiting...");
                        System.exit(2);
                    }
                }
            }
        }
        System.out.println("[MAIN]: Exiting...");
        System.exit(1);
    }
    public void checkThreads(){
        if(worker_threads > max_size){
            System.out.print("[MAIN]: Number of threads exceeds max size. Setting threads to max...");
            worker_threads -= max_size;
            System.out.println("Done!\n[MAIN]: Thread count now " + worker_threads);
        }
    }
    static void killIdleThreads(){
        for (Attempt attempt : currentProcesses){
            if(!attempt.run){
                if(attempt.concatenateDigits().equals(Spassword)){
                    System.out.println("[MAIN]: Exiting...");
                    System.exit(1);
                } else {
                    currentProcesses.remove(attempt);
                }
            }
        }
    }
}
