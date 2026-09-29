# Publish a benchmark package (onboarded suppliers only)

> **Who this is for.** This flow is only for benchmark suppliers whom the
> EvalRouter team has onboarded and whose workspace has a **verified
> namespace**. It is not self-serve. For every other user, follow
> [add-a-benchmark.md](add-a-benchmark.md) for a public catalog request, or
> [private-benchmark.md](private-benchmark.md) for a workspace-private
> benchmark where enabled.

> **Version gate.** The `benchmark` command group is newer than some
> 0.2.0 builds. Run `evalrouter benchmark --help`; if it is not recognised,
> stop and tell the user their installed CLI does not support benchmark
> publishing yet. Do not fall back to raw HTTP.

## 1. Install the offline extra

`init`, `validate` and `bundle` need the version-matched validator extra. The
network commands (`submit`, `status`, `inspect`, `grant`, `revoke`) do not.

```sh
uv tool install --python 3.12 "evalrouter[benchmark]"
```

Without it those three commands stop with `benchmark_extra_required` and print
the exact install string to use.

## 2. Draft

```sh
evalrouter benchmark init ./my-benchmark --namespace NAMESPACE --name my-benchmark --template text
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

This supplier **package** workflow uses local files; `benchmark import` is a
separate workspace-private Hugging Face source flow and does not fill a
supplier package. If the supplier has only a dataset URL, help them prepare
local package material after checking its license. Never include credentials
or private customer data.

## 3. Validate and bundle (offline)

```sh
evalrouter benchmark validate ./my-benchmark
evalrouter benchmark bundle ./my-benchmark --output my-benchmark.zip
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
evalrouter benchmark submit my-benchmark.zip --wait
```

The upload is resumable: by default the idempotency key derives from the bundle
digest, so re-running submit on the same file resumes rather than duplicates.
`--idempotency-key` overrides it. With `--wait`, the CLI polls preparation until
`succeeded`, `failed` or `cancelled` (exit 0, 1, 4). Interrupting the wait cancels
nothing on the server. Accepted preparation is not qualification or admission.

## 5. Inspect and share

```sh
evalrouter benchmark status PACKAGE_ID
evalrouter benchmark inspect PACKAGE_ID
evalrouter benchmark grant PACKAGE_ID --workspace GRANTEE_WORKSPACE_ID --reason "Shared for evaluation" --permissions discover,execute
evalrouter benchmark revoke PACKAGE_ID --workspace GRANTEE_WORKSPACE_ID --reason "Access ended"
```

`status` shows the package lifecycle; `inspect` shows the compiled protocol
(protocol and component digests, compiler version, execution class). Grants are
issued against the compiled protocol for one grantee workspace, with a recorded
reason. `--permissions` is `discover`, `execute` or both (default both).
Revoking blocks new quotes from that workspace.

Once qualified and granted, the benchmark appears through `evalrouter catalog`
for permitted workspaces and is quoted and run with the normal
quote → approval → run flow in SKILL.md section B.
