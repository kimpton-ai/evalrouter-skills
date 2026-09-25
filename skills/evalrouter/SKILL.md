---
name: evalrouter
description: >
  Evaluate language models and repository agents with EvalRouter from the
  terminal. Use when the user wants to run a benchmark against a model, compare
  models on an evaluation, get a quote or spending cap for an eval run, check
  results or export an EvalRouter report, set up the evalrouter CLI or its
  workspace API key, or package, validate and publish their own benchmark on
  EvalRouter. Covers catalog discovery, quote.json, coverage and concurrency,
  approval of spending caps before paid work, run/wait/results/export, and
  benchmark init/validate/bundle/submit.
---

# Evaluate with EvalRouter

EvalRouter runs benchmark evaluations against managed model routes, your own
model endpoints, or qualified repository agents. You work through the
`evalrouter` CLI (Python package `kimpton-evalrouter-sdk`). Every paid run is
bounded by a **quote**: a frozen plan with a spending cap that a human reviews
before anything starts.

**The live docs are the source of truth.** This skill gives the workflow; the
docs carry current flags, limits and wording. Read the relevant page before
acting, and run `evalrouter <command> --help` when you need exact flags:

- Overview: https://evalrouter.ai/developers/docs/overview
- Quickstart: https://evalrouter.ai/developers/docs/quickstart
- Account and key: https://evalrouter.ai/developers/docs/authentication
- CLI commands: https://evalrouter.ai/developers/docs/cli
- Results and exports: https://evalrouter.ai/developers/docs/results
- Availability and limits: https://evalrouter.ai/developers/docs/availability
- Model API (direct HTTP): https://evalrouter.ai/developers/docs/model-api
- Repository agents: https://evalrouter.ai/developers/docs/repository-agents

## Safety rules (non-negotiable)

1. **Never start paid work without explicit human approval of a specific quote.**
   `evalrouter run`, `evalrouter agent-builds create` and `evalrouter benchmark submit`
   create server-side work. Show the quote first, then stop and wait for a clear
   "yes, run quote Q under cap $X". Silence, a general "go ahead" given before the
   quote existed, or approval of a different quote does not count.
2. **Never print, paste, log or commit credentials.** The workspace key lives in
   `EVALROUTER_API_KEY`, set by the human through their secret manager or private
   shell. Never pass it as a command argument, write it into `quote.json`, a
   `.env` you create, a URL, a commit, or chat output. Do not `echo` it to check
   it; check presence with something like `test -n "$EVALROUTER_API_KEY" && echo set`.
   If the user pastes a key into chat, tell them to revoke it and create a new one.
3. **Label results honestly.** A `sample` coverage run is a sample, not a
   benchmark score. Partial, failed and cancelled runs stay labelled as such. Report
   coverage, errors and billing state next to any score. Never present an
   illustrative ID from docs as a real, available target.
4. **Do not invent identifiers.** Profile IDs, route IDs, connection IDs and
   agent refs must come from `evalrouter catalog`, `evalrouter connections list`,
   or `evalrouter agent-builds status` responses in this workspace.
5. **Do not create evaluations to debug auth.** For an invalid or expired key,
   check the workspace ID and key status in the web settings page.

## A. Setup

Requires Python 3.12 or 3.13. Install with [uv](https://docs.astral.sh/uv/)
in its own tool environment (uv supplies Python 3.12 if needed):

```sh
uv tool install --python 3.12 kimpton-evalrouter-sdk
evalrouter --help
```

If the shell cannot find `evalrouter`, run `uv tool update-shell` and restart the
terminal. Upgrade with `uv tool upgrade kimpton-evalrouter-sdk`.

Account and key are browser steps the human does; the CLI never collects a
password (see the authentication doc):

1. Create an account at https://evalrouter.ai/register and verify the email.
2. Create a workspace API key at https://evalrouter.ai/settings/api-keys.
3. The human sets, privately:
   - `EVALROUTER_API_KEY`: the key's secret value
   - `EVALROUTER_WORKSPACE_ID`: that workspace's ID
   - `EVALROUTER_BASE_URL`: `https://api.evalrouter.ai` (no `/v1` suffix)

`--workspace-id` and `--base-url` can override the last two per command; there
is no key flag, by design. Registration and installation give no evaluation
credit; paid runs need available workspace credit.

Global flags on every command: `--json` (one JSON result on stdout, progress on
stderr; prefer it when you parse output), `--timeout SECONDS`, `--base-url`,
`--workspace-id`.

## B. Run an existing benchmark

**1. Discover.** Pick a benchmark profile and a model from real responses:

```sh
evalrouter catalog --status active --json
evalrouter catalog --slug BENCHMARK_SLUG --json
evalrouter catalog --models --json
```

Use a profile whose `quote_availability.status` is `ready_for_quote`; an
`active` listing alone does not mean it can run. Filters: `--query`, `--runner
inspect|lm-eval`, `--capability`, `--cursor`/`--limit`. To evaluate the user's
own endpoint instead of a managed route, use `evalrouter connections create`
(credential read from the env var named by `--key-env`, never a flag), then
`evalrouter connections check CONNECTION_ID` before quoting. A check can send a
small model request that their provider bills.

**2. Write `quote.json`.** Minimal shape (full field reference in
[references/quote-json.md](references/quote-json.md)):

```json
{
  "model": {"kind": "managed", "route_id": "MODEL_ROUTE_ID"},
  "selection": {"profile_ids": ["BENCHMARK_PROFILE_ID"]},
  "coverage": {"mode": "sample", "sample_count": 3, "seed": 42},
  "max_charge_microusd": "1000000"
}
```

Money is a string of integer micro-USD: `"1000000"` is $1. Start small: a
sample with a low cap, unless the user asks for full coverage.

**3. Quote.** This starts no paid work:

```sh
evalrouter quote --config quote.json --json > quote-response.json
```

Optionally `--concurrency auto|max|1..100` (requires a CLI build whose
`evalrouter quote --help` lists it). Summarise for the human, from the response:

- **Compatibility and warnings**: resolve incompatibility before anything else.
- **Coverage**: sample (how many tasks, which seed) or full. A sample is not a
  full-benchmark score.
- **Cost**: `estimated_charge_microusd` versus `max_charge_microusd` (the cap),
  the cost components, and any external charges (connected endpoints bill
  separately, outside the EvalRouter cap). The cap is a ceiling, not a price
  guarantee.
- **Concurrency**: the requested value and the admitted run ceiling, per
  profile. The ceiling can be lower than requested; the quote lists why:
  conservative automatic choice (`auto`), adapter limit, gateway limit, the
  selected task count, or the spending cap. These are ceilings, not live counts.
- **Expiry** (`expires_at`) and the quote `id`.

If anything should change (model, coverage, cap), write a new quote; quotes are
frozen. Retrieve a saved one with `evalrouter quote --id QUOTE_ID`.

**4. STOP. Get explicit approval.** Ask: "Run quote `<id>` with a cap of `$X`?"
Do not continue until the human approves that quote and cap.

**5. Run once, with a durable operation key.** Save the quote ID and an
idempotency key (for example in a local notes file) *before* submitting:

```sh
evalrouter run --quote QUOTE_ID --idempotency-key OPERATION_KEY --wait --json
```

`--wait` follows progress (`--wait-timeout`, default 3600s; `--poll-interval`;
`--progress auto|plain|off`). A progress percentage counts processed samples; it
is not a score. If the response is lost, retry with the **same** quote and key; a
new key can start separate, separately charged work. Interrupting a local wait
does not stop server work. To follow later use `evalrouter wait RUN_ID` or
`evalrouter status RUN_ID`; to stop, `evalrouter cancel RUN_ID` only when the human
intends cancellation.

Exit codes: 0 success; 1 API/transport error or failed run; 2 invalid input or
rejected request; 4 partial or cancelled waited run.

**6. Results and exports.**

```sh
evalrouter results RUN_ID --json
evalrouter export RUN_ID --version RESULT_VERSION --format html --output result.html
evalrouter export RUN_ID --version RESULT_VERSION --format json --output result.json
```

`--format` accepts `json`, `csv` or `html`. Exports need an explicit `--output`
and refuse to overwrite unless `--overwrite` is passed. Use the result's integer
`--version` for repeatable reports and keep it with downstream copies. Report
terminal status, completed versus missing work, errors and billing state with
the scores.

## C. Publish your own benchmark

> Requires a CLI release that includes the `benchmark` command group.
> It is not in every 0.2.0 build: check `evalrouter benchmark --help` first and
> stop if the group is missing. `init`, `validate` and `bundle` also need the
> version-matched extra: `uv tool install --python 3.12 "kimpton-evalrouter-sdk[benchmark]"`.

```sh
evalrouter benchmark init ./my-benchmark --namespace NAMESPACE --name my-benchmark --template text
evalrouter benchmark validate ./my-benchmark
evalrouter benchmark bundle ./my-benchmark --output my-benchmark.zip
evalrouter benchmark submit my-benchmark.zip --wait
```

- `init`, `validate`, `bundle` run offline: no account, no network, and nothing
  in the package is executed. `init` writes an **explicitly synthetic draft**
  (`--template text|custom-scorer|multi-turn`) that claims no license.
- The user must supply the real material locally: tasks, grading fixtures,
  rights/licence documents and attribution, authors and maintainer, limits,
  metrics and limitations. There is no automatic Hugging Face or GitHub importer
  in the CLI; do not claim one. Never include credentials or private customer data.
- Local validation is not admission. `submit` uploads the bundle into the
  workspace's **verified namespace** (requested and verified beforehand), then the
  server revalidates and prepares it. Accepted preparation is not qualification,
  and neither makes it runnable.
- After submit: `evalrouter benchmark status PACKAGE_ID`, `evalrouter benchmark inspect PACKAGE_ID`,
  and sharing via `evalrouter benchmark grant` / `evalrouter benchmark revoke`.

Submitting creates server-side work: confirm with the human first. Full
walkthrough, file roles and grant semantics:
[references/publish-benchmark.md](references/publish-benchmark.md).

## Repository agents (ACP)

To evaluate an agent program from a GitHub repository (Agent Client Protocol,
Node/npm runtime), follow https://evalrouter.ai/developers/docs/repository-agents.
It requires CLI **0.2.0 or later** and a workspace where repository qualification
is enabled: check `evalrouter agent-builds options --json` first and stop if it is
disabled. The flow is `agent-builds preview` (quote, no spend) → human approval →
`agent-builds create` → `agent-builds status` until ready → a separate evaluation
quote using the returned agent ref and coverage. Qualification and evaluation have
separate caps and each needs its own approval.
