using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;

try
{
    string Env(string name) => Environment.GetEnvironmentVariable(name) is { Length: > 0 } value
        ? value : throw new ArgumentException($"Set {name}.");
    if (args.Length < 2) throw new ArgumentException("Use create/get/records/cancel and a value.");
    var (action, value) = (args[0], args[1]);
    var path = "/responses";
    var request = new HttpRequestMessage();
    request.Method = HttpMethod.Get;
    request.Headers.Authorization = new("Bearer", Env("SOCAI_API_KEY"));
    if (action == "create")
    {
        request.Method = HttpMethod.Post;
        request.Headers.Add("Idempotency-Key", Env("SOCAI_IDEMPOTENCY_KEY"));
        request.Content = new StringContent(JsonSerializer.Serialize(new { model = "socai-research", background = true, input = value }), Encoding.UTF8, "application/json");
    }
    else
    {
        if (!Regex.IsMatch(value, @"\Aresp_[A-Za-z0-9_-]+\z")) throw new ArgumentException("Use a Response ID returned by create.");
        path += "/" + value;
        if (action == "records") path += "/records?limit=20" + (args.Length > 2 ? "&cursor=" + Uri.EscapeDataString(args[2]) : "");
        else if (action == "cancel") { request.Method = HttpMethod.Post; path += "/cancel"; }
        else if (action != "get") throw new ArgumentException("Use create, get, records or cancel.");
    }
    request.RequestUri = new Uri(Env("SOCAI_API_BASE_URL").TrimEnd('/') + path);
    using var client = new HttpClient(new HttpClientHandler { AllowAutoRedirect = false }) { Timeout = TimeSpan.FromSeconds(30) };
    using var response = await client.SendAsync(request);
    if (!response.IsSuccessStatusCode)
    {
        var id = response.Headers.TryGetValues("X-Request-ID", out var ids) ? ids.First() : "unavailable";
        throw new HttpRequestException($"HTTP {(int)response.StatusCode}; request ID: {id}");
    }
    Console.WriteLine(await response.Content.ReadAsStringAsync());
}
catch (Exception error)
{
    Console.Error.WriteLine(error.Message.Replace(Environment.GetEnvironmentVariable("SOCAI_API_KEY") is { Length: > 0 } key ? key : "__missing_key__", "[redacted]"));
    return 1;
}
return 0;
