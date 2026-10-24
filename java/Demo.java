import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;

public class Demo {
    static String env(String name) {
        String value = System.getenv(name);
        if (value == null || value.isEmpty()) throw new IllegalArgumentException("Set " + name + ".");
        return value;
    }
    static String quote(String value) {
        StringBuilder result = new StringBuilder("\"");
        for (char c : value.toCharArray()) {
            if (c == '"' || c == '\\') result.append('\\').append(c);
            else if (c < 32) result.append(String.format("\\u%04x", (int)c));
            else result.append(c);
        }
        return result.append('"').toString();
    }
    public static void main(String[] args) {
        try {
            if (args.length < 2) throw new IllegalArgumentException("Use create/get/records/cancel and a value.");
            String action = args[0], value = args[1], path = "/responses";
            HttpRequest.Builder request = HttpRequest.newBuilder().timeout(Duration.ofSeconds(30))
                .header("Authorization", "Bearer " + env("SOCAI_API_KEY")).header("Content-Type", "application/json");
            if (action.equals("create")) {
                request.header("Idempotency-Key", env("SOCAI_IDEMPOTENCY_KEY"));
                request.POST(HttpRequest.BodyPublishers.ofString("{\"model\":\"socai-research\",\"background\":true,\"input\":" + quote(value) + "}"));
            } else {
                if (!value.matches("resp_[A-Za-z0-9_-]+")) throw new IllegalArgumentException("Use a Response ID returned by create.");
                path += "/" + value;
                switch (action) {
                    case "get": request.GET(); break;
                    case "records":
                        path += "/records?limit=20" + (args.length > 2 ? "&cursor=" + URLEncoder.encode(args[2], StandardCharsets.UTF_8) : "");
                        request.GET(); break;
                    case "cancel": path += "/cancel"; request.POST(HttpRequest.BodyPublishers.noBody()); break;
                    default: throw new IllegalArgumentException("Use create, get, records or cancel.");
                }
            }
            request.uri(URI.create(env("SOCAI_API_BASE_URL").replaceAll("/$", "") + path));
            HttpClient client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(30)).followRedirects(HttpClient.Redirect.NEVER).build();
            HttpResponse<String> response = client.send(request.build(), HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8));
            if (response.statusCode() < 200 || response.statusCode() >= 300) throw new IllegalStateException("HTTP " + response.statusCode() + "; request ID: " + response.headers().firstValue("X-Request-ID").orElse("unavailable"));
            System.out.println(response.body());
        } catch (Exception error) {
            String key = System.getenv("SOCAI_API_KEY");
            System.err.println(String.valueOf(error.getMessage()).replace(key == null || key.isEmpty() ? "__missing_key__" : key, "[redacted]"));
            System.exit(1);
        }
    }
}
