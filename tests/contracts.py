"""Local HTTP contract checks; this fixture does not prove cloud research completion."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[1]
seen = []
scenario = "success"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def handle_request(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
        seen.append((self.command, self.path, dict(self.headers), json.loads(body) if body else None))
        code = {"unauthorized": 401, "redirect": 307}.get(scenario, 200)
        if scenario == "success" and self.path == "/v1/responses":
            code = 202
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("X-Request-ID", "req_fixture")
        if scenario == "redirect":
            self.send_header("Location", "/redirected")
        self.end_headers()
        self.wfile.write(json.dumps({"id": "resp_example", "status": "completed", "output_text": "Fixture answer", "items": [], "next_cursor": None}).encode())

    do_GET = do_POST = handle_request


def check(command, env):
    global scenario
    question, cursor = 'Research "可穿戴" feedback\nwith links.', "opaque+中文/&="
    for action in ["create", "get", "records", "cancel"]:
        seen.clear()
        args = [action, question if action == "create" else "resp_example"]
        if action == "records":
            args.append(cursor)
        result = subprocess.run(command + args, env=env, text=True, capture_output=True, timeout=45)
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)["id"] == "resp_example"
        assert len(seen) == 1, seen
        method, path, headers, body = seen[0]
        headers = {k.lower(): v for k, v in headers.items()}
        assert headers["authorization"] == "Bearer fixture-key-never-use-in-production"
        assert method == ("POST" if action in {"create", "cancel"} else "GET")
        if action == "create":
            assert path == "/v1/responses"
            assert body == {"model": "socai-research", "background": True, "input": question}
            assert headers["idempotency-key"] == "fixture-stable-operation"
        elif action == "records":
            assert urlsplit(path).path == "/v1/responses/resp_example/records"
            assert parse_qs(urlsplit(path).query) == {"limit": ["20"], "cursor": [cursor]}
        else:
            assert path == "/v1/responses/resp_example" + ("/cancel" if action == "cancel" else "")
    for failure in ["unauthorized", "redirect"]:
        scenario = failure
        seen.clear()
        result = subprocess.run(command + ["get", "resp_example"], env=env, text=True, capture_output=True, timeout=45)
        assert result.returncode != 0
        assert len(seen) == 1, "Do not follow redirects or retry automatically."
        assert env["SOCAI_API_KEY"] not in result.stderr + result.stdout
    scenario = "success"
    seen.clear()
    result = subprocess.run(command + ["create", question], env={k:v for k,v in env.items() if k != "SOCAI_IDEMPOTENCY_KEY"}, text=True, capture_output=True, timeout=45)
    assert result.returncode != 0
    assert not seen, "Creation without a stable operation key must not reach the server."
    print(f"PASS {' '.join(command[:2])}: four operations, cursor, auth failure, redirect and missing idempotency")


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    env = {**os.environ, "SOCAI_API_BASE_URL": f"http://127.0.0.1:{server.server_port}/v1",
           "SOCAI_API_KEY": "fixture-key-never-use-in-production", "SOCAI_IDEMPOTENCY_KEY": "fixture-stable-operation"}
    try:
        with tempfile.TemporaryDirectory(prefix="socai-examples-") as folder:
            commands = {"python": [sys.executable, str(ROOT / "python/demo.py")],
                        "javascript": ["node", str(ROOT / "javascript/demo.mjs")],
                        "typescript": ["node", str(ROOT / "typescript/demo.ts")],
                        "ruby": ["ruby", str(ROOT / "ruby/demo.rb")]}
            languages = sys.argv[1:] or ["python", "javascript", "typescript", "go", "ruby"]
            if "go" in languages:
                binary = str(Path(folder) / "go-demo")
                subprocess.run(["go", "build", "-o", binary, "."], cwd=ROOT / "go", check=True)
                commands["go"] = [binary]
            if "rust" in languages:
                subprocess.run(["cargo", "build", "--locked"], cwd=ROOT / "rust", check=True)
                commands["rust"] = [str(ROOT / "rust/target/debug/socai-api-example")]
            if "java" in languages:
                subprocess.run(["javac", "-d", folder, str(ROOT / "java/Demo.java")], check=True)
                commands["java"] = ["java", "-cp", folder, "Demo"]
            if "swift" in languages:
                binary = str(Path(folder) / "swift-demo")
                subprocess.run(["swiftc", str(ROOT / "swift/demo.swift"), "-o", binary], check=True)
                commands["swift"] = [binary]
            if "csharp" in languages:
                output = str(Path(folder) / "csharp")
                subprocess.run(["dotnet", "build", "-o", output], cwd=ROOT / "csharp", check=True)
                commands["csharp"] = ["dotnet", str(Path(output) / "SocaiExample.dll")]
            if "php" in languages:
                commands["php"] = ["php", str(ROOT / "php/demo.php")]
            if "kotlin" in languages:
                jar = str(Path(folder) / "kotlin-demo.jar")
                subprocess.run(["kotlinc", str(ROOT / "kotlin/Demo.kt"), "-include-runtime", "-d", jar], check=True)
                commands["kotlin"] = ["java", "-jar", jar]
            for language in languages:
                assert shutil.which(commands[language][0]), f"Install the {language} runtime."
                check(commands[language], env)
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
