# Upgrading SDD Open in a project

[Português](pt-BR/upgrade.md)

When a new SDD Open version ships, your project does not change by itself: `init` never overwrites what already
exists, and `sync` only regenerates the adapters. `upgrade` is what brings the new version into the project. It copies
what belongs to the package and you did not edit, puts the new version **next to** each file you edited, and commits
nothing.

## How you find out

- `doctor` shows the project version, the package version and the latest published one:
  `✅ versão: projeto v2.17.0 · pacote v2.17.0 · última publicada v2.17.0`. When a newer one exists it adds
  `⚠️ saiu a v2.18.0 (seu projeto está na v2.17.0)` and the command to upgrade.
- `sdd-new-session` (when opening a work front) and `sdd-release` (at the start of a release) pass the same notice on in
  one sentence. They never stop or ask: you upgrade when you want to.
- The check is an anonymous `git ls-remote` of the public repository, with a 5-second ceiling. Nothing from your
  project is sent. Offline, `doctor` says `ℹ️ versão nova: não conferida` and carries on.
- To turn it off: `open:` → `check_updates: false` in `sdd/config.yaml` (whole project), or `SDD_OPEN_CHECK_UPDATES=0`
  in the environment (that terminal only).

## The commands

With the package in a clone (`~/sdd-open`), from inside the project folder:

```bash
git -C ~/sdd-open pull                                  # fetch the new package version
bash ~/sdd-open/bin/sdd-open.sh upgrade --dry-run       # show the plan, write nothing
bash ~/sdd-open/bin/sdd-open.sh upgrade                 # show the plan again and ask [y/N]
```

With the package downloaded from the Releases page, replace `~/sdd-open` with the extracted folder
(`sdd-open-v2.18.0`).

## The plan

`upgrade` compares every file the package installs (the skills in `.agents/skills/` and the `sdd/` files `init`
copies) with the new version and with the previous install, recorded in `sdd/open-instalado.txt`:

| Plan line | What it is | What `upgrade` does |
|---|---|---|
| `= N iguais ao pacote novo` | already the new version | nothing |
| `+ N novos` | the new package has it, the project does not | copies it |
| `~ N do pacote, sem edição sua` | from the package, unedited (what the previous version installed) | replaces it with the new version |
| `⚠️ N editados por você` | edited by you: differs from both the previous and the new version | **does not touch it**; puts the new version next to it |
| `⚠️ N saíram do pacote` | the previous version installed it, the new one dropped it | **does not delete it**; only lists it |

Before the `[y/N]` it says: "Nada que você editou será tocado. Nada será commitado." (nothing you edited will be
touched; nothing will be committed). Up to 10 names per line; the rest with `--verbose`.

## Afterwards

- Each edited file gets `<file>.novo` (the new version) and `<file>.diff` (from yours to the new one) under
  `sdd/upgrade/<version>/`. Merge whenever you like; the folder can be deleted afterwards and does not need to be
  committed.
- `upgrade` ends by running `sync` (adapters) and `doctor`, with `RESULTADO: ATUALIZADO` or
  `RESULTADO: ATUALIZADO, N PARA MESCLAR` (N to merge).
- Check with `git status` and commit in a work front, like any change. `sdd/open-instalado.txt` goes along: it is what
  lets the next `upgrade` tell the package's files from yours.
- If something fails midway, the record does not change: run `upgrade` again and it resumes (what was already copied
  becomes "equal").

## Projects installed before v2.17.0

Those projects have no `sdd/open-instalado.txt`. Without it, `upgrade` stops before writing and asks for the package
of the version the project has, with `--de`:

```bash
bash ~/sdd-open/bin/sdd-open.sh upgrade --de v2.12.1    # the tag of the version the project has (from the clone)
# or, with the old package folder (it must be named sdd-open-vX.Y.Z):
git -C ~/sdd-open archive --prefix=sdd-open-v2.12.1/ v2.12.1 | tar -x -C /tmp
bash ~/sdd-open/bin/sdd-open.sh upgrade --de /tmp/sdd-open-v2.12.1
```

Not sure of the version? Look at the commit that installed SDD Open
(`git log --reverse --oneline -- sdd/playbook.md | head -1`) or at the Release you downloaded. If the `--de` folder
does not look like the project's version (fewer than half of the files match), the plan warns before the `[y/N]`.

## Exit codes

`0` upgraded, up to date, dry run or cancelled · `1` write failure (run again, it resumes) · `64` usage or
precondition: no record and no `--de`, `--de` that is not a package, package older than the project, unknown package
version.
