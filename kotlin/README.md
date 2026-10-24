# Kotlin

Kotlin 1.9+ and JDK 17+, no libraries required. Configure the [environment](../README.md#quickstart).

```bash
kotlinc Demo.kt -include-runtime -d demo.jar
java -jar demo.jar create 'Research recent AI wearable feedback on X, with original links.'
java -jar demo.jar get resp_REPLACE_WITH_REAL_ID
java -jar demo.jar records resp_REPLACE_WITH_REAL_ID 'NEXT_CURSOR'
java -jar demo.jar cancel resp_REPLACE_WITH_REAL_ID
```

Omit the cursor on the first page. Each command makes one request and refuses redirects. Poll the same ID while active, and resume it after platform sign-in. Keep your original idempotency key for uncertain creation; cancel only when you intend to stop unfinished work.
