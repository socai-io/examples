# Java

JDK 17+, standard library only. Configure the [environment](../README.md#quickstart).

```bash
java Demo.java create 'Research recent AI wearable feedback on X, with original links.'
java Demo.java get resp_REPLACE_WITH_REAL_ID
java Demo.java records resp_REPLACE_WITH_REAL_ID 'NEXT_CURSOR'
java Demo.java cancel resp_REPLACE_WITH_REAL_ID
```

Omit the cursor for the first page. These commands send one request each; poll `get` while active. Complete sign-in using the returned authorization URL and resume the same ID. Keep a stable idempotency key for creation; timeout does not cancel work.
