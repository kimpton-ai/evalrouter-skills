# Report an EvalRouter defect

Use this when the Feedback rules in `SKILL.md` say a problem is reportable.
The public guide is https://evalrouter.ai/developers/docs/feedback.

## Check first

Use only free, local or read-only steps:

- Compare the command with `evalrouter <command> --help` and the relevant docs
  page. Confirm each identifier came from discovery or a returned record.
- Run `evalrouter whoami` to confirm the sign-in and workspace.
- A read-only discovery call may be repeated once to confirm the behavior.
  Never repeat `run`, `connections check` or another billable step to
  reproduce a defect.

If `evalrouter feedback --help` fails, the installed CLI predates the command.
Don't upgrade or change the user's setup just to send a report; tell the user
about the defect instead.

## What to send

Collect from the failure:

- **API errors:** from the error JSON (`--json` prints `{"error": {...}}`), the
  `code`, the `request_id` (also in `error.feedback` when present) and the HTTP
  status. Name the request with its method and route, using placeholders for
  IDs, for example `/v1/quotes` or `/v1/runs/RUN_ID`.
- **Local CLI errors:** the CLI error code if one was printed. Omit the request
  fields when no request was made.

Write the report text yourself, briefly:

- **Summary** (one line, at most 200 characters): the behavior, without
  identifiers. For example, "Quote rejects an exact catalog route ID as
  ambiguous_model".
- **Details** (at most 5,000 characters): the public command shape with
  placeholders instead of the user's arguments
  (`evalrouter quote --config FILE`), what the docs say should happen, what
  happened instead, and the checks you already made. Describe values by role,
  never by content: "an exact route ID returned by catalog discovery", not the
  ID itself. For example:

  ```text
  Command: evalrouter quote --config FILE (managed route_id, sample coverage)
  Expected: an exact route ID returned by catalog discovery is accepted.
  Observed: HTTP 409 ambiguous_model.
  Checked: flags match --help; route ID copied from discovery in this
  workspace; whoami shows the intended sign-in.
  ```

The CLI adds its own name and version. Add `--agent-name`, and optionally
`--agent-version` and `--agent-model`, only with values you actually know
about yourself; the CLI sends the version and model only together with a name.
They accept letters, digits, spaces and `._/:@+()-`. Pass `--contact-ok` only
if the user agreed to be contacted.

Never include full commands, raw output, logs, tracebacks or environment
variables; keys, tokens or passwords; file paths, repository names or
private IDs (workspace, quote, run, connection); benchmark contents, prompts,
model outputs, scores or run data. The request ID is enough for EvalRouter to
find the request. Server-side redaction is a safety net, not a reason to paste
raw material.

## Send

Pipe the details on stdin so they stay out of shell history and process
listings:

```sh
evalrouter feedback --kind bug --severity degraded --summary "Brief behavior" --error-code ERROR_CODE --request-id REQUEST_ID --http-status 409 --method POST --path /v1/quotes --agent-name AGENT_NAME --details - --json
```

- `--kind`: `bug` when the CLI or API did something wrong, `docs` when the
  documentation is wrong or missing, `confusing_behavior` when it worked as
  designed but misled you.
- `--severity`: `blocker` when you cannot continue, `degraded` when a
  workaround exists, `nice_to_have` otherwise.

The receipt contains `feedback_id`. A non-null `duplicate_of` means EvalRouter
already has the report; don't send it again. If the user asks, show the outcome
with `evalrouter feedback status FEEDBACK_ID`.
