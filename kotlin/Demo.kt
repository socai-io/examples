import java.net.URI
import java.net.URLEncoder
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse
import java.nio.charset.StandardCharsets
import java.time.Duration
import kotlin.system.exitProcess

fun env(name: String): String = System.getenv(name)?.takeIf { it.isNotEmpty() }
    ?: error("Set $name.")

fun quote(value: String): String = buildString {
    append('"')
    for (c in value) when {
        c == '"' || c == '\\' -> { append('\\'); append(c) }
        c.code < 32 -> append("\\u%04x".format(c.code))
        else -> append(c)
    }
    append('"')
}

fun main(args: Array<String>) {
    try {
        require(args.size >= 2) { "Use create/get/records/cancel and a value." }
        val (action, value) = args
        var path = "/responses"
        val request = HttpRequest.newBuilder().timeout(Duration.ofSeconds(30))
            .header("Authorization", "Bearer ${env("SOCAI_API_KEY")}").header("Content-Type", "application/json")
        if (action == "create") {
            request.header("Idempotency-Key", env("SOCAI_IDEMPOTENCY_KEY"))
            request.POST(HttpRequest.BodyPublishers.ofString("""{"model":"socai-research","background":true,"input":${quote(value)}}"""))
        } else {
            require(value.matches(Regex("resp_[A-Za-z0-9_-]+"))) { "Use a Response ID returned by create." }
            path += "/$value"
            when (action) {
                "get" -> request.GET()
                "records" -> {
                    path += "/records?limit=20" + if (args.size > 2) "&cursor=" + URLEncoder.encode(args[2], StandardCharsets.UTF_8) else ""
                    request.GET()
                }
                "cancel" -> { path += "/cancel"; request.POST(HttpRequest.BodyPublishers.noBody()) }
                else -> error("Use create, get, records or cancel.")
            }
        }
        request.uri(URI.create(env("SOCAI_API_BASE_URL").trimEnd('/') + path))
        val client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(30)).followRedirects(HttpClient.Redirect.NEVER).build()
        val response = client.send(request.build(), HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8))
        check(response.statusCode() in 200..299) { "HTTP ${response.statusCode()}; request ID: ${response.headers().firstValue("X-Request-ID").orElse("unavailable")}" }
        println(response.body())
    } catch (error: Exception) {
        System.err.println((error.message ?: "Request failed.").replace(System.getenv("SOCAI_API_KEY")?.takeIf { it.isNotEmpty() } ?: "__missing_key__", "[redacted]"))
        exitProcess(1)
    }
}
