# appa

Portable coding-agent workflow. Carries one set of workflow rules across machines and across agents (Claude Code and pi-coding-agent).

## What it does

On any machine you clone this repo to:

- Symlinks shared slash commands and skills from `commands/` and `skills/` into both `~/.claude/` and `~/.pi/agent/`
- Projects canonical workflow rules (`instructions/`) into `~/.pi/agent/AGENTS.md` so pi loads them at session start
- Reinstalls Claude Code marketplaces and plugins from `agents/claude/settings.json` (currently: superpowers + plannotator)
- Installs the `appa` CLI to `~/.local/bin/appa`

Pi extensions and pi settings (model, theme, etc.) are managed per-machine, not by appa.

Claude memory projection is **deferred** — claude reads its existing per-project memory dirs as-is; we'll revisit the right surface (`~/.claude/CLAUDE.md` vs per-project memory) in a future task.

## Requirements

- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) (≥ 0.11)
- At least one of: `claude` (Claude Code CLI), `pi` (pi-coding-agent CLI)
- `plannotator` CLI (optional, but recommended — used by the workflow rules)

## Quickstart on a new machine

```bash
git clone git@github.com:KaranjotVendal/appa.git ~/dev/appa
cd ~/dev/appa
./bootstrap.sh
```

`bootstrap.sh` is idempotent — safe to re-run after any `git pull`.

## Day-to-day

```bash
appa sync                  # re-project instructions to pi (claude side deferred)
appa status                # show repo state + claude memory drift
appa commit [-m MSG]       # stage tracked files and commit (no auto-push)
```

Commands wired but not yet functional (waiting on the claude-side projection design):

```bash
appa memory pull           # claude-only; depends on .machine-<host> file
appa memory push           # claude-only; depends on .machine-<host> file
appa memory diff           # works (shows snapshot vs canonical diff)
```

## Adding a new workflow rule by hand

```bash
$EDITOR ~/dev/appa/instructions/new_rule.md
# write frontmatter: name, scope (global), type (feedback|user|project|reference), description
# write the body
appa sync                  # projects to pi's AGENTS.md
appa commit -m "instruction: new rule"
git push
```

## Layout

- `instructions/` — canonical workflow rules (the source of truth)
- `commands/` — user-authored slash commands (currently empty)
- `skills/` — user-authored skills (currently empty)
- `agents/claude/settings.json` — canonical claude config (model, theme, enabledPlugins, marketplaces)
- `memory/snapshot/` — raw mirror of claude memory dir (for diffing)
- `bootstrap.sh` — idempotent setup script run once per machine
- `src/appa_lib/` — the Python package backing the CLI

## Updating cherry-picked superpowers skills (pi-only)

Pi loads five superpowers skills from `agents/pi/skills/` because superpowers' upstream plugin doesn't ship a pi-compatible install path. The picks are: `brainstorming`, `writing-plans`, `test-driven-development`, `verification-before-completion`, `receiving-code-review`. When upstream changes meaningfully:

```bash
# update the cached version first
claude plugin install superpowers@claude-plugins-official

# re-cherry-pick from the updated cache
SRC=~/.claude/plugins/cache/claude-plugins-official/superpowers/<version>/skills
DST=~/dev/appa/agents/pi/skills
for s in brainstorming writing-plans test-driven-development verification-before-completion receiving-code-review; do
  cp -R "$SRC/$s/." "$DST/$s/"
done
appa commit -m "chore: re-cherry-pick superpowers skills (v<n>)"
```

Claude side gets the update automatically via the plugin install; pi side doesn't, so this manual step is required.

## Design

See `docs/superpowers/specs/` (gitignored — local-only working artifact).
