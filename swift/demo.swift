import Foundation
#if canImport(FoundationNetworking)
import FoundationNetworking
#endif

func env(_ name: String) throws -> String {
    guard let value = ProcessInfo.processInfo.environment[name], !value.isEmpty else {
        throw NSError(domain: "Socai", code: 1, userInfo: [NSLocalizedDescriptionKey: "Set \(name)."])
    }
    return value
}

func fail(_ message: String) -> NSError {
    NSError(domain: "Socai", code: 1, userInfo: [NSLocalizedDescriptionKey: message])
}

final class NoRedirect: NSObject, URLSessionTaskDelegate {
    func urlSession(_ session: URLSession, task: URLSessionTask,
                    willPerformHTTPRedirection response: HTTPURLResponse,
                    newRequest request: URLRequest,
                    completionHandler: @escaping (URLRequest?) -> Void) {
        completionHandler(nil)
    }
}

do {
    let args = Array(CommandLine.arguments.dropFirst())
    guard args.count >= 2 else { throw fail("Use create/get/records/cancel and a value.") }
    let action = args[0], value = args[1]
    let base = try env("SOCAI_API_BASE_URL").trimmingCharacters(in: CharacterSet(charactersIn: "/"))
    var path = "/responses", body: Data? = nil, method = "GET"
    var operation: String? = nil
    if action == "create" {
        operation = try env("SOCAI_IDEMPOTENCY_KEY")
        method = "POST"
        body = try JSONSerialization.data(withJSONObject: ["model": "socai-research", "background": true, "input": value])
    } else {
        guard value.range(of: "^resp_[A-Za-z0-9_-]+$", options: .regularExpression) != nil else { throw fail("Use a Response ID returned by create.") }
        path += "/" + value
        if action == "records" { path += "/records" }
        else if action == "cancel" { method = "POST"; path += "/cancel" }
        else if action != "get" { throw fail("Use create, get, records or cancel.") }
    }
    guard var url = URLComponents(string: base + path) else { throw fail("Invalid API base URL.") }
    if action == "records" {
        url.queryItems = [URLQueryItem(name: "limit", value: "20")]
        if args.count > 2 { url.queryItems?.append(URLQueryItem(name: "cursor", value: args[2])) }
        url.percentEncodedQuery = url.percentEncodedQuery?.replacingOccurrences(of: "+", with: "%2B")
    }
    guard let endpoint = url.url else { throw fail("Invalid request URL.") }
    var request = URLRequest(url: endpoint, timeoutInterval: 30)
    request.httpMethod = method; request.httpBody = body
    request.setValue("Bearer \(try env("SOCAI_API_KEY"))", forHTTPHeaderField: "Authorization")
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    if let operation { request.setValue(operation, forHTTPHeaderField: "Idempotency-Key") }
    let configuration = URLSessionConfiguration.ephemeral
    configuration.timeoutIntervalForResource = 30
    let session = URLSession(configuration: configuration, delegate: NoRedirect(), delegateQueue: nil)
    let semaphore = DispatchSemaphore(value: 0)
    session.dataTask(with: request) { data, response, error in
        defer { semaphore.signal() }
        if let response = response as? HTTPURLResponse, (200..<300).contains(response.statusCode), let data {
            FileHandle.standardOutput.write(data)
        } else {
            let response = response as? HTTPURLResponse
            let message = error == nil ? "HTTP \(response?.statusCode ?? 0); request ID: \(response?.value(forHTTPHeaderField: "X-Request-ID") ?? "unavailable")" : "HTTP transport failed; creation may be uncertain. Reuse the same operation key."
            FileHandle.standardError.write(Data((message + "\n").utf8))
            exit(1)
        }
    }.resume()
    semaphore.wait()
    session.invalidateAndCancel()
} catch {
    FileHandle.standardError.write(Data((error.localizedDescription + "\n").utf8))
    exit(1)
}
