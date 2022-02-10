import java.security.NoSuchAlgorithmException;
import java.util.Objects;


public class Attempt extends Thread {
    public final int id;
    private final int length;
    private final Iterator[] workers;
    public boolean run = true;
    private double startTime = 0;
    public double endTime = 0;
    public Hasher hasher;

    public Attempt(int id, int length){
        this.id = id;
        this.length = length;
        this.workers = new Iterator[length];

        for(int x = 0; x < this.length; x++){
            this.workers[x] = new Iterator(x);
        }

        this.hasher = new Hasher("");
    }

    public String getTime(){
        double totalTime = this.endTime - this.startTime;
        totalTime /= 1000;  // Converts ms into seconds

        if(totalTime >= (3600)){
            return totalTime / (3600.0) + " hours";
        } else if(totalTime >= (60)){
            return totalTime / (60.0) + " minutes";
        } else {
            return totalTime + " seconds";
        }
    }
    private String concatenateDigits(){
        StringBuilder out = new StringBuilder();
        for(Iterator worker : this.workers){
            out.append(worker.digit);
        }

        return out.toString();
    }

    @Override
    public void run() {
        this.startTime = System.currentTimeMillis();

        try {
            while (!Objects.equals(this.hasher.getHash(), Main.password) && this.run) {
                this.workers[this.workers.length - 1].nextIteration(1, this.workers);

                if (this.workers[0].reset) {
                    this.workers[0].reset = false;
                    break;
                }
                this.hasher.setInput(concatenateDigits());
            }
        } catch(NoSuchAlgorithmException e){
            e.printStackTrace();
        }
        this.endTime = System.currentTimeMillis();

        this.hasher.setInput(concatenateDigits());
        try {
            if(Objects.equals(hasher.getHash(), Main.password) && this.run){
                    System.out.println("[Thread " + this.id + "]: Found password \"" + this.hasher.getHash() + "\" to be \"" + concatenateDigits() + "\" in " + getTime());
            } else {
                System.out.println("[Thread " + this.id + "]: Failed length " + this.length);
            }
        } catch (NoSuchAlgorithmException e) {
            e.printStackTrace();
        }
        this.run = false;
    }
}
