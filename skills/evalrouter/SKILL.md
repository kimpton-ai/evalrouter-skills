---
name: evalrouter
description: >
  Evaluate models with EvalRouter. Use for CLI sign-in, catalog discovery,
  runs, progress, comparisons, results, wallet usage and exports.
  Help create workspace-private benchmarks where enabled,
  prepare public catalog requests, or publish a supplier package only for an
  onboarded supplier. Report EvalRouter defects through feedback.
---

# Evaluate with EvalRouter

EvalRouter runs versioned evaluations against managed model routes or your own
model endpoints. You work through the `evalrouter` CLI (Python package
`evalrouter`). Evaluations draw on the workspace's wallet credit; a spending cap
(`--max-cost`) is optional.

You, the coding agent, use the CLI on the user's behalf. The thing evaluated is
a model, or an agent run with `--agent` (section B). Building executable
benchmarks from a code repository is not a supported public workflow. Say so if
asked, and don't attempt it, even if a CLI build lists related commands.

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
- Private benchmarks: https://evalrouter.ai/developers/docs/byob
- Hugging Face imports: https://evalrouter.ai/developers/docs/huggingface
- Feedback: https://evalrouter.ai/developers/docs/feedback
- Public OpenAPI: https://evalrouter.ai/developers/docs/openapi.json

## Persistent agent installation

For agent setup, save this document as a persistent personal skill before
reporting setup complete:

- Codex: `~/.agents/skills/evalrouter/SKILL.md`
- Claude Code: `~/.claude/skills/evalrouter/SKILL.md`

Download `https://evalrouter.ai/skill.md` to the current agent's path and verify
that the saved file contains the skill's name, description and instructions.
Reading a URL for the current session alone is not installation. Follow section
A to install the CLI and verify sign-in. Report the installed path, CLI
availability and sign-in status separately. Stop after setup; do not evaluate.

## Working rules

1. **Follow the user's requested scope.** A request to run or compare models
   authorizes that evaluation; it needs no separate approval turn and no
   spending cap. Show the user the quoted price. When they ask what a run would
   cost, quote it with `--dry-run`, which starts nothing. Pass `--max-cost` only
   with a cap the user gave; never invent one (section B). A setup, discovery,
   preview or analysis-only request does not authorize inference. Do not expand coverage, start recurring work,
   buy credit, or retry uncertain external work beyond the user's request.
2. **Keep credentials private.** Browser sign-in is the default; the CLI handles
   storing and refreshing its session. Never ask for a password, token, or API key
   in chat or put one in command arguments, files you create, screenshots, or
   logs. For explicit API-key automation, read `EVALROUTER_API_KEY` from the
   user's secret manager or private environment without printing it.
3. **Label results honestly.** A `sample` coverage run is a sample, not a
   benchmark score. Partial, failed and cancelled runs stay labelled as such. Report
   coverage, errors and billing state next to any score. Never present an
   illustrative ID from docs as a real, available target.
4. **Do not invent identifiers.** Profile IDs, route IDs, `eval://` references
   and connection IDs must come from discovery or returned records in this
   workspace, not illustrative examples.
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
terminal. Upgrade with `uv tool upgrade evalrouter`. If a command fails with
`client_upgrade_required`, the installed CLI is older than the API serves:
run `evalrouter upgrade` (or the upgrade command the CLI prints), then repeat
the command. Nothing was run or charged.

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

Commands are `evalrouter <noun> <verb>` (`benchmarks list`, `quotes create`,
`runs create`, `runs results`); `evalrouter --help` lists them. Settings on every
command: `--json` (one JSON document on stdout; an error is one JSON object on
stderr with stdout empty; prefer it when you parse output), `--no-input` (never
prompt; implied by `--json`, CI and agent environments), `--timeout SECONDS`,
`--base-url`, `--workspace-id`, `--profile`. Lists read `--limit` rows (default
50); `--all` reads every page and `--cursor` continues from `next_cursor`.

## B. Run an existing benchmark

**1. Discover.** Pick a benchmark profile and a model from real responses:

```sh
evalrouter benchmarks list --json
evalrouter benchmarks get BENCHMARK_SLUG --json
evalrouter models list --json
```

Use a profile whose `quote_availability.status` is `ready_for_quote`; an
`active` listing alone does not mean it can run. To evaluate the user's own
endpoint instead of a managed route, use `evalrouter connections create` (the
provider key is never a flag: the human types it at the hidden prompt, or pipes
it with `--key-stdin`, or names an env var with `--key-env`; rotate later with
`evalrouter connections update CONNECTION_ID --rotate-key`), then
`evalrouter connections check CONNECTION_ID` before evaluation. A check can send a
small model request that their provider bills. A remote agent is a connection
with `--protocol a2a`; run it with `evalrouter run BENCHMARK --model MODEL
--agent remote:CONNECTION_NAME`. If the agent calls a model through the run's
metered gateway, add `--agent-gateway-api chat_completions`; `--model` is that
model, and its calls are charged to the run.

To evaluate an agent on this machine, `evalrouter agents list` shows the ACP
Registry agents (offline, from the bundled snapshot) with their integrity:
`pinned`, `package-registry` or `unverified-upstream`. Run one with
`evalrouter run BENCHMARK --model MODEL --agent ID` (or `ID@VERSION`, or
`local:<command>` for any ACP command). An `unverified-upstream` agent needs
`--allow-unverified`; pass it only when the user accepts an unverified artifact.

The API also accepts immutable `eval://provider/name/version` references.
Obtain the exact reference from discovery and check its actual coverage and
compatibility; do not turn a catalog name into a guessed reference.

**2. Run the requested evaluation.** Benchmarks and models are names (a slug or
an unambiguous name; exact IDs also work). `--max-cost USD` is the most the run
may charge: it starts only when its quote's maximum charge fits under it.
`--max-cost` is optional: pass it only with a cap the user gave, and never
choose one yourself. Without it the run is bounded by the workspace's wallet
balance (`evalrouter credits` shows it); say so when you show the quoted price.
Start with `--yes` and report the quoted maximum charge from its output; use
`--dry-run` only when the user asks for a price.
Without a terminal a paid start needs `--yes`; without it nothing is quoted or
charged and the command exits 5.

```sh
evalrouter run gsm8k --model gpt-5 --dry-run --json   # the quote; nothing is charged
evalrouter run gsm8k --model gpt-5 --sample 25 --seed 42 --yes --json
evalrouter run gsm8k --model gpt-5 --max-cost 5 --yes --json   # only with a cap the user gave
```

To compare models, run them together: one quote, one cap (or the wallet), the
same tasks. `runs compare` ranks them on the tasks every model finished;
pairwise detail is in the JSON:

```sh
evalrouter run gsm8k --model gpt-5 --model claude-sonnet-5 --dry-run --json
evalrouter runs compare RUN_ID --json
```

A run stopped by its cap, the user's credit or a cancellation has `interruption`
with the reason. `evalrouter runs continue RUN_ID --yes --json` quotes and starts
only its unfinished tasks; finished ones are not charged again. Continue only
when the user asks to.

Or quote first and start the reviewed quote:

```sh
evalrouter quotes create gsm8k --model gpt-5 --json
evalrouter runs create --quote QUOTE_ID --yes --wait --json
```

For a JSON request body (`quotes create --body FILE`), see
[references/quote-json.md](references/quote-json.md).

Respect requested coverage; when the user asks for a sample without a size, the
CLI default is 25 tasks with seed 42. Do not silently replace a full evaluation
with a sample. Keep model settings at their route defaults unless the user
requested an override, and record the settings in the comparison. `--yes`
satisfies the CLI's confirmation for work the user already requested.
`--dry-run` prints the quote (maximum charge and plan) and starts nothing.
Connected providers bill separately; do not invent cost estimates.

**3. Recover and follow progress.** Starting a quote is idempotent: repeating the
same `runs create --quote` (or the same `run` command) after a dropped response
returns the same run and never starts a second one. `run --new` starts separate,
separately charged work. Progress counts processed tasks, not a score.
Interrupting a local wait does not stop server work. Follow an existing run with
`evalrouter runs wait RUN_ID` or `evalrouter runs get RUN_ID`; cancel with
`evalrouter runs cancel RUN_ID` only when the user intends cancellation.

Exit codes: 0 success; 1 the API refused the request; 2 invalid command or
input, nothing sent; 3 the run ended without completing; 4 not signed in or
credential rejected; 5 a confirmation was needed or the quote exceeds
`--max-cost`, nothing started; 6 the API was unreachable (server work
continues); 124 local wait timeout; 130 interrupted.

**4. Results and exports.**

```sh
evalrouter runs results RUN_ID --json
evalrouter runs export RUN_ID --version RESULT_VERSION --file-format html --output result.html
evalrouter runs export RUN_ID --version RESULT_VERSION --file-format json --output result.json
```

`--file-format` accepts `json`, `csv`, `html` or the evidence `bundle`.
`--output` is optional: without it, the CLI chooses a free filename. An explicit
existing filename is refused unless `--overwrite` is passed. Use the result's
integer `--version` for repeatable reports and keep it with downstream copies.
Report terminal status, completed versus missing work, errors and billing state
with the scores.

For separate single-model runs (a multi-model run uses `runs compare`),
`evalrouter comparisons report RUN_A RUN_B
--file-format html --output my-comparison` downloads a descriptive comparison
without inference. Check matching benchmark version, task selection and output
format. Keep partial and unsettled results visible.

## C. Bring or publish a benchmark

Choose the flow that matches the user's goal and the target environment:

1. **Workspace-private benchmark, where enabled:** create one from a local
   JSONL, CSV or Parquet file, or from a workspace-imported Hugging Face file.
   The [private benchmark workflow](references/private-benchmark.md) covers
   rights, verification, built-in generic graders, source quotas and evaluation.
   Availability depends on the current environment and workspace; keep the
   user in their configured environment and check
   [current availability](https://evalrouter.ai/developers/docs/availability).
   This does not publish to the shared catalog. Uploaded data is untrusted
   and never executed.
2. **Public maintained catalog:** check for a ready profile, then use
   [prepare a catalog request](references/add-a-benchmark.md) to record pinned
   public sources, matching maintained task, rights and a draft manifest.
   Preparation does not add or admit the benchmark; the EvalRouter team
   reviews it.
3. **Onboarded supplier with a verified namespace:** use the separate
   [package publishing workflow](references/publish-benchmark.md). The public
   CLI drafts, validates and bundles a package; none of that is platform
   admission.

## Feedback

When you hit what looks like an EvalRouter defect while using this skill,
report it yourself with `evalrouter feedback` as part of the task; don't ask
the user to file it. Before sending, read
[references/report-defects.md](references/report-defects.md) for the checks,
the report contents and the command.

- **Reportable:** after basic local checks (flags match `--help`, identifiers
  came from discovery in this workspace, `evalrouter whoami` shows the intended
  sign-in), the CLI or API contradicts documented behavior. Examples: an exact
  route ID just returned by `evalrouter models list` is rejected as
  `ambiguous_model`; an internal server error; a CLI crash, traceback or
  unparseable response; docs that contradict the shipped command.
- **Not a defect by itself:** signed out, insufficient credit, a validation
  error caused by your input, a feature disabled for this workspace, a rate
  limit or a low score. Resolve these locally or tell the user.
- **Contents:** only the behavior, expected versus observed, the command
  shape with placeholders (`evalrouter run BENCHMARK --model MODEL`), and the error
  code, request ID, HTTP status and route. Leave out every identifier and value
  from this workspace or the user's arguments (route, profile, quote, run,
  workspace and connection IDs, config contents, file paths), raw output,
  secrets, benchmark or run data. The request ID is enough to trace it. Pass
  `--contact-ok` only if the user agreed to be contacted.
- **Limits:** one report per distinct defect per task, and at most three per
  session. Use the current sign-in and environment: never sign up, create keys,
  switch account or environment, or repeat a paid action to reproduce or
  report. If the report itself fails, don't report that failure; continue.
- **Permission:** skip reporting if the user opted out or the work is offline.
  Follow the platform's tool permissions for this command as for any other; a
  permission granted for another command doesn't cover it.
- **After sending:** keep the returned `feedback_id` in your working context to
  avoid duplicates, not in the user's files. Don't show the report text; a
  brief mention is enough, and never hide or deny the report when asked. Tell
  the user about the defect itself whenever it still blocks or changes their
  result.
