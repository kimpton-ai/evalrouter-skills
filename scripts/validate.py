#!/usr/bin/env python3
"""Validate this skills repository.

1. The Claude plugin manifests parse and agree with each other.
2. Every SKILL.md has valid YAML frontmatter with `name` and `description`.
3. Every `evalrouter ...` command mentioned in the skill Markdown exists in the
   shipped CLI's argparse tree, including each `--flag` used with it.

Usage (needs httpx and PyYAML, e.g. via uv):
    uv run --with httpx --with pyyaml --with rich python scripts/validate.py \
        --cli /path/to/kimpton-evalrouter/packages/python/public/cli.py

The CLI is imported only to build its parser; no command is executed and no
network request is made.
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
failures: list[str] = []


def fail(message: str) -> None:
    failures.append(message)
    print(f"FAIL {message}")


def ok(message: str) -> None:
    print(f"ok   {message}")


# --- 1. manifests -----------------------------------------------------------


def check_manifests() -> None:
    parsed = {}
    for name in ("marketplace.json", "plugin.json"):
        path = ROOT / ".claude-plugin" / name
        try:
            parsed[name] = json.loads(path.read_text())
            ok(f".claude-plugin/{name} parses")
        except (OSError, ValueError) as error:
            fail(f".claude-plugin/{name}: {error}")
    market, plugin = parsed.get("marketplace.json"), parsed.get("plugin.json")
    if not (market and plugin):
        return
    entries = {entry.get("name"): entry for entry in market.get("plugins", [])}
    entry = entries.get(plugin.get("name"))
    if entry is None:
        fail(f"marketplace lists no plugin named {plugin.get('name')!r}")
        return
    ok(f"marketplace {market.get('name')!r} lists plugin {plugin.get('name')!r}")
    source = (ROOT / entry.get("source", "")).resolve()
    if source != ROOT:
        fail(f"plugin source {entry.get('source')!r} does not resolve to the repo root")
    else:
        ok("plugin source './' resolves to the repo root")


# --- 2. frontmatter ---------------------------------------------------------


def check_frontmatter() -> list[Path]:
    skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
    if not skills:
        fail("no skills/*/SKILL.md found")
    for path in skills:
        text = path.read_text()
        match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        rel = path.relative_to(ROOT)
        if not match:
            fail(f"{rel}: missing frontmatter")
            continue
        try:
            meta = yaml.safe_load(match.group(1))
        except yaml.YAMLError as error:
            fail(f"{rel}: frontmatter is not valid YAML: {error}")
            continue
        if not isinstance(meta, dict) or not meta.get("name") or not meta.get("description"):
            fail(f"{rel}: frontmatter needs name and description")
            continue
        if meta["name"] != path.parent.name:
            fail(f"{rel}: name {meta['name']!r} differs from directory {path.parent.name!r}")
            continue
        lines = text.count("\n")
        ok(
            f"{rel}: valid YAML frontmatter (name={meta['name']!r}, "
            f"description {len(meta['description'])} chars, {lines} lines)"
        )
    return skills


# --- 3. commands ------------------------------------------------------------


def load_parser(cli_path: Path) -> argparse.ArgumentParser:
    """Build the shipped parser from public/ overlaid on the generated SDK sources.

    public/ holds the hand-written published modules (cli.py, __init__.py, ...);
    the generated ones (types.py, _resources.py, _transport.py) live in
    src/kimpton_evalrouter/. Both are copied into a temporary package so that
    public/cli.py is imported exactly as shipped.
    """
    import shutil
    import tempfile

    public = cli_path.parent
    generated = public.parent / "src" / "kimpton_evalrouter"
    staging = Path(tempfile.mkdtemp()) / "kimpton_evalrouter"
    shutil.copytree(generated, staging)
    for module in public.glob("*.py"):
        shutil.copy2(module, staging / module.name)
    sys.path.insert(0, str(staging.parent))
    import kimpton_evalrouter  # noqa: E402
    from kimpton_evalrouter import cli  # noqa: E402

    print(f"     CLI version {kimpton_evalrouter.__version__} from {cli_path}")
    return cli.parser()


def subcommands(parser: argparse.ArgumentParser) -> dict[str, argparse.ArgumentParser]:
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return dict(action.choices)
    return {}


def options(parser: argparse.ArgumentParser) -> set[str]:
    return {flag for action in parser._actions for flag in action.option_strings}


def mentions(path: Path) -> list[str]:
    """`evalrouter ...` invocations inside inline code spans and fenced blocks."""
    text = path.read_text()
    found = []
    for block in re.findall(r"```[a-z]*\n(.*?)```", text, re.S):
        found += [line.strip() for line in block.splitlines() if line.strip().startswith("evalrouter ")]
    prose = re.sub(r"```.*?```", "", text, flags=re.S)
    for span in re.findall(r"`([^`\n]+)`", prose):
        if span.startswith("evalrouter "):
            found.append(span.strip())
    return found


def check_command(root: argparse.ArgumentParser, command: str) -> str | None:
    try:
        tokens = shlex.split(command)[1:]
    except ValueError:
        tokens = command.split()[1:]
    parser, path = root, ["evalrouter"]
    for token in tokens:
        if token.startswith("<"):  # e.g. `evalrouter <command> --help`
            return None
        children = subcommands(parser)
        if token.startswith("-") and token != "-":  # a bare - is a stdin value
            flag = token.split("=", 1)[0]
            if flag not in options(parser):
                return f"{' '.join(path)} has no option {flag}"
            continue
        if children:
            if token not in children:
                return f"{' '.join(path)} has no subcommand {token!r}"
            parser = children[token]
            path.append(token)
        # Otherwise a positional placeholder such as RUN_ID or ./my-benchmark.
    if subcommands(parser) and "--help" not in tokens:
        return f"{' '.join(path)} needs a subcommand"
    return None


def check_commands(cli: Path, files: list[Path]) -> None:
    root = load_parser(cli)
    seen: dict[str, list[str]] = {}
    for path in files:
        for command in mentions(path):
            seen.setdefault(command, []).append(str(path.relative_to(ROOT)))
    bad = 0
    for command, where in sorted(seen.items()):
        problem = check_command(root, command)
        if problem:
            bad += 1
            fail(f"{problem}  [{command}] in {', '.join(sorted(set(where)))}")
    ok(f"{len(seen) - bad}/{len(seen)} distinct `evalrouter ...` mentions resolve against argparse")
    used = set()
    for command in seen:
        words = [t for t in command.split()[1:] if not t.startswith(("-", "<"))]
        parser, name = root, []
        for word in words:
            children = subcommands(parser)
            if word not in children:
                break
            parser = children[word]
            name.append(word)
        if name:
            used.add(" ".join(name))
    print("     commands referenced: " + ", ".join(sorted(used)))


def main() -> int:
    arguments = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    arguments.add_argument("--cli", required=True, type=Path, help="Path to public/cli.py")
    args = arguments.parse_args()
    check_manifests()
    skills = check_frontmatter()
    markdown = sorted({*skills, *(ROOT / "skills").glob("*/references/*.md"), ROOT / "README.md"})
    check_commands(args.cli.resolve(), markdown)
    print(f"\n{'FAILED' if failures else 'PASSED'}: {len(failures)} problem(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
