# Build Process — Pursuit of Peace  v1.0.0-stable

This document explains how to build standalone executables for the game and for DevTools, both manually and using the DevTools Build Tool.

---

## Prerequisites

- Python 3.10+
- PyInstaller: `pip install pyinstaller`
- The `data/` folder must remain next to any compiled executable.

---

## Using the DevTools Build Tool (Recommended)

Open DevTools:

```
python DevTools.pyw
```

Navigate to the **Build Tool** tab.

### Building a Single Target

1. Select the **Build Game** or **Build DevTools** tab inside the Build Tool.
2. Verify the script path is correct (auto-detected from the current directory).
3. Set your executable name (default: `PursuitOfPeace` / `DevTools`).
4. Configure options:
   - **Windowed** — suppress the terminal window (recommended for game release).
   - **Copy data/ folder** — copies `data/` next to the `.exe` automatically after build.
   - **Clean first** — deletes `build/` and `dist/` before building (recommended).
   - **UPX compression** — requires UPX on PATH; reduces executable size.
   - **Architecture** — `default` uses the host machine; `x86_64` or `x86` for cross-targeting.
   - **Debug symbols** — passes `--debug=all` to PyInstaller; for diagnosing startup failures.
5. Click **BUILD GAME** or **BUILD DEVTOOLS**.
6. Watch the log. On success: `✓ GAME build succeeded.`

### One-Click Both Builds

Click **⚡ BUILD BOTH (Game + DevTools → versioned folder)**.

This runs the Game build followed by the DevTools build. Both executables and the `data/` folder are placed in:

```
Build Output (v1.0.0-stable)/
├── Game/
│   ├── PursuitOfPeace.exe
│   └── data/
└── DevTools/
    └── DevTools.exe
```

The version string is read from `app/version.py`.

---

## Manual Build (Command Line)

### Game Executable

```bash
pyinstaller --onefile --windowed --noconfirm --name=PursuitOfPeace main.pyw
```

After building, copy the `data/` folder next to the executable:

```bash
cp -r data/ dist/data/
```

The final distributable structure:

```
dist/
├── PursuitOfPeace.exe   (or PursuitOfPeace on Linux/macOS)
└── data/
    ├── actions/
    ├── city/
    ├── dungeon/
    ├── economy/
    ├── events/
    ├── fish_pool.json
    ├── lore/
    ├── player/
    │   └── profiles/    (created on first run)
    ├── schemas/
    └── ui/
```

### DevTools Executable

DevTools does not need the `data/` folder — it reads it from the project root when run as a script, or from next to the `.exe` when frozen.

```bash
pyinstaller --onefile --noconfirm --name=DevTools DevTools.pyw
```

---

## How Path Resolution Works in the Executable

`app/paths.py` provides `get_base_dir()`:

```python
def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent   # folder containing the .exe
    return Path(__file__).resolve().parent.parent  # project root in script mode
```

`data_path(*parts)` returns `get_base_dir() / "data" / Path(*parts)`.

This means the game always looks for `data/` in the same folder as the executable, whether running as `python main.pyw` or as `PursuitOfPeace.exe`.

---

## Troubleshooting

### "Unknown or unavailable action" in the built game

The `data/` folder is missing or not in the same directory as the `.exe`. Copy the entire `data/` tree next to the executable.

### Module not found at startup

A Python file was added to `app/` but not discovered by PyInstaller. Add a `--hidden-import=app.my_module` flag to the PyInstaller command, or use `--collect-all=app`.

### The game window opens then immediately closes

Run with a console window (remove `--windowed`) to see the traceback. Alternatively, check the log file in `logs/`.

### UPX not found

Install UPX from [upx.github.io](https://upx.github.io) and add its folder to your `PATH`. Alternatively, uncheck the UPX option in the Build Tool.

### The built executable is very large

This is normal for PyInstaller `--onefile` — it includes the entire Python runtime. Typical sizes: ~15–25 MB on Windows. UPX compression can reduce this by 30–50%.

---

## Profiles and Saves in the Built Game

Profile files are stored at `<exe_dir>/data/player/profiles/`. These persist between runs. When distributing an update, do not delete the `profiles/` folder — players will lose their saves.

To include a fresh set of profile files in a distribution (or none at all), simply omit the `profiles/` directory from the `data/` copy.
