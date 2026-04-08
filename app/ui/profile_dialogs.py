import tkinter as tk
from tkinter import messagebox, simpledialog
from app.profile_manager import ProfileManager


class ProfileDialogs:
    """Static methods to show profile dialogs using a given root and profile manager."""

    @staticmethod
    def select_or_create(root: tk.Tk, profile_mgr: ProfileManager, data_loader, logger=None):
        """
        Shows modal dialog to select or create a profile.
        Returns (profile_name, loaded_state) or (None, None) if cancelled.
        """
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
        scrollbar = tk.Scrollbar(frame, command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        profiles = profile_mgr.list_profiles()
        for p in profiles:
            listbox.insert(tk.END, p)

        result = {"name": None, "state": None}

        def load_selected():
            sel = listbox.curselection()
            if not sel:
                messagebox.showwarning("No Selection", "Please select a profile.")
                return
            name = listbox.get(sel[0])
            state = profile_mgr.load_profile(name)
            if state:
                result["name"] = name
                result["state"] = state
                dialog.destroy()
            else:
                messagebox.showerror("Error", f"Failed to load profile '{name}'.")

        def create_new():
            name = simpledialog.askstring("New Profile", "Enter profile name:",
                                          parent=dialog)
            if not name or not name.strip():
                return
            name = name.strip()
            if profile_mgr.profile_exists(name):
                messagebox.showerror("Error", "Profile already exists.")
                return
            defaults = data_loader.get_player_defaults()
            state = profile_mgr.create_new_profile(name, defaults)
            if state:
                result["name"] = name
                result["state"] = state
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to create profile.")

        def delete_profile():
            sel = listbox.curselection()
            if not sel:
                return
            name = listbox.get(sel[0])
            if messagebox.askyesno("Delete Profile", f"Delete profile '{name}'?"):
                if profile_mgr.delete_profile(name):
                    listbox.delete(sel[0])
                    messagebox.showinfo("Deleted", f"Profile '{name}' deleted.")
                else:
                    messagebox.showerror("Error", "Could not delete profile.")

        btn_frame = tk.Frame(dialog, bg="#0d1b2a")
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(btn_frame, text="Load Selected", command=load_selected,
                  bg="#0f3460", fg="#d4c9a8", font=("Courier", 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="New Profile", command=create_new,
                  bg="#0f3460", fg="#d4c9a8", font=("Courier", 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete Profile", command=delete_profile,
                  bg="#0f3460", fg="#d4c9a8", font=("Courier", 10)).pack(side=tk.LEFT, padx=5)

        root.wait_window(dialog)
        return result["name"], result["state"]

    @staticmethod
    def load_profile_dialog(root: tk.Tk, profile_mgr: ProfileManager, logger=None):
        """Show dialog to select a profile to load, returns (name, state) or (None,None)."""
        profiles = profile_mgr.list_profiles()
        if not profiles:
            messagebox.showinfo("No Profiles", "No profiles found.")
            return None, None

        dialog = tk.Toplevel(root)
        dialog.title("Load Profile")
        dialog.geometry("300x400")
        dialog.configure(bg="#0d1b2a")
        dialog.transient(root)
        dialog.grab_set()

        tk.Label(dialog, text="Select Profile", font=("Courier", 12, "bold"),
                 fg="#e2b96f", bg="#0d1b2a").pack(pady=10)

        listbox = tk.Listbox(dialog, bg="#16213e", fg="#d4c9a8",
                             font=("Courier", 11))
        for p in profiles:
            listbox.insert(tk.END, p)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        result = {"name": None, "state": None}

        def do_load():
            sel = listbox.curselection()
            if not sel:
                return
            name = listbox.get(sel[0])
            state = profile_mgr.load_profile(name)
            if state:
                result["name"] = name
                result["state"] = state
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to load profile.")

        tk.Button(dialog, text="Load", command=do_load,
                  bg="#0f3460", fg="#d4c9a8", font=("Courier", 10)).pack(pady=10)

        root.wait_window(dialog)
        return result["name"], result["state"]