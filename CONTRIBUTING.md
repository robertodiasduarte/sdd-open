# Contributing

Read this before opening a pull request — the model here is unusual and you deserve to know it
before spending your time.

## How this repository is maintained

SDD Open is a **curated snapshot** of a framework in daily production use in a private codebase.
Changes flow one way: they are made and proven in that private repository, then exported here
through a scripted, gated publication. This repository is never the source.

The practical consequences:

- **Pull requests cannot be merged directly.** A merge here would be overwritten by the next
  export. A PR that is accepted gets reimplemented upstream and arrives in the following release,
  with attribution in the commit and the release notes.
- **Releases are periodic, not continuous.** There is no promise of cadence.
- **The private layer never appears here.** Concrete landmine rules, domain skills and internal
  conventions are excluded by an allowlist, not by a filter.

If that model does not suit you, forking is genuinely reasonable — this is a few hundred lines
of bash, two small Python validators and a set of markdown skills. The MIT license is there for that.

## What is most useful

**Issues, above all.** Especially:

- The exit contract behaving differently than documented on your platform (bash version, macOS
  vs Linux vs Git Bash, CI runner).
- A false positive in the ambiguity detection — a spec that should pass returning exit `5`.
- An agent that does not pick up `.agents/skills/` or the `AGENTS.md` block the way
  [docs/quickstart.md](docs/quickstart.md) claims. Say which agent, which version, what you ran.
- Documentation that is wrong about another framework in [comparison.md](docs/comparison.md).
  Corrections from maintainers of those projects are especially welcome.
- Adaptation friction: a stack where the slots in `sdd/config.yaml` do not stretch far enough.

**Discussion before code.** If you want to change the gate mechanism, the exit contract or the
generated-adapter model, open an issue first. Those are the framework's spine.

## If you do send a PR

- Run the fixtures: `sdd/bin/verify-gate.sh` against the three in `sdd/fixtures/`, expecting
  `0 / 5 / 64`. Run `sdd/bin/playbook-lint.sh --self-test`. A PR that changes those expectations
  changes the contract, which is an issue-first discussion.
- Run `bash -n` on every script and `python3 sdd/bin/skill-lint.py` on every `SKILL.md` you touch.
- Keep examples in a neutral domain (e-commerce, SaaS, blog). No real personal data, no real
  hostnames, no credentials — not even fake-looking ones.
- **bash 3.2**: no `declare -A`, no `mapfile`, no `${var,,}`; `${VAR}` with braces before any
  non-ASCII character. No zsh, no symlinks.
- Follow [docs/cli-conventions.md](docs/cli-conventions.md): symbol always with a word, every
  error with cause and fix, every verdict ending in `RESULTADO:`.
- Small and focused beats broad. Surgical changes, nothing unrequested.

## Language

Skill bodies, templates, fragments and command messages are written in **Brazilian Portuguese**
and that is canonical. `README.md` and `docs/quickstart.md` exist in English as translations of
the Portuguese originals; other English docs under `docs/` are kept in step when they change.
Translations into other languages are welcome as issues first, so we can agree on maintenance
before the files exist.

## Code of conduct

Be decent. Assume the other person is competent and busy. Technical disagreement is welcome;
contempt is not.
