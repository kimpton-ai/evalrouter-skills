# EvalRouter Agent Skills

Agent skills for [EvalRouter](https://evalrouter.ai): run benchmark evaluations
behind a reviewed quote and spending cap, read and export results, and check
whether your own benchmark can run on EvalRouter and prepare it to be added.

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

> Can my Hugging Face dataset ORG/DATASET run on EvalRouter? Check the catalog,
> and if it is not there, prepare it to be added.

Self-serve benchmark submission is not available yet: the skill prepares your
benchmark (pinned public source, hashes, matching lm-eval or Inspect task,
license check, draft manifest) and helps you request it from EvalRouter.

The skill never starts paid work without your explicit approval of a quote, and
never handles your API key beyond reading `EVALROUTER_API_KEY` from your
environment.

| Skill | Purpose |
|---|---|
| [evalrouter](skills/evalrouter/SKILL.md) | Set up the CLI, run benchmarks behind an approved quote, export results, prepare your own benchmark to be added |

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
