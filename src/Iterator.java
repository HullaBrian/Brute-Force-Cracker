public class Iterator {
    private final char[] chars = {
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
            ')', '!', '@', '#', '$', '%', '^', '&', '*', '('
    };
    private int i;
    public char digit;
    private final int id;
    public boolean reset;

    public Iterator(){
        this(-1);
        System.out.println("[MAIN/WARNING]: Iterator object initialized with id of -1!");
    }
    public Iterator(int id){
        this.i = 0;
        this.digit = chars[0];
        this.id = id;
        this.reset = false;
    }
    public void nextIteration(int step, Iterator[] workers){
        this.reset = false;
        if(this.i + step >= this.chars.length){
            if(this.id != 0){
                workers[this.id - 1].nextIteration(step, workers);
            }
            this.i = 0;
            this.reset = true;
        } else {
            this.i += step;
        }
        this.digit = this.chars[this.i];
    }
    public void nextIteration(Iterator[] workers){nextIteration(1, workers);}
}
