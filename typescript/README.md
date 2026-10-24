# TypeScript

Node.js 24+ runs this file directly with built-in type stripping; no packages or build step are required. Configure the environment from the [quickstart](../README.md#quickstart).

```bash
node demo.ts create 'Research recent AI wearable feedback on X, with original links.'
node demo.ts get resp_REPLACE_WITH_REAL_ID
node demo.ts records resp_REPLACE_WITH_REAL_ID 'NEXT_CURSOR'
node demo.ts cancel resp_REPLACE_WITH_REAL_ID
```

Omit the cursor for the first page. Each command makes one request. Poll the same ID until completion, resuming it after platform sign-in. Save the idempotency key before creation; do not automatically submit another task after a timeout. Cancel only when you intend to stop unfinished work.
