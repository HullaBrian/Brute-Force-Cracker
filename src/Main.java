import java.io.File;
import java.io.FileNotFoundException;
import java.security.NoSuchAlgorithmException;
import java.util.*;


public class Main {
    public static String password;
    private static int max_size = 0;
    private static int worker_threads = 0;
    private static int length = 0;
    private static ArrayList<Attempt> currentProcesses = new ArrayList<>();
    private static ArrayList<Attempt> thread_queue = new ArrayList<>();

    public static void main(String[] args) throws InterruptedException, FileNotFoundException, NoSuchAlgorithmException {
        System.out.println("[MAIN/INFO]: Starting configuration...");
        getConfig( new File("config.dat"));
        System.out.println("[MAIN/INFO]: Completed configuration!");
        checkThreads();

        System.out.print("[MAIN/QUEUER]: Populating thread queue...");
        for(int x = length; x < max_size; x++){
            Attempt attempt = new Attempt(x, length);
            attempt.setDaemon(true);
            thread_queue.add(attempt);
            length++;
        }
        System.out.println("Done!");

        System.out.print("[MAIN/QUEUER]: Queuing initial threads...");
        for(int x = 0; x < worker_threads; x++){
            currentProcesses.add(thread_queue.get(0));
            thread_queue.remove(thread_queue.get(0));
            currentProcesses.get(currentProcesses.size() - 1).start();
        }
        System.out.println("Done!");

        System.out.println("[MAIN/INFO]: Brute forcing password with " + worker_threads + " thread(s)...");
        while(currentProcesses.size() > 0){
            int processes1 = currentProcesses.size();
            killIdleThreads();
            int processes2 = currentProcesses.size();

            if (processes1 > processes2){
                for(int x = 0; x < processes1 - processes2; x++){
                    try{
                        System.out.println("[MAIN/INFO]: Started thread for length " + thread_queue.get(0).id);
                        currentProcesses.add(thread_queue.get(0));
                        thread_queue.remove(thread_queue.get(0));
                        currentProcesses.get(currentProcesses.size() - 1).start();
                    } catch(IndexOutOfBoundsException e){
                        for (Attempt attempt : currentProcesses){
                            attempt.join();
                        }
                        System.out.println("[MAIN/WARNING]: Exiting...");
                        System.exit(2);
                    }
                }
            }
        }
        System.out.println("[MAIN/WARNING]: Exiting...");
        System.exit(1);
    }
    static void checkThreads(){
        if(worker_threads > max_size){
            System.out.print("[MAIN/WARNING]: Number of threads exceeds max size. Setting threads to max...");
            worker_threads -= max_size;
            System.out.println("Done!\n[MAIN/INFO]: Thread count now " + worker_threads);
        }
    }
    static void killIdleThreads() throws NoSuchAlgorithmException {
        List<Attempt> toRemove = new ArrayList<Attempt>();
        for (Attempt attempt : currentProcesses) {
            if (!attempt.run) {
                if(attempt.hasher.getHash().equals(password)){
                    System.out.println("[MAIN/WARNING]: Exiting...");
                    System.exit(1);
                } else {
                    toRemove.add(attempt);
                }
            }
        }
        currentProcesses.removeAll(toRemove);
    }
    static void getConfig(File configFile) throws FileNotFoundException {
        Scanner scanner = new Scanner(configFile);

        try {
            while (scanner.hasNextLine()) {
                String[] line = scanner.nextLine().split(" ");

                switch (line[0]) {
                    case "max-size" -> max_size = Integer.parseInt(line[1]);
                    case "worker-threads" -> worker_threads = Integer.parseInt(line[1]);
                    case "start-length" -> length = Integer.parseInt(line[1]);
                    case "password" -> password = line[1];
                }
                System.out.println("[MAIN/CONFIG]: Configured " + line[0] + " to \"" + line[1] + "\"");
            }
        } catch (IndexOutOfBoundsException e) {
            System.out.println("Error loading configuration file");
        }
    }
}
