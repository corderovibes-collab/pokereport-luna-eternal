import java.io.File;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.List;
import java.util.StringTokenizer;

/**
 * Lanzador puente para Pterodactyl.
 *
 * El egg del panel arranca siempre "java -Xms128M -Xmx<RAM>M -jar server.jar" y no
 * se puede editar desde la API de cliente. Ese comando pone el heap de Java al 100%
 * del limite del contenedor, sin margen para metaspace, GC ni buffers -> OOM kill.
 *
 * Este jar ocupa el lugar de server.jar, lee las flags de jvm-args.txt y arranca el
 * Fabric real (fabric-server-launch.jar) en un proceso hijo con memoria acotada.
 * La consola del panel sigue funcionando porque heredamos stdin/stdout/stderr.
 */
public final class Launcher {

    private static final String ARGS_FILE = "jvm-args.txt";
    private static final String TARGET_JAR = "fabric-server-launch.jar";

    public static void main(String[] args) throws Exception {
        List<String> cmd = new ArrayList<String>();
        cmd.add(System.getProperty("java.home") + File.separator + "bin" + File.separator + "java");

        File flags = new File(ARGS_FILE);
        if (flags.isFile()) {
            for (String line : Files.readAllLines(flags.toPath(), StandardCharsets.UTF_8)) {
                String s = line.trim();
                if (s.isEmpty() || s.startsWith("#")) {
                    continue;
                }
                StringTokenizer st = new StringTokenizer(s);
                while (st.hasMoreTokens()) {
                    cmd.add(st.nextToken());
                }
            }
        } else {
            System.out.println("[launcher] " + ARGS_FILE + " no encontrado, usando flags por defecto");
            cmd.add("-Xms4096M");
            cmd.add("-Xmx12288M");
            cmd.add("-XX:+UseG1GC");
        }

        cmd.add("-jar");
        cmd.add(TARGET_JAR);
        cmd.add("nogui");

        System.out.println("[launcher] arrancando: " + join(cmd));
        final Process child = new ProcessBuilder(cmd).inheritIO().start();

        // El panel para el servidor con SIGTERM: propagarlo para que Minecraft guarde y cierre.
        Runtime.getRuntime().addShutdownHook(new Thread() {
            @Override
            public void run() {
                child.destroy();
                try {
                    child.waitFor();
                } catch (InterruptedException ignored) {
                    Thread.currentThread().interrupt();
                }
            }
        });

        System.exit(child.waitFor());
    }

    private static String join(List<String> parts) {
        StringBuilder sb = new StringBuilder();
        for (String p : parts) {
            if (sb.length() > 0) {
                sb.append(' ');
            }
            sb.append(p);
        }
        return sb.toString();
    }
}
