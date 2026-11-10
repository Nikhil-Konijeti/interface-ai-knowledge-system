# interface.ai — Knowledge that knows what's true now

A temporal, provenance-aware knowledge system for the Software Engineer II engineering assignment. It reads five snapshots, answers date-qualified credit-union questions with sources, and identifies conflicting information.

## Files

- `submission/solution.py`: `build()` and required `ingest`, `answer`, `conflicts` methods.
- `submission/requirements.txt`: no third-party dependencies.
- `submission/NOTES.md`: architecture, source authority, temporal rules, validation and limitations.
- `submission/tests/test_solution.py`: synthetic regression tests.
- `VALIDATION.md`: local practice and self-test results.

## Running against the provided kit

Place `submission/` in the **original participant kit root**, alongside its `harness/`, `eval/`, and `snapshots_zip/` directories. Then run:

```bash
python harness/run_eval.py --submission submission --eval eval/public_eval.jsonl
python -m unittest discover -s submission/tests -v
```

The harness unpacks the snapshots locally on the first run. **The snapshots are not redistributed by this repository.**

Python 3.11; standard library only. No credentials, API keys, network calls or paid APIs.

## Results

The public 40-question practice run scored **0.9690** (no stale-value traps or errors, p95 ~0.02 seconds); the kit's self-test including one conflict case scored **1.0000**. The practice score excludes the unavailable hidden conflict-gold criterion and does not guarantee hidden evaluation performance. See `VALIDATION.md` and `submission/NOTES.md` for details.

## Submission

Push these code files to a **new public GitHub repository**, keeping the original participant snapshots and API keys excluded. Provide its URL and the desired reviewed commit hash to `assignments@interface.ai`, per the recruiting email.
