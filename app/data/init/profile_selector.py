"""Shows profile pick/create dialog at startup. Returns (name, player_state)."""
import tkinter as tk
from tkinter import messagebox, simpledialog
from typing import Optional, Tuple


class ProfileSelector:
    @staticmethod
    def select_or_create(root, profile_mgr, config_loader,
                         logger=None) -> Tuple[Optional[str], Optional[dict]]:
        dialog = tk.Toplevel(root)
        dialog.title("Select Profile")
        dialog.geometry("400x300")
        dialog.configure(bg="#0d1b2a")
        dialog.transient(root)
        dialog.grab_set()
        dialog.resizable(False, False)

        tk.Label(dialog, text="Player Profiles", font=("Courier", 14, "bold"),
                 fg="#e2b96f", bg="#0d1b2a").pack(pady=10)
        frame = tk.Frame(dialog, bg="#0d1b2a")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        listbox = tk.Listbox(frame, bg="#16213e", fg="#d4c9a8",
                             font=("Courier", 11), selectbackground="#0f3460")
        sb = tk.Scrollbar(frame, command=listbox.yview)
        listbox.configure(yscrollcommand=sb.set)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        for p in profile_mgr.list():
            listbox.insert(tk.END, p)

        result = {"name": None, "state": None}

        def _load():
            sel = listbox.curselection()
            if not sel:
                messagebox.showwarning("No Selection", "Please select a profile.")
                return
            name = listbox.get(sel[0])
            state = profile_mgr.load(name)
            if state:
                result["name"], result["state"] = name, state
                dialog.destroy()
            else:
                messagebox.showerror("Error", f"Failed to load '{name}'.")

        def _new():
            name = simpledialog.askstring("New Profile", "Enter profile name:", parent=dialog)
            if not name or not name.strip():
                return
            name = name.strip()
            state = profile_mgr.create(name, config_loader.defaults())
            if state:
                result["name"], result["state"] = name, state
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Could not create profile.")

        btn_frame = tk.Frame(dialog, bg="#0d1b2a")
        btn_frame.pack(pady=8)
        tk.Button(btn_frame, text="Load", command=_load,
                  bg="#1a3a5c", fg="white", width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="New Profile", command=_new,
                  bg="#1a3a5c", fg="white", width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Quit",
                  command=lambda: (result.update(name=None, state=None), dialog.destroy()),
                  bg="#3a1a1a", fg="white", width=8).pack(side=tk.LEFT, padx=5)

        root.wait_window(dialog)
        return result["name"], result["state"]
