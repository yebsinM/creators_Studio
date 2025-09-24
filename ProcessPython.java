

public class ProcessPython {
    public static void main(String[] args) {
        try {
            ProcessBuilder pb = new ProcessBuilder("python", "app.py");
            pb.inheritIO(); 
            Process process = pb.start();
            process.waitFor();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}

