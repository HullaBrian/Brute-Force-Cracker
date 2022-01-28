import java.util.Objects;

public class Attempt extends Thread {
    private final int id;
    private final int length;
    private final Iterator[] workers;
    private boolean run = true;
    private double startTime = 0;
    public double endTime = 0;

    public Attempt(int id, int length){
        this.id = id;
        this.length = length;

        this.workers = new Iterator[length];
        for(int x = 0; x < this.length; x++){
            this.workers[x] = new Iterator();
        }
    }

    public String getTime(double startTime, double endTime){
        double totalTime = endTime - startTime;

        if(totalTime >= 3600){
            return totalTime / 3600.0 + " hours";
        } else if(totalTime >= 60){
            return totalTime / 60.0 + " minutes";
        } else {
            return totalTime + " seconds";
        }
    }
    public String concatonateDigits(){
        StringBuilder out = new StringBuilder();
        for(Iterator worker : this.workers){
            out.append(worker.getDigit());
        }
        return out.toString();
    }

    @Override
    public void run() {
        this.startTime = System.currentTimeMillis();

        while(!Objects.equals(concatonateDigits(), Main.Spassword) && this.run){
            this.workers[this.workers.length - 1].nextIteration(1, this.workers);

            if(this.workers[0].reset) {
                this.workers[0].reset = false;
                if (this.workers.length + 1 <= this.length){
                    System.out.println("oops...");
                } else {
                    break;
                }
            }
        }
    }
}
