# Swift

Swift 5.9+ with Foundation; on Linux, FoundationNetworking is imported automatically. Configure the [environment](../README.md#quickstart).

```bash
swift demo.swift create 'Research recent AI wearable feedback on X, with original links.'
swift demo.swift get resp_REPLACE_WITH_REAL_ID
swift demo.swift records resp_REPLACE_WITH_REAL_ID 'NEXT_CURSOR'
swift demo.swift cancel resp_REPLACE_WITH_REAL_ID
```

Omit the cursor for the first page. Each command makes one request with a 30-second resource limit and refuses redirects. Poll the same ID while active, resuming after platform sign-in. Timeout does not cancel work or authorize creating a duplicate task.
