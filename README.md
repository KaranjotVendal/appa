# appa

Portable coding-agent workflow. Carries one workflow across machines and across agents (Claude Code, pi-coding-agent).

## Quickstart on a new machine

```bash
git clone <repo-url> ~/dev/appa
cd ~/dev/appa
./bootstrap.sh
```

Bootstrap requires `uv` and at least one supported agent CLI (`claude` or `pi`). It runs `uv sync`, backs up any existing config, symlinks shared content into the right places, projects workflow instructions into each agent's native format, and installs the `appa` CLI to `~/.local/bin/appa`.

## Day-to-day

- `appa sync` — re-project instructions after editing `instructions/`
- `appa memory pull` — capture rules Claude wrote during sessions
- `appa commit` — stage and commit (no auto-push)
- `appa status` — what's drifted between live and canonical

See `docs/superpowers/specs/` for the design.
