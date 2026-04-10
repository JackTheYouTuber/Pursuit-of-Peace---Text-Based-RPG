#!/usr/bin/env python3
"""
DevTools – Merged Utility for "Pursuit of Peace"

This application provides three essential development tools in one window:

1. Pycache Cleaner
   Recursively deletes all `__pycache__` folders inside a user‑selected directory.

2. Audit Tool
   Runs the game engine with random actions for a given number of steps,
   logs progress, detects crashes, and allows exporting the log.
   Requires the game's `app` modules to be importable.

3. Build Tool
   Checks for PyInstaller, installs it if missing, and builds a standalone
   executable (one‑file, optional console/windowed mode). It can also copy
   the `data/` folder next to the built executable.

All tools share a consistent dark theme and provide tooltips for better usability.
"""

import os
import sys
import shutil
import subprocess
import threading
import queue
import traceback
import random
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from datetime import datetime
from typing import Optional, Tuple, Dict, Any, List


# ----------------------------------------------------------------------
# Helper: Tooltip
# ----------------------------------------------------------------------
class ToolTip:
    """
    Create a simple tooltip that appears when hovering over a widget.

    Usage:
        ToolTip(widget, "Helpful text")
    """

    def __init__(self, widget: tk.Widget, text: str) -> None:
        """
        Attach a tooltip to the given widget.

        Args:
            widget: The Tkinter widget that will show the tooltip.
            text:   The tooltip text to display.
        """
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind('<Enter>', self.enter)
        widget.bind('<Leave>', self.leave)

    def enter(self, event=None) -> None:
        """Show the tooltip window near the widget."""
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
        """Destroy the tooltip window."""
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


# ----------------------------------------------------------------------
# Section 1: Pycache Cleaner
# ----------------------------------------------------------------------
class PycacheCleaner(tk.Frame):
    """
    A frame that allows the user to delete all __pycache__ folders
    recursively under a chosen directory.
    """

    def __init__(self, parent: tk.Widget) -> None:
        """
        Initialize the Pycache Cleaner UI.

        Args:
            parent: The parent widget (usually a ttk.Notebook tab).
        """
        super().__init__(parent, bg="#1e1e2e")
        self.path_var = tk.StringVar()
        self._build_ui()
        self.log("Ready. Select a directory and click 'Start Deletion'.")

    def _build_ui(self) -> None:
        """Create all widgets for this tool."""
        # Path selection row
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

        # Action buttons
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

        # Log area
        self.log_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=80, height=25,
                                                  bg="#1e1e2e", fg="#cdd6f4",
                                                  insertbackground="#cdd6f4")
        self.log_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def browse_folder(self) -> None:
        """Open a directory chooser and set the target path."""
        folder = filedialog.askdirectory(title="Select Directory to Scan")
        if folder:
            self.path_var.set(folder)

    def log(self, message: str) -> None:
        """Insert a message into the log area and scroll to the end."""
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.update_idletasks()

    def clear_log(self) -> None:
        """Clear all text from the log area."""
        self.log_area.delete(1.0, tk.END)

    def _delete_pycache_folders(self, root_path: str) -> Tuple[int, int]:
        """
        Walk through root_path and delete every '__pycache__' directory.

        Returns:
            Tuple (deleted_count, error_count)
        """
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
        """Start the deletion process after validation and confirmation."""
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
# Section 2: Audit Tool
# ----------------------------------------------------------------------
# Attempt to import the game engine components; handle gracefully if missing.
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
    """
    Logger that puts messages into a queue for the GUI to consume.
    Mimics the logging interface expected by the game engine.
    """

    def __init__(self, log_queue: queue.Queue) -> None:
        """
        Args:
            log_queue: Queue to which log messages will be sent.
        """
        self.log_queue = log_queue

    def _put(self, level: str, msg: str, context: Any = None) -> None:
        """Internal method to queue a log message."""
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
        # Not used in this audit tool, but required by the engine's logger interface.
        pass


class AuditRunner:
    """
    Runs the game engine in a background thread, performing random actions
    for a given number of steps. Reports crashes and logs progress.
    """

    def __init__(self, max_steps: int, seed: Optional[int], log_queue: queue.Queue) -> None:
        """
        Args:
            max_steps: Number of random actions to simulate.
            seed:      Optional random seed for reproducibility.
            log_queue: Queue to send log messages and progress updates.
        """
        self.max_steps = max_steps
        self.seed = seed
        self.log_queue = log_queue
        self.logger = QueueLogger(log_queue)
        self.stop_flag = threading.Event()
        self.running = False
        self.crash_info: Optional[Dict[str, Any]] = None

    def run(self) -> None:
        """Start the audit. This method is intended to run in a separate thread."""
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
            self.log_queue.put({"progress": step})

        self.running = False
        if not self.crash_info and not self.stop_flag.is_set():
            self.logger.system(f"Audit finished: {self.max_steps} steps without crash.")
        elif self.crash_info:
            self.logger.system("Audit terminated due to crash.")

    def _init_game(self) -> None:
        """Instantiate the game engine and its dependencies."""
        loader = DataLoader(logger=self.logger)
        dungeon_mgr = DungeonManager(loader, logger=self.logger)
        location_mgr = LocationManager(loader, dungeon_mgr, logger=self.logger)
        self.engine = GameEngine(loader, location_mgr, dungeon_mgr, logger=self.logger)

    def _do_one_step(self) -> None:
        """Perform one random action based on the current game state."""
        if self.combat_active and self.current_enemy:
            self._do_combat_action()
        elif self.engine.dungeon_state is not None:
            self._do_dungeon_action()
        else:
            self._do_city_action()

    def _do_city_action(self) -> None:
        """Choose a random city action and execute it."""
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
        """Choose a random dungeon action and execute it."""
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
        """Choose a random combat action (attack or flee)."""
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
    """
    GUI for the Audit Tool. Provides controls to start/stop an audit,
    displays progress, and shows coloured log output.
    """

    def __init__(self, parent: tk.Widget) -> None:
        """
        Args:
            parent: The parent widget (usually a ttk.Notebook tab).
        """
        super().__init__(parent, bg="#1e1e2e")
        self.parent = parent
        self.audit_thread: Optional[threading.Thread] = None
        self.runner: Optional[AuditRunner] = None
        self.log_queue = queue.Queue()
        self.after_id: Optional[str] = None
        self._build_ui()
        self._poll_queue()

    def _build_ui(self) -> None:
        """Create all widgets for the audit tool."""
        # Control row
        control_frame = tk.Frame(self, bg="#1e1e2e")
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(control_frame, text="Steps:", bg="#1e1e2e", fg="#cdd6f4") \
            .grid(row=0, column=0, sticky=tk.W, padx=5)
        self.steps_var = tk.StringVar(value="1000")
        steps_entry = tk.Entry(control_frame, textvariable=self.steps_var,
                               width=10, bg="#313244", fg="#cdd6f4",
                               insertbackground="#cdd6f4")
        steps_entry.grid(row=0, column=1, padx=5)
        ToolTip(steps_entry, "Number of random actions to simulate")

        tk.Label(control_frame, text="Seed (optional):", bg="#1e1e2e", fg="#cdd6f4") \
            .grid(row=0, column=2, sticky=tk.W, padx=5)
        self.seed_var = tk.StringVar(value="")
        seed_entry = tk.Entry(control_frame, textvariable=self.seed_var,
                              width=15, bg="#313244", fg="#cdd6f4",
                              insertbackground="#cdd6f4")
        seed_entry.grid(row=0, column=3, padx=5)
        ToolTip(seed_entry, "Fixed random seed for reproducible runs")

        self.run_btn = ttk.Button(control_frame, text="Run Audit", command=self.start_audit)
        self.run_btn.grid(row=0, column=4, padx=10)
        ToolTip(self.run_btn, "Start the audit process")

        self.stop_btn = ttk.Button(control_frame, text="Stop", command=self.stop_audit,
                                   state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=5, padx=5)
        ToolTip(self.stop_btn, "Stop the currently running audit")

        self.export_btn = ttk.Button(control_frame, text="Export Log", command=self.export_log)
        self.export_btn.grid(row=0, column=6, padx=5)
        ToolTip(self.export_btn, "Save the log to a text file")

        # Progress bar
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(self, variable=self.progress_var,
                                            maximum=100, mode='determinate')
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)

        # Status label
        self.status_label = tk.Label(self, text="Ready", bg="#1e1e2e", fg="#a6adc8")
        self.status_label.pack(anchor=tk.W, padx=10, pady=2)

        # Log display
        self.log_display = scrolledtext.ScrolledText(self, wrap=tk.WORD, bg="#1e1e2e",
                                                     fg="#cdd6f4", font=("Consolas", 9),
                                                     height=25)
        self.log_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Colour tags for log levels
        self.log_display.tag_config("INFO", foreground="#89b4fa")
        self.log_display.tag_config("WARN", foreground="#f9e2af")
        self.log_display.tag_config("ERROR", foreground="#f38ba8")
        self.log_display.tag_config("SYSTEM", foreground="#cba6f7")

        if not GAME_MODULES_AVAILABLE:
            self.log_display.insert(tk.END,
                                    f"WARNING: Game modules not found. Audit will fail.\n"
                                    f"{GAME_IMPORT_ERROR}\n", "ERROR")

    def _poll_queue(self) -> None:
        """
        Periodically check the log queue and update the GUI.
        This method is called repeatedly via `after()`.
        """
        try:
            while True:
                msg = self.log_queue.get_nowait()
                if "progress" in msg:
                    step = msg["progress"]
                    total = int(self.steps_var.get()) if self.steps_var.get().isdigit() else 1000
                    percent = int((step / total) * 100)
                    self.progress_var.set(percent)
                    self.status_label.config(text=f"Step {step} / {total}")
                else:
                    ts = msg.get("timestamp", "")
                    level = msg.get("level", "INFO")
                    text = msg.get("message", "")
                    line = f"[{ts}] [{level}] {text}\n"
                    self.log_display.insert(tk.END, line, level)
                    self.log_display.see(tk.END)
        except queue.Empty:
            pass
        self.after_id = self.after(100, self._poll_queue)

    def start_audit(self) -> None:
        """Validate inputs and start the audit in a background thread."""
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

        # Clear previous log and reset UI
        self.log_display.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.status_label.config(text="Running...")
        self.run_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.export_btn.config(state=tk.DISABLED)

        self.runner = AuditRunner(max_steps=steps, seed=seed, log_queue=self.log_queue)
        self.audit_thread = threading.Thread(target=self.runner.run, daemon=True)
        self.audit_thread.start()
        self._monitor_audit()

    def _monitor_audit(self) -> None:
        """Check if the audit thread is still alive; re-enable UI when finished."""
        if self.audit_thread and self.audit_thread.is_alive():
            self.after(500, self._monitor_audit)
        else:
            self.run_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.export_btn.config(state=tk.NORMAL)
            if self.runner and self.runner.crash_info:
                self.status_label.config(text="Crash detected! See log.")
                crash = self.runner.crash_info
                messagebox.showerror("Crash during audit",
                                     f"Crash at step {crash.get('step', '?')}\n"
                                     f"{crash.get('exception', '')}\n\nFull details in log.")
            else:
                self.status_label.config(text="Audit completed.")

    def stop_audit(self) -> None:
        """Signal the audit runner to stop."""
        if self.runner:
            self.runner.stop_flag.set()
            self.status_label.config(text="Stopping...")
            self.stop_btn.config(state=tk.DISABLED)

    def export_log(self) -> None:
        """Save the current log content to a text file."""
        if not self.log_display.get(1.0, tk.END).strip():
            messagebox.showinfo("No log", "Nothing to export.")
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Log files", "*.log")]
        )
        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(self.log_display.get(1.0, tk.END))
                messagebox.showinfo("Export successful", f"Log saved to {filepath}")
            except Exception as e:
                messagebox.showerror("Export failed", str(e))


# ----------------------------------------------------------------------
# Section 3: Build Tool
# ----------------------------------------------------------------------
def check_pyinstaller() -> bool:
    """
    Check whether PyInstaller is available on the system.

    Returns:
        True if `pyinstaller --version` runs successfully, else False.
    """
    try:
        subprocess.run(["pyinstaller", "--version"],
                       capture_output=True, check=True,
                       creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


class BuildTool(tk.Frame):
    """
    GUI for building the game into a standalone executable using PyInstaller.
    """

    def __init__(self, parent: tk.Widget, main_root: tk.Tk) -> None:
        """
        Args:
            parent:    The parent widget (usually a ttk.Notebook tab).
            main_root: The root Tk window (used for popup dialogs).
        """
        super().__init__(parent, bg="#1e1e2e")
        self.parent = parent
        self.main_root = main_root

        # User options
        default_script = os.path.abspath("main.pyw")
        self.main_script = tk.StringVar(value=default_script)
        self.output_name = tk.StringVar(value="PursuitOfPeace")
        self.icon_path = tk.StringVar(value="")
        self.console_mode = tk.BooleanVar(value=False)   # False = windowed
        self.copy_data = tk.BooleanVar(value=True)
        self.clean_before = tk.BooleanVar(value=True)

        self.build_btn: Optional[ttk.Button] = None
        self.status_label: Optional[tk.Label] = None
        self.log_text: Optional[scrolledtext.ScrolledText] = None
        self.install_btn: Optional[ttk.Button] = None

        self._create_widgets()
        self._check_pyinstaller_status()
        # Automatically search for main script if default not found
        self._ensure_main_script_exists()

    def _ensure_main_script_exists(self) -> None:
        """If the current main script path is invalid, try to find it or ask the user."""
        current = self.main_script.get().strip()
        if os.path.isfile(current):
            return  # already valid

        # Try to find main.pyw or main.py in current directory or one level up
        search_dirs = [os.getcwd(), os.path.dirname(os.getcwd())]
        found = None
        for d in search_dirs:
            for candidate in ["main.pyw", "main.py"]:
                path = os.path.join(d, candidate)
                if os.path.isfile(path):
                    found = path
                    break
            if found:
                break

        if found:
            self.main_script.set(found)
            self._log(f"Auto‑detected main script: {found}")
        else:
            # Ask the user to locate it
            self._log("Main script not found automatically. Please locate it manually.")
            self._prompt_for_main_script()

    def _prompt_for_main_script(self) -> None:
        """Show a dialog asking the user to select the main script."""
        answer = messagebox.askyesno(
            "Main Script Missing",
            "Could not find 'main.pyw' or 'main.py' in the current or parent directory.\n\n"
            "Do you want to locate it manually now?\n"
            "If you click No, you can browse later using the 'Browse...' button."
        )
        if answer:
            self._browse_main()

    def _create_widgets(self) -> None:
        """Create all widgets for the build tool."""
        main_frame = tk.Frame(self, bg="#1e1e2e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Row 0: Main script
        row = 0
        tk.Label(main_frame, text="Main script:", bg="#1e1e2e", fg="#cdd6f4") \
            .grid(row=row, column=0, sticky=tk.W, pady=5)
        self.script_entry = tk.Entry(main_frame, textvariable=self.main_script,
                                     width=60, bg="#313244", fg="#cdd6f4",
                                     insertbackground="#cdd6f4")
        self.script_entry.grid(row=row, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        btn_browse_script = ttk.Button(main_frame, text="Browse...", command=self._browse_main)
        btn_browse_script.grid(row=row, column=2, padx=5, pady=5)
        ToolTip(btn_browse_script, "Select your main game script (main.pyw or main.py)")

        # Row 1: Output name
        row += 1
        tk.Label(main_frame, text="Executable name:", bg="#1e1e2e", fg="#cdd6f4") \
            .grid(row=row, column=0, sticky=tk.W, pady=5)
        self.output_entry = tk.Entry(main_frame, textvariable=self.output_name,
                                     width=30, bg="#313244", fg="#cdd6f4")
        self.output_entry.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        tk.Label(main_frame, text="(.exe added on Windows)", bg="#1e1e2e", fg="#a6adc8") \
            .grid(row=row, column=2, sticky=tk.W, padx=5)
        ToolTip(self.output_entry, "Name of the final executable file")

        # Row 2: Icon file
        row += 1
        tk.Label(main_frame, text="Icon file (.ico):", bg="#1e1e2e", fg="#cdd6f4") \
            .grid(row=row, column=0, sticky=tk.W, pady=5)
        self.icon_entry = tk.Entry(main_frame, textvariable=self.icon_path,
                                   width=60, bg="#313244", fg="#cdd6f4")
        self.icon_entry.grid(row=row, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        btn_browse_icon = ttk.Button(main_frame, text="Browse...", command=self._browse_icon)
        btn_browse_icon.grid(row=row, column=2, padx=5, pady=5)
        ToolTip(btn_browse_icon, "Optional: select an .ico file for the executable")

        # Row 3: Build options frame
        row += 1
        options_frame = tk.LabelFrame(main_frame, text="Build Options",
                                      bg="#313244", fg="#cdd6f4", padx=5, pady=5)
        options_frame.grid(row=row, column=0, columnspan=3, sticky=tk.W+tk.E, pady=10)

        # One-file is always enabled and not user‑changeable.
        tk.Checkbutton(options_frame, text="One-file executable (--onefile)",
                       state="disabled", bg="#313244", fg="#a6adc8",
                       selectcolor="#313244").grid(row=0, column=0, sticky=tk.W)

        self.windowed_check = tk.Checkbutton(options_frame,
                                             text="Windowed mode (no console) (--windowed)",
                                             variable=self.console_mode,
                                             onvalue=False, offvalue=True,
                                             bg="#313244", fg="#cdd6f4", selectcolor="#313244")
        self.windowed_check.grid(row=0, column=1, sticky=tk.W, padx=20)
        ToolTip(self.windowed_check, "If checked, the game will run without a terminal window")

        self.copy_check = tk.Checkbutton(options_frame,
                                         text="Copy 'data/' folder next to executable after build",
                                         variable=self.copy_data,
                                         bg="#313244", fg="#cdd6f4", selectcolor="#313244")
        self.copy_check.grid(row=1, column=0, sticky=tk.W)
        ToolTip(self.copy_check, "Automatically copy the data folder into the dist/ directory")

        self.clean_check = tk.Checkbutton(options_frame,
                                          text="Remove previous 'build/' and 'dist/' folders before building",
                                          variable=self.clean_before,
                                          bg="#313244", fg="#cdd6f4", selectcolor="#313244")
        self.clean_check.grid(row=1, column=1, sticky=tk.W, padx=20)
        ToolTip(self.clean_check, "Start with a fresh build environment")

        # Row 4: Build button
        row += 1
        self.build_btn = ttk.Button(main_frame, text="BUILD GAME",
                                    command=self._start_build, width=20)
        self.build_btn.grid(row=row, column=0, columnspan=3, pady=15)
        ToolTip(self.build_btn, "Start building the game executable")

        # Row 5: Status label
        row += 1
        self.status_label = tk.Label(main_frame, text="Ready", bg="#1e1e2e", fg="#a6adc8")
        self.status_label.grid(row=row, column=0, columnspan=3, sticky=tk.W)

        # Row 6 & 7: Build output log
        row += 1
        tk.Label(main_frame, text="Build Output:", bg="#1e1e2e", fg="#cdd6f4") \
            .grid(row=row, column=0, sticky=tk.W, pady=(10, 0))
        row += 1
        self.log_text = scrolledtext.ScrolledText(main_frame, height=18, width=90,
                                                  wrap=tk.WORD, bg="#1e1e2e",
                                                  fg="#cdd6f4", insertbackground="#cdd6f4")
        self.log_text.grid(row=row, column=0, columnspan=3, pady=5,
                           sticky=tk.W+tk.E+tk.N+tk.S)

        # Configure grid weights for resizing
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(row, weight=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def _check_pyinstaller_status(self) -> None:
        """Update UI based on whether PyInstaller is installed."""
        if not check_pyinstaller():
            self.status_label.config(text="PyInstaller not found. Click 'Install PyInstaller' first.",
                                     foreground="#f38ba8")
            self.install_btn = ttk.Button(self, text="Install PyInstaller",
                                          command=self._install_pyinstaller)
            self.install_btn.place(relx=0.5, rely=0.9, anchor=tk.CENTER)
            self.build_btn.config(state="disabled")
        else:
            self.status_label.config(text="PyInstaller is ready.", foreground="#a6e3a1")
            self.build_btn.config(state="normal")

    def _install_pyinstaller(self) -> None:
        """Install PyInstaller via pip in a background thread, showing a progress popup."""
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
                messagebox.showinfo("Success",
                                    "PyInstaller installed successfully.\nYou can now build the game.")
                self._check_pyinstaller_status()
            else:
                messagebox.showerror("Installation Failed",
                                     f"Could not install PyInstaller.\n\n{''.join(output_lines)[:500]}")
            self.build_btn.config(state="normal")

        progress_window = tk.Toplevel(self.main_root)
        progress_window.title("Installing PyInstaller")
        progress_window.geometry("500x100")
        progress_label = tk.Label(progress_window, text="Installing... please wait")
        progress_label.pack(pady=20)
        tk.Label(progress_window, text="This may take a minute.").pack()
        self.build_btn.config(state="disabled")
        threading.Thread(target=install_thread, daemon=True).start()

    def _browse_main(self) -> None:
        """Open a file dialog to select the main script."""
        filename = filedialog.askopenfilename(title="Select main script",
                                              filetypes=[("Python files", "*.py *.pyw")])
        if filename:
            self.main_script.set(filename)
            self._log(f"Main script set to: {filename}")

    def _browse_icon(self) -> None:
        """Open a file dialog to select an icon file."""
        filename = filedialog.askopenfilename(title="Select icon file (.ico)",
                                              filetypes=[("Icon files", "*.ico")])
        if filename:
            self.icon_path.set(filename)
            self._log(f"Icon set to: {filename}")

    def _log(self, message: str) -> None:
        """Append a message to the build output log."""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.update_idletasks()

    def _start_build(self) -> None:
        """Validate options and start the PyInstaller build in a background thread."""
        if not check_pyinstaller():
            messagebox.showerror("Missing Dependency",
                                 "PyInstaller is not installed.\nClick 'Install PyInstaller' first.")
            return

        main_script = self.main_script.get().strip()
        if not os.path.isfile(main_script):
            error_msg = f"Main script not found:\n{main_script}\n\nPlease select a valid script using 'Browse...'."
            messagebox.showerror("Error", error_msg)
            self._log(error_msg)
            return

        output_name = self.output_name.get().strip()
        if not output_name:
            messagebox.showerror("Error", "Please enter an executable name.")
            return

        if self.clean_before.get():
            for folder in ["build", "dist"]:
                if os.path.exists(folder):
                    try:
                        shutil.rmtree(folder)
                        self._log(f"Removed existing '{folder}/' folder.")
                    except Exception as e:
                        self._log(f"Warning: could not remove {folder}: {e}")

        cmd = ["pyinstaller", "--onefile", "--noconfirm"]
        if not self.console_mode.get():
            cmd.append("--windowed")
        icon = self.icon_path.get().strip()
        if icon and os.path.isfile(icon):
            cmd.append(f"--icon={icon}")
        cmd.append(f"--name={output_name}")
        cmd.append(main_script)

        self._log("=== Starting build ===")
        self._log(f"Command: {' '.join(cmd)}")
        self.status_label.config(text="Building... please wait", foreground="#89b4fa")
        self.build_btn.config(state="disabled")
        threading.Thread(target=self._run_build, args=(cmd,), daemon=True).start()

    def _run_build(self, cmd: List[str]) -> None:
        """
        Execute PyInstaller and capture its output.

        Args:
            cmd: The PyInstaller command as a list of strings.
        """
        try:
            # Hide the console window completely on Windows.
            startupinfo = None
            creationflags = 0
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0  # SW_HIDE
                creationflags = subprocess.CREATE_NO_WINDOW

            proc = subprocess.Popen(cmd,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    text=True,
                                    bufsize=1,
                                    startupinfo=startupinfo,
                                    creationflags=creationflags)
            for line in iter(proc.stdout.readline, ""):
                if line:
                    self._log(line.rstrip())
            proc.wait()
            if proc.returncode == 0:
                self._log("\n=== Build completed successfully ===")
                self.status_label.config(text="Build successful!", foreground="#a6e3a1")
                if self.copy_data.get():
                    self._copy_data_folder()
            else:
                self._log(f"\n=== Build failed with error code {proc.returncode} ===")
                self.status_label.config(text="Build failed. See output above.", foreground="#f38ba8")
        except Exception as e:
            self._log(f"Exception during build: {e}")
            self.status_label.config(text="Build error occurred.", foreground="#f38ba8")
        finally:
            self.build_btn.config(state="normal")

    def _copy_data_folder(self) -> None:
        """Copy the 'data/' folder from the main script's directory to the 'dist/' folder."""
        main_dir = os.path.dirname(self.main_script.get())
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
# Main Application
# ----------------------------------------------------------------------
class DevToolsApp:
    """Main application window containing a notebook with the three tools."""

    def __init__(self) -> None:
        """Set up the root window, apply theme, and create tabs."""
        self.root = tk.Tk()
        self.root.title("DevTools – Pursuit of Peace")
        self.root.geometry("1000x750")
        self.root.configure(bg="#1e1e2e")

        # Configure ttk styles for a consistent dark look
        self.style = ttk.Style()
        if 'clam' in self.style.theme_names():
            self.style.theme_use('clam')
        self.style.configure("TFrame", background="#1e1e2e")
        self.style.configure("TLabel", background="#1e1e2e", foreground="#cdd6f4")
        self.style.configure("TButton", background="#45475a", foreground="#cdd6f4")
        self.style.map("TButton", background=[("active", "#89b4fa")])
        self.style.configure("TEntry", fieldbackground="#313244", foreground="#cdd6f4")
        self.style.configure("TProgressbar", background="#89b4fa")

        # Notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab 1: Pycache Cleaner
        self.pycache_frame = PycacheCleaner(self.notebook)
        self.notebook.add(self.pycache_frame, text="Pycache Cleaner")

        # Tab 2: Audit Tool
        self.audit_frame = AuditToolFrame(self.notebook)
        self.notebook.add(self.audit_frame, text="Audit Tool")

        # Tab 3: Build Tool (pass the main root for popups)
        self.build_frame = BuildTool(self.notebook, self.root)
        self.notebook.add(self.build_frame, text="Build Tool")

    def run(self) -> None:
        """Start the Tkinter main loop."""
        self.root.mainloop()


if __name__ == "__main__":
    app = DevToolsApp()
    app.run()