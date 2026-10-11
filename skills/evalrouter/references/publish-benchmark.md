# Publish a benchmark package (onboarded suppliers only)

> **Who this is for.** This flow is only for benchmark suppliers whom the
> EvalRouter team has onboarded and whose workspace has a **verified
> namespace**. It is not self-serve. For every other user, follow
> [add-a-benchmark.md](add-a-benchmark.md) for a public catalog request, or
> [private-benchmark.md](private-benchmark.md) for a workspace-private
> benchmark where enabled.

> **Availability gate.** Run `evalrouter benchmarks --help`. The network
> commands (`submit`, `status`, `inspect`, `grant`, `revoke`) appear only in
> builds where supplier publishing is enabled; the public release lists only
> `init`, `validate` and `bundle`. If `submit` is not listed, stop after
> bundling and tell the user that submission is not available to them yet. Do
> not fall back to raw HTTP.

## 1. Install

`init`, `validate` and `bundle` run offline with the base installation:

```sh
uv tool install --python 3.12 evalrouter
```

## 2. Draft

```sh
evalrouter benchmarks init ./my-benchmark --namespace NAMESPACE --name my-benchmark --template text
```

`--namespace` and `--name` are required. `--template` is `text` (default,
declarative exact-match scoring), `custom-scorer` or `multi-turn` (both sandboxed,
with an `evaluation.py` entrypoint and a dependency lock). The destination must
not already exist.

The draft is **synthetic** and grants no rights. It contains `evalrouter.json`
(the package manifest, schema `evalrouter.package.v1`) plus role-tagged files:

| File | Role | The user must replace it with |
| --- | --- | --- |
| `tasks.jsonl` | dataset | Real tasks (`evalrouter.tasks.v1`: `id`, `input`, `target`) |
| `fixtures.jsonl` | fixtures | Grading fixtures: known outputs and the score each must get |
| `RIGHTS.txt` | license | The actual code, data and test licences and attribution |
| `README.md` | documentation | What the benchmark measures, maintainer, limits |
| `evaluation.py`, `dependencies.lock` | code, dependencies | Only for sandbox templates: a real scorer and hashed, resolved deps |

In `evalrouter.json`, the user must also set title, description, authors,
maintainer, `rights` entries (the draft uses `LicenseRef-NotGranted` and
`unknown` permissions), dataset split and task count, limits, metrics and
limitations, and review the `"synthetic": true` flag once the content is real
(check the current docs or `validate` output for how it is treated).

This supplier **package** workflow uses local files; `benchmarks imports huggingface` is a
separate workspace-private Hugging Face source flow and does not fill a
supplier package. If the supplier has only a dataset URL, help them prepare
local package material after checking its license. Never include credentials
or private customer data.

## 3. Validate and bundle (offline)

```sh
evalrouter benchmarks validate ./my-benchmark
evalrouter benchmarks bundle ./my-benchmark --output my-benchmark.zip
```

Nothing is executed or sent. `validate` reports validity, package and component
SHA-256, task count and warnings. After editing files, file-table hashes in
`evalrouter.json` must match; re-run `validate` until it passes. `bundle` never
overwrites an existing `--output`. Local validation is not platform admission.

## 4. Submit (network, needs approval)

Requirements: sign in to the intended workspace (browser sign-in by default,
or a scoped API key for explicit automation) and confirm a **verified
namespace** there whose slug equals the package's `namespace` (otherwise
`namespace_not_found`). Review the package and any server-side cost or work
before obtaining the human's submission approval. Submission does not approve
any later evaluation charge.

```sh
evalrouter benchmarks submit my-benchmark.zip --wait
```

The upload is resumable: the idempotency key derives from the bundle digest, so
re-running submit on the same file resumes rather than duplicates. With `--wait`, the CLI polls preparation until
`succeeded`, `failed` or `cancelled` (exit 0, 1, 4). Interrupting the wait cancels
nothing on the server. Accepted preparation is not qualification or admission.

## 5. Inspect and share

```sh
evalrouter benchmarks status PACKAGE_ID
evalrouter benchmarks inspect PACKAGE_ID
evalrouter benchmarks grant PACKAGE_ID --workspace GRANTEE_WORKSPACE_ID --reason "Shared for evaluation" --permissions discover,execute
evalrouter benchmarks revoke PACKAGE_ID --workspace GRANTEE_WORKSPACE_ID --reason "Access ended"
```

`status` shows the package lifecycle; `inspect` shows the compiled protocol
(protocol and component digests, compiler version, execution class). Grants are
issued against the compiled protocol for one grantee workspace, with a recorded
reason. `--permissions` is `discover`, `execute` or both (default both).
Revoking blocks new quotes from that workspace.

Once qualified and granted, the benchmark appears through `evalrouter benchmarks list`
for permitted workspaces and runs with the normal
wallet-funded evaluation flow in SKILL.md section B.
