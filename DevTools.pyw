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

# ----------------------------------------------------------------------
# Import game UI components (replaces raw Tkinter)
# ----------------------------------------------------------------------
try:
    from app.ui.simple.basic.text_display import TextDisplay
    from app.ui.simple.basic.menu_list import MenuList
    from app.ui.simple.basic.stat_bar import StatBar
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
        frame_path = tk.Frame(self, bg="#1e1e2e")
        frame_path.pack(pady=10, padx=10, fill=tk.X)

        tk.Label(frame_path, text="Target Directory:", bg="#1e1e2e", fg="#cdd6f4") \
            .pack(side=tk.LEFT, padx=(0, 5))
        self.entry_path = tk.Entry(frame_path, textvariable=self.path_var,
                                   width=50, bg="#313244", fg="#cdd6f4",
                                   insertbackground="#cdd6f4")
        self.entry_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        btn_browse = ttk.Button(frame_path, text="Browse...", command=self.browse_folder)
        btn_browse.pack(side=tk.RIGHT)
        ToolTip(btn_browse, "Select the root folder to scan for __pycache__ directories")

        frame_buttons = tk.Frame(self, bg="#1e1e2e")
        frame_buttons.pack(pady=5)

        btn_start = tk.Button(frame_buttons, text="Start Deletion", command=self.start_deletion,
                              bg="#89b4fa", fg="#1e1e2e", padx=10, pady=5,
                              font=("Segoe UI", 9, "bold"))
        btn_start.pack(side=tk.LEFT, padx=5)
        ToolTip(btn_start, "Delete all __pycache__ folders inside the selected directory")

        btn_clear = tk.Button(frame_buttons, text="Clear Log", command=self.clear_log,
                              bg="#f38ba8", fg="#1e1e2e", padx=10, pady=5)
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
        ended, msg, _ = self.engine.do_combat_action(action_id, self.current_enemy)
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
        control_frame = tk.Frame(self, bg="#1e1e2e")
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(control_frame, text="Steps:", bg="#1e1e2e", fg="#cdd6f4") \
            .grid(row=0, column=0, sticky=tk.W, padx=5)
        self.steps_var = tk.StringVar(value="1000")
        steps_entry = tk.Entry(control_frame, textvariable=self.steps_var,
                               width=10, bg="#313244", fg="#cdd6f4")
        steps_entry.grid(row=0, column=1, padx=5)
        ToolTip(steps_entry, "Number of random actions to simulate")

        tk.Label(control_frame, text="Seed (optional):", bg="#1e1e2e", fg="#cdd6f4") \
            .grid(row=0, column=2, sticky=tk.W, padx=5)
        self.seed_var = tk.StringVar(value="")
        seed_entry = tk.Entry(control_frame, textvariable=self.seed_var,
                              width=15, bg="#313244", fg="#cdd6f4")
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

    def export_log(self) -> None:
        content = ""
        if UI_AVAILABLE and hasattr(self.log_display, 'get_content'):
            content = self.log_display.get_content()
        else:
            content = self.log_display.get(1.0, tk.END)
        if not content.strip():
            messagebox.showinfo("No log", "Nothing to export.")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".txt",
                                                filetypes=[("Text files", "*.txt")])
        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                messagebox.showinfo("Export successful", f"Log saved to {filepath}")
            except Exception as e:
                messagebox.showerror("Export failed", str(e))


# ----------------------------------------------------------------------
# Section 3: Build Tool (now can build both Game and DevTools)
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
    def __init__(self, parent: tk.Widget, main_root: tk.Tk) -> None:
        super().__init__(parent, bg="#1e1e2e")
        self.parent = parent
        self.main_root = main_root

        # Game build options
        self.game_script = tk.StringVar(value=os.path.abspath("main.pyw"))
        self.game_output = tk.StringVar(value="PursuitOfPeace")
        self.game_icon = tk.StringVar(value="")
        self.game_console = tk.BooleanVar(value=False)
        self.game_copy_data = tk.BooleanVar(value=True)
        self.game_clean = tk.BooleanVar(value=True)

        # DevTools build options
        self.dev_script = tk.StringVar(value=os.path.abspath("DevTools.pyw"))
        self.dev_output = tk.StringVar(value="DevTools")
        self.dev_icon = tk.StringVar(value="")
        self.dev_console = tk.BooleanVar(value=True)   # DevTools should show console for debug output
        self.dev_copy_data = tk.BooleanVar(value=False)  # DevTools doesn't need data folder
        self.dev_clean = tk.BooleanVar(value=True)

        self.build_btn_game: Optional[ttk.Button] = None
        self.build_btn_dev: Optional[ttk.Button] = None
        self.status_label: Optional[tk.Label] = None
        self.log_text: Optional[TextDisplay] = None
        self.install_btn: Optional[ttk.Button] = None

        self._create_widgets()
        self._check_pyinstaller_status()
        self._ensure_scripts_exist()

    def _ensure_scripts_exist(self) -> None:
        for var, name in [(self.game_script, "main.pyw"), (self.dev_script, "DevTools.pyw")]:
            path = var.get()
            if not os.path.isfile(path):
                # try current directory
                alt = os.path.join(os.getcwd(), name)
                if os.path.isfile(alt):
                    var.set(alt)
                    self._log(f"Auto-detected {alt}")

    def _create_widgets(self) -> None:
        main_frame = tk.Frame(self, bg="#1e1e2e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Notebook for two build configurations
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=5)

        # Tab 1: Build Game
        game_frame = ttk.Frame(notebook)
        notebook.add(game_frame, text="Build Game")
        self._build_config_ui(game_frame, "game")

        # Tab 2: Build DevTools
        dev_frame = ttk.Frame(notebook)
        notebook.add(dev_frame, text="Build DevTools")
        self._build_config_ui(dev_frame, "dev")

        # Status and log area (shared)
        self.status_label = tk.Label(main_frame, text="Ready", bg="#1e1e2e", fg="#a6adc8")
        self.status_label.pack(anchor=tk.W, pady=5)

        if UI_AVAILABLE:
            self.log_text = TextDisplay(main_frame, content="")
        else:
            self.log_text = tk.Text(main_frame, wrap=tk.WORD, bg="#1e1e2e", fg="#cdd6f4", height=18)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)

    def _build_config_ui(self, parent, target: str) -> None:
        """Add UI controls for a build target (game or dev)."""
        # Script path
        row = 0
        tk.Label(parent, text="Main script:", bg="#1e1e2e", fg="#cdd6f4") \
            .grid(row=row, column=0, sticky=tk.W, pady=5)
        entry_var = self.game_script if target == "game" else self.dev_script
        entry = tk.Entry(parent, textvariable=entry_var, width=60,
                         bg="#313244", fg="#cdd6f4")
        entry.grid(row=row, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        btn_browse = ttk.Button(parent, text="Browse...",
                                command=lambda: self._browse_script(target))
        btn_browse.grid(row=row, column=2, padx=5)
        ToolTip(btn_browse, "Select the main Python script")

        # Output name
        row += 1
        tk.Label(parent, text="Executable name:", bg="#1e1e2e", fg="#cdd6f4") \
            .grid(row=row, column=0, sticky=tk.W, pady=5)
        out_var = self.game_output if target == "game" else self.dev_output
        out_entry = tk.Entry(parent, textvariable=out_var, width=30,
                             bg="#313244", fg="#cdd6f4")
        out_entry.grid(row=row, column=1, sticky=tk.W, padx=5)
        ToolTip(out_entry, "Name of the final executable (no extension)")

        # Icon
        row += 1
        tk.Label(parent, text="Icon file (.ico):", bg="#1e1e2e", fg="#cdd6f4") \
            .grid(row=row, column=0, sticky=tk.W, pady=5)
        icon_var = self.game_icon if target == "game" else self.dev_icon
        icon_entry = tk.Entry(parent, textvariable=icon_var, width=60,
                              bg="#313244", fg="#cdd6f4")
        icon_entry.grid(row=row, column=1, padx=5, sticky=tk.W+tk.E)
        btn_browse_icon = ttk.Button(parent, text="Browse...",
                                     command=lambda: self._browse_icon(target))
        btn_browse_icon.grid(row=row, column=2, padx=5)
        ToolTip(btn_browse_icon, "Optional: select an .ico file")

        # Options
        row += 1
        options_frame = tk.LabelFrame(parent, text="Build Options",
                                      bg="#313244", fg="#cdd6f4", padx=5, pady=5)
        options_frame.grid(row=row, column=0, columnspan=3, sticky=tk.W+tk.E, pady=10)

        console_var = self.game_console if target == "game" else self.dev_console
        cb_windowed = tk.Checkbutton(options_frame, text="Windowed mode (no console)",
                                     variable=console_var, onvalue=False, offvalue=True,
                                     bg="#313244", fg="#cdd6f4", selectcolor="#313244")
        cb_windowed.grid(row=0, column=0, sticky=tk.W)
        ToolTip(cb_windowed, "If checked, the executable will not open a terminal window")

        copy_var = self.game_copy_data if target == "game" else self.dev_copy_data
        cb_copy = tk.Checkbutton(options_frame, text="Copy 'data/' folder after build",
                                 variable=copy_var, bg="#313244", fg="#cdd6f4",
                                 selectcolor="#313244")
        cb_copy.grid(row=1, column=0, sticky=tk.W)
        ToolTip(cb_copy, "Automatically copy the data folder into the dist/ directory")

        clean_var = self.game_clean if target == "game" else self.dev_clean
        cb_clean = tk.Checkbutton(options_frame, text="Remove previous build/ and dist/ folders",
                                  variable=clean_var, bg="#313244", fg="#cdd6f4",
                                  selectcolor="#313244")
        cb_clean.grid(row=2, column=0, sticky=tk.W)
        ToolTip(cb_clean, "Start with a fresh build environment")

        # Build button
        row += 1
        btn = ttk.Button(parent, text=f"BUILD {target.upper()}",
                         command=lambda: self._start_build(target))
        btn.grid(row=row, column=0, columnspan=3, pady=15)
        if target == "game":
            self.build_btn_game = btn
        else:
            self.build_btn_dev = btn

        # Configure grid weights
        parent.columnconfigure(1, weight=1)

    def _browse_script(self, target: str) -> None:
        filename = filedialog.askopenfilename(title="Select main script",
                                              filetypes=[("Python files", "*.py *.pyw")])
        if filename:
            if target == "game":
                self.game_script.set(filename)
            else:
                self.dev_script.set(filename)
            self._log(f"Script set to: {filename}")

    def _browse_icon(self, target: str) -> None:
        filename = filedialog.askopenfilename(title="Select icon file (.ico)",
                                              filetypes=[("Icon files", "*.ico")])
        if filename:
            if target == "game":
                self.game_icon.set(filename)
            else:
                self.dev_icon.set(filename)
            self._log(f"Icon set to: {filename}")

    def _log(self, message: str) -> None:
        if UI_AVAILABLE and hasattr(self.log_text, 'append'):
            self.log_text.append(message + "\n")
        else:
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
        self.update_idletasks()

    def _check_pyinstaller_status(self) -> None:
        if not check_pyinstaller():
            self.status_label.config(text="PyInstaller not found. Click 'Install PyInstaller' first.",
                                     foreground="#f38ba8")
            self.install_btn = ttk.Button(self, text="Install PyInstaller",
                                          command=self._install_pyinstaller)
            self.install_btn.place(relx=0.5, rely=0.95, anchor=tk.CENTER)
            if self.build_btn_game:
                self.build_btn_game.config(state="disabled")
            if self.build_btn_dev:
                self.build_btn_dev.config(state="disabled")
        else:
            self.status_label.config(text="PyInstaller is ready.", foreground="#a6e3a1")
            if self.build_btn_game:
                self.build_btn_game.config(state="normal")
            if self.build_btn_dev:
                self.build_btn_dev.config(state="normal")

    def _install_pyinstaller(self) -> None:
        def install_thread():
            creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            proc = subprocess.Popen(
                [sys.executable, "-m", "pip", "install", "pyinstaller"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                creationflags=creationflags
            )
            output_lines = []
            for line in proc.stdout:
                output_lines.append(line)
                if progress_label.winfo_exists():
                    progress_label.config(text=line.strip()[:80])
                    progress_window.update()
            proc.wait()
            progress_window.destroy()
            if proc.returncode == 0:
                messagebox.showinfo("Success", "PyInstaller installed successfully.")
                self._check_pyinstaller_status()
            else:
                messagebox.showerror("Installation Failed",
                                     f"Could not install PyInstaller.\n\n{''.join(output_lines)[:500]}")
        progress_window = tk.Toplevel(self.main_root)
        progress_window.title("Installing PyInstaller")
        progress_window.geometry("500x100")
        progress_label = tk.Label(progress_window, text="Installing... please wait")
        progress_label.pack(pady=20)
        threading.Thread(target=install_thread, daemon=True).start()

    def _start_build(self, target: str) -> None:
        if not check_pyinstaller():
            messagebox.showerror("Missing Dependency", "PyInstaller is not installed.")
            return

        if target == "game":
            script = self.game_script.get().strip()
            output = self.game_output.get().strip()
            icon = self.game_icon.get().strip()
            console_mode = self.game_console.get()
            copy_data = self.game_copy_data.get()
            clean = self.game_clean.get()
        else:
            script = self.dev_script.get().strip()
            output = self.dev_output.get().strip()
            icon = self.dev_icon.get().strip()
            console_mode = self.dev_console.get()
            copy_data = self.dev_copy_data.get()
            clean = self.dev_clean.get()

        if not os.path.isfile(script):
            messagebox.showerror("Error", f"Main script not found:\n{script}")
            return
        if not output:
            messagebox.showerror("Error", "Please enter an executable name.")
            return

        if clean:
            for folder in ["build", "dist"]:
                if os.path.exists(folder):
                    try:
                        shutil.rmtree(folder)
                        self._log(f"Removed existing '{folder}/' folder.")
                    except Exception as e:
                        self._log(f"Warning: could not remove {folder}: {e}")

        cmd = ["pyinstaller", "--onefile", "--noconfirm"]
        if not console_mode:
            cmd.append("--windowed")
        if icon and os.path.isfile(icon):
            cmd.append(f"--icon={icon}")
        cmd.append(f"--name={output}")
        cmd.append(script)

        self._log(f"=== Building {target.upper()} ===")
        self._log(f"Command: {' '.join(cmd)}")
        self.status_label.config(text=f"Building {target}... please wait", foreground="#89b4fa")
        if target == "game" and self.build_btn_game:
            self.build_btn_game.config(state="disabled")
        elif target == "dev" and self.build_btn_dev:
            self.build_btn_dev.config(state="disabled")
        threading.Thread(target=self._run_build, args=(cmd, target, copy_data), daemon=True).start()

    def _run_build(self, cmd: List[str], target: str, copy_data: bool) -> None:
        try:
            startupinfo = None
            creationflags = 0
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0
                creationflags = subprocess.CREATE_NO_WINDOW

            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True, bufsize=1, startupinfo=startupinfo,
                                    creationflags=creationflags)
            for line in iter(proc.stdout.readline, ""):
                if line:
                    self._log(line.rstrip())
            proc.wait()
            if proc.returncode == 0:
                self._log(f"\n=== Build {target.upper()} completed successfully ===")
                self.status_label.config(text=f"Build {target} successful!", foreground="#a6e3a1")
                if copy_data and target == "game":
                    self._copy_data_folder()
                elif copy_data and target == "dev":
                    self._log("Note: DevTools does not require the data folder. Skipping copy.")
            else:
                self._log(f"\n=== Build failed with error code {proc.returncode} ===")
                self.status_label.config(text=f"Build {target} failed.", foreground="#f38ba8")
        except Exception as e:
            self._log(f"Exception during build: {e}")
            self.status_label.config(text="Build error occurred.", foreground="#f38ba8")
        finally:
            if target == "game" and self.build_btn_game:
                self.build_btn_game.config(state="normal")
            elif target == "dev" and self.build_btn_dev:
                self.build_btn_dev.config(state="normal")

    def _copy_data_folder(self) -> None:
        main_dir = os.path.dirname(self.game_script.get())
        source_data = os.path.join(main_dir, "data")
        if not os.path.isdir(source_data):
            self._log(f"Warning: data folder not found at '{source_data}'. Skipping copy.")
            return
        dest_dir = os.path.join(os.getcwd(), "dist")
        dest_data = os.path.join(dest_dir, "data")
        try:
            if os.path.exists(dest_data):
                shutil.rmtree(dest_data)
                self._log(f"Removed existing '{dest_data}'.")
            shutil.copytree(source_data, dest_data)
            self._log(f"Successfully copied 'data/' folder to '{dest_data}'.")
            self._log("Your game executable is ready in the 'dist' folder.")
        except Exception as e:
            self._log(f"Error copying data folder: {e}")


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
        actions_dir = pathlib.Path("data/actions")
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

        actions_dir = pathlib.Path("data/actions")
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
            theme = load_theme("data/ui/themes.json", logger=None)
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

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    app = DevToolsApp()
    app.run()