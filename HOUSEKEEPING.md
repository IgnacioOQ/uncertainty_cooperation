# Housekeeping Workflow
- status: active
- type: workflow
- description: Recurring sanity check for the uncertainty_cooperation repo — verifies notebooks execute end-to-end, dependencies resolve, and the structure stays consistent with README.md.
- label: [core, agent]
- injection: excluded
- volatility: evolving
- scope: project-specific
- last_checked: 2026-05-14
<!-- content -->
Per-repository instance of the `HOUSEKEEPING_TEMPLATE.md` pattern in the knowledge base. This is a research codebase: there are no production tests, but every notebook should still execute end-to-end on a clean environment and the four research strands must stay legible from the README.

**Execution model:** sequential — each phase has an explicit exit criterion.

**Prerequisites:**
- Python ≥ 3.10 with `pip` available.
- Jupyter installed (`jupyter nbconvert` is the test harness here).
- A `WORKLOG.md` and `TODO_WORKFLOW.md` at the repo root.

---

## Phase 1 — Context Load

**Goal:** Confirm the toolchain matches what `README.md` and `requirements.txt` describe.

1. Read `README.md` and verify the repository map still matches the on-disk layout (`find . -type f -name "*.ipynb"` should match the table).
2. Read `requirements.txt`; confirm every import in the notebooks resolves to a listed package.
3. Read the **Latest Report** at the bottom of this file. Note the prior pass/fail counts per notebook.

**Exit criterion:** Layout matches README; dependency list is current; prior baseline is loaded.

---

## Phase 2 — Static Quality Checks

**Goal:** Catch syntax or import-time errors before paying the cost of full notebook execution.

### Step 1 — Notebook JSON validity

```bash
for f in $(find . -name "*.ipynb" -not -path "*/.ipynb_checkpoints/*"); do
  python3 -c "import json,sys; json.load(open('$f'))" && echo "OK: $f" || echo "BROKEN: $f"
done
```

### Step 2 — Import-time syntax check (per notebook)

```bash
for f in $(find . -name "*.ipynb" -not -path "*/.ipynb_checkpoints/*"); do
  jupyter nbconvert --to script --stdout "$f" 2>/dev/null | python3 -c "import sys, ast; ast.parse(sys.stdin.read())" \
    && echo "OK: $f" || echo "PARSE-FAIL: $f"
done
```

**Exit criterion:** Every notebook parses; no JSON corruption.

---

## Phase 3 — Notebook Execution Tests

**Goal:** Each notebook runs end-to-end on a clean kernel. This is the closest analogue to a "test suite" the repo has.

For each notebook (heavy ones — deep-ensemble runs — can be cut down by reducing `MAX_EPISODES` / `NUM_TRIALS` to a smoke-test value before running here):

```bash
jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=600 \
  path/to/notebook.ipynb
```

Record per-notebook: status (pass / timeout / error), wall-clock, and any new warnings. A timeout on the deep-ensemble notebook is acceptable if the smoke-test config was used; record `n/a-pending` rather than `pass`.

**Exit criterion:** Every notebook either passes or has a documented reason for being skipped.

---

## Phase 4 — Repository Health Checks

### Step 1 — Dependency drift

```bash
pip list --outdated
```

Note any major-version drift on `torch`, `numpy`, `matplotlib`. If `torch` has jumped a major version, schedule a manual re-run before trusting prior results.

### Step 2 — Dead artifacts

```bash
find . -name "*.ipynb_checkpoints" -o -name "__pycache__" -o -name ".DS_Store"
```

These should not be tracked. If any are under git, add them to `.gitignore` and `git rm --cached`.

### Step 3 — Documentation freshness

- Does the **Repository map** in `README.md` match the actual directory tree?
- Do per-folder `README.md` files in `0*/` still describe what their notebooks do?
- Is `notes/` aligned with the strands in `README.md`?

### Step 4 — Notebook output bloat

```bash
find . -name "*.ipynb" -not -path "*/.ipynb_checkpoints/*" -exec du -h {} +
```

Notebooks ≫ 1 MB usually carry embedded image outputs. Decide whether to commit them or strip outputs (`jupyter nbconvert --clear-output --inplace`) before the next commit.

**Exit criterion:** No surprising drift; anything actionable is filed in `TODO_WORKFLOW.md`.

---

## Phase 5 — Report & Close

1. Rename the existing `## Latest Report` to `## Previous Report`.
2. Append a new `## Latest Report` using the template at the bottom.
3. File any unresolved findings in `TODO_WORKFLOW.md`.
4. Bump `last_checked` in the metadata header.

**Exit criterion:** "Latest Report" reflects today's run; deferrals are in `TODO_WORKFLOW.md`.

---

## Quick Reference — Checklist

```
[ ] Phase 1: Layout matches README; requirements current; prior baseline read
[ ] Phase 2: All notebooks JSON-valid; all parse as Python
[ ] Phase 3: Each notebook runs end-to-end (or has a documented skip reason)
[ ] Phase 4: No dependency drift surprises; no stray caches; docs current
[ ] Phase 5: New "Latest Report" appended; `last_checked` bumped
```

---

## Latest Report Template

````markdown
## Latest Report

**Date:** YYYY-MM-DD
**Trigger:** {{routine cadence | post-merge | pre-release | post-incident}}

### Artifact counts
- Notebooks: N
- Lines of Python (nbconvert --to script | wc -l): N
- Notes (docx): N

### Static quality
- JSON validity: pass | N broken
- Python parse: pass | N parse-fails

### Notebook execution
- 01_imprecise_probabilities/ucb_initialization_study.ipynb: {{pass | error | n/a-pending}}
- 02_repeated_games_ucb/stag_hunt_egreedy_vs_ucb.ipynb: ...
- 02_repeated_games_ucb/ucb_testing_cooperation.ipynb: ...
- 03_sequential_games_ucb/polluted_river_public_goods.ipynb: ...
- 04_deep_ensembles/uncertainty_estimation_sandbox.ipynb: ...
- 04_deep_ensembles/deep_ensemble_polluted_river.ipynb: ...

### Repository health
- Dependencies: in sync | N outdated
- Stray caches: none | listed
- Docs: current | N drift items
- Notebook bloat: largest notebook = X MB

### Notable events
- {{Surprises, root-caused issues, decisions made.}}

### Follow-ups recorded in TODO_WORKFLOW.md
- {{Title — short reason | none}}
````

---

## Latest Report

**Date:** 2026-05-14
**Trigger:** Initial repository organisation — baseline run.

### Artifact counts
- Notebooks: 6
- Notes (docx): 3

### Static quality
- JSON validity: not yet measured (file extensions were just normalised from raw JSON blobs to `.ipynb`)
- Python parse: not yet measured

### Notebook execution
- Not yet measured — first execution sweep is deferred to the next housekeeping run (see `TODO_WORKFLOW.md`).

### Repository health
- Dependencies: `requirements.txt` created from observed imports; no version pins yet
- Stray caches: none
- Docs: current — README, per-folder READMEs, and HOUSEKEEPING all written together
- Notebook bloat: not yet measured

### Notable events
- Six untyped JSON files (notebooks saved without `.ipynb`) and one mis-extensioned `.py` notebook were renamed and sorted into the four research-strand folders described in `README.md`.
- Three `.docx` research notes were moved to `notes/`.
- Repository has no prior commits; this report is the baseline.

### Follow-ups recorded in TODO_WORKFLOW.md
- Run a full notebook execution sweep and populate the Notebook execution section.
- Pin versions in `requirements.txt` once a working environment is confirmed.
- Factor `PollutedRiverEnv` into a shared module (currently duplicated between the two Polluted River notebooks).
