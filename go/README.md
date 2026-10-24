# Go

Go 1.22+, standard library only. Configure the [environment](../README.md#quickstart), then run from this directory:

```bash
go run . create 'Research recent AI wearable feedback on X, with original links.'
go run . get resp_REPLACE_WITH_REAL_ID
go run . records resp_REPLACE_WITH_REAL_ID 'NEXT_CURSOR'
go run . cancel resp_REPLACE_WITH_REAL_ID
```

Omit the cursor for the first page. Poll `get` about every three seconds while active, and resume the same ID after platform sign-in. Creation requires a saved, stable idempotency key. Requests time out after 30 seconds without automatically cancelling or resubmitting work.
