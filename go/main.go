package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"regexp"
	"strings"
	"time"
)

func run() error {
	if len(os.Args) < 3 {
		return fmt.Errorf("use create/get/records/cancel and a value")
	}
	action, value := os.Args[1], os.Args[2]
	base, key := strings.TrimRight(os.Getenv("SOCAI_API_BASE_URL"), "/"), os.Getenv("SOCAI_API_KEY")
	if base == "" || key == "" {
		return fmt.Errorf("set SOCAI_API_BASE_URL and SOCAI_API_KEY")
	}
	method, path := "GET", "/responses"
	var body []byte
	if action == "create" {
		if os.Getenv("SOCAI_IDEMPOTENCY_KEY") == "" {
			return fmt.Errorf("set a stable SOCAI_IDEMPOTENCY_KEY")
		}
		method = "POST"
		body, _ = json.Marshal(map[string]any{"model": "socai-research", "background": true, "input": value})
	} else {
		if !regexp.MustCompile(`^resp_[A-Za-z0-9_-]+$`).MatchString(value) {
			return fmt.Errorf("use a Response ID returned by create")
		}
		path += "/" + value
		switch action {
		case "get":
		case "records":
			query := url.Values{"limit": {"20"}}
			if len(os.Args) > 3 {
				query.Set("cursor", os.Args[3])
			}
			path += "/records?" + query.Encode()
		case "cancel":
			method, path = "POST", path+"/cancel"
		default:
			return fmt.Errorf("use create, get, records or cancel")
		}
	}
	request, err := http.NewRequest(method, base+path, bytes.NewReader(body))
	if err != nil {
		return err
	}
	request.Header.Set("Authorization", "Bearer "+key)
	request.Header.Set("Content-Type", "application/json")
	if action == "create" {
		request.Header.Set("Idempotency-Key", os.Getenv("SOCAI_IDEMPOTENCY_KEY"))
	}
	client := &http.Client{Timeout: 30 * time.Second, CheckRedirect: func(*http.Request, []*http.Request) error { return http.ErrUseLastResponse }}
	response, err := client.Do(request)
	if err != nil {
		return err
	}
	defer response.Body.Close()
	if response.StatusCode < 200 || response.StatusCode >= 300 {
		return fmt.Errorf("HTTP %d; request ID: %s", response.StatusCode, response.Header.Get("X-Request-ID"))
	}
	_, err = io.Copy(os.Stdout, response.Body)
	return err
}

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
