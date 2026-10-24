#!/usr/bin/env python3
import json
import os
import re
import sys
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def main():
    action, value, *extra = sys.argv[1:]
    base = os.environ["SOCAI_API_BASE_URL"].rstrip("/")
    key = os.environ["SOCAI_API_KEY"]
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    body = None
    if action == "create":
        headers["Idempotency-Key"] = os.environ["SOCAI_IDEMPOTENCY_KEY"]
        body = json.dumps({"model": "socai-research", "background": True, "input": value}).encode()
        method, path = "POST", "/responses"
    else:
        if not re.fullmatch(r"resp_[A-Za-z0-9_-]+", value):
            raise ValueError("Use a Response ID returned by create.")
        method, path = "GET", f"/responses/{value}"
        if action == "records":
            path += "/records?" + urlencode({"limit": 20, **({"cursor": extra[0]} if extra else {})})
        elif action == "cancel":
            method, path = "POST", path + "/cancel"
        elif action != "get":
            raise ValueError("Use create, get, records or cancel.")
    try:
        with build_opener(NoRedirect()).open(Request(base + path, data=body, headers=headers, method=method), timeout=30) as response:
            print(response.read().decode())
    except HTTPError as error:
        raise RuntimeError(f"HTTP {error.code}; request ID: {error.headers.get('X-Request-ID', 'unavailable')}") from None


if __name__ == "__main__":
    try:
        main()
    except (KeyError, ValueError, OSError, RuntimeError) as error:
        print(str(error).replace(os.environ.get("SOCAI_API_KEY") or "__missing_key__", "[redacted]"), file=sys.stderr)
        sys.exit(1)
