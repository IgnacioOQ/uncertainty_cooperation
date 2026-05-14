# TODO Workflow
- status: active
- type: plan
- id: uncertainty_cooperation.todo_workflow
- description: Cross-session task backlog for the uncertainty_cooperation repository; each task is self-contained and can be picked up by a coding agent.
- label: [planning, agent]
- injection: excluded
- volatility: evolving
- owner: agent
- last_checked: 2026-05-14
<!-- content -->
Cross-session task backlog. Tasks are added here when work started in a session cannot be completed immediately. Each task is fully self-contained — a fresh agent should be able to pick it up using only the task body, with no additional context.

This file lives at the root of the **working repository** and is intentionally **not registered with kb_mcp** — access it via the filesystem `Read` / `Edit` tools, never via `knowledge_base_*` calls.

**Agent rules (picking up tasks):**
1. Read each task in full before starting. If its preconditions are unmet, skip it and note the blocker.
2. **Triage before committing.** If multiple tasks are open, scan them all and rank by value/difficulty. Re-validate the author-set `difficulty` and `value` against the current state of the repo — conditions may have shifted.
3. After completing a task, delete its entire block (from the `---` above the `##` header to the `---` below the last line).
4. After completing one or more tasks, assess whether a `WORKLOG.md` entry is warranted.
5. Confirm a task is still valid before executing.

**Adding tasks (session authors):**
- Copy the template at the bottom (without fences), fill in all fields, and insert it as a new `##` block above the Template section, preceded and followed by `---`.
- Rate `difficulty` and `value` (low / medium / high).
- Be precise: include file paths, expected outcomes, and a verification step.

---

## Run a full notebook execution sweep and populate the housekeeping baseline
- status: todo
- type: task
- id: todo.notebook_exec_baseline
- description: Execute every notebook end-to-end, record pass/fail and wall-clock, and fill in the Phase 3 section of HOUSEKEEPING.md's Latest Report.
- owner: agent
- blocked_by: []
- difficulty: medium
- value: high
- last_checked: 2026-05-14
<!-- content -->
**Context:** The initial organisation pass (see `WORKLOG.md`, 2026-05-14) renamed the notebooks but did not execute any of them on the new structure. The first `HOUSEKEEPING.md` Latest Report shows the Notebook Execution section as "not yet measured." Until this is run, we have no confidence that the reorganised notebooks still execute on a clean kernel.

**Preconditions:**
- `requirements.txt` resolves cleanly in a fresh venv. Confirm with `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`.

**Steps:**
1. For each notebook below, run:
   ```bash
   jupyter nbconvert --to notebook --execute --inplace \
       --ExecutePreprocessor.timeout=600 path/to/notebook.ipynb
   ```
   Notebooks:
   - `01_imprecise_probabilities/ucb_initialization_study.ipynb`
   - `02_repeated_games_ucb/stag_hunt_egreedy_vs_ucb.ipynb`
   - `02_repeated_games_ucb/ucb_testing_cooperation.ipynb`
   - `03_sequential_games_ucb/polluted_river_public_goods.ipynb`
   - `04_deep_ensembles/uncertainty_estimation_sandbox.ipynb`
   - `04_deep_ensembles/deep_ensemble_polluted_river.ipynb`
2. For the two heavy notebooks under `04_deep_ensembles/`, if 10 minutes is not enough, run a smoke-test variant (reduce `MAX_EPISODES` to ~20) and record the smoke-test status. The full-run version stays unmodified.
3. Update `HOUSEKEEPING.md` → demote current Latest Report to Previous Report, append a new Latest Report with the Phase 3 results filled in.

**Verification:** `HOUSEKEEPING.md` Latest Report has every notebook listed with a non-`not yet measured` status, and a new entry exists in `WORKLOG.md` linking to the report.

**On completion:** Delete this entire task block from `TODO_WORKFLOW.md`.

---

## Verify pinned requirements run every notebook end-to-end
- status: todo
- type: task
- id: todo.verify_pinned_requirements
- description: Confirm the pre-pinned requirements.txt / requirements-deep.txt files resolve and execute every notebook on a fresh venv, then tighten or relax pins as needed.
- owner: agent
- blocked_by: [todo.notebook_exec_baseline]
- difficulty: low
- value: medium
- last_checked: 2026-05-14
<!-- content -->
**Context:** `requirements.txt` and `requirements-deep.txt` were pinned on 2026-05-14 from the user's current macOS Intel / Anaconda base environment (Python 3.10.9). They have not yet been validated against a fresh venv that actually runs every notebook end-to-end. Once `todo.notebook_exec_baseline` has executed the notebooks, confirm the pinned versions still work and tighten or relax pins where appropriate.

**Preconditions:**
- The notebook execution sweep has succeeded (`todo.notebook_exec_baseline` complete).

**Steps:**
1. Wipe any prior venv: `rm -rf .venv` (only after confirming no uncommitted work depends on it).
2. Run `./setup.sh --with-torch` and confirm the install completes without `ResolutionImpossible`.
3. Activate the venv and re-execute the notebook sweep from `todo.notebook_exec_baseline`. If any notebook fails on a version-related error, adjust the pin and re-test.
4. If the env on the test machine is wildly different from macOS Intel / Python 3.10 (e.g. Linux + Python 3.12), record the new platform in the comment block at the top of `requirements.txt` and consider whether to relax `==` to `~=`.

**Verification:** `pip install -r requirements-deep.txt` in a fresh venv resolves cleanly and every notebook executes end-to-end on the resulting environment.

**On completion:** Delete this entire task block.

---

## Add a paper-figure manifest under results/
- status: todo
- type: task
- id: todo.figure_manifest
- description: Each plotted figure in the notebooks should be saved to results/ with a deterministic filename, and results/MANIFEST.md should list which figure goes with which paper claim.
- owner: agent
- blocked_by: []
- difficulty: low
- value: medium
- last_checked: 2026-05-14
<!-- content -->
**Context:** The paper outline in `notes/paper_outline.docx` references empirical claims (e.g. "UCB cooperates while ε-greedy defects in the iterated PD") that are currently illustrated by inline `plt.show()` calls in the notebooks. Without a manifest, the link between a figure on a paper page and the notebook cell that produced it is implicit and easily lost.

**Preconditions:** none.

**Steps:**
1. In each notebook, just before each `plt.show()`, add `plt.savefig(f"../results/{notebook_slug}__{fig_slug}.png", dpi=150, bbox_inches="tight")`.
2. Create `results/MANIFEST.md` with one row per figure: `| figure file | source notebook | paper section |`.
3. Add `results/*.png` to git tracking; leave intermediate `.npy` / `.pkl` outputs gitignored.

**Verification:** Re-running all notebooks repopulates `results/`; every row in `MANIFEST.md` references a file that exists.

**On completion:** Delete this entire task block.

---

## Realign strand folders and notebooks with original research intent
- status: todo
- type: task
- id: todo.realign_strands_with_intent
- description: Current folder names and notebook content do not reflect the user's intended research structure; rename strands and rewrite or replace notebooks so each strand matches the question it was meant to answer.
- owner: agent
- blocked_by: []
- difficulty: high
- value: high
- last_checked: 2026-05-14
<!-- content -->
**Context:** The initial repository reorganisation (see `WORKLOG.md`, 2026-05-14 "Initial repository organisation") accepted the inherited file content at face value and mapped each notebook into one of four strand folders. The user has since flagged that the inferred mapping does not match the intended research structure:

- `01_imprecise_probabilities/` is too narrow — imprecise probabilities are *one kind* of set-point estimate among others, and the strand is really about **set-point estimates in static social dilemmas** as a class. The folder name should not single out imprecise probabilities.
- The notebook in that folder (`ucb_initialization_study.ipynb`) is not doing the study the strand is supposed to do. The initialisation sweep is adjacent but not the central question.
- Similar misalignments exist in other folders — the user did not enumerate them. A fresh agent picking this up must walk each strand with the user before acting.

This is a structural rework, not a cosmetic rename. Picking it up halfway leaves the repo in a worse state than today (inconsistent folder names + partial rewrites). Block downstream tasks that pin specific notebook paths until this is done — `todo.notebook_exec_baseline` and `todo.figure_manifest` in particular.

**Preconditions:**
- A conversation with the user covering, per strand: (a) the intended research question, (b) the correct folder name, (c) whether the existing notebook stays, is rewritten, or is replaced.
- `notes/paper_outline.docx` and `notes/rl_cooperation.docx` re-read with the user's intent in mind — the paper structure should drive the strand structure, not the inherited filenames.
- Confirm via `git log --oneline` that the repo has at least one commit so `git mv` can preserve rename history; if not, prompt the user to commit the current state first.

**Steps:**
1. With the user, for each strand folder, document in a scratch table:
   - Current folder name and current notebook(s).
   - Intended research question (one sentence).
   - Correct folder name (numeric-prefix + topic, lowercase snake_case).
   - Action for each existing notebook: *keep*, *rewrite in place*, *replace with new study*, or *move to another strand / `notes/`*.
2. For each folder rename:
   - `git mv` the folder.
   - Rename the per-folder `UPPER_SNAKE.md` to match the new topic.
   - Rename the corresponding `src/<strand_pkg>/` package and grep for `from src.<old>` across all notebooks to fix imports.
3. For each notebook rewrite / replace:
   - Follow `content/how-to/NOTEBOOK_WRITING_SKILL.md` §2 (cell structure) and `content/how-to/ACADEMIC_REPO_SKILL.md` §4 (code-vs-paper boundary) in the KB.
   - Use the `/tmp/build_notebooks.py`-style programmatic-authoring pattern from `NOTEBOOK_WRITING_SKILL.md` §9 with cell-`id` generation.
4. Update `README.md` (strand table + repo map), per-folder `UPPER_SNAKE.md` files, and `HOUSEKEEPING.md` Latest Report to reflect the new structure.
5. Re-point any TODO tasks that reference moved or renamed notebooks (`todo.notebook_exec_baseline`, `todo.figure_manifest`, `todo.verify_pinned_requirements`).
6. Add a `WORKLOG.md` entry summarising the renames and the per-strand notebook decision.

**Verification:**
- `find . -name "*.ipynb" -not -path "./.venv/*"` matches the strand table in `README.md` exactly.
- Every strand's `UPPER_SNAKE.md` accurately describes the notebook(s) it contains.
- The notebook execution sweep (`todo.notebook_exec_baseline`) can be unblocked and re-run.

**On completion:** Delete this entire task block from `TODO_WORKFLOW.md`.

---

## Task Template

Copy the block below (without the outer fences), fill in all fields, and insert it as a new `## [Task Title]` task block above this Template section, surrounded by `---` dividers.

````markdown
## [Task Title]
- status: todo
- type: task
- id: todo.[short_id]
- description: One-sentence description of what this task accomplishes.
- owner: agent
- blocked_by: []
- difficulty: low | medium | high
- value: low | medium | high
- last_checked: YYYY-MM-DD
<!-- content -->
**Context:** Why this task exists and what triggered it. Include the relevant file paths.

**Preconditions:** Any state that must be true before starting. Write `none` if there are none.

**Steps:**
1. (Include specific commands or file paths where possible.)
2. ...

**Verification:** How to confirm the task is complete.

**On completion:** Delete this entire task block from `TODO_WORKFLOW.md`.
````
