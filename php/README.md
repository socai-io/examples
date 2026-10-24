# PHP

PHP 8.1+ with the `curl` extension, no Composer packages. Configure the [environment](../README.md#quickstart).

```bash
php demo.php create 'Research recent AI wearable feedback on X, with original links.'
php demo.php get resp_REPLACE_WITH_REAL_ID
php demo.php records resp_REPLACE_WITH_REAL_ID 'NEXT_CURSOR'
php demo.php cancel resp_REPLACE_WITH_REAL_ID
```

Omit the cursor for the first page. Poll the same ID until completion, resuming after platform sign-in. Do not resubmit with a fresh idempotency key after a network error. Each command makes one request and refuses redirects; cancel only when stopping unfinished work is intended.
