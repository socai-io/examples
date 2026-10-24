# Rust

Install stable Rust and configure the [environment](../README.md#quickstart). This example uses blocking `ureq`, `serde_json` and `url` rather than introducing an async runtime.

```bash
cargo run --locked -- create 'Research recent AI wearable feedback on X, with original links.'
cargo run --locked -- get resp_REPLACE_WITH_REAL_ID
cargo run --locked -- records resp_REPLACE_WITH_REAL_ID 'NEXT_CURSOR'
cargo run --locked -- cancel resp_REPLACE_WITH_REAL_ID
```

Omit the cursor for the first page. Poll the same ID while active and resume it after platform sign-in. Save a stable idempotency key before creation. Requests have a 30-second limit, do not follow redirects, and do not automatically create replacement work after a timeout.
