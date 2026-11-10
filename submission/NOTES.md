# Submission notes — temporal knowledge system

## Architecture and data flow

`build()` constructs `GroundedKnowledge`, which implements the required `ingest(snapshot)`, `answer(question, as_of=None)`, and `conflicts()` interface. The evaluator supplies the snapshots; the solution makes **no network calls**. `ingest` indexes the pages in chronological, snapshot-scoped BM25-style inverted indexes. Index entries are short paragraphs, bullet points and individual Markdown table rows with their headings, column values, title, source URL and crawl snapshot ID. The original markdown is also retained in memory for source-backed extraction. Nothing is persisted across runs.

On a query, explicit `as_of` and recognized date language are resolved to the latest snapshot **not later than the requested date**. The default is the most recent ingested snapshot. Query normalization (loan synonyms, term durations, year ranges and account/product names) produces candidates quickly. Document authority and complete qualifiers are important: a specific current loan schedule outranks a calculator or stale promotion, while a rate, APY and dividend rate are *different* metrics. Separate tier rows are never presented as conflicting rates merely because the numbers differ.

A deterministic evidence extraction layer handles high-risk structured topics such as auto and mortgage terms, account balance tiers, certificate APYs, personal vs. business card APRs, branch information and membership. It reads and verifies matching rows or exact passages in the **selected snapshot** rather than using the practice questions as a lookup table. General questions fall back to ranked passage retrieval. Unavailable product tiers and unpublished rates result in a citation-free, low-confidence refusal. If a stable administrative fee page vanishes from an incremental crawl, the system can cite its previous snapshot; this restricted fallback **does not** apply to prices, rates, promotions or time-limited offers.

Answers carry source URLs, snapshot IDs and short evidence quotes. Repeated questions are cached to guarantee deterministic behavior. No LLM API, external vector index, or model installation is used. This is a deliberate engineering tradeoff: speed, provenance, reproducibility and no runtime dependencies at the expense of richer semantic paraphrase handling.

## Conflict detection

The system keeps each snapshot's rate facts and compares numeric values for matching page, product qualifiers, amount/term tier and metric. It reports changed values with original source snapshots and resolves to the latest published rate. Certificate table headers are normalized across crawl/template changes. It also detects clear simultaneous discrepancies between the dedicated auto-loan schedule and a promotional page and between newer and older dated official branch-count statements. Direct source authority and publication chronology are recorded in each conflict reason. Other ambiguities remain known limitations: prose-only contradictions not recognized by the patterns may be missed; unrelated products with weak table labels can yield ambiguous matches.

## Environment

- Python **3.11** compatible; the implementation and test suite use only the Python standard library.
- **No API keys, payments, credentials, network access, GPUs or model downloads required.** `requirements.txt` has no third-party dependencies.
- Code and synthetic tests may be published. **Do not commit** the supplied website snapshots, zipped snapshots, raw participant kit, credentials or `.env` files. Those inputs are provided to the evaluator separately.
- The `harness/contract.py` API and its scorer are **not modified** in the participant kit.

## How to run

From the **original participant kit's** top folder, after placing this repo's `submission/` directory there (or specifying its absolute path):

```bash
python harness/run_eval.py --submission submission --eval eval/public_eval.jsonl
python -m unittest discover -s submission/tests -v
```

The first command automatically unpacks the bundled snapshots into the local kit folder, outside this submission. To exercise the kit's small self-test including its published conflict gold:

```bash
python harness/run_eval.py --submission submission \
  --snapshots harness/selftest/snapshots \
  --eval harness/selftest/eval.jsonl \
  --conflicts-gold harness/selftest/conflicts_gold.json
```

## Validation and limitations

Local practice run (40 public questions): **0.9690**, with 0 stale-value traps, no answer errors and approximate 0.02s p95 query latency. Five snapshots were ingested in approximately 10–11 seconds. Public evaluation does **not** provide the hidden conflict-gold list; therefore the 0.9690 figure is the public scorer's renormalized score over the pillars present, **not** an estimate of the hidden four-pillar score. The supplied five-question self-test with conflict gold scored **1.0000**. All synthetic unit tests pass. One public item has neither `must_include` nor `expected_sources`, for which the deterministic public scorer awards zero independently of the content returned; our system still lists the certificate rates.

Hidden questions, paraphrases, source-quality checks and conflict judgments may uncover additional shortcomings. A production extension would add a stronger calibrated semantic reranker, broader entity canonicalization and a human-review queue for unresolved contradictions. Source-grounded abstention is preferable to inventing a value.