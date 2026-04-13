# DevTools Guide — Pursuit of Peace  v1.0.0-stable

DevTools is a standalone developer utility bundled with the game. It runs independently of the game window.

```
python DevTools.pyw
```

It has seven tabs, each described below.

---

## Tab 1 — Pycache Cleaner

**What it does:** Recursively deletes all `__pycache__` folders inside a chosen directory.

**When to use:** Before packaging a release, after a major refactor, or when resolving import issues caused by stale cached bytecode.

**How to use:**
1. Click **Browse…** to select a directory (typically the project root).
2. Click **Start Deletion**.
3. The log shows each deleted folder.
4. Click **Clear Log** to reset the display.

---

## Tab 2 — Audit Tool

**What it does:** Runs the game engine headlessly for a configurable number of random steps, logging every action and reporting any crash.

**When to use:** After any engine change, resolver addition, or data file modification. Set a high step count (5000+) and leave it running overnight to find edge cases.

**How to use:**
1. Set **Steps** (number of random actions to simulate).
2. Optionally set a **Seed** for a reproducible run.
3. Click **Run Audit**.
4. Watch the progress bar. The log streams live.
5. If a crash occurs, a dialog shows the step number and exception.
6. Click **Export Log** to save the full session log to a `.txt` file.
7. Click **Stop** at any time to halt the run early.

**What it tests:** City actions (rest, buy, sell, hear rumors, pay taxes, navigate). Dungeon actions (enter, next room, flee). Combat is not currently simulated headlessly.

---

## Tab 3 — Build Tool

See `docs/BUILD_PROCESS.md` for the full build guide.

**Summary:**
- The **Build Game** sub-tab builds the game executable.
- The **Build DevTools** sub-tab builds the DevTools executable.
- The **⚡ BUILD BOTH** button builds both in sequence, placing them in a versioned output folder.

**Options per target:**
- Main script path, executable name, icon file, output folder.
- Architecture (default / x86_64 / x86).
- Windowed mode, copy data/ folder, clean first, UPX compression, debug symbols.

---

## Tab 4 — Validate Actions

**What it does:** Reads every JSON file in `data/actions/` and checks that each has the required `id` and `resolver` fields, that the `id` matches the filename stem, and that the `resolver` path is formatted correctly.

**When to use:** After adding or editing action JSON files. Catches typos and missing fields before launching the game.

**How to use:**
1. Click **Run Validation**.
2. Green lines = valid. Red `[ERROR]` lines = problems to fix.
3. Click **Clear** to reset the log.

---

## Tab 5 — Generate Resolver

**What it does:** Scaffolds a new action JSON file and a stub resolver Python file from two text inputs.

**When to use:** When adding a new action to avoid typing boilerplate by hand.

**How to use:**
1. Enter the **Action ID** (e.g. `pray_at_shrine`). Must not contain spaces.
2. Enter the **Resolver** path (e.g. `location.pray`). Must not contain spaces.
3. Click **Generate**.
4. The tool creates:
   - `data/actions/pray_at_shrine.json` with boilerplate fields.
   - `app/logic/resolvers/location/pray.py` with a stub `resolve` function and `__init__.py` if needed.
5. Edit both files to implement the actual logic.

---

## Tab 6 — JSON Workshop

**What it does:** A visual form-based editor for the game's data files. Browse, edit, create, duplicate, and delete entries for items, enemies, services, and actions — without writing raw JSON.

**Categories:**
- **Items** — `data/dungeon/items/items.json`
- **Enemies** — `data/dungeon/enemies/enemies.json`
- **Services** — `data/city/services.json`
- **Actions** — all files in `data/actions/`

### Common Tasks

**Editing an enemy's HP:**
1. Click **Enemies** in the left panel.
2. Select the enemy from the list.
3. Change the **HP** spinbox.
4. Click **💾 Save**. The change is written to `enemies.json` immediately.

**Creating a new action:**
1. Click **Actions**.
2. Click **New**.
3. Fill in ID, Resolver (choose from the dropdown of all registered resolvers), Description, and optional cost.
4. Click **Save**. A new `data/actions/<id>.json` file is created.
5. Also create the resolver module manually (or use the Generate Resolver tab).

**Duplicating an enemy:**
1. Select the enemy to copy.
2. Click **Duplicate**. A copy with `_copy` appended to the ID appears.
3. Edit the ID and other fields.
4. Click **Save**.

**Previewing JSON:**
Click **{ } Preview JSON** at any time to see a formatted read-only view of the current form state before saving.

**Reverting changes:**
Click **↺ Revert** to reload the entry from disk, discarding all unsaved edits.

**Filtering the list:**
Type in the **Filter** box to search entries by name or ID.

### Services (Raw JSON Editor)

Services entries are complex and free-form, so they are shown as a raw JSON text area rather than a form. Edit the JSON directly and click **Save** to write the change to `services.json`.

---

## Tab 7 — File Auditor

**What it does:** Scans the project for redundant files and flags them for optional deletion. Categories:

- **Cache** — `__pycache__/` directories and `.pyc` files.
- **Backup** — `*.bak`, `*.orig`, `*.old` files.
- **Empty** — Python files that are 0 bytes or whitespace-only.
- **Unused** — Python files that are never referenced by any `import` statement in the project (identified via full AST analysis of all `.py` files).

**How to use:**
1. Click **🔍 Scan Project**. The scan runs synchronously — for large projects this takes a few seconds.
2. Review the findings list. Each item has a checkbox.
3. Check the items you want to delete, or click **☑ Select All**.
4. Click **🗑 Delete Selected**.
5. A red inline confirmation bar appears. Click **Yes, delete** to confirm or **Cancel** to abort.
6. After deletion the scan runs again automatically to show the updated state.

**What is excluded from the scan:** `.git/`, `__pycache__/`, `logs/`, `dist/`, `build/`, `Build Output (*/`

**Safety note:** The Unused detection uses conservative static analysis (AST imports only). Files that are loaded dynamically (e.g. via `importlib`) may be flagged as unused even if they are needed. Review before deleting.
