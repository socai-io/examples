use serde_json::json;
use std::{env, error::Error, time::Duration};

fn run() -> Result<(), Box<dyn Error>> {
    let args: Vec<String> = env::args().skip(1).collect();
    if args.len() < 2 {
        return Err("Use create/get/records/cancel and a value.".into());
    }
    let (action, value) = (args[0].as_str(), args[1].as_str());
    let base = env::var("SOCAI_API_BASE_URL")?;
    let key = env::var("SOCAI_API_KEY")?;
    let agent: ureq::Agent = ureq::Agent::config_builder()
        .timeout_global(Some(Duration::from_secs(30)))
        .max_redirects(0)
        .http_status_as_error(false)
        .build()
        .into();
    let mut endpoint = url::Url::parse(&format!("{}/responses", base.trim_end_matches('/')))?;
    let mut response = if action == "create" {
        let operation = env::var("SOCAI_IDEMPOTENCY_KEY")?;
        if operation.is_empty() {
            return Err("Set a stable SOCAI_IDEMPOTENCY_KEY.".into());
        }
        agent
            .post(endpoint.as_str())
            .header("Authorization", format!("Bearer {key}"))
            .header("Idempotency-Key", operation)
            .send_json(json!({"model":"socai-research", "background":true, "input":value}))?
    } else {
        if !value.starts_with("resp_")
            || !value
                .bytes()
                .all(|c| c.is_ascii_alphanumeric() || c == b'_' || c == b'-')
        {
            return Err("Use a Response ID returned by create.".into());
        }
        endpoint
            .path_segments_mut()
            .map_err(|_| "Invalid API base URL")?
            .push(value);
        match action {
            "get" => {}
            "records" => {
                endpoint.path_segments_mut().unwrap().push("records");
                endpoint.query_pairs_mut().append_pair("limit", "20");
                if let Some(cursor) = args.get(2) {
                    endpoint.query_pairs_mut().append_pair("cursor", cursor);
                }
            }
            "cancel" => {
                endpoint.path_segments_mut().unwrap().push("cancel");
            }
            _ => return Err("Use create, get, records or cancel.".into()),
        }
        if action == "cancel" {
            agent
                .post(endpoint.as_str())
                .header("Authorization", format!("Bearer {key}"))
                .send_empty()?
        } else {
            agent
                .get(endpoint.as_str())
                .header("Authorization", format!("Bearer {key}"))
                .call()?
        }
    };
    if !response.status().is_success() {
        return Err(format!(
            "HTTP {}; request ID: {}",
            response.status(),
            response
                .headers()
                .get("X-Request-ID")
                .and_then(|v| v.to_str().ok())
                .unwrap_or("unavailable")
        )
        .into());
    }
    println!("{}", response.body_mut().read_to_string()?);
    Ok(())
}

fn main() {
    if let Err(error) = run() {
        let key = env::var("SOCAI_API_KEY").unwrap_or_else(|_| "__missing_key__".into());
        eprintln!("{}", error.to_string().replace(&key, "[redacted]"));
        std::process::exit(1);
    }
}
