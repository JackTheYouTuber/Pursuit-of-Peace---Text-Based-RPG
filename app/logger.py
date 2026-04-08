import os
import queue
import shutil
import subprocess
import sys
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk


# ---------------------------------------------------------------------------
# Colour palette (Section 5 — Visual Style)
# ---------------------------------------------------------------------------
_C = {
    "bg_void":   "#030008",
    "panel":     "#0f0a1e",
    "card":      "#150d28",
    "text":      "#c0b8d4",
    "muted":     "#6a607a",
    "accent":    "#00ffcc",
    "error":     "#ff3333",
    "warn":      "#ffe600",
    "system":    "#6a607a",
    "info":      "#00ffcc",
    "loot":      "#aa66ff",
    "movement":  "#00ffcc",
    "stat":      "#3388ff",
    "sep":       "#006655",
}

_FONT_BODY    = ("Courier New", 10)
_FONT_HEADING = ("Courier New", 14, "bold")
_FONT_BTN     = ("Courier New", 10)


# ---------------------------------------------------------------------------
# GameLogger
# ---------------------------------------------------------------------------

class GameLogger:
    """
    Centralised logging and monitoring system for the text RPG.

    Architecture:
    - All log calls push entries to a queue.Queue.
    - When the monitor window exists the Tkinter main thread polls every 80ms.
    - Entries are written to the session file immediately, before queuing.
    - The monitor window is a tk.Toplevel opened on demand.
    """

    def __init__(self, root=None):
        self._root = root
        self._q = queue.Queue()
        self._monitor = None
        self._entry_count = 0
        self._session_file = None
        self._session_path = ""

        # In-memory buffers for replay when monitor opens
        self._buf_system = []
        self._buf_events = []
        self._buf_errors = []

        # Tab widget dicts (populated in _build_monitor)
        self._tab_system = {}
        self._tab_events = {}
        self._tab_errors = {}
        self._tab_session = {}

        self._open_session_file()

        if self._root:
            self._start_poll()

    # ------------------------------------------------------------------
    # set_root: inject root after construction if needed
    # ------------------------------------------------------------------

    def set_root(self, root):
        if self._root is None:
            self._root = root
            self._start_poll()

    # ------------------------------------------------------------------
    # Public Logger API
    # ------------------------------------------------------------------

    def info(self, message, context=None):
        self._log("INFO", message, context)

    def warn(self, message, context=None):
        self._log("WARN", message, context)

    def error(self, message, context=None):
        self._log("ERROR", message, context)

    def system(self, message):
        self._log("SYSTEM", message)

    def data(self, event, detail=None):
        self._log("DATA", event, detail=detail)

    def open_monitor(self):
        """Open the monitor window; raise if already open."""
        if self._monitor is not None:
            try:
                if self._monitor.winfo_exists():
                    self._monitor.lift()
                    return
            except Exception:
                pass
        if self._root is None:
            return
        self._build_monitor()
        self._flush_buffers()

    def export_all(self, directory):
        """Export all four tabs to directory with a timestamp prefix."""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            self._write_export(
                os.path.join(directory, f"{ts}_system.txt"),
                self._buf_system, "system",
            )
            self._write_export(
                os.path.join(directory, f"{ts}_game_events.txt"),
                self._buf_events, "events",
            )
            self._write_export(
                os.path.join(directory, f"{ts}_errors.txt"),
                self._buf_errors, "errors",
            )
            dst = os.path.join(directory, f"{ts}_session_copy.log")
            shutil.copy2(self._session_path, dst)
            self.system(f"Exported to: {directory}")
        except Exception as ex:
            self.error(f"Export failed: {ex}")
            messagebox.showerror("Export Failed", str(ex))

    def shutdown(self):
        """Close session file cleanly. Call on application exit."""
        self.system("[STOP] Application shut down")
        if self._session_file:
            try:
                self._session_file.close()
            except Exception:
                pass
            self._session_file = None

    # ------------------------------------------------------------------
    # Session file
    # ------------------------------------------------------------------

    def _open_session_file(self):
        os.makedirs("logs", exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._session_path = os.path.join("logs", f"session_{ts}.log")
        try:
            self._session_file = open(self._session_path, "a", encoding="utf-8")
        except OSError:
            self._session_file = None

    def _write_to_session(self, entry):
        if not self._session_file:
            return
        ts    = entry["timestamp"]
        level = entry["level"]
        ctx   = entry.get("context")
        msg   = entry["message"]
        if ctx:
            line = f"[{ts}] [{level}] [{ctx}] {msg}\n"
        else:
            line = f"[{ts}] [{level}] {msg}\n"
        try:
            self._session_file.write(line)
            self._session_file.flush()
        except OSError:
            pass

    # ------------------------------------------------------------------
    # Core log dispatcher
    # ------------------------------------------------------------------

    def _log(self, level, message, context=None, detail=None):
        ts = datetime.now().strftime("%H:%M:%S")
        entry = {
            "timestamp": ts,
            "level":     level,
            "message":   message,
            "context":   context,
            "detail":    detail,
        }
        self._entry_count += 1
        self._write_to_session(entry)

        if level == "DATA":
            self._buf_events.append(entry)
        else:
            self._buf_system.append(entry)
            if level in ("WARN", "ERROR"):
                self._buf_errors.append(entry)

        self._q.put(entry)

    # ------------------------------------------------------------------
    # Tkinter poll loop
    # ------------------------------------------------------------------

    def _start_poll(self):
        self._root.after(80, self._poll_queue)

    def _poll_queue(self):
        try:
            while True:
                entry = self._q.get_nowait()
                if self._monitor is not None:
                    try:
                        if self._monitor.winfo_exists():
                            self._render_entry(entry)
                    except Exception:
                        pass
        except queue.Empty:
            pass
        if self._root:
            self._root.after(80, self._poll_queue)

    # ------------------------------------------------------------------
    # Monitor window construction
    # ------------------------------------------------------------------

    def _build_monitor(self):
        win = tk.Toplevel(self._root)
        win.title("Grimveil Monitor")
        win.geometry("900x580")
        win.configure(bg=_C["bg_void"])
        win.protocol("WM_DELETE_WINDOW", win.withdraw)
        self._monitor = win

        tk.Label(
            win,
            text="GRIMVEIL  //  LOG MONITOR",
            font=_FONT_HEADING,
            bg=_C["bg_void"],
            fg=_C["accent"],
        ).pack(anchor="w", padx=12, pady=(8, 2))

        _sep(win).pack(fill="x", padx=8, pady=2)

        style = ttk.Style(win)
        style.theme_use("default")
        style.configure("TNotebook", background=_C["panel"], borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background=_C["card"],
            foreground=_C["text"],
            font=_FONT_BODY,
            padding=[8, 4],
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", _C["panel"])],
            foreground=[("selected", _C["accent"])],
        )

        nb = ttk.Notebook(win)
        nb.pack(fill="both", expand=True, padx=8, pady=4)

        self._tab_system  = self._build_tab_system(nb)
        self._tab_events  = self._build_tab_events(nb)
        self._tab_errors  = self._build_tab_errors(nb)
        self._tab_session = self._build_tab_session(nb, win)

    # ---- Tab 1: System Log -----------------------------------------------

    def _build_tab_system(self, nb):
        frame = tk.Frame(nb, bg=_C["panel"])
        nb.add(frame, text="  System Log  ")

        toolbar = tk.Frame(frame, bg=_C["panel"])
        toolbar.pack(fill="x", padx=6, pady=4)

        auto_scroll = tk.BooleanVar(value=True)
        filter_var  = tk.StringVar(value="ALL")

        text_widget = _scrolled_text(frame)
        text_widget.tag_configure("INFO",   foreground=_C["info"])
        text_widget.tag_configure("WARN",   foreground=_C["warn"])
        text_widget.tag_configure("ERROR",  foreground=_C["error"])
        text_widget.tag_configure("SYSTEM", foreground=_C["system"])

        def apply_filter(fval="ALL"):
            filter_var.set(fval)
            text_widget.config(state="normal")
            text_widget.delete("1.0", "end")
            for e in self._buf_system:
                if fval == "ALL" or e["level"] == fval:
                    _insert_system_row(text_widget, e, auto_scroll)
            text_widget.config(state="disabled")

        for label, val in [
            ("ALL", "ALL"), ("INFO", "INFO"),
            ("WARN", "WARN"), ("ERROR", "ERROR"), ("SYS", "SYSTEM"),
        ]:
            _flat_btn(toolbar, label, lambda v=val: apply_filter(v)).pack(
                side="left", padx=2
            )

        tk.Checkbutton(
            toolbar, text="Auto-scroll", variable=auto_scroll,
            bg=_C["panel"], fg=_C["text"],
            selectcolor=_C["card"], activebackground=_C["panel"],
            font=_FONT_BTN,
        ).pack(side="left", padx=8)

        _flat_btn(
            toolbar, "EXPORT",
            lambda: self._export_tab(self._buf_system, "system"),
        ).pack(side="right", padx=2)
        _flat_btn(toolbar, "CLEAR", lambda: _clear_text(text_widget)).pack(
            side="right", padx=2
        )

        _sep(frame).pack(fill="x", padx=4, pady=2)

        return {
            "text":        text_widget,
            "auto_scroll": auto_scroll,
            "filter_var":  filter_var,
        }

    # ---- Tab 2: Game Events ----------------------------------------------

    def _build_tab_events(self, nb):
        frame = tk.Frame(nb, bg=_C["panel"])
        nb.add(frame, text="  Game Events  ")

        toolbar = tk.Frame(frame, bg=_C["panel"])
        toolbar.pack(fill="x", padx=6, pady=4)

        auto_scroll = tk.BooleanVar(value=True)

        text_widget = _scrolled_text(frame)
        text_widget.tag_configure("combat",   foreground="#ff4444")
        text_widget.tag_configure("loot",     foreground=_C["loot"])
        text_widget.tag_configure("movement", foreground=_C["movement"])
        text_widget.tag_configure("stat",     foreground=_C["stat"])
        text_widget.tag_configure("default",  foreground=_C["text"])

        tk.Checkbutton(
            toolbar, text="Auto-scroll", variable=auto_scroll,
            bg=_C["panel"], fg=_C["text"],
            selectcolor=_C["card"], activebackground=_C["panel"],
            font=_FONT_BTN,
        ).pack(side="left", padx=8)

        _flat_btn(
            toolbar, "EXPORT",
            lambda: self._export_tab(self._buf_events, "events"),
        ).pack(side="right", padx=2)
        _flat_btn(toolbar, "CLEAR", lambda: _clear_text(text_widget)).pack(
            side="right", padx=2
        )

        _sep(frame).pack(fill="x", padx=4, pady=2)

        return {"text": text_widget, "auto_scroll": auto_scroll}

    # ---- Tab 3: Errors ---------------------------------------------------

    def _build_tab_errors(self, nb):
        frame = tk.Frame(nb, bg=_C["panel"])
        nb.add(frame, text="  Errors  ")

        toolbar = tk.Frame(frame, bg=_C["panel"])
        toolbar.pack(fill="x", padx=6, pady=4)

        auto_scroll = tk.BooleanVar(value=True)
        filter_var  = tk.StringVar(value="ALL")

        text_widget = _scrolled_text(frame)
        text_widget.tag_configure("WARN",  foreground=_C["warn"])
        text_widget.tag_configure("ERROR", foreground=_C["error"])

        def apply_filter(fval="ALL"):
            filter_var.set(fval)
            text_widget.config(state="normal")
            text_widget.delete("1.0", "end")
            for e in self._buf_errors:
                if fval == "ALL" or e["level"] == fval:
                    _insert_system_row(text_widget, e, auto_scroll)
            text_widget.config(state="disabled")

        for label, val in [("ALL", "ALL"), ("WARN", "WARN"), ("ERROR", "ERROR")]:
            _flat_btn(toolbar, label, lambda v=val: apply_filter(v)).pack(
                side="left", padx=2
            )

        tk.Checkbutton(
            toolbar, text="Auto-scroll", variable=auto_scroll,
            bg=_C["panel"], fg=_C["text"],
            selectcolor=_C["card"], activebackground=_C["panel"],
            font=_FONT_BTN,
        ).pack(side="left", padx=8)

        _flat_btn(
            toolbar, "EXPORT",
            lambda: self._export_tab(self._buf_errors, "errors"),
        ).pack(side="right", padx=2)
        _flat_btn(toolbar, "CLEAR", lambda: _clear_text(text_widget)).pack(
            side="right", padx=2
        )

        _sep(frame).pack(fill="x", padx=4, pady=2)

        return {
            "text":        text_widget,
            "auto_scroll": auto_scroll,
            "filter_var":  filter_var,
        }

    # ---- Tab 4: Session File ---------------------------------------------

    def _build_tab_session(self, nb, win):
        frame = tk.Frame(nb, bg=_C["panel"])
        nb.add(frame, text="  Session File  ")

        info_frame = tk.Frame(frame, bg=_C["card"], padx=12, pady=12)
        info_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(
            info_frame,
            text=f"Path:  {self._session_path}",
            font=_FONT_BODY, bg=_C["card"], fg=_C["accent"], anchor="w",
        ).pack(fill="x")

        size_var  = tk.StringVar(value="Size: —")
        count_var = tk.StringVar(value=f"Entries: {self._entry_count}")

        tk.Label(
            info_frame, textvariable=size_var,
            font=_FONT_BODY, bg=_C["card"], fg=_C["text"], anchor="w",
        ).pack(fill="x", pady=2)

        tk.Label(
            info_frame, textvariable=count_var,
            font=_FONT_BODY, bg=_C["card"], fg=_C["text"], anchor="w",
        ).pack(fill="x")

        btn_frame = tk.Frame(frame, bg=_C["panel"])
        btn_frame.pack(anchor="w", padx=10, pady=6)

        _flat_btn(btn_frame, "OPEN LOG FOLDER", self._open_log_folder).pack(
            side="left", padx=4
        )
        _flat_btn(btn_frame, "EXPORT SESSION", self._export_session).pack(
            side="left", padx=4
        )

        tab = {"size_var": size_var, "count_var": count_var}

        def _refresh():
            try:
                sz = os.path.getsize(self._session_path)
                size_var.set(f"Size: {sz:,} bytes")
            except OSError:
                size_var.set("Size: unavailable")
            count_var.set(f"Entries: {self._entry_count}")
            try:
                if self._monitor and self._monitor.winfo_exists():
                    win.after(5000, _refresh)
            except Exception:
                pass

        win.after(5000, _refresh)
        tab["refresh"] = _refresh
        return tab

    # ------------------------------------------------------------------
    # Render and flush helpers
    # ------------------------------------------------------------------

    def _render_entry(self, entry):
        level = entry["level"]
        if level == "DATA":
            if self._tab_events.get("text"):
                _insert_event_row(
                    self._tab_events["text"],
                    entry,
                    self._tab_events["auto_scroll"],
                )
        else:
            if self._tab_system.get("text"):
                fv = self._tab_system.get("filter_var")
                current = fv.get() if fv else "ALL"
                if current == "ALL" or current == level:
                    _insert_system_row(
                        self._tab_system["text"],
                        entry,
                        self._tab_system["auto_scroll"],
                    )
            if level in ("WARN", "ERROR") and self._tab_errors.get("text"):
                efv = self._tab_errors.get("filter_var")
                ecurrent = efv.get() if efv else "ALL"
                if ecurrent == "ALL" or ecurrent == level:
                    _insert_system_row(
                        self._tab_errors["text"],
                        entry,
                        self._tab_errors["auto_scroll"],
                    )

    def _flush_buffers(self):
        """Replay buffered entries into newly built monitor widgets."""
        for e in self._buf_system:
            _insert_system_row(
                self._tab_system["text"], e, self._tab_system["auto_scroll"]
            )
        for e in self._buf_events:
            _insert_event_row(
                self._tab_events["text"], e, self._tab_events["auto_scroll"]
            )
        for e in self._buf_errors:
            _insert_system_row(
                self._tab_errors["text"], e, self._tab_errors["auto_scroll"]
            )

    # ------------------------------------------------------------------
    # Export helpers
    # ------------------------------------------------------------------

    def _export_tab(self, buf, mode):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            self._write_export(path, buf, mode)
            self.system(f"Exported to: {path}")
        except Exception as ex:
            self.error(f"Export failed: {ex}")
            messagebox.showerror("Export Failed", str(ex))

    def _write_export(self, path, buf, mode):
        with open(path, "w", encoding="utf-8") as fh:
            for e in buf:
                ts = e["timestamp"]
                if mode == "events":
                    detail = e.get("detail") or ""
                    fh.write(f"[{ts}] {e['message']}: {detail}\n")
                else:
                    fh.write(f"[{ts}] [{e['level']}] {e['message']}\n")

    def _export_session(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            shutil.copy2(self._session_path, path)
            self.system(f"Exported to: {path}")
        except Exception as ex:
            self.error(f"Export failed: {ex}")
            messagebox.showerror("Export Failed", str(ex))

    def _open_log_folder(self):
        folder = os.path.abspath("logs")
        try:
            if sys.platform == "win32":
                os.startfile(folder)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", folder])
            else:
                subprocess.Popen(["xdg-open", folder])
        except Exception as ex:
            messagebox.showerror("Error", f"Could not open folder: {ex}")


# ---------------------------------------------------------------------------
# Module-level widget helpers
# ---------------------------------------------------------------------------

def _sep(parent):
    return tk.Frame(parent, bg=_C["sep"], height=1)


def _flat_btn(parent, text, command):
    btn = tk.Button(
        parent,
        text=text,
        font=_FONT_BTN,
        bg=_C["card"],
        fg=_C["accent"],
        activebackground=_C["panel"],
        activeforeground=_C["accent"],
        relief=tk.FLAT,
        bd=0,
        cursor="hand2",
        padx=8,
        pady=3,
        command=command,
    )
    btn.bind("<Enter>", lambda _: btn.config(bg=_C["panel"]))
    btn.bind("<Leave>", lambda _: btn.config(bg=_C["card"]))
    return btn


def _scrolled_text(parent):
    frame = tk.Frame(parent, bg=_C["bg_void"])
    frame.pack(fill="both", expand=True, padx=6, pady=(0, 6))

    sb = tk.Scrollbar(frame, bg=_C["panel"], troughcolor=_C["card"])
    sb.pack(side="right", fill="y")

    widget = tk.Text(
        frame,
        font=_FONT_BODY,
        bg=_C["bg_void"],
        fg=_C["text"],
        insertbackground=_C["accent"],
        selectbackground=_C["card"],
        relief=tk.FLAT,
        bd=0,
        wrap="word",
        state="disabled",
        yscrollcommand=sb.set,
    )
    widget.pack(side="left", fill="both", expand=True)
    sb.config(command=widget.yview)
    return widget


def _clear_text(widget):
    widget.config(state="normal")
    widget.delete("1.0", "end")
    widget.config(state="disabled")


def _insert_system_row(widget, entry, auto_scroll):
    ts      = entry["timestamp"]
    level   = entry["level"]
    ctx     = entry.get("context")
    message = entry["message"]
    ctx_part = f" [{ctx}]" if ctx else ""
    line = f"[{ts}] [{level}]{ctx_part}  {message}\n"
    widget.config(state="normal")
    widget.insert("end", line, level)
    widget.config(state="disabled")
    if auto_scroll.get():
        widget.see("end")


def _insert_event_row(widget, entry, auto_scroll):
    ts     = entry["timestamp"]
    event  = entry["message"]
    detail = entry.get("detail") or ""
    line   = f"[{ts}]  {event}  {detail}\n"

    ev_lower  = event.lower()
    det_lower = detail.lower()
    if "combat" in ev_lower or "attack" in det_lower or "fight" in ev_lower:
        tag = "combat"
    elif "loot" in ev_lower or "item" in ev_lower or "pickup" in ev_lower:
        tag = "loot"
    elif "location" in ev_lower or "move" in ev_lower or "travel" in ev_lower:
        tag = "movement"
    elif "stat" in ev_lower or "hp" in det_lower or "gold" in det_lower:
        tag = "stat"
    else:
        tag = "default"

    widget.config(state="normal")
    widget.insert("end", line, tag)
    widget.config(state="disabled")
    if auto_scroll.get():
        widget.see("end")
