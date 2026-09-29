# Request a benchmark for the maintained public catalog

Use this when the user wants a benchmark reviewed for EvalRouter's maintained
**public catalog**. For workspace-private data, use
[private-benchmark.md](private-benchmark.md) where enabled. Verified suppliers
have a separate [package flow](publish-benchmark.md).

**Be honest about this path.** Preparing a draft does not submit, admit or
publish a public catalog benchmark. The EvalRouter team adds one after review.
What you can do for the user is:

1. check whether the benchmark is already in the catalog, and run it if so;
2. prepare the benchmark so it is ready for that review;
3. tell them how to request it.

Never say a benchmark "has been added", "is submitted" or "will be available"
because you prepared it. It becomes runnable only when it shows up in
`evalrouter catalog` for their workspace with `quote_availability.status` =
`ready_for_quote`.

## 1. Is it already in the catalog?

```sh
evalrouter catalog --query "BENCHMARK NAME" --json
evalrouter catalog --slug BENCHMARK_SLUG --json
evalrouter catalog --runner lm-eval --json
evalrouter catalog --runner inspect --json
```

If a matching profile is `ready_for_quote`, stop here and use the normal
quote, approval, run flow in SKILL.md section B. Read the profile's source,
split, metrics and license before telling the user it is "their" benchmark. A
catalog entry with the same name can use a different split or protocol.

## 2. Prepare the benchmark

Work through these checks with the user and write down the result of each. If
one fails, say which one and why. Do not work around it.

### a. Host the data on Hugging Face and pin it to one commit

For this maintained-catalog request, use a **public Hugging Face dataset**,
with every data file from the same dataset and commit. GitHub pins a task
definition here, not the data. If the data lives only on GitHub, it needs a
permitted public dataset host for this path. Private files can instead become
workspace-private benchmarks where that feature is enabled; they do not
become public catalog data.

Pin every file to an exact commit: a 40-character hexadecimal commit ID.
Branches, tags, `main` and "latest" are refused because they can change. To
turn a tag or branch into a commit ID:

```sh
# Hugging Face dataset (the ref can be a tag or a branch)
git ls-remote https://huggingface.co/datasets/ORG/DATASET REF
```

If the user has Python and `huggingface_hub`, this prints the commit, each
file's size and its SHA-256, reading metadata only:

```sh
uv run --no-project --with huggingface_hub python -c '
from huggingface_hub import HfApi
info = HfApi().dataset_info("ORG/DATASET", revision="REF", files_metadata=True)
print("commit", info.sha)
for f in info.siblings:
    print(f.rfilename, f.size, f.lfs.sha256 if f.lfs else "not-lfs: hash the download")
'
```

Write data sources as URIs with the commit in them:
`hf://ORG/DATASET@COMMIT/path/to/file.parquet`.

### b. List every file with its SHA-256 and size

For each file the benchmark needs (the scored split, plus any split or notice
the loader also reads), record the pinned URI, the SHA-256 and the size in
bytes. Compute them from a download at the pinned commit, not from a branch:

```sh
curl -fsSL -o file.parquet "https://huggingface.co/datasets/ORG/DATASET/resolve/COMMIT/path/to/file.parquet"
shasum -a 256 file.parquet
wc -c < file.parquet
```

Mark which file is scored and why each other file is there (for example
"companion split the loader reads, not scored").

### c. Match an existing lm-eval or Inspect task

EvalRouter runs benchmarks through maintained evaluation harnesses. A
benchmark can be added only when an existing task in one of them already
scores it:

- an **lm-evaluation-harness** task, named by its path under `lm_eval/tasks/`
  (for example `super_glue/copa/default.yaml`), or
- an **Inspect** task from `inspect_evals`.

Find the task, then confirm it reads the same dataset, split and columns as the
user's data, and note its metrics. The grader must be that task exactly as it
is at the harness revision EvalRouter's runners pin. A task that exists only in
a newer or forked version of the harness, or one the user has changed, does not
count. The user only names the task; EvalRouter records the pinned revision.

If no existing task fits, or this proposed benchmark needs its own grading
code, an LLM judge, tools, multiple turns or a code sandbox, tell the user
plainly that this **maintained-catalog request path** does not cover it. Do not
write a grader as a workaround. An onboarded supplier may have a separate
reviewed package path; never promise it will be accepted.

### d. Check the license

The data license must be one of: **MIT, Apache-2.0, BSD-2-Clause,
BSD-3-Clause, CC-BY-4.0, CC-BY-SA-4.0, CC0-1.0**. Anything else is refused.
EvalRouter reviews licenses by hand and never infers one from a name alone.

Check that the license shown on the dataset host (the Hugging Face card's
`license:` field) matches the license the
authors grant. If the host shows `other`, `unknown` or nothing, find the
authors' own grant (paper, website or LICENSE file) and record the link;
expect a manual review, which can end in a refusal. Record the license's URL
and any notice text that has to be kept. Do not state that a dataset is
licensed for commercial evaluation unless its license says so.

### e. Draft the manifest

Write a draft in the shape EvalRouter's catalog uses. The EvalRouter team
completes the operational fields during review; leave them as shown. Use only
values you have verified in steps a to d. Never invent a hash, size or commit.

```yaml
schema: evalrouter.catalog.benchmark.v1
slug: my-benchmark                 # lowercase letters, digits and hyphens
name: "My Benchmark: test split (complete 500)"
category: Reasoning
description: One sentence saying what is scored and how.

source:                            # the scored file
  uri: hf://ORG/DATASET@0123456789abcdef0123456789abcdef01234567/data/test.parquet
  sha256: <64 hex characters>
  bytes: <integer>
  additional_files:                # other files the loader reads (optional)
    - uri: hf://ORG/DATASET@0123456789abcdef0123456789abcdef01234567/data/train.parquet
      sha256: <64 hex characters>
      bytes: <integer>
      role: loader companion split (not scored)

adapter:
  runner: lm-eval                  # or inspect
  entrypoint: my_task/default.yaml # the lm-eval task path, or the Inspect task
  split: test
  # EvalRouter fills in protocol, source_sha256 and capability.

grader:
  # The harness's own task and metric, called directly (no custom code).
  kind: author-native
  metrics: [acc]
  # EvalRouter fills in the pinned uri.

sampling:
  generation: greedy               # or provider_default
  max_output_tokens: 0             # 0 for likelihood tasks; a limit for generation
  attempts_per_task: 1

license:
  data: CC-BY-4.0                  # must be on the allowlist
  code: MIT
  url: https://link-to-the-authors-license-grant

# EvalRouter fills in display, pricing_class, concurrency_class,
# qualification and environments during review.
```

Never put credentials, access tokens or private customer data in the manifest
or in anything you send.

## 3. Request that it be added

The public docs (https://evalrouter.ai/developers/docs) list support at
`info@kimpton.ai`. Help the user write a short request with:

- the benchmark name and what it measures;
- the drafted manifest from step 2e;
- the matched lm-eval or Inspect task and its metrics;
- the license, the link to the authors' grant, and any notice;
- a note of anything that failed or is uncertain (for example a host license of
  `other`).

The user sends it. Do not send email for them unless they ask and you have a
tool for it. Adding the benchmark is a reviewed decision by the EvalRouter
team; it can be declined, and there is no timeline to promise.

After it is added, it appears in `evalrouter catalog`. Running it is ordinary
paid work: quote first, then the user's explicit approval of that quote and
its cap (SKILL.md section B).

## Other paths and limits

Private benchmarks in a workspace and pinned Hugging Face imports are
available where enabled; see [private-benchmark.md](private-benchmark.md).
They are separate from public catalog review. Do not offer automatic task
detection or a per-run ephemeral dataset import as a substitute for review.
