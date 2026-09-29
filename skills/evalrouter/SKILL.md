---
name: evalrouter
description: >
  Evaluate models and repository agents with EvalRouter. Use for CLI sign-in,
  catalog discovery, quotes and spending caps, runs, progress, comparisons,
  results and exports. Help create workspace-private benchmarks where enabled,
  prepare public catalog requests, or publish a supplier package only for an
  onboarded supplier. Report EvalRouter defects through feedback.
---

# Evaluate with EvalRouter

EvalRouter runs versioned evaluations against managed model routes, your own
model endpoints, or qualified repository agents. You work through the
`evalrouter` CLI (Python package `evalrouter`). Every paid run is
bounded by a **quote**: a frozen plan with a spending cap that a human reviews
before anything starts.

**Check current availability before acting.** The API contract includes routes
that may not be enabled for this workspace or in Production. The live docs
carry current flags and limits. Read the relevant page before acting, and run
`evalrouter <command> --help` when you need exact flags:

- Overview: https://evalrouter.ai/developers/docs/overview
- Quickstart: https://evalrouter.ai/developers/docs/quickstart
- Browser sign-in: https://evalrouter.ai/developers/docs/cli-login
- Automation keys: https://evalrouter.ai/developers/docs/authentication
- CLI commands: https://evalrouter.ai/developers/docs/cli
- Results and exports: https://evalrouter.ai/developers/docs/results
- Availability and limits: https://evalrouter.ai/developers/docs/availability
- Model API (direct HTTP): https://evalrouter.ai/developers/docs/model-api
- Repository agents: https://evalrouter.ai/developers/docs/repository-agents
- Private benchmarks: https://evalrouter.ai/developers/docs/byob
- Hugging Face imports: https://evalrouter.ai/developers/docs/huggingface
- Feedback: https://evalrouter.ai/developers/docs/feedback
- Public OpenAPI: https://evalrouter.ai/developers/docs/openapi.json

## Safety rules (non-negotiable)

1. **Never start paid work without explicit human approval of a specific quote.**
   `evalrouter run` and `evalrouter agent-builds create` start quoted
   server-side work. Preparing a benchmark never justifies a paid run:
   any run needs its own quote, cap and approval. Show the quote first, then stop and wait for a clear
   "yes, run quote Q under cap $X". Silence, a general "go ahead" given before the
   quote existed, or approval of a different quote does not count. Repository
   preparation and evaluation have separate quotes and approvals. Supplier
   `evalrouter benchmark submit` needs approval of the exact package; it does
   not authorize later paid evaluation.
2. **Keep credentials private.** Browser sign-in is the default; the CLI handles
   storing and refreshing its session. Never ask for a password, token, or API key
   in chat or put one in command arguments, files you create, screenshots, or
   logs. For explicit API-key automation, read `EVALROUTER_API_KEY` from the
   user's secret manager or private environment without printing it.
3. **Label results honestly.** A `sample` coverage run is a sample, not a
   benchmark score. Partial, failed and cancelled runs stay labelled as such. Report
   coverage, errors and billing state next to any score. Never present an
   illustrative ID from docs as a real, available target.
4. **Do not invent identifiers.** Profile IDs, route IDs, `eval://` references,
   connection IDs and agent refs must come from discovery or returned records
   in this workspace, not illustrative examples.
5. **Do not create evaluations to debug auth.** Use `evalrouter whoami`; for an
   expired browser session run `evalrouter login` again. Troubleshoot workspace
   keys only when the user has chosen key-based automation.

## A. Setup

Requires Python 3.12 or 3.13. Install with [uv](https://docs.astral.sh/uv/)
in its own tool environment (uv supplies Python 3.12 if needed):

```sh
uv tool install --python 3.12 evalrouter
evalrouter --help
```

If the shell cannot find `evalrouter`, run `uv tool update-shell` and restart the
terminal. Upgrade with `uv tool upgrade evalrouter`.

Start with `evalrouter whoami`. If it reports that the user is signed out,
run the browser sign-in command and keep it running while the user approves:

```sh
evalrouter login
evalrouter whoami
```

Describe the user action simply: “Sign in or create your account in the browser,
then approve the code.” If the agent cannot open the browser, give the verification
URL and code printed by the CLI. On a remote terminal use `evalrouter login
--no-browser`; approval can happen on the user's own computer. If the command
finishes before they approve, rerun it and use its new code.

The CLI selects the only workspace automatically. If there are several, show the
returned choices and use `evalrouter login --workspace NAME_OR_ID` for the one the
user selects. Don't ask them to hunt for a workspace UUID. A new account may need
to finish setup in the EvalRouter website; follow the CLI's setup link with the
same identity, then let the command continue. Older CLI versions may ask you to
rerun login afterwards.

Do not ask the user to install a keychain package, configure a credential backend,
export API variables, or generate a workspace API key for normal browser sign-in.
Credential storage is handled by the CLI. Keep routine updates focused on sign-in
and the next action; omit storage-backend details unless troubleshooting needs them.
Explain an actual operating-system
permission prompt only if one appears; don't disable its protections. Production
is the default API. If an older installed CLI reports a missing base URL, upgrade
it or pass `--base-url https://api.evalrouter.ai` without making the user configure
environment variables. Use another environment only when the user requests it.

For CI, an explicitly selected automation flow, or a server that says browser
sign-in is unavailable, follow the automation-key documentation. Don't silently
switch to manual API keys after another authentication error.

Registration and installation give no evaluation credit. Discovery and quotes
start no paid work; evaluation execution needs available workspace credit.
Production is the default API. If a feature is unavailable there, do not infer
that Dev is an acceptable target without the user's direction.

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
(the provider key is never a flag: the human types it at the hidden prompt, or
pipes it with `--key-stdin`, or names an env var with `--key-env`; rotate later
with `evalrouter connections update CONNECTION_ID --rotate-key`), then
`evalrouter connections check CONNECTION_ID` before quoting. A check can send a
small model request that their provider bills.

The API also accepts immutable `eval://provider/name/version` references.
Obtain the exact reference from discovery and quote its actual coverage and
compatibility; do not turn a catalog name into a guessed reference.

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
- **Cost**: `expected_charge_microusd` and `expected_range` (p50-p90 with a
  stated basis), when present; `worst_case_charge_microusd`; the enforced
  `max_charge_microusd` cap; cost components; and external charges. The legacy
  `estimated_charge_microusd` field names the conservative **worst case**, not
  expected spend. Connected endpoints bill separately, outside EvalRouter's
  cap. The cap is a ceiling, not a price guarantee.
- **Concurrency**: the requested value and the admitted run ceiling, per
  profile. The ceiling can be lower than requested; the quote lists why:
  conservative automatic choice (`auto`), adapter limit, gateway limit, the
  selected task count, or the spending cap. These are ceilings, not live counts.
- **Expiry** (`expires_at`) and the quote `id`.
- **Output format**, when selectable: the quote freezes it and scores from
  different formats must not be ranked together.

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

For a person at a terminal, `evalrouter run BENCHMARK --model MODEL` guides
discovery, shows a free quote, asks for a cap and offers Start run or Cancel.
`--dry-run` stops at the quote. The CLI stores the accepted quote and operation
key for recovery. Scripts and agents do not get that prompt; use the explicit
quote flow above and never add `--yes` before approval. For an earlier run,
`run --from` is a new, independently charged evaluation; `resume` is a
separate, availability-gated continuation workflow. See the current CLI docs.

Exit codes: 0 success; 1 API/transport error or failed run; 2 invalid input or
rejected request; 4 partial or cancelled waited run; 5 declined confirmation
with nothing started; 6 local watch disconnected while server work continues.

**6. Results and exports.**

```sh
evalrouter results RUN_ID --json
evalrouter export RUN_ID --version RESULT_VERSION --format html --output result.html
evalrouter export RUN_ID --version RESULT_VERSION --format json --output result.json
```

`--format` accepts `json`, `csv` or `html`; recent CLI versions also offer an
evidence `bundle`. `--output` is optional: without it, the CLI chooses a free
filename. An explicit existing filename is refused unless `--overwrite` is
passed. Use the result's integer
`--version` for repeatable reports and keep it with downstream copies. Report
terminal status, completed versus missing work, errors and billing state with
the scores.

For compatible model runs, `evalrouter compare RUN_A RUN_B --format html
--output my-comparison` downloads a descriptive comparison without inference.
Check matching benchmark version, task selection and output format. Keep
partial and unsettled results visible.

## C. Bring or publish a benchmark

Choose the flow that matches the user's goal and the target environment:

1. **Workspace-private benchmark, where enabled:** create one from a local
   JSONL, CSV or Parquet file, or from a workspace-imported Hugging Face file.
   The [private benchmark workflow](references/private-benchmark.md) covers
   rights, verification, built-in generic graders, source quotas and quoting.
   This feature is enabled in Dev only; it does not publish to the shared
   catalog or imply Production availability. Uploaded data is untrusted and
   never executed.
2. **Public maintained catalog:** check for a ready profile, then use
   [prepare a catalog request](references/add-a-benchmark.md) to record pinned
   public sources, matching maintained task, rights and a draft manifest.
   Preparation does not add or admit the benchmark; the EvalRouter team
   reviews it.
3. **Onboarded supplier with a verified namespace:** use the separate
   [package publishing workflow](references/publish-benchmark.md). Local
   validation and server submission are not platform admission.

## Repository agents (ACP)

To evaluate an agent program from a GitHub repository (Agent Client Protocol,
Node/npm runtime), follow https://evalrouter.ai/developers/docs/repository-agents.
It requires CLI **0.2.0 or later** and a workspace where repository qualification
is enabled: check `evalrouter agent-builds options --json` first and stop if it is
disabled. The flow is `agent-builds preview` (quote, no spend) → human approval →
`agent-builds create` → `agent-builds status` until ready → a separate evaluation
quote using the returned agent ref and coverage. Qualification and evaluation have
separate caps and each needs its own approval.

## Feedback

If an API or documentation defect blocks work, follow
https://evalrouter.ai/developers/docs/feedback and send one concise report with
`evalrouter feedback --kind bug --severity degraded --summary "Brief problem"`.
Include a safe request ID and error code when available. Never include secrets,
customer data or hidden evaluation content. Resolve expected validation
refusals locally.
