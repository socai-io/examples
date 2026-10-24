# JavaScript

Node.js 22+, no packages required. Configure the environment from the [quickstart](../README.md#quickstart).

```bash
node demo.mjs create 'Research recent AI wearable feedback on X, with original links.'
node demo.mjs get resp_REPLACE_WITH_REAL_ID
node demo.mjs records resp_REPLACE_WITH_REAL_ID 'NEXT_CURSOR'
node demo.mjs cancel resp_REPLACE_WITH_REAL_ID
```

Omit the cursor for the first records page. Each command makes one request. Poll `get` while active and resume the same ID after platform sign-in. Use the original idempotency key and identical prompt after uncertain creation. Cancel only when you intend to stop work.
