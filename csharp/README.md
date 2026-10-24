# C#

.NET 8 SDK, no extra packages. Configure the [environment](../README.md#quickstart).

```bash
dotnet run -- create 'Research recent AI wearable feedback on X, with original links.'
dotnet run -- get resp_REPLACE_WITH_REAL_ID
dotnet run -- records resp_REPLACE_WITH_REAL_ID 'NEXT_CURSOR'
dotnet run -- cancel resp_REPLACE_WITH_REAL_ID
```

Omit the cursor for the first page. Each command makes one request. Poll the same ID until terminal status, and resume it after sign-in. A timeout does not cancel work; use your original operation key and identical body if creation was uncertain.
