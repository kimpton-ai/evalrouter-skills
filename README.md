# EvalRouter Agent Skills

Agent skills for [EvalRouter](https://evalrouter.ai): run versioned evaluations
behind a reviewed quote and spending cap, read and compare results, create
workspace-private benchmarks where enabled, and prepare public catalog or
onboarded supplier submissions.

Read [SKILL.md](skills/evalrouter/SKILL.md) on GitHub, or fetch the
[raw Markdown](https://raw.githubusercontent.com/kimpton-ai/evalrouter-skills/main/skills/evalrouter/SKILL.md).

## Install

### Claude Code plugin

```bash
claude plugin marketplace add kimpton-ai/evalrouter-skills
claude plugin install evalrouter@kimpton-ai
```

In Claude Code you can invoke the skill explicitly with `/evalrouter:evalrouter`.

### Other agents (skills.sh)

```bash
npx skills add kimpton-ai/evalrouter-skills --skill evalrouter
```

Select your agent when prompted. Installation is project-local by default; add
`-g` to install globally.

## Use

Ask your agent, for example:

> Use EvalRouter to run a small sample of a ready benchmark against a managed
> model. Show me the quote and wait for my approval before running anything.

> Can my Hugging Face dataset ORG/DATASET run on EvalRouter? Check whether I
> should create a workspace-private benchmark or request public catalog review.

Workspace-private benchmark availability depends on the current environment
and workspace. Keep the user in their configured environment and check the
[current availability](https://evalrouter.ai/developers/docs/availability).
Public catalog admission remains reviewed by EvalRouter; preparing a draft
does not publish it. Onboarded suppliers use a separate package workflow.

The skill never starts paid work without your explicit approval of a quote, and
uses browser sign-in by default. Workspace keys are for explicit automation;
the skill never asks you to paste credentials into chat.

| Skill | Purpose |
|---|---|
| [evalrouter](skills/evalrouter/SKILL.md) | Sign in, quote and run evaluations, read results, prepare private or public benchmark workflows |

## Development

```bash
uv run --no-project --python 3.12 --with httpx==0.28.1 --with pyyaml --with rich \
  python scripts/validate.py --cli PATH/TO/kimpton-evalrouter/packages/python/public/cli.py
```

Checks that the JSON manifests parse, the SKILL.md frontmatter is valid YAML,
and every evalrouter command mentioned in the skill exists in the CLI's
argparse definition.

## License

Not yet decided. See [LICENSE](LICENSE).
