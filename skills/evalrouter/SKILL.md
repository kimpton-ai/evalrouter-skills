---
name: evalrouter
description: >
  Evaluate models with EvalRouter. Use for CLI sign-in, catalog discovery,
  runs, progress, comparisons, results, wallet usage and exports.
  Help create workspace-private benchmarks where enabled,
  prepare public catalog requests, or publish a supplier package only for an
  onboarded supplier. Where enabled, turn an app's traces into a private
  benchmark, or tune a repository's agent and open a pull request with the
  result. Report EvalRouter defects through feedback.
---

# Evaluate with EvalRouter

EvalRouter runs versioned evaluations against managed model routes or your own
model endpoints. You work through the `evalrouter` CLI (Python package
`evalrouter`). New one-time evaluations use available workspace wallet credit;
they do not require a quote or a customer spending cap.

You, the coding agent, use the CLI on the user's behalf; the thing evaluated is
a model. Two repository workflows are supported where they are enabled: turning
an app's traces into a private benchmark (section D) and tuning a Python
LangGraph agent and opening a pull request with the result (section E). Other
ways of building or evaluating agent programs or executable benchmarks from a
code repository are not supported public workflows. Say so if asked, and don't
attempt them, even if a CLI build lists related commands.

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
- Traces to a benchmark: https://evalrouter.ai/developers/docs/trace-datasets
- Tune: https://evalrouter.ai/developers/docs/tune
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
   authorizes that evaluation. Proceed without asking for approval of a quote or
   adding a spending cap. A setup, discovery, preview or analysis-only request
   does not authorize inference. Do not expand coverage, start recurring work,
   buy credit, or retry uncertain external work beyond the user's request.
   Tune sweeps (section E) are the exception: each one has a spending cap, and
   the human approves that cap before the sweep starts.
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
`evalrouter connections check CONNECTION_ID` before evaluation. A check can send a
small model request that their provider bills.

The API also accepts immutable `eval://provider/name/version` references.
Obtain the exact reference from discovery and check its actual coverage and
compatibility; do not turn a catalog name into a guessed reference.

**2. Run the requested evaluation.** Use the exact profile and model IDs from
catalog discovery. For a sample comparison, run the models together on the
same tasks and seed:

```sh
evalrouter run BENCHMARK_PROFILE_ID --model MODEL_ROUTE_A --model MODEL_ROUTE_B --mode matched --sample 25 --seed 42 --yes --json
```

For one model, use one `--model`. Respect requested coverage; when the user asks
for a sample without a size, the CLI default is 25 tasks with seed 42. Do not
silently replace a full evaluation with a sample. Keep model settings at their
route defaults unless the user requested an override, and record the settings
in the comparison. Check `evalrouter run --help` for installed flags. `--yes`
satisfies the CLI's terminal confirmation for work the user already requested;
it does not require another conversation turn. `--dry-run` previews without
starting work when the user asks for a preview or compatibility needs checking.

Do not send `--max-cost`, `max_charge_microusd`, `budget_usd` or per-model caps for
new one-time evaluations. Available wallet credit funds mandatory fees and
pending operations. If credit cannot back another operation, new work stops
and results can be partial. An in-flight usage charge may settle above its hold
and leave the wallet negative, so wallet credit is not a guaranteed maximum.
Connected providers bill separately. Explain this briefly when relevant; do not
invent cost estimates, a dollar ceiling or an approval step.

For a multi-benchmark job, use `evalrouter evaluation-jobs --help` and the
[current CLI documentation](https://evalrouter.ai/developers/docs/cli).
Preflight resolves the compatible pairs and coverage before launch; use
`evaluation-jobs start --yes` with a persisted idempotency key for the requested
work. Explicit provider-cost acknowledgements required by the API still apply.
If the installed CLI lacks the documented workflow, upgrade it; do not fall
back to a cap-and-quote flow for a new one-time job. Report unavailable hosted
features instead of switching environments.

**3. Recover and follow progress.** The guided CLI persists the operation key;
repeating the same command after a dropped response recovers the same work.
For explicit job starts, save an idempotency key before submitting and reuse the
same key and body on a transport retry. A new key or `--new` can start separate,
separately charged work. Progress counts processed tasks, not a score.
Interrupting a local wait does not stop server work. Follow an existing run with
`evalrouter wait RUN_ID` or `evalrouter status RUN_ID`; cancel only when the user
intends cancellation. Adding credit does not automatically resume unfinished
work. Do not continue or rerun it unless that is within the user's request;
uncertain prior external effects require explicit review.

Existing quoted runs retain their frozen terms. Use
[references/quote-json.md](references/quote-json.md) only for an existing quote
or an explicitly selected legacy workflow, not as the default launch path.

Exit codes: 0 success; 1 API/transport error or failed run; 2 invalid input or
rejected request; 4 partial or cancelled waited run; 5 declined confirmation
with nothing started; 6 local watch disconnected while server work continues.

**4. Results and exports.**

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
   [package publishing workflow](references/publish-benchmark.md). Local
   validation and server submission are not platform admission.

## D. Turn an app's traces into a benchmark

This workflow is enabled on Dev (https://dev.evalrouter.ai) and is not yet
enabled in Production. If Production reports a command as unavailable, tell the
user. Use Dev only when the user directs it, with the API base URL from the Dev
documentation passed as `--base-url`.

Sections D and E need a CLI release that includes the `traces`, `datasets` and
`improvements` command groups. Check with `evalrouter traces --help`. If the
installed CLI lacks them after `uv tool upgrade evalrouter`, tell the user that
the workflow is not yet available in their CLI.

**1. Connect.** An API key needs the `eval:write` and `traces:write` scopes; a
CLI sign-in needs the admin or owner role in the workspace.

```sh
evalrouter traces connect --name APP_NAME --env-file .env.local --json
```

The ingest key is shown only once. Always pass `--env-file`: the CLI then
appends `EVALROUTER_TRACE_CONNECTION_ID` and `EVALROUTER_TRACE_KEY` to that file
with mode 0600 and does not print the key. Without it the key appears in the
output. Check that git ignores the file (`git check-ignore .env.local`) before
you run the command. Never read the key back into the conversation, logs or
commits.

**2. Capture traces.** Instrument the app with the EvalRouter SDK using those two
variables. Set the root span input to the user's request and the root span
output to the app's final answer. Plain text works best. Once the app has served
traffic, check what has arrived:

```sh
evalrouter traces connections list --json
evalrouter traces list --connection CONNECTION_ID --json
```

**3. Create a dataset and import traces.** Importing records the workspace's
attestation that it may evaluate models on this data, so confirm that with the
user before you run it.

```sh
evalrouter datasets create --name "APP_NAME production" --json
evalrouter datasets import-traces DATASET_ID --connection CONNECTION_ID --limit 200 --json
```

Each recent completed trace becomes one held-out example. The root span input
is the task and the root span output is the reference answer. Traces without
both, traces whose root span failed and oversized traces are skipped and counted
in `skipped`.

**4. Approve and freeze a version.** Before approving, show the person what they
are approving: the created and skipped counts, and the examples themselves on
the dataset's page in the browser. Approve only after they agree. `--all`
approves every pending example at its current draft. To approve a reviewed
subset, repeat `--example EXAMPLE_ID` instead.

```sh
evalrouter datasets approve DATASET_ID --all --json
evalrouter datasets versions create DATASET_ID --json
```

**5. Build the benchmark.** Pass the version number returned by
`versions create` (or the version ID). Choose the judge route from
`evalrouter models list --json`.

```sh
evalrouter datasets benchmark DATASET_ID 1 --grader match-production --judge-route JUDGE_ROUTE --json
```

The `match-production` grader asks a managed judge model whether each answer is
at least as correct, complete and helpful as the app's answer for the same
input. Each grade is a metered judge call. `--grader exact-match` compares text
and needs no judge. An API key needs the `benchmarks:submit` scope for this
step. The command returns `benchmark_id`.

**6. Run several models.** Run each model the user asked for on the same
benchmark at full coverage. The rules of section B apply: the user's request
authorizes these runs and wallet credit funds them.

```sh
evalrouter run BENCHMARK_ID --model MODEL_ROUTE_A --full --yes --json
evalrouter run BENCHMARK_ID --model MODEL_ROUTE_B --full --yes --json
evalrouter runs results RUN_ID --json
```

In the public CLI build that includes these commands, each model runs
separately. The internal build also has evaluation jobs, where
`evaluation-jobs results --rank` orders models by score and then by spend. When
that command is absent, compare the run results yourself.

**7. Recommend a model.** Order the models by score, then by cost. The usual
recommendation is the cheapest model whose score is within one standard error
of the best score. A judge that cannot decide leaves that case ungraded, so
report coverage, errors and spend next to each score, and say so when a run is
partial.

## E. Tune a repository's agent and open a pull request

Tune and improvement projects are a preview. They are enabled on Dev
(https://dev.evalrouter.ai) and are not yet enabled in Production. The Dev rule
from section D applies.

Requirements:

- A local clone of a Python repository that uses uv and LangGraph, with
  `langgraph.json` and `uv.lock`.
- Model roles declared in `evalrouter-model-policy.json` and read in the code
  with `from evalrouter_model_policy import get_model`. Tune changes only
  declared roles. Hard-coded model names stay as they are.
- An active trace connection for the agent (section D). `improvements create`
  uses the workspace's only active connection. When there are several, pass
  `--trace-connection CONNECTION_ID`.
- The EvalRouter GitHub App, connected once in the browser at
  `/settings/integrations` on the EvalRouter site with access to the
  repository. This is the only browser step. When the app cannot read the
  repository, `evalrouter improvements create` stops with
  `github_repository_unreadable` and prints the link; give it to the user.

EvalRouter only reads the repository and never needs write access to it. You
open the pull request with the user's own git and GitHub CLI credentials.

**1. Create and prepare the project.**

```sh
evalrouter improvements create --repo OWNER/NAME --ref main --json
evalrouter improvements prepare PROJECT_ID --json
evalrouter improvements get PROJECT_ID --json
```

`create` pins the commit of `--ref`. `prepare` fetches that commit and finds the
LangGraph entrypoint from `langgraph.json` and `uv.lock`. Confirm with `get`
that preparation finished before you continue.

**2. Prepare a dataset version.** Tune needs an approved dataset version with
both validation and held-out examples. Trace imports create held-out examples
only, so before approval the person moves part of them to the validation split
in the dataset's example editor in the browser. Then approve and freeze a
version as in section D, step 4. Use the version ID returned by
`evalrouter datasets versions create DATASET_ID` or listed by
`evalrouter datasets versions list DATASET_ID --json`. A version without both splits is rejected with
`tune_workload_split_unavailable`.

**3. Quote, get the cap approved, and run the sweep.** Every Tune sweep has a
spending cap. Ask the person for the cap, show them the quote made with it, and
start the sweep only after they approve that cap.

```sh
evalrouter tune start --agent-project PROJECT_ID --dataset-version VERSION_ID --json
evalrouter tune quote SESSION_ID --max-cost USD_CAP --json
evalrouter tune start-sweep SESSION_ID --json
evalrouter tune status SESSION_ID --json
evalrouter tune result SESSION_ID --json
```

Repeat `status` about once a minute until the session is complete. Candidates
run on the validation examples. Tune then compares one finalist with the
current agent on the held-out examples. Incomplete execution cannot establish a
successful replacement, so report it as incomplete.

**4. Export the patch.**

```sh
evalrouter tune export SESSION_ID --patch ../tune.patch --json
```

The patch applies at `source_commit_sha` in the export. When the result keeps
the current agent, the command stops with `tune_no_change`. Tell the user; there
is nothing to open.

**5. Open the pull request.** Write `../tune-summary.md` from `tune result`: the
held-out quality and cost of the current agent and of the candidate, and the
session ID. Keep both files outside the clone. Then, from the clone:

```sh
git fetch origin
git switch -c evalrouter/tune-SESSION_ID SOURCE_COMMIT_SHA
git apply --index ../tune.patch
git commit -m "Apply EvalRouter Tune result SESSION_ID"
git push -u origin evalrouter/tune-SESSION_ID
gh pr create --title "Apply EvalRouter Tune result" --body-file ../tune-summary.md
```

Opening the pull request does not merge or deploy it. Leave review and merge to
the person.

## Feedback

When you hit what looks like an EvalRouter defect while using this skill,
report it yourself with `evalrouter feedback` as part of the task; don't ask
the user to file it. Before sending, read
[references/report-defects.md](references/report-defects.md) for the checks,
the report contents and the command.

- **Reportable:** after basic local checks (flags match `--help`, identifiers
  came from discovery in this workspace, `evalrouter whoami` shows the intended
  sign-in), the CLI or API contradicts documented behavior. Examples: an exact
  route ID just returned by `evalrouter catalog --models` is rejected as
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
