#!/usr/bin/env python3
"""
DevTools – Merged Utility for "Pursuit of Peace"

This application provides five development tools in one window:

1. Pycache Cleaner – delete all __pycache__ folders.
2. Audit Tool – runs the game engine with random actions, logs progress.
3. Build Tool – builds standalone executables for the Game and for DevTools itself.
4. Validate Actions – checks all data/actions/*.json against schema.
5. Generate Resolver – scaffolds a new action JSON and resolver stub.

All tools share a consistent dark theme via the game's UI system.
"""

import os
import sys
import shutil
import subprocess
import threading
import queue
import traceback
import random
import json
import pathlib
import textwrap
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from typing import Optional, Tuple, Dict, Any, List

# Ensure the project root (folder containing this file) is on sys.path so that
# app.paths and other app modules are importable when DevTools is run directly.
_DEVTOOLS_DIR = pathlib.Path(__file__).resolve().parent
if str(_DEVTOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_DEVTOOLS_DIR))

from app.paths import data_path, get_base_dir

# ----------------------------------------------------------------------
# Import game UI components (replaces raw Tkinter)
# ----------------------------------------------------------------------
try:
    from app.ui.simple.basic.text_display import TextDisplay
    from app.ui.simple.basic.menu_list import MenuList
    from app.ui.simple.basic.stat_bar import StatBar
    from app.ui.simple.basic.input_field import InputField
    from app.ui.simple.style_manager import StyleManager
    from app.ui.simple.theme import load_theme
    UI_AVAILABLE = True
except ImportError:
    UI_AVAILABLE = False
    # Fallback: we will still run but with raw widgets (should not happen in correct environment)

# ----------------------------------------------------------------------
# Helper: Tooltip (unchanged, uses raw Tk because it's simple)
# ----------------------------------------------------------------------
class ToolTip:
    def __init__(self, widget: tk.Widget, text: str) -> None:
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind('<Enter>', self.enter)
        widget.bind('<Leave>', self.leave)

    def enter(self, event=None) -> None:
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack()

    def leave(self, event=None) -> None:
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


# ----------------------------------------------------------------------
# Section 1: Pycache Cleaner (unchanged logic, but uses themed parent)
# ----------------------------------------------------------------------
class PycacheCleaner(tk.Frame):
    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, bg="#1e1e2e")
        self.path_var = tk.StringVar()
        self._build_ui()
        self.log("Ready. Select a directory and click 'Start Deletion'.")

    def _build_ui(self) -> None:
        frame_path = ttk.Frame(self)
        frame_path.pack(pady=10, padx=10, fill=tk.X)

        ttk.Label(frame_path, text="Target Directory:") \
            .pack(side=tk.LEFT, padx=(0, 5))
        self.entry_path = ttk.Entry(frame_path, textvariable=self.path_var, width=50)
        self.entry_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        btn_browse = ttk.Button(frame_path, text="Browse...", command=self.browse_folder)
        btn_browse.pack(side=tk.RIGHT)
        ToolTip(btn_browse, "Select the root folder to scan for __pycache__ directories")

        frame_buttons = ttk.Frame(self)
        frame_buttons.pack(pady=5)

        btn_start = ttk.Button(frame_buttons, text="Start Deletion",
                               command=self.start_deletion, style="Action.TButton")
        btn_start.pack(side=tk.LEFT, padx=5)
        ToolTip(btn_start, "Delete all __pycache__ folders inside the selected directory")

        btn_clear = ttk.Button(frame_buttons, text="Clear Log", command=self.clear_log)
        btn_clear.pack(side=tk.LEFT, padx=5)
        ToolTip(btn_clear, "Clear the log display")

        # Use game's TextDisplay instead of ScrolledText
        if UI_AVAILABLE:
            self.log_area = TextDisplay(self, content="")
        else:
            self.log_area = tk.Text(self, wrap=tk.WORD, bg="#1e1e2e", fg="#cdd6f4")
        self.log_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def browse_folder(self) -> None:
        folder = filedialog.askdirectory(title="Select Directory to Scan")
        if folder:
            self.path_var.set(folder)

    def log(self, message: str) -> None:
        if UI_AVAILABLE and hasattr(self.log_area, 'append'):
            self.log_area.append(message + "\n")
        else:
            self.log_area.insert(tk.END, message + "\n")
            self.log_area.see(tk.END)
        self.update_idletasks()

    def clear_log(self) -> None:
        if UI_AVAILABLE and hasattr(self.log_area, 'set_content'):
            self.log_area.set_content("")
        else:
            self.log_area.delete(1.0, tk.END)

    def _delete_pycache_folders(self, root_path: str) -> Tuple[int, int]:
        deleted = 0
        errors = 0
        for dirpath, dirnames, _ in os.walk(root_path):
            if '__pycache__' in dirnames:
                pycache_path = os.path.join(dirpath, '__pycache__')
                try:
                    shutil.rmtree(pycache_path)
                    self.log(f"Deleted: {pycache_path}")
                    deleted += 1
                except Exception as e:
                    self.log(f"ERROR deleting {pycache_path}: {e}")
                    errors += 1
        return deleted, errors

    def start_deletion(self) -> None:
        target = self.path_var.get().strip()
        if not target:
            messagebox.showwarning("No Directory", "Please select a directory first.")
            return
        if not os.path.isdir(target):
            messagebox.showerror("Invalid Path", f"'{target}' is not a valid directory.")
            return
        if not messagebox.askyesno("Confirm Deletion",
                                   f"Delete ALL '__pycache__' folders inside:\n\n{target}\n\nThis cannot be undone."):
            self.log("Operation cancelled.")
            return

        self.log(f"\n--- Scanning: {target} ---")
        deleted, errors = self._delete_pycache_folders(target)
        self.log("--- Finished ---")
        self.log(f"Deleted {deleted} '__pycache__' folder(s).")
        if errors:
            self.log(f"Encountered {errors} error(s).")
        if deleted == 0 and errors == 0:
            self.log("No '__pycache__' folders found.")
        elif deleted > 0:
            messagebox.showinfo("Completed", f"Deleted {deleted} '__pycache__' folder(s).")


# ----------------------------------------------------------------------
# Section 2: Audit Tool (refactored to use TextDisplay and StatBar)
# ----------------------------------------------------------------------
try:
    from app.data_loader import DataLoader
    from app.dungeon_manager import DungeonManager
    from app.location_manager import LocationManager
    from app.game_engine import GameEngine
    GAME_MODULES_AVAILABLE = True
except ImportError as e:
    GAME_MODULES_AVAILABLE = False
    GAME_IMPORT_ERROR = str(e)

class QueueLogger:
    def __init__(self, log_queue: queue.Queue) -> None:
        self.log_queue = log_queue

    def _put(self, level: str, msg: str, context: Any = None) -> None:
        self.log_queue.put({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "level": level,
            "message": msg,
            "context": context,
        })

    def info(self, msg: str, context: Any = None) -> None:
        self._put("INFO", msg, context)
    def warn(self, msg: str, context: Any = None) -> None:
        self._put("WARN", msg, context)
    def error(self, msg: str, context: Any = None) -> None:
        self._put("ERROR", msg, context)
    def system(self, msg: str) -> None:
        self._put("SYSTEM", msg)
    def data(self, event: str, detail: Any = None) -> None:
        pass

class AuditRunner:
    def __init__(self, max_steps: int, seed: Optional[int], log_queue: queue.Queue) -> None:
        self.max_steps = max_steps
        self.seed = seed
        self.log_queue = log_queue
        self.logger = QueueLogger(log_queue)
        self.stop_flag = threading.Event()
        self.running = False
        self.crash_info: Optional[Dict[str, Any]] = None

    def run(self) -> None:
        self.running = True
        self.stop_flag.clear()
        if self.seed is not None:
            random.seed(self.seed)
            self.logger.system(f"Random seed set to {self.seed}")

        if not GAME_MODULES_AVAILABLE:
            self.crash_info = {"exception": f"Missing game modules: {GAME_IMPORT_ERROR}"}
            self.logger.error(f"CRASH: {GAME_IMPORT_ERROR}")
            self.running = False
            return

        self._init_game()
        self.history: List[str] = []
        self.combat_active = False
        self.current_enemy: Optional[Dict[str, Any]] = None

        for step in range(1, self.max_steps + 1):
            if self.stop_flag.is_set():
                self.logger.system("Audit stopped by user.")
                break
            try:
                self._do_one_step()
            except Exception as e:
                self.crash_info = {
                    "step": step,
                    "exception": str(e),
                    "traceback": traceback.format_exc(),
                    "history": self.history[-20:],
                }
                self.logger.error(f"CRASH at step {step}: {e}")
                self.logger.error(traceback.format_exc())
                break
            if step % 100 == 0:
                self.logger.info(f"Step {step} completed.")
            self.log_queue.put({"progress": step, "step": step, "total": self.max_steps})

        self.running = False
        if not self.crash_info and not self.stop_flag.is_set():
            self.logger.system(f"Audit finished: {self.max_steps} steps without crash.")
        elif self.crash_info:
            self.logger.system("Audit terminated due to crash.")

    def _init_game(self) -> None:
        loader = DataLoader(logger=self.logger)
        dungeon_mgr = DungeonManager(loader, logger=self.logger)
        location_mgr = LocationManager(loader, dungeon_mgr, logger=self.logger)
        self.engine = GameEngine(loader, location_mgr, dungeon_mgr, logger=self.logger)

    def _do_one_step(self) -> None:
        if self.combat_active and self.current_enemy:
            self._do_combat_action()
        elif self.engine.dungeon_state is not None:
            self._do_dungeon_action()
        else:
            self._do_city_action()

    def _do_city_action(self) -> None:
        state = self.engine.get_view_state("city")
        actions = state.get("location", {}).get("actions", [])
        if not actions:
            actions = [{"id": "go_tavern"}]
        action = random.choice(actions)
        action_id = action["id"]
        self.history.append(f"city: {action_id}")
        _, msg = self.engine.do_location_action(action_id)
        if msg:
            self.logger.info(msg)

    def _do_dungeon_action(self) -> None:
        state = self.engine.get_view_state("dungeon")
        actions = state.get("location", {}).get("actions", [])
        if not actions:
            actions = [{"id": "flee_dungeon"}]
        action = random.choice(actions)
        action_id = action["id"]
        self.history.append(f"dungeon: {action_id}")
        _, msg, combat_state = self.engine.do_dungeon_action(action_id)
        if msg:
            self.logger.info(msg)
        if combat_state is not None:
            self.combat_active = True
            room = self.engine._dungeon_mgr.get_current_room(self.engine.dungeon_state)
            if room and room.get("enemy"):
                self.current_enemy = room["enemy"]
            else:
                self.current_enemy = {"id": "unknown", "name": "Enemy", "hp": 10}

    def _do_combat_action(self) -> None:
        actions = [{"id": "attack"}, {"id": "flee"}]
        action = random.choice(actions)
        action_id = action["id"]
        self.history.append(f"combat: {action_id}")
        ended, msg, _fled, _dead = self.engine.do_combat_action(action_id, self.current_enemy)
        if msg:
            self.logger.info(f"Combat: {msg}")
        if ended:
            self.combat_active = False
            self.current_enemy = None


class AuditToolFrame(tk.Frame):
    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, bg="#1e1e2e")
        self.parent = parent
        self.audit_thread: Optional[threading.Thread] = None
        self.runner: Optional[AuditRunner] = None
        self.log_queue = queue.Queue()
        self.after_id: Optional[str] = None
        self._build_ui()
        self._poll_queue()

    def _build_ui(self) -> None:
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(control_frame, text="Steps:") \
            .grid(row=0, column=0, sticky=tk.W, padx=5)
        self.steps_var = tk.StringVar(value="1000")
        steps_entry = ttk.Entry(control_frame, textvariable=self.steps_var, width=10)
        steps_entry.grid(row=0, column=1, padx=5)
        ToolTip(steps_entry, "Number of random actions to simulate")

        ttk.Label(control_frame, text="Seed (optional):") \
            .grid(row=0, column=2, sticky=tk.W, padx=5)
        self.seed_var = tk.StringVar(value="")
        seed_entry = ttk.Entry(control_frame, textvariable=self.seed_var, width=15)
        seed_entry.grid(row=0, column=3, padx=5)
        ToolTip(seed_entry, "Fixed random seed for reproducible runs")

        self.run_btn = ttk.Button(control_frame, text="Run Audit", command=self.start_audit)
        self.run_btn.grid(row=0, column=4, padx=10)

        self.stop_btn = ttk.Button(control_frame, text="Stop", command=self.stop_audit,
                                   state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=5, padx=5)

        self.export_btn = ttk.Button(control_frame, text="Export Log", command=self.export_log)
        self.export_btn.grid(row=0, column=6, padx=5)

        # Use StatBar for progress + status
        self.progress_stat = StatBar(self, label="Progress:", value="0%")
        self.progress_stat.pack(fill=tk.X, padx=10, pady=5)

        # Use TextDisplay for log output
        if UI_AVAILABLE:
            self.log_display = TextDisplay(self, content="")
        else:
            self.log_display = tk.Text(self, wrap=tk.WORD, bg="#1e1e2e", fg="#cdd6f4")
        self.log_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        if not GAME_MODULES_AVAILABLE:
            self._log(f"WARNING: Game modules not found. Audit will fail.\n{GAME_IMPORT_ERROR}")

    def _log(self, text: str, level: str = "INFO") -> None:
        if UI_AVAILABLE and hasattr(self.log_display, 'append'):
            self.log_display.append(text + "\n")
        else:
            self.log_display.insert(tk.END, text + "\n")
            self.log_display.see(tk.END)

    def _poll_queue(self) -> None:
        try:
            while True:
                msg = self.log_queue.get_nowait()
                if "progress" in msg:
                    step = msg["step"]
                    total = msg["total"]
                    percent = int((step / total) * 100)
                    self.progress_stat.set_value(f"{percent}% ({step}/{total})")
                else:
                    ts = msg.get("timestamp", "")
                    level = msg.get("level", "INFO")
                    text = msg.get("message", "")
                    line = f"[{ts}] [{level}] {text}"
                    self._log(line)
        except queue.Empty:
            pass
        self.after_id = self.after(100, self._poll_queue)

    def start_audit(self) -> None:
        try:
            steps = int(self.steps_var.get())
            if steps <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid input", "Steps must be a positive integer.")
            return

        seed = None
        seed_str = self.seed_var.get().strip()
        if seed_str:
            try:
                seed = int(seed_str)
            except ValueError:
                messagebox.showerror("Invalid input", "Seed must be an integer.")
                return

        if UI_AVAILABLE and hasattr(self.log_display, 'set_content'):
            self.log_display.set_content("")
        else:
            self.log_display.delete(1.0, tk.END)

        self.progress_stat.set_value("0%")
        self.run_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.export_btn.config(state=tk.DISABLED)

        self.runner = AuditRunner(max_steps=steps, seed=seed, log_queue=self.log_queue)
        self.audit_thread = threading.Thread(target=self.runner.run, daemon=True)
        self.audit_thread.start()
        self._monitor_audit()

    def _monitor_audit(self) -> None:
        if self.audit_thread and self.audit_thread.is_alive():
            self.after(500, self._monitor_audit)
        else:
            self.run_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.export_btn.config(state=tk.NORMAL)
            if self.runner and self.runner.crash_info:
                crash = self.runner.crash_info
                messagebox.showerror("Crash during audit",
                                     f"Crash at step {crash.get('step', '?')}\n{crash.get('exception', '')}")
            else:
                self.progress_stat.set_value("Audit completed")

    def stop_audit(self) -> None:
        if self.runner:
            self.runner.stop_flag.set()
            self.stop_btn.config(state=tk.DISABLED)

    def get_log_content(self) -> str:
        """Return all text currently in the log display, regardless of widget type."""
        if UI_AVAILABLE and hasattr(self.log_display, "get_content"):
            return self.log_display.get_content()
        return self.log_display.get(1.0, tk.END)

    def export_log(self) -> None:
        content = self.get_log_content()
        if not content.strip():
            messagebox.showinfo("No log", "Nothing to export.")
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save audit log",
        )
        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                messagebox.showinfo("Exported", f"Log saved to:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Export failed", str(e))


# ----------------------------------------------------------------------
# Section 3: Build Tool (one-click, versioned output, extra options)
# ----------------------------------------------------------------------
def check_pyinstaller() -> bool:
    try:
        subprocess.run(["pyinstaller", "--version"],
                       capture_output=True, check=True,
                       creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

class BuildTool(tk.Frame):
    """Build Tool — compile Game and/or DevTools via PyInstaller.

    New in v1.1.0:
      • UPX compression toggle
      • Target-architecture selector (x86_64 / x86 / default)
      • Custom dist/output folder per target
      • Debug-symbols toggle
      • One-click BUILD BOTH button → versioned output folder
      • StatBar progress indicator for build steps
    """

    def __init__(self, parent: tk.Widget, main_root: tk.Tk) -> None:
        super().__init__(parent, bg="#1e1e2e")
        self.parent    = parent
        self.main_root = main_root
        self._building = False                 # guard against concurrent builds

        # ── per-target option vars ────────────────────────────────────────
        def _mkstr(v): return tk.StringVar(value=v)
        def _mkbool(v): return tk.BooleanVar(value=v)

        # Game
        self.game_script   = _mkstr(os.path.abspath("main.pyw"))
        self.game_output   = _mkstr("PursuitOfPeace")
        self.game_icon     = _mkstr("")
        self.game_dist     = _mkstr("dist")
        self.game_console  = _mkbool(False)
        self.game_copy_data= _mkbool(True)
        self.game_clean    = _mkbool(True)
        self.game_upx      = _mkbool(False)
        self.game_debug    = _mkbool(False)
        self.game_arch     = _mkstr("default")

        # DevTools
        self.dev_script    = _mkstr(os.path.abspath("DevTools.pyw"))
        self.dev_output    = _mkstr("DevTools")
        self.dev_icon      = _mkstr("")
        self.dev_dist      = _mkstr("dist")
        self.dev_console   = _mkbool(True)
        self.dev_copy_data = _mkbool(False)
        self.dev_clean     = _mkbool(True)
        self.dev_upx       = _mkbool(False)
        self.dev_debug     = _mkbool(False)
        self.dev_arch      = _mkstr("default")

        self.build_btn_game: Optional[ttk.Button] = None
        self.build_btn_dev:  Optional[ttk.Button] = None
        self.build_btn_both: Optional[ttk.Button] = None
        self.status_label:   Optional[tk.Label]   = None
        self.progress_bar:   Optional[StatBar]    = None
        self.log_text:       Optional[Any]        = None
        self.install_btn:    Optional[ttk.Button] = None

        self._create_widgets()
        self._check_pyinstaller_status()
        self._ensure_scripts_exist()

    # ── helpers ──────────────────────────────────────────────────────────

    def _vars(self, target: str):
        """Return the option-var group for *target* ('game' or 'dev')."""
        if target == "game":
            return (self.game_script, self.game_output, self.game_icon,
                    self.game_dist,   self.game_console, self.game_copy_data,
                    self.game_clean,  self.game_upx,     self.game_debug,
                    self.game_arch)
        return (self.dev_script, self.dev_output, self.dev_icon,
                self.dev_dist,   self.dev_console, self.dev_copy_data,
                self.dev_clean,  self.dev_upx,     self.dev_debug,
                self.dev_arch)

    def _ensure_scripts_exist(self) -> None:
        for var, name in [(self.game_script, "main.pyw"),
                          (self.dev_script,  "DevTools.pyw")]:
            if not os.path.isfile(var.get()):
                alt = os.path.join(os.getcwd(), name)
                if os.path.isfile(alt):
                    var.set(alt)

    def _log(self, text: str) -> None:
        if self.log_text is None:
            return
        if UI_AVAILABLE and hasattr(self.log_text, "append"):
            self.log_text.append(text + "\n")
        else:
            self.log_text.insert(tk.END, text + "\n")
            self.log_text.see(tk.END)

    def _set_progress(self, text: str) -> None:
        if self.progress_bar:
            self.progress_bar.set_value(text)

    def _set_status(self, text: str, colour: str = "#a6adc8") -> None:
        if self._status_var:
            self._status_var.set(text)

    def _all_build_buttons(self):
        return [b for b in (self.build_btn_game, self.build_btn_dev,
                            self.build_btn_both) if b is not None]

    def _lock_buttons(self) -> None:
        for b in self._all_build_buttons():
            b.config(state="disabled")
        self._building = True

    def _unlock_buttons(self) -> None:
        self._building = False
        self._check_pyinstaller_status()   # re-enables only if PyInstaller present

    # ── widget construction ───────────────────────────────────────────────

    def _create_widgets(self) -> None:
        outer = ttk.Frame(self)
        outer.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ── notebook (one tab per target) ────────────────────────────────
        notebook = ttk.Notebook(outer)
        notebook.pack(fill=tk.X, pady=5)

        game_frame = ttk.Frame(notebook)
        notebook.add(game_frame, text="Build Game")
        self._build_config_ui(game_frame, "game")

        dev_frame = ttk.Frame(notebook)
        notebook.add(dev_frame, text="Build DevTools")
        self._build_config_ui(dev_frame, "dev")

        # ── one-click BUILD BOTH ─────────────────────────────────────────
        both_frame = ttk.Frame(outer)
        both_frame.pack(fill=tk.X, pady=6)

        self.build_btn_both = ttk.Button(
            both_frame,
            text="⚡  BUILD BOTH  (Game + DevTools → versioned folder)",
            command=self._start_build_both,
        )
        self.build_btn_both.pack(side=tk.LEFT, padx=4)
        ToolTip(self.build_btn_both,
                "Builds Game then DevTools and places both in a\n"
                "versioned 'Build Output (vX.Y.Z)/' folder next to this file.")

        # ── progress + status ────────────────────────────────────────────
        self.progress_bar = StatBar(outer, label="Build:", value="Idle")
        self.progress_bar.pack(fill=tk.X, pady=3)

        self._status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(outer, textvariable=self._status_var)
        self.status_label.pack(anchor=tk.W, pady=2)

        # ── shared log ───────────────────────────────────────────────────
        if UI_AVAILABLE:
            self.log_text = TextDisplay(outer, content="")
        else:
            self.log_text = tk.Text(outer, wrap=tk.WORD, bg="#1e1e2e",
                                    fg="#cdd6f4", height=14)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)

    def _build_config_ui(self, parent, target: str) -> None:
        """Grid-based form for one build target."""
        (script_v, output_v, icon_v, dist_v,
         console_v, copy_v, clean_v, upx_v,
         debug_v, arch_v) = self._vars(target)

        row = 0

        def lbl(text, r, c=0):
            ttk.Label(parent, text=text).grid(
                row=r, column=c, sticky=tk.W, pady=3, padx=4)

        # Script path
        lbl("Main script:", row)
        ttk.Entry(parent, textvariable=script_v, width=54).grid(
            row=row, column=1, padx=4, sticky=tk.W+tk.E)
        ttk.Button(parent, text="Browse…",
                   command=lambda: self._browse_script(target)
                   ).grid(row=row, column=2, padx=4)

        # Executable name
        row += 1
        lbl("Executable name:", row)
        ttk.Entry(parent, textvariable=output_v, width=28).grid(
            row=row, column=1, sticky=tk.W, padx=4)

        # Icon
        row += 1
        lbl("Icon (.ico):", row)
        ttk.Entry(parent, textvariable=icon_v, width=54).grid(
            row=row, column=1, padx=4, sticky=tk.W+tk.E)
        ttk.Button(parent, text="Browse…",
                   command=lambda: self._browse_icon(target)
                   ).grid(row=row, column=2, padx=4)

        # Custom output (dist) folder
        row += 1
        lbl("Output folder:", row)
        ttk.Entry(parent, textvariable=dist_v, width=28).grid(
            row=row, column=1, sticky=tk.W, padx=4)
        ToolTip(ttk.Label(parent, text="(default: dist)"),
                "Where PyInstaller places its output before the versioned copy step")

        # Architecture
        row += 1
        lbl("Architecture:", row)
        arch_menu = ttk.Combobox(parent, textvariable=arch_v, width=14,
                                 state="readonly",
                                 values=["default", "x86_64", "x86"])
        arch_menu.grid(row=row, column=1, sticky=tk.W, padx=4)
        ToolTip(arch_menu, "Target CPU architecture for PyInstaller\n"
                           "('default' uses the host machine's architecture)")

        # Options checkboxes — keep tk.Checkbutton for custom selectcolor support
        row += 1
        opts = ttk.LabelFrame(parent, text="Options", padding=(6, 4))
        opts.grid(row=row, column=0, columnspan=3, sticky=tk.W+tk.E, pady=8, padx=4)

        OBG = "#313244"
        FG  = "#cdd6f4"
        def cb(parent, text, var, tip, r, c):
            w = tk.Checkbutton(parent, text=text, variable=var,
                               bg=OBG, fg=FG, selectcolor=OBG,
                               activebackground=OBG, activeforeground=FG)
            w.grid(row=r, column=c, sticky=tk.W, padx=6)
            ToolTip(w, tip)

        cb(opts, "Windowed (no console)",         console_v,
           "Suppress the terminal window — use for the final game release",   0, 0)
        cb(opts, "Copy data/ folder after build", copy_v,
           "Copies the game's data/ folder next to the generated executable", 1, 0)
        cb(opts, "Clean build/ and dist/ first",  clean_v,
           "Delete previous PyInstaller artefacts before building",           2, 0)
        cb(opts, "UPX compression",               upx_v,
           "Shrink the executable with UPX (must be installed and on PATH)",  0, 1)
        cb(opts, "Include debug symbols",         debug_v,
           "Pass --debug=all to PyInstaller for verbose runtime output",      1, 1)

        # Individual build button
        row += 1
        btn = ttk.Button(parent, text=f"BUILD {target.upper()}",
                         command=lambda: self._start_build(target))
        btn.grid(row=row, column=0, columnspan=3, pady=12)
        if target == "game":
            self.build_btn_game = btn
        else:
            self.build_btn_dev = btn

        parent.columnconfigure(1, weight=1)

    # ── browse helpers ────────────────────────────────────────────────────

    def _browse_script(self, target: str) -> None:
        f = filedialog.askopenfilename(title="Select main script",
                                       filetypes=[("Python files", "*.py *.pyw")])
        if f:
            (self.game_script if target == "game" else self.dev_script).set(f)
            self._log(f"Script → {f}")

    def _browse_icon(self, target: str) -> None:
        f = filedialog.askopenfilename(title="Select icon (.ico)",
                                       filetypes=[("Icon files", "*.ico")])
        if f:
            (self.game_icon if target == "game" else self.dev_icon).set(f)
            self._log(f"Icon → {f}")

    # ── PyInstaller status ────────────────────────────────────────────────

    def _check_pyinstaller_status(self) -> None:
        if self._building:
            return
        if not check_pyinstaller():
            self._set_status("PyInstaller not found. Click 'Install PyInstaller'.",
                             "#f38ba8")
            if not self.install_btn:
                self.install_btn = ttk.Button(self, text="Install PyInstaller",
                                              command=self._install_pyinstaller)
                self.install_btn.place(relx=0.5, rely=0.97, anchor=tk.CENTER)
            for b in self._all_build_buttons():
                b.config(state="disabled")
        else:
            self._set_status("PyInstaller is ready.", "#a6e3a1")
            if self.install_btn:
                self.install_btn.place_forget()
                self.install_btn = None
            for b in self._all_build_buttons():
                b.config(state="normal")

    def _install_pyinstaller(self) -> None:
        win = tk.Toplevel(self.main_root)
        win.title("Installing PyInstaller")
        win.geometry("500x100")
        lbl = tk.Label(win, text="Installing… please wait")
        lbl.pack(pady=20)

        def _thread():
            cf = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            proc = subprocess.Popen(
                [sys.executable, "-m", "pip", "install", "pyinstaller"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, creationflags=cf)
            lines = []
            for line in proc.stdout:
                lines.append(line)
                if win.winfo_exists():
                    lbl.config(text=line.strip()[:80])
                    win.update()
            proc.wait()
            win.destroy()
            if proc.returncode == 0:
                messagebox.showinfo("Success", "PyInstaller installed successfully.")
                self._check_pyinstaller_status()
            else:
                messagebox.showerror("Failed",
                    f"Could not install PyInstaller.\n\n{''.join(lines)[:500]}")

        threading.Thread(target=_thread, daemon=True).start()

    # ── build command builder ─────────────────────────────────────────────

    def _build_cmd(self, target: str, dist_dir: str) -> List[str]:
        """Assemble the pyinstaller command for *target* using *dist_dir*."""
        (script_v, output_v, icon_v, _dist_v,
         console_v, _copy_v, _clean_v, upx_v,
         debug_v, arch_v) = self._vars(target)

        script  = script_v.get().strip()
        output  = output_v.get().strip()
        icon    = icon_v.get().strip()
        windowed= console_v.get()     # BoolVar: False = windowed
        use_upx = upx_v.get()
        use_dbg = debug_v.get()
        arch    = arch_v.get()

        cmd = ["pyinstaller", "--onefile", "--noconfirm",
               f"--distpath={dist_dir}"]
        if not windowed:
            cmd.append("--windowed")
        if icon and os.path.isfile(icon):
            cmd.append(f"--icon={icon}")
        if use_upx:
            cmd.append("--upx-dir=.")      # UPX must be on PATH or in cwd
        else:
            cmd.append("--noupx")
        if use_dbg:
            cmd.append("--debug=all")
        if arch and arch != "default":
            cmd.append(f"--target-architecture={arch}")
        cmd.append(f"--name={output}")
        cmd.append(script)
        return cmd

    # ── run subprocess helper ─────────────────────────────────────────────

    def _run_subprocess(self, cmd: List[str]) -> int:
        """Run *cmd*, stream output to log, return returncode."""
        si, cf = None, 0
        if sys.platform == "win32":
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = 0
            cf = subprocess.CREATE_NO_WINDOW
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, bufsize=1, startupinfo=si, creationflags=cf)
        for line in iter(proc.stdout.readline, ""):
            if line:
                self._log(line.rstrip())
        proc.wait()
        return proc.returncode

    # ── data-folder copy ─────────────────────────────────────────────────

    def _copy_data_to(self, dest_dir: str) -> None:
        """Copy the project's data/ folder into *dest_dir*."""
        src = str(get_base_dir() / "data")
        dst = os.path.join(dest_dir, "data")
        try:
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            self._log(f"  Copied data/ → {dst}")
        except Exception as exc:
            self._log(f"  Warning: could not copy data/: {exc}")

    # ── individual build ──────────────────────────────────────────────────

    def _start_build(self, target: str) -> None:
        if self._building:
            return
        if not check_pyinstaller():
            messagebox.showerror("Missing", "PyInstaller is not installed.")
            return

        (script_v, output_v, _icon_v, dist_v,
         _con_v, copy_v, clean_v, *_rest) = self._vars(target)

        script = script_v.get().strip()
        if not os.path.isfile(script):
            messagebox.showerror("Error", f"Script not found:\n{script}")
            return
        if not output_v.get().strip():
            messagebox.showerror("Error", "Executable name cannot be empty.")
            return

        dist_dir = dist_v.get().strip() or "dist"
        copy_data = copy_v.get()
        clean = clean_v.get()

        self._lock_buttons()
        self._set_status(f"Building {target}…", "#89b4fa")
        self._set_progress(f"Step 1/1 — {target}")

        def _thread():
            try:
                if clean:
                    for folder in ["build", dist_dir]:
                        if os.path.exists(folder):
                            try:
                                shutil.rmtree(folder)
                                self._log(f"Cleaned '{folder}/'")
                            except Exception as e:
                                self._log(f"Warning: could not clean {folder}: {e}")

                cmd = self._build_cmd(target, dist_dir)
                self._log(f"\n=== BUILD {target.upper()} ===")
                self._log("Command: " + " ".join(cmd))
                rc = self._run_subprocess(cmd)

                if rc == 0:
                    self._log(f"\n✓ {target.upper()} build succeeded.")
                    self._set_status(f"{target} build succeeded!", "#a6e3a1")
                    if copy_data and target == "game":
                        self._copy_data_to(dist_dir)
                else:
                    self._log(f"\n✗ Build failed (exit {rc}).")
                    self._set_status(f"{target} build failed.", "#f38ba8")
            except Exception as exc:
                self._log(f"Exception: {exc}")
                self._set_status("Build error.", "#f38ba8")
            finally:
                self._set_progress("Idle")
                self._unlock_buttons()

        threading.Thread(target=_thread, daemon=True).start()

    # ── BUILD BOTH ────────────────────────────────────────────────────────

    def _start_build_both(self) -> None:
        if self._building:
            return
        if not check_pyinstaller():
            messagebox.showerror("Missing", "PyInstaller is not installed.")
            return

        for target, sv in [("game", self.game_script), ("dev", self.dev_script)]:
            if not os.path.isfile(sv.get().strip()):
                messagebox.showerror("Error",
                    f"{target} script not found:\n{sv.get()}")
                return

        self._lock_buttons()

        def _thread():
            try:
                # Read version label
                try:
                    from app.version import VERSION_LABEL
                    ver = VERSION_LABEL            # e.g. "v1.0.0"
                except Exception:
                    ver = "v?.?.?"

                project_root = pathlib.Path(__file__).resolve().parent
                out_root = project_root / f"Build Output ({ver})"
                game_out  = out_root / "Game"
                dev_out   = out_root / "DevTools"
                game_out.mkdir(parents=True, exist_ok=True)
                dev_out.mkdir(parents=True, exist_ok=True)

                self._log(f"\n{'='*60}")
                self._log(f"BUILD BOTH → {out_root}")
                self._log(f"{'='*60}")

                tmp_game = str(project_root / "_build_tmp_game")
                tmp_dev  = str(project_root / "_build_tmp_dev")

                success_game = success_dev = False

                # ── Step 1: Game ───────────────────────────────────────
                self._set_progress("Step 1/2 — Game")
                self._set_status("Building Game…", "#89b4fa")

                if self.game_clean.get():
                    for d in ["build", tmp_game]:
                        if os.path.exists(d):
                            shutil.rmtree(d, ignore_errors=True)

                cmd_game = self._build_cmd("game", tmp_game)
                self._log("\n--- Game build ---")
                self._log("Command: " + " ".join(cmd_game))
                rc = self._run_subprocess(cmd_game)

                if rc == 0:
                    self._log("✓ Game build OK")
                    success_game = True
                    # Find the .exe / binary and copy to versioned folder
                    game_name = self.game_output.get().strip()
                    self._copy_artifact(tmp_game, game_name, str(game_out))
                    # Copy data/ folder once, next to game exe
                    self._copy_data_to(str(game_out))
                else:
                    self._log(f"✗ Game build failed (exit {rc})")
                    self._set_status("Game build failed.", "#f38ba8")

                # ── Step 2: DevTools ───────────────────────────────────
                self._set_progress("Step 2/2 — DevTools")
                self._set_status("Building DevTools…", "#89b4fa")

                if self.dev_clean.get():
                    for d in ["build", tmp_dev]:
                        if os.path.exists(d):
                            shutil.rmtree(d, ignore_errors=True)

                cmd_dev = self._build_cmd("dev", tmp_dev)
                self._log("\n--- DevTools build ---")
                self._log("Command: " + " ".join(cmd_dev))
                rc = self._run_subprocess(cmd_dev)

                if rc == 0:
                    self._log("✓ DevTools build OK")
                    success_dev = True
                    dev_name = self.dev_output.get().strip()
                    self._copy_artifact(tmp_dev, dev_name, str(dev_out))
                else:
                    self._log(f"✗ DevTools build failed (exit {rc})")

                # ── Cleanup temp dirs ──────────────────────────────────
                for d in [tmp_game, tmp_dev, "build"]:
                    if os.path.exists(d):
                        shutil.rmtree(d, ignore_errors=True)

                # ── Summary ────────────────────────────────────────────
                self._log(f"\n{'='*60}")
                if success_game and success_dev:
                    summary = f"Both builds succeeded → {out_root}"
                    self._log(f"✓ {summary}")
                    self._set_status(summary, "#a6e3a1")
                else:
                    parts = []
                    if not success_game: parts.append("Game")
                    if not success_dev:  parts.append("DevTools")
                    self._set_status(f"Partial failure: {', '.join(parts)}", "#f38ba8")
                self._log(f"Output: {out_root}")

            except Exception as exc:
                self._log(f"\nException during BUILD BOTH: {exc}")
                self._set_status("Build error.", "#f38ba8")
            finally:
                self._set_progress("Idle")
                self._unlock_buttons()

        threading.Thread(target=_thread, daemon=True).start()

    def _copy_artifact(self, src_dist: str, name: str, dest_dir: str) -> None:
        """Copy the built executable from *src_dist* into *dest_dir*."""
        # PyInstaller places the binary directly in dist_dir
        for ext in ("", ".exe"):
            candidate = os.path.join(src_dist, name + ext)
            if os.path.isfile(candidate):
                dst = os.path.join(dest_dir, os.path.basename(candidate))
                shutil.copy2(candidate, dst)
                self._log(f"  Copied {os.path.basename(candidate)} → {dest_dir}")
                return
        self._log(f"  Warning: could not find built binary '{name}' in {src_dist}")





# ----------------------------------------------------------------------
# Section 4: Validate Actions (refactored to use TextDisplay)
# ----------------------------------------------------------------------
class ValidateActionsFrame(ttk.Frame):
    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        ttk.Label(self, text="Validate Action JSON Files",
                  font=("Segoe UI", 12, "bold")).pack(pady=(10, 4))
        ttk.Label(self, text=("Reads every file in data/actions/ and checks required fields."),
                  wraplength=700, justify=tk.LEFT).pack(padx=10, anchor=tk.W)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=6)
        ttk.Button(btn_frame, text="Run Validation", command=self._run).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Clear", command=self._clear).pack(side=tk.LEFT, padx=4)

        if UI_AVAILABLE:
            self._log = TextDisplay(self, content="")
        else:
            self._log = tk.Text(self, wrap=tk.WORD, bg="#1e1e2e", fg="#cdd6f4", height=28)
        self._log.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

    def _write(self, text: str, tag: str = "") -> None:
        if UI_AVAILABLE and hasattr(self._log, 'append'):
            self._log.append(text + "\n")
        else:
            self._log.insert(tk.END, text + "\n")
            self._log.see(tk.END)

    def _clear(self) -> None:
        if UI_AVAILABLE and hasattr(self._log, 'set_content'):
            self._log.set_content("")
        else:
            self._log.delete("1.0", tk.END)

    def _run(self) -> None:
        self._clear()
        actions_dir = data_path("actions")
        if not actions_dir.exists():
            self._write("ERROR: data/actions/ directory not found.", "err")
            return

        files = sorted(actions_dir.rglob("*.json"))
        self._write(f"Found {len(files)} action file(s).\n", "head")

        ok = err = 0
        for fp in files:
            try:
                with open(fp) as f:
                    data = json.load(f)
            except Exception as e:
                self._write(f"  [PARSE ERROR] {fp.name}: {e}", "err")
                err += 1
                continue

            missing = {"id", "resolver"} - set(data.keys())
            if missing:
                self._write(f"  [MISSING] {fp.name}: missing fields: {missing}", "err")
                err += 1
                continue

            type_errors = []
            if not isinstance(data.get("id"), str):
                type_errors.append("'id' must be a string")
            if not isinstance(data.get("resolver"), str):
                type_errors.append("'resolver' must be a string")
            if "cost" in data and not isinstance(data["cost"], dict):
                type_errors.append("'cost' must be an object")
            if "effects" in data and not isinstance(data["effects"], list):
                type_errors.append("'effects' must be an array")

            if type_errors:
                self._write(f"  [TYPE ERROR] {fp.name}: {'; '.join(type_errors)}", "err")
                err += 1
            else:
                self._write(f"  [OK] {fp.name}  (id={data['id']}, resolver={data['resolver']})", "ok")
                ok += 1

        self._write(f"\n─── Result: {ok} OK, {err} error(s). ───", "head")


# ----------------------------------------------------------------------
# Section 5: Generate Resolver (refactored to use TextDisplay)
# ----------------------------------------------------------------------
class GenerateResolverFrame(ttk.Frame):
    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        ttk.Label(self, text="Generate New Action + Resolver Stub",
                  font=("Segoe UI", 12, "bold")).pack(pady=(10, 4))
        ttk.Label(self, text=("Enter an action ID and resolver path. The tool creates the action JSON "
                              "and a stub resolver Python file automatically."),
                  wraplength=700, justify=tk.LEFT).pack(padx=10, anchor=tk.W)

        form = ttk.Frame(self)
        form.pack(padx=16, pady=8, fill=tk.X)

        ttk.Label(form, text="Action ID:").grid(row=0, column=0, sticky=tk.W, pady=3)
        self._action_id = ttk.Entry(form, width=40)
        self._action_id.insert(0, "pray_at_shrine")
        self._action_id.grid(row=0, column=1, sticky=tk.W, padx=8)

        ttk.Label(form, text="Resolver:").grid(row=1, column=0, sticky=tk.W, pady=3)
        self._resolver = ttk.Entry(form, width=40)
        self._resolver.insert(0, "location.pray")
        self._resolver.grid(row=1, column=1, sticky=tk.W, padx=8)

        ttk.Label(form, text="Description:").grid(row=2, column=0, sticky=tk.W, pady=3)
        self._desc = ttk.Entry(form, width=60)
        self._desc.insert(0, "Stub action — fill in resolver logic.")
        self._desc.grid(row=2, column=1, columnspan=2, sticky=tk.W, padx=8)

        ttk.Button(self, text="Generate Files", command=self._generate).pack(pady=6)

        if UI_AVAILABLE:
            self._log = TextDisplay(self, content="")
        else:
            self._log = tk.Text(self, wrap=tk.WORD, bg="#1e1e2e", fg="#cdd6f4", height=22)
        self._log.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

    def _write(self, text: str, tag: str = "") -> None:
        if UI_AVAILABLE and hasattr(self._log, 'append'):
            self._log.append(text + "\n")
        else:
            self._log.insert(tk.END, text + "\n")
            self._log.see(tk.END)

    def _generate(self) -> None:
        action_id = self._action_id.get().strip()
        resolver = self._resolver.get().strip()
        description = self._desc.get().strip()

        self._clear()

        if not action_id or not resolver:
            self._write("ERROR: Action ID and Resolver are required.", "err")
            return
        if " " in action_id or " " in resolver:
            self._write("ERROR: No spaces allowed in Action ID or Resolver.", "err")
            return

        actions_dir = data_path("actions")
        actions_dir.mkdir(parents=True, exist_ok=True)
        json_path = actions_dir / f"{action_id}.json"
        if json_path.exists():
            self._write(f"WARN: {json_path} already exists — skipping JSON.", "err")
        else:
            payload = {
                "id": action_id, "resolver": resolver,
                "cost": {}, "effects": [], "context_requirements": [],
                "description": description or "Stub action."
            }
            with open(json_path, "w") as f:
                json.dump(payload, f, indent=2)
            self._write(f"[CREATED] {json_path}", "ok")

        parts = resolver.split(".")
        resolver_dir = pathlib.Path("app/logic/resolvers").joinpath(*parts[:-1])
        resolver_dir.mkdir(parents=True, exist_ok=True)
        init = resolver_dir / "__init__.py"
        if not init.exists():
            init.touch()
        py_path = resolver_dir / f"{parts[-1]}.py"
        if py_path.exists():
            self._write(f"WARN: {py_path} already exists — skipping Python stub.", "err")
        else:
            stub = textwrap.dedent(f"""
                \"\"\"
                {resolver} — stub resolver generated by DevTools.
                Action: {action_id}
                \"\"\"
                from app.logic.action_types import ActionContext, ActionResult


                def resolve(ctx: ActionContext) -> ActionResult:
                    ps = dict(ctx.player_state)
                    # TODO: implement {action_id} logic here
                    return ActionResult(
                        new_player_state  = ps,
                        new_dungeon_state = ctx.dungeon_state,
                        messages          = ["[Stub] {action_id} not yet implemented."],
                    )
            """).lstrip()
            py_path.write_text(stub)
            self._write(f"[CREATED] {py_path}", "ok")

        self._write("\nDone. Restart the game/dispatcher to auto-discover the new resolver.", "head")

    def _clear(self) -> None:
        if UI_AVAILABLE and hasattr(self._log, 'set_content'):
            self._log.set_content("")
        else:
            self._log.delete("1.0", tk.END)



# ----------------------------------------------------------------------
# Section 6: JSON Workshop – visual editor for game data files
# ----------------------------------------------------------------------
class JSONWorkshopFrame(tk.Frame):
    """
    Visual form-based editor for items, enemies, services, and actions.

    Layout:
      Left  — category selector + entry list + action buttons
      Right — dynamic form for the selected entry + Preview JSON button
    """

    # ── category definitions ──────────────────────────────────────────────
    CATEGORIES = ["Items", "Enemies", "Services", "Actions"]

    # Field specs: (field_key, label, widget_type, options/range)
    # widget_type: "entry" | "combo" | "spin" | "check" | "text_ro"
    ITEM_FIELDS = [
        ("id",         "ID",          "entry",  None),
        ("name",       "Name",        "entry",  None),
        ("type",       "Type",        "combo",  ["weapon", "armor", "consumable", "misc"]),
        ("value",      "Value (gold)","spin",   (0, 9999)),
        ("min_depth",  "Min Depth",   "spin",   (0, 20)),
        ("durability", "Durability",  "spin",   (0, 200)),
        ("stat_bonus_damage",  "Stat Bonus: Damage",  "spin", (0, 50)),
        ("stat_bonus_defense", "Stat Bonus: Defense", "spin", (0, 50)),
        ("effect",     "Effect",      "entry",  None),
        ("source",     "Source",      "entry",  None),
    ]
    ENEMY_FIELDS = [
        ("id",          "ID",           "entry", None),
        ("name",        "Name",         "entry", None),
        ("min_depth",   "Min Depth",    "spin",  (1, 20)),
        ("max_depth",   "Max Depth",    "spin",  (1, 20)),
        ("hp",          "HP",           "spin",  (1, 500)),
        ("damage_min",  "Damage Min",   "spin",  (0, 100)),
        ("damage_max",  "Damage Max",   "spin",  (0, 100)),
        ("gold_min",    "Gold Min",     "spin",  (0, 200)),
        ("gold_max",    "Gold Max",     "spin",  (0, 200)),
        ("loot_chance", "Loot Chance",  "spin_float", (0.0, 1.0, 0.05)),
        ("loot_count",  "Loot Count",   "spin",  (0, 10)),
    ]
    ACTION_FIELDS = [
        ("id",          "ID",           "entry", None),
        ("resolver",    "Resolver",     "combo", []),   # filled dynamically
        ("description", "Description",  "entry", None),
        ("cost_gold",   "Cost: Gold",   "spin",  (0, 9999)),
        ("reference",   "Reference",    "entry", None),
    ]

    # ── colours ───────────────────────────────────────────────────────────
    BG  = "#1e1e2e"
    FBG = "#313244"
    FG  = "#cdd6f4"
    ACC = "#89b4fa"
    ERR = "#f38ba8"
    OK  = "#a6e3a1"

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, bg=self.BG)
        self._data:    Dict[str, Any] = {}   # category → {id: entry_dict}
        self._current_cat:   str = "Items"
        self._current_id:    Optional[str] = None
        self._field_vars:    Dict[str, tk.Variable] = {}
        self._loot_items:    List[str] = []  # for enemy loot table
        self._dirty:         bool = False

        self._resolvers: List[str] = self._load_resolver_names()
        self._all_item_ids: List[str] = []

        self._build_ui()
        self._load_all()

    # ── data loading ──────────────────────────────────────────────────────

    def _load_resolver_names(self) -> List[str]:
        try:
            from app.logic.resolver_registry import ResolverRegistry
            return sorted(ResolverRegistry().all_names())
        except Exception:
            return []

    def _load_all(self) -> None:
        self._data = {}
        self._data["Items"]    = self._load_items()
        self._data["Enemies"]  = self._load_enemies()
        self._data["Services"] = self._load_services()
        self._data["Actions"]  = self._load_actions()
        self._all_item_ids     = sorted(self._data["Items"].keys())
        self._refresh_list()

    def _load_items(self) -> Dict:
        try:
            with open(data_path("dungeon", "items", "items.json"), encoding="utf-8") as f:
                return {i["id"]: i for i in json.load(f)}
        except Exception as e:
            self._status(f"Could not load items: {e}", error=True)
            return {}

    def _load_enemies(self) -> Dict:
        try:
            with open(data_path("dungeon", "enemies", "enemies.json"), encoding="utf-8") as f:
                return {e["id"]: e for e in json.load(f)}
        except Exception as e:
            self._status(f"Could not load enemies: {e}", error=True)
            return {}

    def _load_services(self) -> Dict:
        try:
            with open(data_path("city", "services.json"), encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self._status(f"Could not load services: {e}", error=True)
            return {}

    def _load_actions(self) -> Dict:
        actions = {}
        actions_dir = data_path("actions")
        if not actions_dir.exists():
            return actions
        for fp in sorted(actions_dir.rglob("*.json")):
            try:
                with open(fp, encoding="utf-8") as f:
                    a = json.load(f)
                a["_file"] = str(fp)   # track source file
                actions[a.get("id", fp.stem)] = a
            except Exception:
                pass
        return actions

    # ── UI construction ───────────────────────────────────────────────────

    def _build_ui(self) -> None:
        pane = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg=self.BG,
                              sashwidth=5, sashrelief=tk.RIDGE)
        pane.pack(fill=tk.BOTH, expand=True)

        # ── Left pane ────────────────────────────────────────────────────
        left = ttk.Frame(pane, width=230)
        pane.add(left, minsize=180)

        # Category buttons
        cat_frame = ttk.Frame(left)
        cat_frame.pack(fill=tk.X, pady=(6, 2))
        self._cat_btns: Dict[str, ttk.Button] = {}
        for cat in self.CATEGORIES:
            b = ttk.Button(cat_frame, text=cat,
                           command=lambda c=cat: self._select_category(c))
            b.pack(fill=tk.X, padx=4, pady=1)
            self._cat_btns[cat] = b

        # Entry list
        tk.Label(left, text="Entries", bg=self.BG, fg=self.ACC,
                 font=("Segoe UI", 9, "bold")).pack(padx=6, anchor=tk.W)

        list_frame = ttk.Frame(left)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)

        self._listbox = tk.Listbox(list_frame, bg=self.FBG, fg=self.FG,
                                   selectbackground=self.ACC,
                                   selectforeground="#1e1e2e",
                                   activestyle="none", relief=tk.FLAT,
                                   font=("Segoe UI", 9))
        sb = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,
                           command=self._listbox.yview)
        self._listbox.configure(yscrollcommand=sb.set)
        self._listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._listbox.bind("<<ListboxSelect>>", self._on_list_select)

        # Search box
        search_frame = ttk.Frame(left)
        search_frame.pack(fill=tk.X, padx=4, pady=(0, 2))
        ttk.Label(search_frame, text="Filter:").pack(side=tk.LEFT)
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._refresh_list())
        ttk.Entry(search_frame, textvariable=self._search_var,
                  width=18).pack(side=tk.LEFT, padx=3)

        # Left action buttons
        lb_btns = ttk.Frame(left)
        lb_btns.pack(fill=tk.X, padx=4, pady=4)
        for text, cmd in [("New",       self._cmd_new),
                          ("Duplicate", self._cmd_duplicate),
                          ("Delete",    self._cmd_delete)]:
            ttk.Button(lb_btns, text=text, command=cmd).pack(
                side=tk.LEFT, padx=2)

        # ── Right pane ───────────────────────────────────────────────────
        right = ttk.Frame(pane)
        pane.add(right, minsize=380)

        # Form header
        self._form_title = tk.Label(right, text="Select an entry",
                                    bg=self.BG, fg=self.ACC,
                                    font=("Segoe UI", 11, "bold"))
        self._form_title.pack(anchor=tk.W, padx=10, pady=(8, 2))

        # Scrollable form area
        canvas_frame = ttk.Frame(right)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=6)

        self._canvas = tk.Canvas(canvas_frame, bg=self.BG,
                                 highlightthickness=0)
        form_sb = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL,
                                command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=form_sb.set)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        form_sb.pack(side=tk.RIGHT, fill=tk.Y)

        self._form_inner = tk.Frame(self._canvas, bg=self.BG)
        self._canvas_win = self._canvas.create_window(
            (0, 0), window=self._form_inner, anchor="nw")
        self._form_inner.bind("<Configure>",
            lambda e: self._canvas.configure(
                scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>",
            lambda e: self._canvas.itemconfig(
                self._canvas_win, width=e.width))

        # Loot table widget (enemy only, shown/hidden dynamically)
        self._loot_frame = tk.LabelFrame(self._form_inner,
                                         text="Loot Table",
                                         bg=self.BG, fg=self.ACC,
                                         padx=4, pady=4)

        loot_list_frame = ttk.Frame(self._loot_frame)
        loot_list_frame.pack(fill=tk.X)
        self._loot_listbox = tk.Listbox(loot_list_frame,
                                        bg=self.FBG, fg=self.FG,
                                        selectbackground=self.ACC,
                                        height=4, font=("Segoe UI", 9))
        self._loot_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        loot_btn_frame = ttk.Frame(self._loot_frame)
        loot_btn_frame.pack(fill=tk.X, pady=3)
        self._loot_add_combo = ttk.Combobox(loot_btn_frame, width=28,
                                            state="readonly")
        self._loot_add_combo.pack(side=tk.LEFT, padx=2)
        ttk.Button(loot_btn_frame, text="Add",
                   command=self._loot_add).pack(side=tk.LEFT, padx=2)
        ttk.Button(loot_btn_frame, text="Remove",
                   command=self._loot_remove).pack(side=tk.LEFT, padx=2)

        # Status bar
        self._status_var = tk.StringVar(value="Ready")
        tk.Label(right, textvariable=self._status_var,
                 bg=self.BG, fg=self.FG,
                 font=("Segoe UI", 8), anchor=tk.W).pack(
                     fill=tk.X, padx=10)

        # Bottom buttons
        btn_row = ttk.Frame(right)
        btn_row.pack(fill=tk.X, padx=8, pady=6)
        ttk.Button(btn_row, text="💾 Save",
                   command=self._cmd_save).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_row, text="↺ Revert",
                   command=self._cmd_revert).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_row, text="{ } Preview JSON",
                   command=self._cmd_preview).pack(side=tk.LEFT, padx=3)

        # Start on Items
        self._select_category("Items")

    # ── category / list management ────────────────────────────────────────

    def _select_category(self, cat: str) -> None:
        if self._dirty:
            if not messagebox.askyesno("Unsaved changes",
                    "You have unsaved changes. Discard them?"):
                return
        self._current_cat = cat
        self._current_id  = None
        self._dirty       = False
        self._refresh_list()
        self._clear_form()
        for c, b in self._cat_btns.items():
            b.configure(style="Accent.TButton" if c == cat else "TButton")

    def _refresh_list(self) -> None:
        self._listbox.delete(0, tk.END)
        cat  = self._current_cat
        data = self._data.get(cat, {})
        filt = self._search_var.get().lower() if hasattr(self, "_search_var") else ""

        if cat == "Services":
            keys = sorted(data.keys())
        else:
            keys = sorted(data.keys())

        for k in keys:
            display = k
            if cat in ("Items", "Enemies"):
                display = data[k].get("name", k)
            if filt and filt not in display.lower() and filt not in k.lower():
                continue
            self._listbox.insert(tk.END, display)
            # Store id as tag via a parallel list
        # Build parallel id list matching listbox order
        self._list_ids = []
        for k in keys:
            display = k
            if cat in ("Items", "Enemies"):
                display = data[k].get("name", k)
            if filt and filt not in display.lower() and filt not in k.lower():
                continue
            self._list_ids.append(k)

    def _on_list_select(self, event=None) -> None:
        sel = self._listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx >= len(self._list_ids):
            return
        entry_id = self._list_ids[idx]
        if self._dirty:
            if not messagebox.askyesno("Unsaved changes",
                    "Discard unsaved changes?"):
                self._listbox.selection_clear(0, tk.END)
                return
        self._current_id = entry_id
        self._dirty = False
        self._populate_form(entry_id)

    # ── form building ─────────────────────────────────────────────────────

    def _clear_form(self) -> None:
        for w in self._form_inner.winfo_children():
            if w is not self._loot_frame:
                w.destroy()
        self._loot_frame.pack_forget()
        self._field_vars.clear()
        self._form_title.config(text="Select an entry")

    def _build_form(self, fields) -> None:
        """Render a list of field specs as a grid inside _form_inner."""
        self._field_vars.clear()
        for r, (key, label, wtype, opts) in enumerate(fields):
            tk.Label(self._form_inner, text=label + ":",
                     bg=self.BG, fg=self.FG,
                     font=("Segoe UI", 9), anchor=tk.E, width=20
                     ).grid(row=r, column=0, sticky=tk.E, padx=6, pady=3)

            if wtype == "entry":
                var = tk.StringVar()
                w = tk.Entry(self._form_inner, textvariable=var, width=36,
                             bg=self.FBG, fg=self.FG,
                             insertbackground=self.FG)
                w.grid(row=r, column=1, sticky=tk.W, padx=4, pady=3)
                var.trace_add("write", lambda *_: self._mark_dirty())
                self._field_vars[key] = var

            elif wtype == "combo":
                var = tk.StringVar()
                values = list(opts) if opts else []
                # For resolver field, inject live resolver names
                if key == "resolver" and self._resolvers:
                    values = self._resolvers
                w = ttk.Combobox(self._form_inner, textvariable=var,
                                 values=values, width=34, state="normal")
                w.grid(row=r, column=1, sticky=tk.W, padx=4, pady=3)
                var.trace_add("write", lambda *_: self._mark_dirty())
                self._field_vars[key] = var

            elif wtype == "spin":
                lo, hi = opts
                var = tk.IntVar(value=lo)
                w = ttk.Spinbox(self._form_inner, textvariable=var,
                                from_=lo, to=hi, width=10)
                w.grid(row=r, column=1, sticky=tk.W, padx=4, pady=3)
                var.trace_add("write", lambda *_: self._mark_dirty())
                self._field_vars[key] = var

            elif wtype == "spin_float":
                lo, hi, step = opts
                var = tk.DoubleVar(value=lo)
                w = ttk.Spinbox(self._form_inner, textvariable=var,
                                from_=lo, to=hi, increment=step,
                                format="%.2f", width=10)
                w.grid(row=r, column=1, sticky=tk.W, padx=4, pady=3)
                var.trace_add("write", lambda *_: self._mark_dirty())
                self._field_vars[key] = var

        self._form_inner.columnconfigure(1, weight=1)

    def _populate_form(self, entry_id: str) -> None:
        self._clear_form()
        cat  = self._current_cat
        data = self._data[cat]

        if cat == "Items":
            entry = data.get(entry_id, {})
            self._form_title.config(text=f"Item — {entry.get('name', entry_id)}")
            self._build_form(self.ITEM_FIELDS)
            sb = entry.get("stat_bonus") or {}
            self._field_vars["id"].set(entry.get("id", ""))
            self._field_vars["name"].set(entry.get("name", ""))
            self._field_vars["type"].set(entry.get("type", "misc"))
            self._field_vars["value"].set(entry.get("value", 0))
            self._field_vars["min_depth"].set(entry.get("min_depth", 0))
            self._field_vars["durability"].set(entry.get("durability", 0))
            self._field_vars["stat_bonus_damage"].set(sb.get("damage", 0))
            self._field_vars["stat_bonus_defense"].set(sb.get("defense", 0))
            self._field_vars["effect"].set(entry.get("effect") or "")
            self._field_vars["source"].set(entry.get("source") or "")

        elif cat == "Enemies":
            entry = data.get(entry_id, {})
            self._form_title.config(text=f"Enemy — {entry.get('name', entry_id)}")
            self._build_form(self.ENEMY_FIELDS)
            self._field_vars["id"].set(entry.get("id", ""))
            self._field_vars["name"].set(entry.get("name", ""))
            self._field_vars["min_depth"].set(entry.get("min_depth", 1))
            self._field_vars["max_depth"].set(entry.get("max_depth", 5))
            self._field_vars["hp"].set(entry.get("hp", 10))
            self._field_vars["damage_min"].set(entry.get("damage_min", 1))
            self._field_vars["damage_max"].set(entry.get("damage_max", 3))
            self._field_vars["gold_min"].set(entry.get("gold_min", 1))
            self._field_vars["gold_max"].set(entry.get("gold_max", 5))
            self._field_vars["loot_chance"].set(entry.get("loot_chance", 0.5))
            self._field_vars["loot_count"].set(entry.get("loot_count", 1))
            # Loot table widget
            row_count = len(self.ENEMY_FIELDS)
            self._loot_frame.grid(in_=self._form_inner,
                                  row=row_count, column=0,
                                  columnspan=2, sticky=tk.W+tk.E,
                                  padx=6, pady=6)
            self._loot_listbox.delete(0, tk.END)
            self._loot_items = list(entry.get("loot_table", []))
            for item_id in self._loot_items:
                self._loot_listbox.insert(tk.END, item_id)
            self._loot_add_combo.configure(values=self._all_item_ids)

        elif cat == "Services":
            entry = data.get(entry_id, {})
            self._form_title.config(text=f"Service — {entry_id}")
            # Services are complex free-form dicts; show JSON in a text widget
            self._build_services_form(entry_id, entry)

        elif cat == "Actions":
            entry = data.get(entry_id, {})
            self._form_title.config(text=f"Action — {entry_id}")
            fields = [(k, l, t, o) for k, l, t, o in self.ACTION_FIELDS]
            # patch resolver values dynamically
            fields = [
                (k, l, t, self._resolvers if k == "resolver" else o)
                for k, l, t, o in fields
            ]
            self._build_form(fields)
            self._field_vars["id"].set(entry.get("id", ""))
            self._field_vars["resolver"].set(entry.get("resolver", ""))
            self._field_vars["description"].set(entry.get("description", ""))
            cost = entry.get("cost", {})
            self._field_vars["cost_gold"].set(cost.get("gold", 0))
            self._field_vars["reference"].set(entry.get("reference") or "")

        self._dirty = False

    def _build_services_form(self, service_id: str, entry: Dict) -> None:
        """Services are free-form; show editable JSON text area."""
        row = 0
        tk.Label(self._form_inner, text="Service ID:",
                 bg=self.BG, fg=self.FG, anchor=tk.E, width=20
                 ).grid(row=row, column=0, sticky=tk.E, padx=6, pady=3)
        id_var = tk.StringVar(value=service_id)
        tk.Entry(self._form_inner, textvariable=id_var, width=36,
                 bg=self.FBG, fg=self.FG,
                 insertbackground=self.FG, state="readonly"
                 ).grid(row=row, column=1, sticky=tk.W, padx=4)
        self._field_vars["_service_id"] = id_var

        row += 1
        tk.Label(self._form_inner, text="JSON (raw):",
                 bg=self.BG, fg=self.FG, anchor=tk.NE, width=20
                 ).grid(row=row, column=0, sticky=tk.NE, padx=6, pady=3)
        txt = tk.Text(self._form_inner, width=46, height=12,
                      bg=self.FBG, fg=self.FG,
                      insertbackground=self.FG, wrap=tk.NONE,
                      font=("Consolas", 9))
        txt.grid(row=row, column=1, sticky=tk.W+tk.E, padx=4, pady=3)
        txt.insert("1.0", json.dumps(entry, indent=2))
        txt.bind("<Key>", lambda *_: self._mark_dirty())
        self._field_vars["_service_json_widget"] = txt   # type: ignore

    # ── loot table helpers ────────────────────────────────────────────────

    def _loot_add(self) -> None:
        item_id = self._loot_add_combo.get()
        if item_id and item_id not in self._loot_items:
            self._loot_items.append(item_id)
            self._loot_listbox.insert(tk.END, item_id)
            self._mark_dirty()

    def _loot_remove(self) -> None:
        sel = self._loot_listbox.curselection()
        if sel:
            idx = sel[0]
            self._loot_items.pop(idx)
            self._loot_listbox.delete(idx)
            self._mark_dirty()

    # ── dirty tracking ────────────────────────────────────────────────────

    def _mark_dirty(self) -> None:
        self._dirty = True

    def _status(self, msg: str, error: bool = False, ok: bool = False) -> None:
        colour = self.ERR if error else (self.OK if ok else self.FG)
        self._status_var.set(msg)
        # Find the label and recolour it
        for w in self.winfo_children():
            pass   # status label is in right pane; access via stringvar (colour not critical)

    # ── entry gathering from form ─────────────────────────────────────────

    def _gather_item(self) -> Optional[Dict]:
        try:
            entry = {
                "id":         self._field_vars["id"].get().strip(),
                "name":       self._field_vars["name"].get().strip(),
                "type":       self._field_vars["type"].get().strip(),
                "value":      int(self._field_vars["value"].get()),
                "min_depth":  int(self._field_vars["min_depth"].get()),
                "durability": int(self._field_vars["durability"].get()),
                "effect":     self._field_vars["effect"].get().strip() or None,
                "source":     self._field_vars["source"].get().strip() or None,
                "stat_bonus": {},
            }
            dmg = int(self._field_vars["stat_bonus_damage"].get())
            dfn = int(self._field_vars["stat_bonus_defense"].get())
            if dmg: entry["stat_bonus"]["damage"] = dmg
            if dfn: entry["stat_bonus"]["defense"] = dfn
            if not entry["stat_bonus"]:
                entry["stat_bonus"] = None
            return entry
        except (ValueError, KeyError) as e:
            messagebox.showerror("Validation error", str(e))
            return None

    def _gather_enemy(self) -> Optional[Dict]:
        try:
            return {
                "id":          self._field_vars["id"].get().strip(),
                "name":        self._field_vars["name"].get().strip(),
                "min_depth":   int(self._field_vars["min_depth"].get()),
                "max_depth":   int(self._field_vars["max_depth"].get()),
                "hp":          int(self._field_vars["hp"].get()),
                "damage_min":  int(self._field_vars["damage_min"].get()),
                "damage_max":  int(self._field_vars["damage_max"].get()),
                "gold_min":    int(self._field_vars["gold_min"].get()),
                "gold_max":    int(self._field_vars["gold_max"].get()),
                "loot_chance": round(float(self._field_vars["loot_chance"].get()), 2),
                "loot_count":  int(self._field_vars["loot_count"].get()),
                "loot_table":  list(self._loot_items),
            }
        except (ValueError, KeyError) as e:
            messagebox.showerror("Validation error", str(e))
            return None

    def _gather_action(self) -> Optional[Dict]:
        try:
            action_id  = self._field_vars["id"].get().strip()
            resolver   = self._field_vars["resolver"].get().strip()
            desc       = self._field_vars["description"].get().strip()
            cost_gold  = int(self._field_vars["cost_gold"].get())
            reference  = self._field_vars["reference"].get().strip() or None
            return {
                "id":          action_id,
                "resolver":    resolver,
                "description": desc,
                "cost":        {"gold": cost_gold} if cost_gold else {},
                "reference":   reference,
            }
        except (ValueError, KeyError) as e:
            messagebox.showerror("Validation error", str(e))
            return None

    def _gather_service(self) -> Optional[tuple]:
        """Returns (service_id, dict) or None."""
        try:
            txt_widget = self._field_vars.get("_service_json_widget")
            if txt_widget is None:
                return None
            raw = txt_widget.get("1.0", tk.END).strip()
            entry = json.loads(raw)
            sid   = self._field_vars["_service_id"].get().strip()
            return sid, entry
        except json.JSONDecodeError as e:
            messagebox.showerror("JSON error", f"Invalid JSON:\n{e}")
            return None

    # ── validation ────────────────────────────────────────────────────────

    def _validate(self, cat: str, entry: Dict) -> Optional[str]:
        """Return an error string, or None if valid."""
        if cat in ("Items", "Enemies", "Actions"):
            if not entry.get("id"):
                return "ID cannot be empty."
        if cat == "Items":
            if not entry.get("name"):
                return "Name cannot be empty."
            if entry["type"] not in ("weapon", "armor", "consumable", "misc"):
                return f"Invalid type '{entry['type']}'."
        if cat == "Enemies":
            if not entry.get("name"):
                return "Name cannot be empty."
            if entry["damage_min"] > entry["damage_max"]:
                return "Damage Min must be ≤ Damage Max."
            if entry["gold_min"] > entry["gold_max"]:
                return "Gold Min must be ≤ Gold Max."
            if entry["min_depth"] > entry["max_depth"]:
                return "Min Depth must be ≤ Max Depth."
        if cat == "Actions":
            if not entry.get("resolver"):
                return "Resolver cannot be empty."
        return None

    # ── commands ──────────────────────────────────────────────────────────

    def _cmd_new(self) -> None:
        cat = self._current_cat
        defaults = {
            "Items":    {"id": "item_new_01", "name": "New Item",
                         "type": "misc", "value": 0, "min_depth": 0,
                         "durability": 0, "effect": None, "source": None,
                         "stat_bonus": None},
            "Enemies":  {"id": "enemy_new_01", "name": "New Enemy",
                         "min_depth": 1, "max_depth": 5, "hp": 10,
                         "damage_min": 1, "damage_max": 3,
                         "gold_min": 1, "gold_max": 5,
                         "loot_chance": 0.5, "loot_count": 1,
                         "loot_table": []},
            "Actions":  {"id": "new_action", "resolver": "",
                         "description": "", "cost": {}, "reference": None,
                         "_file": str(data_path("actions", "new_action.json"))},
            "Services": {"actions": []},
        }
        new_id = f"__new__{len(self._data[cat])}"
        entry  = defaults.get(cat, {})
        entry_id = entry.get("id", new_id)
        self._data[cat][entry_id] = entry
        self._refresh_list()
        # Select the new entry
        if entry_id in self._list_ids:
            idx = self._list_ids.index(entry_id)
            self._listbox.selection_clear(0, tk.END)
            self._listbox.selection_set(idx)
            self._listbox.see(idx)
            self._current_id = entry_id
            self._populate_form(entry_id)
        self._mark_dirty()

    def _cmd_duplicate(self) -> None:
        if not self._current_id:
            messagebox.showinfo("Nothing selected", "Select an entry first.")
            return
        cat   = self._current_cat
        entry = dict(self._data[cat].get(self._current_id, {}))
        new_id = (entry.get("id", self._current_id) or self._current_id) + "_copy"
        entry["id"] = new_id
        self._data[cat][new_id] = entry
        self._refresh_list()
        if new_id in self._list_ids:
            idx = self._list_ids.index(new_id)
            self._listbox.selection_clear(0, tk.END)
            self._listbox.selection_set(idx)
            self._listbox.see(idx)
            self._current_id = new_id
            self._populate_form(new_id)
        self._mark_dirty()

    def _cmd_delete(self) -> None:
        if not self._current_id:
            messagebox.showinfo("Nothing selected", "Select an entry first.")
            return
        cat = self._current_cat
        if not messagebox.askyesno("Confirm delete",
                f"Delete '{self._current_id}' from {cat}?\n"
                "This will be permanent when you save."):
            return
        self._data[cat].pop(self._current_id, None)
        self._current_id = None
        self._dirty = False
        self._refresh_list()
        self._clear_form()
        self._status_var.set(f"Entry deleted (save to persist).")

    def _cmd_save(self) -> None:
        cat = self._current_cat
        if cat == "Items":
            entry = self._gather_item()
            if entry is None: return
            err = self._validate(cat, entry)
            if err:
                messagebox.showerror("Validation", err); return
            old_id = self._current_id
            new_id = entry["id"]
            if old_id and old_id != new_id:
                self._data[cat].pop(old_id, None)
            self._data[cat][new_id] = entry
            self._current_id = new_id
            path = data_path("dungeon", "items", "items.json")
            items_list = list(self._data[cat].values())
            self._write_json(path, items_list)

        elif cat == "Enemies":
            entry = self._gather_enemy()
            if entry is None: return
            err = self._validate(cat, entry)
            if err:
                messagebox.showerror("Validation", err); return
            old_id = self._current_id
            new_id = entry["id"]
            if old_id and old_id != new_id:
                self._data[cat].pop(old_id, None)
            self._data[cat][new_id] = entry
            self._current_id = new_id
            path = data_path("dungeon", "enemies", "enemies.json")
            enemies_list = list(self._data[cat].values())
            self._write_json(path, enemies_list)

        elif cat == "Services":
            result = self._gather_service()
            if result is None: return
            sid, entry = result
            self._data[cat][sid] = entry
            path = data_path("city", "services.json")
            self._write_json(path, self._data[cat])

        elif cat == "Actions":
            entry = self._gather_action()
            if entry is None: return
            err = self._validate(cat, entry)
            if err:
                messagebox.showerror("Validation", err); return
            old_id     = self._current_id
            new_id     = entry["id"]
            # Determine file path — use existing or derive from new id
            old_entry  = self._data[cat].get(old_id, {})
            file_path  = old_entry.get("_file") or \
                         str(data_path("actions", f"{new_id}.json"))
            # Update _file to match new id if changed
            if old_id != new_id:
                file_path = str(data_path("actions", f"{new_id}.json"))
                self._data[cat].pop(old_id, None)
            entry["_file"] = file_path
            self._data[cat][new_id] = entry
            self._current_id = new_id
            # Write only this action's file (strip internal _file key)
            clean = {k: v for k, v in entry.items() if k != "_file"}
            self._write_json(pathlib.Path(file_path), clean)

        self._dirty = False
        self._refresh_list()
        self._status_var.set("✓ Saved successfully.")

    def _write_json(self, path, data_obj) -> None:
        try:
            path = pathlib.Path(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data_obj, f, indent=2)
        except Exception as e:
            messagebox.showerror("Save failed", str(e))

    def _cmd_revert(self) -> None:
        if not self._current_id:
            return
        self._load_all()
        self._populate_form(self._current_id)
        self._dirty = False
        self._status_var.set("Reverted to saved data.")

    def _cmd_preview(self) -> None:
        cat = self._current_cat
        if not self._current_id:
            messagebox.showinfo("Nothing selected", "Select an entry first.")
            return
        # Gather current (possibly unsaved) state
        if cat == "Items":
            entry = self._gather_item()
        elif cat == "Enemies":
            entry = self._gather_enemy()
        elif cat == "Actions":
            entry = self._gather_action()
        elif cat == "Services":
            result = self._gather_service()
            entry  = result[1] if result else None
        else:
            entry = None

        text = json.dumps(entry, indent=2) if entry else "(nothing to preview)"

        win = tk.Toplevel(self)
        win.title(f"Preview JSON — {self._current_id}")
        win.geometry("520x380")
        win.configure(bg=self.BG)
        txt = tk.Text(win, bg=self.FBG, fg=self.FG,
                      font=("Consolas", 10), wrap=tk.NONE)
        txt.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        txt.insert("1.0", text)
        txt.configure(state="disabled")
        ttk.Button(win, text="Close", command=win.destroy).pack(pady=4)



# ----------------------------------------------------------------------
# Section 7: File Auditor – scan for dead/redundant files
# ----------------------------------------------------------------------
class FileAuditorFrame(tk.Frame):
    """
    Scans the project for redundant Python files, empty files, and
    files that are never imported, then lets the user delete them
    with a single in-frame confirmation step — no popups.

    Categories flagged:
      • __pycache__ directories and .pyc files
      • *.bak / *.orig / *.old files
      • Empty Python files (0 bytes or whitespace only)
      • Python files that are never imported anywhere in the project
        and are not known entry points
    """

    BG  = "#1e1e2e"
    FBG = "#313244"
    FG  = "#cdd6f4"
    ACC = "#89b4fa"
    ERR = "#f38ba8"
    OK  = "#a6e3a1"
    WRN = "#f9e2af"

    EXCLUDE_DIRS   = {".git", "__pycache__", "logs", "dist", "build",
                      "_build_tmp_game", "_build_tmp_dev", "Build Output"}
    ENTRY_POINTS   = {"main", "DevTools"}    # scripts run directly, not imported
    SCAN_ROOT      = pathlib.Path(__file__).resolve().parent

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, bg=self.BG)
        self._findings: List[Dict[str, Any]] = []   # [{path, category, reason}]
        self._check_vars: List[tk.BooleanVar] = []  # one per finding row
        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        # Top control bar
        ctrl = ttk.Frame(self)
        ctrl.pack(fill=tk.X, padx=10, pady=8)

        ttk.Button(ctrl, text="🔍  Scan Project",
                   command=self._run_scan).pack(side=tk.LEFT, padx=4)
        ttk.Button(ctrl, text="☑  Select All",
                   command=self._select_all).pack(side=tk.LEFT, padx=4)
        ttk.Button(ctrl, text="☐  Deselect All",
                   command=self._deselect_all).pack(side=tk.LEFT, padx=4)
        self._delete_btn = ttk.Button(ctrl, text="🗑  Delete Selected",
                                      command=self._confirm_delete,
                                      state="disabled")
        self._delete_btn.pack(side=tk.LEFT, padx=4)

        # Status / summary label — keep as tk.Label for accent colour support
        self._summary_var = tk.StringVar(value="Press 'Scan Project' to begin.")
        tk.Label(self, textvariable=self._summary_var,
                 bg=self.BG, fg=self.ACC,
                 font=("Segoe UI", 9), anchor=tk.W
                 ).pack(fill=tk.X, padx=12, pady=(0, 4))

        # Inline confirmation bar (hidden until Delete is clicked)
        self._confirm_bar = tk.Frame(self, bg="#3b1515")
        self._confirm_label = tk.Label(self._confirm_bar, text="",
                                       bg="#3b1515", fg=self.ERR,
                                       font=("Segoe UI", 9))
        self._confirm_label.pack(side=tk.LEFT, padx=10, pady=4)
        ttk.Button(self._confirm_bar, text="Yes, delete",
                   command=self._do_delete).pack(side=tk.LEFT, padx=4)
        ttk.Button(self._confirm_bar, text="Cancel",
                   command=self._hide_confirm).pack(side=tk.LEFT, padx=2)
        # Not packed yet

        # Scrollable findings area
        canvas_frame = ttk.Frame(self)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        self._canvas = tk.Canvas(canvas_frame, bg=self.BG,
                                 highlightthickness=0)
        sb = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL,
                           command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=sb.set)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self._findings_frame = tk.Frame(self._canvas, bg=self.BG)
        self._canvas_win = self._canvas.create_window(
            (0, 0), window=self._findings_frame, anchor="nw")
        self._findings_frame.bind("<Configure>",
            lambda e: self._canvas.configure(
                scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>",
            lambda e: self._canvas.itemconfig(self._canvas_win, width=e.width))

    # ── scanning ──────────────────────────────────────────────────────────

    def _run_scan(self) -> None:
        self._summary_var.set("Scanning…")
        self.update_idletasks()
        self._findings = []
        self._check_vars = []

        root = self.SCAN_ROOT

        # 1. __pycache__ dirs and .pyc files
        for p in root.rglob("__pycache__"):
            if self._excluded(p): continue
            self._findings.append({"path": p, "category": "Cache",
                                    "reason": "__pycache__ directory"})
        for p in root.rglob("*.pyc"):
            if self._excluded(p): continue
            self._findings.append({"path": p, "category": "Cache",
                                    "reason": "Compiled .pyc file"})

        # 2. Backup / temp files
        for pat in ("*.bak", "*.orig", "*.old"):
            for p in root.rglob(pat):
                if self._excluded(p): continue
                self._findings.append({"path": p, "category": "Backup",
                                        "reason": f"Backup/temp file ({p.suffix})"})

        # 3. Empty Python files
        for p in root.rglob("*.py"):
            if self._excluded(p): continue
            try:
                content = p.read_text(encoding="utf-8", errors="replace").strip()
                if not content:
                    self._findings.append({"path": p, "category": "Empty",
                                            "reason": "Empty Python file (0 bytes)"})
            except Exception:
                pass

        # 4. Never-imported Python files (static analysis)
        never_imported = self._find_never_imported(root)
        for p in sorted(never_imported):
            self._findings.append({"path": p, "category": "Unused",
                                    "reason": "Never imported anywhere in the project"})

        self._render_findings()

    def _excluded(self, path: pathlib.Path) -> bool:
        return any(part in self.EXCLUDE_DIRS or
                   part.startswith("Build Output")
                   for part in path.parts)

    def _find_never_imported(self, root: pathlib.Path) -> List[pathlib.Path]:
        """Return Python files that appear in no import statement project-wide."""
        import ast as _ast

        # Collect all module references from every .py file
        all_refs: set = set()
        py_files = [p for p in root.rglob("*.py") if not self._excluded(p)]

        for f in py_files:
            try:
                src = f.read_text(encoding="utf-8", errors="replace")
                tree = _ast.parse(src, filename=str(f))
            except Exception:
                continue
            for node in _ast.walk(tree):
                if isinstance(node, _ast.Import):
                    for alias in node.names:
                        all_refs.add(alias.name)
                        # add all prefixes
                        parts = alias.name.split(".")
                        for i in range(1, len(parts)):
                            all_refs.add(".".join(parts[:i]))
                elif isinstance(node, _ast.ImportFrom) and node.module:
                    all_refs.add(node.module)
                    parts = node.module.split(".")
                    for i in range(1, len(parts)):
                        all_refs.add(".".join(parts[:i]))

        never: List[pathlib.Path] = []
        for f in py_files:
            stem = f.stem
            if stem == "__init__": continue
            if stem in self.ENTRY_POINTS: continue

            # Convert file path to dotted module name relative to scan root
            try:
                rel = f.relative_to(root)
            except ValueError:
                continue
            mod = ".".join(rel.with_suffix("").parts)

            imported = any(
                ref == mod or
                mod.startswith(ref + ".") or
                ref.startswith(mod + ".")
                for ref in all_refs
            )
            if not imported:
                never.append(f)
        return never

    # ── rendering ─────────────────────────────────────────────────────────

    def _render_findings(self) -> None:
        # Clear previous rows
        for w in self._findings_frame.winfo_children():
            w.destroy()
        self._check_vars.clear()

        if not self._findings:
            tk.Label(self._findings_frame, text="✓  No issues found.",
                     bg=self.BG, fg=self.OK,
                     font=("Segoe UI", 10)).pack(padx=10, pady=20)
            self._summary_var.set("Scan complete — project is clean.")
            self._delete_btn.configure(state="disabled")
            return

        # Group by category
        from itertools import groupby
        sorted_findings = sorted(self._findings,
                                  key=lambda f: (f["category"], str(f["path"])))

        CAT_COLOURS = {
            "Cache":  "#6c7086",
            "Backup": self.WRN,
            "Empty":  self.WRN,
            "Unused": self.ERR,
        }

        row = 0
        current_cat = None
        for finding in sorted_findings:
            cat  = finding["category"]
            path = finding["path"]
            rel  = path.relative_to(self.SCAN_ROOT) if path.is_absolute() else path

            # Category header
            if cat != current_cat:
                current_cat = cat
                colour = CAT_COLOURS.get(cat, self.FG)
                hdr = tk.Label(self._findings_frame,
                                text=f"  ── {cat} ──",
                                bg=self.BG, fg=colour,
                                font=("Segoe UI", 9, "bold"),
                                anchor=tk.W)
                hdr.grid(row=row, column=0, columnspan=3,
                          sticky=tk.W, padx=6, pady=(10, 2))
                row += 1

            # Checkbox
            var = tk.BooleanVar(value=False)
            self._check_vars.append(var)
            finding["_var"] = var

            cb = tk.Checkbutton(self._findings_frame, variable=var,
                                 bg=self.BG, fg=self.FG,
                                 selectcolor=self.FBG,
                                 activebackground=self.BG)
            cb.grid(row=row, column=0, sticky=tk.W, padx=(8, 0))

            # Path label
            colour = CAT_COLOURS.get(cat, self.FG)
            tk.Label(self._findings_frame, text=str(rel),
                      bg=self.BG, fg=colour,
                      font=("Consolas", 8), anchor=tk.W
                      ).grid(row=row, column=1, sticky=tk.W, padx=4)

            # Reason
            tk.Label(self._findings_frame, text=finding["reason"],
                      bg=self.BG, fg="#6c7086",
                      font=("Segoe UI", 8), anchor=tk.W
                      ).grid(row=row, column=2, sticky=tk.W, padx=8)

            row += 1

        self._findings_frame.columnconfigure(1, weight=1)

        total = len(self._findings)
        cats  = {}
        for f in self._findings:
            cats[f["category"]] = cats.get(f["category"], 0) + 1
        cat_str = "  |  ".join(f"{c}: {n}" for c, n in sorted(cats.items()))
        self._summary_var.set(f"Found {total} item(s).  {cat_str}")
        self._delete_btn.configure(state="normal")

    # ── selection helpers ─────────────────────────────────────────────────

    def _select_all(self) -> None:
        for v in self._check_vars: v.set(True)

    def _deselect_all(self) -> None:
        for v in self._check_vars: v.set(False)

    # ── deletion ──────────────────────────────────────────────────────────

    def _selected_findings(self) -> List[Dict]:
        return [f for f in self._findings if f.get("_var") and f["_var"].get()]

    def _confirm_delete(self) -> None:
        sel = self._selected_findings()
        if not sel:
            self._summary_var.set("No items selected.")
            return
        self._confirm_label.config(
            text=f"Permanently delete {len(sel)} selected item(s)?")
        self._confirm_bar.pack(fill=tk.X, padx=8, pady=4)
        self._confirm_bar.lift()

    def _hide_confirm(self) -> None:
        self._confirm_bar.pack_forget()

    def _do_delete(self) -> None:
        self._hide_confirm()
        sel = self._selected_findings()
        deleted_ok = 0
        errors: List[str] = []
        for finding in sel:
            p = finding["path"]
            try:
                if p.is_dir():
                    import shutil as _shutil
                    _shutil.rmtree(p)
                elif p.exists():
                    p.unlink()
                deleted_ok += 1
            except Exception as exc:
                errors.append(f"{p.name}: {exc}")
        # Re-scan to refresh the list
        self._run_scan()
        msg = f"Deleted {deleted_ok} item(s)."
        if errors:
            msg += f"  {len(errors)} error(s): {'; '.join(errors)}"
        self._summary_var.set(msg)


# ----------------------------------------------------------------------
# Main Application
# ----------------------------------------------------------------------
class DevToolsApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("DevTools – Pursuit of Peace")
        self.root.geometry("1000x750")
        self.root.configure(bg="#1e1e2e")

        # Load game theme and initialise style manager (if UI available)
        if UI_AVAILABLE:
            theme = load_theme(str(data_path("ui", "themes.json")), logger=None)
            StyleManager.init_styles(self.root, theme)

        # Apply basic ttk styles for fallback
        self.style = ttk.Style()
        if 'clam' in self.style.theme_names():
            self.style.theme_use('clam')
        self.style.configure("TFrame", background="#1e1e2e")
        self.style.configure("TLabel", background="#1e1e2e", foreground="#cdd6f4")
        self.style.configure("TButton", background="#45475a", foreground="#cdd6f4")
        self.style.map("TButton", background=[("active", "#89b4fa")])

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab 1: Pycache Cleaner
        self.pycache_frame = PycacheCleaner(self.notebook)
        self.notebook.add(self.pycache_frame, text="Pycache Cleaner")

        # Tab 2: Audit Tool
        self.audit_frame = AuditToolFrame(self.notebook)
        self.notebook.add(self.audit_frame, text="Audit Tool")

        # Tab 3: Build Tool
        self.build_frame = BuildTool(self.notebook, self.root)
        self.notebook.add(self.build_frame, text="Build Tool")

        # Tab 4: Validate Actions
        self.validate_frame = ValidateActionsFrame(self.notebook)
        self.notebook.add(self.validate_frame, text="Validate Actions")

        # Tab 5: Generate Resolver
        self.gen_frame = GenerateResolverFrame(self.notebook)
        self.notebook.add(self.gen_frame, text="Generate Resolver")

        # Tab 6: JSON Workshop
        self.workshop_frame = JSONWorkshopFrame(self.notebook)
        self.notebook.add(self.workshop_frame, text="JSON Workshop")

        # Tab 7: File Auditor
        self.auditor_frame = FileAuditorFrame(self.notebook)
        self.notebook.add(self.auditor_frame, text="File Auditor")

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    app = DevToolsApp()
    app.run()