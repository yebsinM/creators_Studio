import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;

public class ProcessPython {
    public static void main(String[] args) throws IOException, InterruptedException {
        String ruta = "C:\\Users\\MULTI\\Documents\\creators\\creators_Studio\\app.py";
        Process p = new ProcessBuilder("py", ruta).start();

        InputStream salida = p.getInputStream();
        BufferedReader lector = new BufferedReader(new InputStreamReader(salida));
        
        String linea;
        while ((linea = lector.readLine()) != null) {
            System.out.println(linea);
        }

        int codigoSalida = p.waitFor();
        System.out.println("El proceso terminó con el código: " + codigoSalida);
    }
}