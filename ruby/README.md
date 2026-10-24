# Ruby

Ruby 3+, standard library only. Configure the [environment](../README.md#quickstart).

```bash
ruby demo.rb create 'Research recent AI wearable feedback on X, with original links.'
ruby demo.rb get resp_REPLACE_WITH_REAL_ID
ruby demo.rb records resp_REPLACE_WITH_REAL_ID 'NEXT_CURSOR'
ruby demo.rb cancel resp_REPLACE_WITH_REAL_ID
```

Omit the cursor on the first page. Each command makes one request, does not follow redirects, and does not retry automatically. Poll the same ID while active; resume after sign-in rather than creating a duplicate. Cancel is an explicit stop action, not required after completion.
