# Python

Python 3.10+, standard library only. First configure the environment shown in the [quickstart](../README.md#quickstart).

```bash
python3 demo.py create 'Research recent AI wearable feedback on X, with original links.'
python3 demo.py get resp_REPLACE_WITH_REAL_ID
python3 demo.py records resp_REPLACE_WITH_REAL_ID
python3 demo.py records resp_REPLACE_WITH_REAL_ID 'NEXT_CURSOR'
python3 demo.py cancel resp_REPLACE_WITH_REAL_ID
```

Each command makes one request. Poll `get` while active; on platform sign-in, complete authorization and resume the same ID. Save and reuse `SOCAI_IDEMPOTENCY_KEY` after an uncertain creation. `cancel` stops unfinished work; it is not part of the normal successful flow.
