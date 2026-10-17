# Very Small Homer — Dev Log
**Slogan:** Bone simple Homer

A running log of what happened, how, and why — written for programmers who want to
learn from the process as much as ship the product.

---

## 2026-10-16

### Repo reorganized: one directory per version

**What changed**

The repo now has three version directories at the top level:

```
caveman/    ← all caveman-edition content (moved here today)
STE-10/     ← reserved for STE-10 adaptation
Eli10/      ← reserved for Eli10 adaptation
```

Previously, `episodes/`, `episodes-src/`, `scripts/`, `STYLE.md`, and `index.html`
lived at the repo root. They were moved with `git mv` so history follows the files.

**Unix note — `git mv` vs `mv`**

Plain `mv` just moves a file. Git would see a deleted file + an untracked file and
lose the history connection. `git mv` tells Git to rename, so `git log --follow`
can trace a file's history across the move:

```sh
git log --follow caveman/episodes/book-01-gods.html
```

Try it. You'll see commits predating today's reorganization.

**Root index.html**

A thin redirect page now lives at the repo root. GitHub Pages serves from root,
so `index.html` there immediately bounces browsers to `caveman/index.html`.
No content — just a `<meta http-equiv="refresh">` tag, the oldest redirect trick on the web.

**Build script paths**

`caveman/scripts/build-episodes.py` uses Python's `pathlib`:

```python
out_dir = src_path.parent.parent / 'episodes'
```

`src_path` is e.g. `caveman/episodes-src/book-04-sparta.md`.
`parent` = `caveman/episodes-src/`
`parent.parent` = `caveman/`
`/ 'episodes'` = `caveman/episodes/`

Run the builder from inside `caveman/`:

```sh
cd caveman
python3 scripts/build-episodes.py episodes-src/*.md
```

**Empty directories and `.gitkeep`**

Git tracks files, not directories. An empty directory is invisible to git.
Convention: drop a zero-byte file called `.gitkeep` to make git notice the folder.
It has no special meaning to git — it's just a placeholder by community agreement.

```sh
ls -la STE-10/     # shows .gitkeep
git status         # shows it as a new tracked file
```

---

## 2026-10-16 (continued)

### STE-10 Book I — structure first, then prose

**What was built**

Ten episodes of Book I in the STE-10 voice, organized into four chapters:

```
STE-10/
  STYLE.md
  book-01/
    STRUCTURE.md          ← episode outline with Homer line numbers
    index.html            ← two-level index: chapters containing episodes
    episodes/
      ch1-ep1-the-muse.html
      ch1-ep2-the-gods-decide.html
      ch2-ep1-mentes-at-the-gate.html
      ch2-ep2-what-the-boy-carries.html
      ch2-ep3-the-bard-sings.html
      ch3-ep1-what-mentes-knows.html
      ch3-ep2-the-instructions.html
      ch3-ep3-antinoos-and-eurymakhos.html
      ch4-ep1-the-stranger-gone.html
      ch4-ep2-eurykleia.html
```

**The two-level structure**

| Chapter | Phase | Episodes |
|---------|-------|----------|
| 1 — The Singer Calls | Divine frame | 1.1 The Muse, 1.2 The Gods Decide |
| 2 — The Hall of the Suitors | Ithaka, the feast hall | 2.1–2.3 |
| 3 — The Stranger's Words | The advice from Mentes | 3.1–3.3 |
| 4 — After Dark | The night that follows | 4.1–4.2 |

The principle: **chapters are dramatic phases** (one location, one emotional arc);
**episodes are close-ups** on individual moments within that phase.

**Unix note — thinking in trees**

This directory structure is not arbitrary. It encodes the two-level hierarchy
directly in the filesystem:

```
book-01/           ← the book
  index.html       ← navigates by chapter
  episodes/        ← the atomic units
    ch{N}-ep{N}-*.html
```

The file names carry their own address: `ch2-ep1-mentes-at-the-gate.html` tells
you exactly where it sits in the structure without opening it. Good file naming is
a form of documentation. You can navigate the story with `ls`:

```sh
ls STE-10/book-01/episodes/ | sort
```

The story is visible in the output.

## 2026-10-17

### STE-10 Book II — the assembly, the ship, the night

Ten more episodes, three chapters:

| Chapter | Episodes |
|---------|----------|
| 1 — The Assembly | 1.1 Morning · 1.2 Telemakhos Speaks · 1.3 Antinoos Answers · 1.4 The Eagles · 1.5 The Assembly Ends |
| 2 — The Ship | 2.1 Athena on the Shore · 2.2 The Storeroom · 2.3 The Oath |
| 3 — The Night | 3.1 The Crew · 3.2 The Dark Departure |

Built the same way: edit `.md` in `book-02/episodes-src/`, run `python3 scripts/build.py book-02`.

**Unix note — reusing the pipeline**

The build script takes a book directory as its argument. Adding Book II required
zero changes to the script — the same `build.py` that built Book I builds Book II.
This is the Unix philosophy in action: write tools that do one thing and take
input as a parameter, not hardcoded into the tool itself.

```sh
python3 scripts/build.py book-01   # ten episodes
python3 scripts/build.py book-02   # ten more
```

The script does not know or care that there are now two books. It just reads
`.md` files, sorts by chapter/episode, and writes HTML. Adding Book III will
require the same zero changes.

**The STE-10 voice**

STE-10 is prose narrative — a narrator who can put the reader in the room. Where the
Caveman edition strips to pure dialogue, STE-10 adds small, precise observations:
the servants moving with eyes down; the folded tunic on the peg; the empty road where
the stranger should still be visible.

Present tense. Short paragraphs. No subordinate clauses stacked three deep. Vocabulary
that a confident ten-year-old can absorb from context. The stakes are real throughout.

---
