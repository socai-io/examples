<div align="center">

<h1>
  <a href="https://socai.io/"><img src="https://raw.githubusercontent.com/socai-io/socai/main/site/public/icon-192.png" width="36" alt="socai icon" align="absmiddle"></a>
  socai examples
</h1>

**Connect your app to real social research.**

**English** · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

[![website](https://img.shields.io/badge/website-socai.io-555?style=flat-square&color=blue)](https://socai.io/)
[![API reference](https://img.shields.io/badge/API-reference-555?style=flat-square&color=blue)](https://agent.socai.io/api/server/docs.md)

</div>

Small, server-side examples for the Socai hosted API. Every language exposes the same four operations: create research, read its answer, page its source records and cancel unfinished work. These examples use the cloud service, not your local Chrome.

## Quickstart

Sign in to Socai, open **API keys** in the sidebar, and create a key. Copy it once and save it in your server's secret manager.

```bash
export SOCAI_API_BASE_URL='https://agent.socai.io/api/server/v1'
# Set SOCAI_API_KEY securely in your server environment.
export SOCAI_IDEMPOTENCY_KEY="$(uuidgen)"
python3 python/demo.py create 'Research recent AI wearable feedback on X, with original links.'
```

For China, use `https://agentcn.socai.io/api/server/v1`. Dev uses `https://agent-dev.socai.io/api/server/v1` and is not a production endpoint.

Creation returns `202` and an `id`. Save that ID and the idempotency key; never retry uncertain creation with a new key.

```bash
python3 python/demo.py get resp_REPLACE_WITH_REAL_ID
python3 python/demo.py records resp_REPLACE_WITH_REAL_ID
# Cancel only if you intend to stop this task:
python3 python/demo.py cancel resp_REPLACE_WITH_REAL_ID
```

## Choose a language

Each directory contains a runnable example and its own setup instructions. All four operations use the same CLI arguments across languages.

| Language | Directory |
| --- | --- |
| Python | [python](python/) |
| JavaScript | [javascript](javascript/) |
| TypeScript | [typescript](typescript/) |
| Go | [go](go/) |
| Rust | [rust](rust/) |
| Java | [java](java/) |
| C# | [csharp](csharp/) |
| Ruby | [ruby](ruby/) |
| PHP | [php](php/) |
| Swift | [swift](swift/) |
| Kotlin | [kotlin](kotlin/) |

## API operations

| CLI | Request | Meaning |
| --- | --- | --- |
| `create 'your question'` | `POST /responses` | Create once, with `background: true` and your stable `Idempotency-Key`. |
| `get resp_…` | `GET /responses/{id}` | Read the status and final `output_text`. |
| `records resp_… [cursor]` | `GET /responses/{id}/records` | Read one page of original-source evidence. |
| `cancel resp_…` | `POST /responses/{id}/cancel` | Explicitly stop unfinished work. |

Poll `get` about every three seconds while `queued` or `in_progress`. For `requires_action`, open `socai.required_action.authorization_url` as the signed-in Socai user, complete platform sign-in, then continue querying the **same ID**. Stop on `completed`, `failed` or `cancelled`.

For records, repeat the command with the returned opaque `next_cursor` until it is null. Empty source records are valid; do not fabricate missing evidence. The examples deliberately make one HTTP request per command, with a 30-second request timeout and no redirects or automatic retries. A network timeout does not cancel a task.

## Authentication and errors

- Keep `SOCAI_API_KEY` on your server, not in frontend bundles, prompts, screenshots or git.
- Keys use the account's Credits and managed platform connections, scoped to their project. Reuse that project for the whole workflow.
- A missing, revoked or expired key returns `401`; account restrictions return `403`.
- `409` indicates an idempotency or version conflict. Retry uncertain creation only with the identical body and original operation key.
- For `429`, distinguish quota exhaustion from a retryable rate limit and honor `Retry-After`. Do not loop on an insufficient balance.
- A non-success response exits nonzero. Keep its request ID for support; never log the Bearer key.

See the [Markdown reference](https://agent.socai.io/api/server/docs.md) for full schemas, platform selection, multi-turn conversations, monitoring and analysis. Chat Completions and Messages compatibility also uses Socai's asynchronous `background: true` extension; these demos do not claim streaming compatibility.
