#!/usr/bin/env python3
"""
Audit GUI for Pursuit of Peace.
Runs the game engine without UI, randomly selects actions, and reports crashes.
Provides a Tkinter interface for controlling the audit and exporting results.
"""

import random
import sys
import threading
import queue
import traceback
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from datetime import datetime
from typing import Dict, Any, Optional, List

# Import game components (no UI)
from app.data_loader import DataLoader
from app.dungeon_manager import DungeonManager
from app.location_manager import LocationManager
from app.game_engine import GameEngine


class QueueLogger:
    """Logger that puts messages into a queue for GUI consumption."""
    def __init__(self, log_queue):
        self.log_queue = log_queue

    def _put(self, level, msg, context=None):
        self.log_queue.put({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "level": level,
            "message": msg,
            "context": context,
        })

    def info(self, msg, context=None):
        self._put("INFO", msg, context)
    def warn(self, msg, context=None):
        self._put("WARN", msg, context)
    def error(self, msg, context=None):
        self._put("ERROR", msg, context)
    def system(self, msg):
        self._put("SYSTEM", msg)
    def data(self, event, detail=None):
        # Optionally log data events
        # self._put("DATA", event, detail)
        pass


class AuditRunnerGUI:
    def __init__(self, max_steps: int, seed: Optional[int], log_queue):
        self.max_steps = max_steps
        self.seed = seed
        self.log_queue = log_queue
        self.logger = QueueLogger(log_queue)
        self.stop_flag = threading.Event()
        self.running = False
        self.crash_info = None

    def run(self):
        self.running = True
        self.stop_flag.clear()
        if self.seed is not None:
            random.seed(self.seed)
            self.logger.system(f"Random seed set to {self.seed}")
        self._init_game()
        self.history = []
        self.combat_active = False
        self.current_enemy = None

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
            self.log_queue.put({"progress": step})  # special message for progress bar

        self.running = False
        if not self.crash_info and not self.stop_flag.is_set():
            self.logger.system(f"Audit finished: {self.max_steps} steps without crash.")
        elif self.crash_info:
            self.logger.system("Audit terminated due to crash.")

    def _init_game(self):
        loader = DataLoader(logger=self.logger)
        dungeon_mgr = DungeonManager(loader, logger=self.logger)
        location_mgr = LocationManager(loader, dungeon_mgr, logger=self.logger)
        self.engine = GameEngine(loader, location_mgr, dungeon_mgr, logger=self.logger)
        # Ensure player state initialised (engine does it in __init__)
        self.step_count = 0

    def _do_one_step(self):
        if self.combat_active and self.current_enemy:
            self._do_combat_action()
        elif self.engine.dungeon_state is not None:
            self._do_dungeon_action()
        else:
            self._do_city_action()

    def _do_city_action(self):
        state = self.engine.get_view_state("city")
        actions = state.get("location", {}).get("actions", [])
        if not actions:
            actions = [{"id": "go_tavern"}]
        action = random.choice(actions)
        action_id = action["id"]
        self.history.append(f"city: {action_id}")
        changed, msg = self.engine.do_location_action(action_id)
        if msg:
            self.logger.info(msg)

    def _do_dungeon_action(self):
        state = self.engine.get_view_state("dungeon")
        actions = state.get("location", {}).get("actions", [])
        if not actions:
            actions = [{"id": "flee_dungeon"}]
        action = random.choice(actions)
        action_id = action["id"]
        self.history.append(f"dungeon: {action_id}")
        changed, msg, combat_state = self.engine.do_dungeon_action(action_id)
        if msg:
            self.logger.info(msg)
        if combat_state is not None:
            self.combat_active = True
            # Retrieve enemy from dungeon room
            room = self.engine._dungeon_mgr.get_current_room(self.engine.dungeon_state)
            if room and room.get("enemy"):
                self.current_enemy = room["enemy"]
            else:
                self.current_enemy = {"id": "unknown", "name": "Enemy", "hp": 10}

    def _do_combat_action(self):
        actions = [{"id": "attack"}, {"id": "flee"}]
        action = random.choice(actions)
        action_id = action["id"]
        self.history.append(f"combat: {action_id}")
        ended, msg, fled = self.engine.do_combat_action(action_id, self.current_enemy)
        if msg:
            self.logger.info(f"Combat: {msg}")
        if ended:
            self.combat_active = False
            self.current_enemy = None

    def get_crash_info(self):
        return self.crash_info

    def get_history(self):
        return self.history


class AuditGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pursuit of Peace - Audit Tool")
        self.root.geometry("900x700")
        self.root.configure(bg="#0d1b2a")

        self.audit_thread = None
        self.runner = None
        self.log_queue = queue.Queue()
        self.after_id = None

        self._build_ui()
        self._poll_queue()

    def _build_ui(self):
        # Control frame
        control_frame = tk.Frame(self.root, bg="#16213e", padx=10, pady=10)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        # Steps
        tk.Label(control_frame, text="Steps:", bg="#16213e", fg="#d4c9a8", font=("Courier", 10)).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.steps_var = tk.StringVar(value="1000")
        tk.Entry(control_frame, textvariable=self.steps_var, width=10, bg="#0d1b2a", fg="#d4c9a8", insertbackground="#d4c9a8").grid(row=0, column=1, padx=5)

        # Seed
        tk.Label(control_frame, text="Seed (optional):", bg="#16213e", fg="#d4c9a8", font=("Courier", 10)).grid(row=0, column=2, sticky=tk.W, padx=5)
        self.seed_var = tk.StringVar(value="")
        tk.Entry(control_frame, textvariable=self.seed_var, width=15, bg="#0d1b2a", fg="#d4c9a8", insertbackground="#d4c9a8").grid(row=0, column=3, padx=5)

        # Buttons
        self.run_btn = tk.Button(control_frame, text="Run Audit", command=self.start_audit, bg="#0f3460", fg="#d4c9a8", activebackground="#e94560", font=("Courier", 10, "bold"))
        self.run_btn.grid(row=0, column=4, padx=10)
        self.stop_btn = tk.Button(control_frame, text="Stop", command=self.stop_audit, bg="#0f3460", fg="#d4c9a8", activebackground="#e94560", font=("Courier", 10, "bold"), state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=5, padx=5)
        self.export_btn = tk.Button(control_frame, text="Export Log", command=self.export_log, bg="#0f3460", fg="#d4c9a8", activebackground="#e94560", font=("Courier", 10, "bold"))
        self.export_btn.grid(row=0, column=6, padx=5)

        # Progress bar
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(self.root, variable=self.progress_var, maximum=100, mode='determinate')
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)

        # Status label
        self.status_label = tk.Label(self.root, text="Ready", bg="#0d1b2a", fg="#7a8fa6", font=("Courier", 10))
        self.status_label.pack(anchor=tk.W, padx=10, pady=2)

        # Log display (scrolled text)
        self.log_display = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, bg="#1a1a2e", fg="#d4c9a8", font=("Courier", 10), height=25)
        self.log_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tag configuration for colors
        self.log_display.tag_config("INFO", foreground="#00ffcc")
        self.log_display.tag_config("WARN", foreground="#ffe600")
        self.log_display.tag_config("ERROR", foreground="#ff3333")
        self.log_display.tag_config("SYSTEM", foreground="#6a607a")
        self.log_display.tag_config("DATA", foreground="#aa66ff")

    def _poll_queue(self):
        """Process messages from the audit thread queue."""
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
                    # Log message
                    ts = msg.get("timestamp", "")
                    level = msg.get("level", "INFO")
                    text = msg.get("message", "")
                    context = msg.get("context")
                    line = f"[{ts}] [{level}]"
                    if context:
                        line += f" [{context}]"
                    line += f" {text}\n"
                    self.log_display.insert(tk.END, line, level)
                    self.log_display.see(tk.END)
        except queue.Empty:
            pass
        self.after_id = self.root.after(100, self._poll_queue)

    def start_audit(self):
        # Validate steps
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

        # Clear log and progress
        self.log_display.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.status_label.config(text="Running...")
        self.run_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.export_btn.config(state=tk.DISABLED)

        # Start audit in background thread
        self.runner = AuditRunnerGUI(max_steps=steps, seed=seed, log_queue=self.log_queue)
        self.audit_thread = threading.Thread(target=self.runner.run, daemon=True)
        self.audit_thread.start()

        # Monitor thread completion
        self._monitor_audit()

    def _monitor_audit(self):
        if self.audit_thread and self.audit_thread.is_alive():
            self.root.after(500, self._monitor_audit)
        else:
            # Audit finished
            self.run_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.export_btn.config(state=tk.NORMAL)
            if self.runner and self.runner.crash_info:
                self.status_label.config(text="Crash detected! See log for details.")
                # Optionally show crash dialog
                crash = self.runner.crash_info
                messagebox.showerror("Crash during audit",
                    f"Crash at step {crash['step']}\n{crash['exception']}\n\nFull details in log.")
            else:
                self.status_label.config(text="Audit completed.")

    def stop_audit(self):
        if self.runner:
            self.runner.stop_flag.set()
            self.status_label.config(text="Stopping...")
            self.stop_btn.config(state=tk.DISABLED)

    def export_log(self):
        """Save the current log content to a file."""
        if not self.log_display.get(1.0, tk.END).strip():
            messagebox.showinfo("No log", "Nothing to export.")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("Log files", "*.log")])
        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(self.log_display.get(1.0, tk.END))
                messagebox.showinfo("Export successful", f"Log saved to {filepath}")
            except Exception as e:
                messagebox.showerror("Export failed", str(e))

    def run(self):
        self.root.mainloop()
        if self.after_id:
            self.root.after_cancel(self.after_id)


if __name__ == "__main__":
    app = AuditGUI()
    app.run()