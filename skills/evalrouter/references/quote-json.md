# Quote request body reference

Most evaluations need only the flags in [SKILL.md](../SKILL.md) section B. Use
this reference when you write the quote request yourself.

`evalrouter quotes create --body FILE` (or `--body -` for stdin) sends one JSON
object, the API's `NewQuote` request; flags override its fields. Unknown fields
are rejected. Never put credentials in it. Start a reviewed quote with
`evalrouter runs create --quote QUOTE_ID --yes`.

## Fields

| Field | Required | Shape |
| --- | --- | --- |
| `model` | yes | Target model, see below |
| `selection` | yes | What to evaluate, see below |
| `coverage` | no | `{"mode": "sample", "sample_count": N, "seed": S}` or `{"mode": "full"}` |
| `max_charge_microusd` | no | Spending cap as a string of integer micro-USD. `"1000000"` = $1. Omitted: the run is bounded by the wallet |
| `concurrency` | no | `"auto"`, `"max"` or an integer 1 to 100 (see below) |
| `output_format` | no | `"default"`, `"leaderboard"`, `"prompt_json"`, `"native_json"` or `"json_schema"`; supported formats depend on the exact benchmark version and model route |

### `model`

```json
{"kind": "managed", "route_id": "ROUTE_ID_FROM_models_list"}
```

```json
{"kind": "connection", "connection_id": "CHECKED_CONNECTION_UUID"}
```

A connection must pass `evalrouter connections check` before it can be quoted
(`connection_unverified` otherwise). Its model provider bills separately, outside
the EvalRouter cap.

### `selection`

- Benchmark profiles (the common case): `{"profile_ids": ["PROFILE_ID", ...]}`,
  1 to 50 IDs, each from `evalrouter benchmarks get SLUG` with
  `quote_availability.status` = `ready_for_quote`.
- A suite version: `{"suite_version_id": "UUID"}`.
- A universal evaluation reference: `{"eval": "eval://provider/name/version"}`.
  Use an exact reference returned by discovery. The router chooses a registered
  provider; the quote reports actual compatibility and execution selection.

### `coverage`

- `sample`: `sample_count` 1 to 1000 (default 25), `seed` 0 to 2^32-1 (default 42).
  Results from a sample are a sample, never a full-benchmark score.
- `full`: every task in the selection.

### `concurrency`

A requested ceiling on concurrent model requests for the run. `--concurrency` on
the command line overrides the file. It is frozen at quote time; the response
reports the admitted run ceiling and per-profile ceilings with reasons:

| Reason | Meaning |
| --- | --- |
| `auto_heuristic` | `auto` picks a conservative value |
| `adapter_limit` | The benchmark's runner supports fewer concurrent samples |
| `gateway_limit` | Platform per-run, per-workspace or per-provider limits |
| `task_count` | Fewer selected tasks (times attempts) than requested |
| `budget_limit` | The cap cannot cover that many worst-case samples at once |

Some execution pathways reject any `concurrency` value with
`concurrency_unsupported`; omit the field there.

### `output_format`

The quote freezes the chosen output format. A benchmark with a fixed format
refuses an override, and `leaderboard` refuses a model route that does not
declare that format. Results from different formats are not ranked together.
The API field is `output_format`; the CLI flag is `--output-format`.

## Common quote refusals

- `model_unavailable`, `unbounded_model_cost`, `judge_only_route`: pick another route.
- `budget_limit`: the cap exceeds the per-run maximum; lower it.
- Insufficient credit, a cap below required work, revoked permissions or a
  withdrawn asset can block admission at run time even after a quote.

## Reading the response

Top-level fields include `id`, `expires_at`, `plan`, `max_charge_microusd`,
`price_version` and `retention`. The cap is `max_charge_microusd`; actual
charges follow usage and cannot exceed it. Do not present pre-run cost
estimates or forecasts, even if a response still contains such fields.
Summarise compatibility, warnings, coverage, the frozen cap, external charges,
concurrency and expiry. Run only within the user's requested scope; a request to
run the evaluation does not require a separate quote-approval turn.
