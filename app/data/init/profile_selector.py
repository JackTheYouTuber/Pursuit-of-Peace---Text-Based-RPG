"""
profile_selector.py

Provides ProfileSelectorFrame — a tkinter Frame that embeds directly in
the root window (no Toplevel).  The frame fills the window and lets the
player pick an existing profile, create a new one, or quit — all without
opening a separate window or popup.

Usage (in app.py):
    result = {}
    done   = tk.BooleanVar(value=False)
    frame  = ProfileSelectorFrame(root, profile_mgr, config_loader,
                                  result=result, done=done)
    frame.place(relx=0, rely=0, relwidth=1, relheight=1)
    root.wait_variable(done)
    frame.destroy()
    name, state = result.get("name"), result.get("state")
"""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional, Tuple

_BG     = "#0f172a"
_PANEL  = "#1e293b"
_ACCENT = "#fbbf24"
_FG     = "#e2e8f0"
_MUTED  = "#94a3b8"
_BTN_BG = "#334155"
_BTN_ACT= "#3b82f6"
_SEL_BG = "#3b82f6"
_ERR    = "#f87171"
_OK     = "#4ade80"


class ProfileSelectorFrame(tk.Frame):
    """Full-window profile selector embedded directly in the root tk window."""

    def __init__(self, parent, profile_mgr, config_loader,
                 result: dict, done: tk.BooleanVar, logger=None):
        super().__init__(parent, bg=_BG)
        self._mgr    = profile_mgr
        self._cfg    = config_loader
        self._result = result
        self._done   = done
        self._logger = logger
        self._build()
        self._refresh_list()

    def _build(self) -> None:
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0, minsize=440)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=1)

        card = tk.Frame(self, bg=_PANEL, padx=28, pady=24)
        card.grid(row=1, column=1, sticky="nsew", ipadx=4, ipady=4)

        tk.Label(card, text="PURSUIT OF PEACE",
                 font=("Segoe UI", 18, "bold"),
                 fg=_ACCENT, bg=_PANEL).pack(pady=(0, 2))
        tk.Label(card, text="Select a profile to continue, or create a new one.",
                 font=("Segoe UI", 9), fg=_MUTED, bg=_PANEL).pack(pady=(0, 14))

        list_frame = tk.Frame(card, bg=_PANEL)
        list_frame.pack(fill=tk.BOTH, expand=True)
        self._listbox = tk.Listbox(list_frame, bg=_BG, fg=_FG,
                                   selectbackground=_SEL_BG, selectforeground="#fff",
                                   activestyle="none", font=("Segoe UI", 11),
                                   relief=tk.FLAT, bd=0,
                                   highlightthickness=1, highlightcolor=_BTN_ACT,
                                   height=8)
        sb = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self._listbox.yview)
        self._listbox.configure(yscrollcommand=sb.set)
        self._listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._listbox.bind("<Double-Button-1>", lambda _: self._do_load())
        self._listbox.bind("<Return>",          lambda _: self._do_load())

        # Inline new-profile entry
        self._new_frame = tk.Frame(card, bg=_PANEL)
        tk.Label(self._new_frame, text="Profile name:",
                 fg=_MUTED, bg=_PANEL, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0,6))
        self._name_var = tk.StringVar()
        self._name_entry = tk.Entry(self._new_frame, textvariable=self._name_var,
                                    bg=_BG, fg=_FG, insertbackground=_FG,
                                    relief=tk.FLAT, bd=1, font=("Segoe UI", 10), width=22)
        self._name_entry.pack(side=tk.LEFT, padx=(0,6))
        self._name_entry.bind("<Return>", lambda _: self._do_create())
        self._name_entry.bind("<Escape>", lambda _: self._hide_new_entry())
        tk.Button(self._new_frame, text="Create", bg=_BTN_ACT, fg="#fff",
                  activebackground=_BTN_ACT, relief=tk.FLAT, padx=10, pady=3,
                  font=("Segoe UI", 9), command=self._do_create).pack(side=tk.LEFT, padx=2)
        tk.Button(self._new_frame, text="Cancel", bg=_BTN_BG, fg=_FG,
                  activebackground=_BTN_BG, relief=tk.FLAT, padx=8, pady=3,
                  font=("Segoe UI", 9), command=self._hide_new_entry).pack(side=tk.LEFT, padx=2)

        # Inline delete-confirmation bar
        self._confirm_frame = tk.Frame(card, bg="#3b1515")
        self._confirm_label = tk.Label(self._confirm_frame, text="",
                                       fg=_ERR, bg="#3b1515", font=("Segoe UI", 9))
        self._confirm_label.pack(side=tk.LEFT, padx=8)
        tk.Button(self._confirm_frame, text="Yes, delete", bg="#7f1d1d", fg="#fff",
                  activebackground="#991b1b", relief=tk.FLAT, padx=10, pady=3,
                  font=("Segoe UI", 9),
                  command=self._do_delete_confirmed).pack(side=tk.LEFT, padx=4)
        tk.Button(self._confirm_frame, text="Cancel", bg=_BTN_BG, fg=_FG,
                  activebackground=_BTN_BG, relief=tk.FLAT, padx=8, pady=3,
                  font=("Segoe UI", 9), command=self._hide_confirm).pack(side=tk.LEFT, padx=2)

        # Status
        self._status_var = tk.StringVar(value="")
        self._status_lbl = tk.Label(card, textvariable=self._status_var,
                                    fg=_MUTED, bg=_PANEL, font=("Segoe UI", 9))
        self._status_lbl.pack(pady=(8, 0))

        # Action buttons
        btn_row = tk.Frame(card, bg=_PANEL)
        btn_row.pack(pady=(10, 0), fill=tk.X)
        def _btn(parent, text, cmd, accent=False):
            bg = _BTN_ACT if accent else _BTN_BG
            return tk.Button(parent, text=text, command=cmd, bg=bg,
                             fg="#fff" if accent else _FG,
                             activebackground=bg, relief=tk.FLAT,
                             padx=14, pady=6, cursor="hand2",
                             font=("Segoe UI", 10, "bold" if accent else "normal"))
        _btn(btn_row, "▶  Load",        self._do_load,           accent=True).pack(side=tk.LEFT, padx=4)
        _btn(btn_row, "+  New Profile",  self._show_new_entry               ).pack(side=tk.LEFT, padx=4)
        _btn(btn_row, "✕  Delete",       self._show_confirm_delete           ).pack(side=tk.LEFT, padx=4)
        _btn(btn_row, "Quit",            self._do_quit                       ).pack(side=tk.RIGHT, padx=4)

    def _refresh_list(self) -> None:
        self._listbox.delete(0, tk.END)
        for name in self._mgr.list():
            self._listbox.insert(tk.END, f"  {name}")
        if self._listbox.size():
            self._listbox.selection_set(0)

    def _selected_name(self) -> Optional[str]:
        sel = self._listbox.curselection()
        return self._listbox.get(sel[0]).strip() if sel else None

    def _set_status(self, msg: str, ok: bool = False, error: bool = False) -> None:
        self._status_lbl.config(fg=_OK if ok else (_ERR if error else _MUTED))
        self._status_var.set(msg)

    def _do_load(self) -> None:
        name = self._selected_name()
        if not name:
            self._set_status("Please select a profile first.", error=True); return
        state = self._mgr.load(name)
        if state:
            self._result["name"] = name; self._result["state"] = state
            self._done.set(True)
        else:
            messagebox.showerror("Error", f"Failed to load '{name}'.")

    def _show_new_entry(self) -> None:
        self._hide_confirm()
        self._name_var.set("")
        self._new_frame.pack(fill=tk.X, pady=(8,0))
        self._name_entry.focus_set()
        self._set_status("Enter a name and press Create (or Enter).")

    def _hide_new_entry(self) -> None:
        self._new_frame.pack_forget(); self._set_status("")

    def _do_create(self) -> None:
        name = self._name_var.get().strip()
        if not name:
            self._set_status("Name cannot be empty.", error=True); return
        if self._mgr.exists(name):
            self._set_status(f"Profile '{name}' already exists.", error=True); return
        state = self._mgr.create(name, self._cfg.defaults())
        if state:
            self._result["name"] = name; self._result["state"] = state
            self._done.set(True)
        else:
            messagebox.showerror("Error", "Could not create profile.")

    def _show_confirm_delete(self) -> None:
        name = self._selected_name()
        if not name:
            self._set_status("Select a profile to delete.", error=True); return
        self._hide_new_entry()
        self._confirm_label.config(text=f"Delete '{name}'? This cannot be undone.")
        self._confirm_frame.pack(fill=tk.X, pady=(8,0))

    def _hide_confirm(self) -> None:
        self._confirm_frame.pack_forget(); self._set_status("")

    def _do_delete_confirmed(self) -> None:
        name = self._selected_name()
        if not name: return
        if self._mgr.delete(name):
            self._set_status(f"Profile '{name}' deleted.", ok=True)
            self._refresh_list()
        else:
            messagebox.showerror("Error", f"Could not delete '{name}'.")
        self._hide_confirm()

    def _do_quit(self) -> None:
        self._result["name"] = None; self._result["state"] = None
        self._done.set(True)


class ProfileSelector:
    """Backward-compat shim — wraps ProfileSelectorFrame in a wait_variable loop."""
    @staticmethod
    def select_or_create(root, profile_mgr, config_loader,
                         logger=None) -> Tuple[Optional[str], Optional[dict]]:
        result: dict = {}
        done = tk.BooleanVar(value=False)
        frame = ProfileSelectorFrame(root, profile_mgr, config_loader,
                                     result=result, done=done, logger=logger)
        frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        frame.lift()
        root.wait_variable(done)
        frame.destroy()
        return result.get("name"), result.get("state")
