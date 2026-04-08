import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

class PycacheCleaner:
    def __init__(self, root):
        self.root = root
        self.root.title("Delete __pycache__ Folders")
        self.root.geometry("700x500")
        self.root.resizable(True, True)

        # Path selection frame
        frame_path = tk.Frame(root)
        frame_path.pack(pady=10, padx=10, fill=tk.X)

        tk.Label(frame_path, text="Target Directory:").pack(side=tk.LEFT, padx=(0, 5))
        self.path_var = tk.StringVar()
        self.entry_path = tk.Entry(frame_path, textvariable=self.path_var, width=50)
        self.entry_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        btn_browse = tk.Button(frame_path, text="Browse...", command=self.browse_folder)
        btn_browse.pack(side=tk.RIGHT)

        # Buttons frame
        frame_buttons = tk.Frame(root)
        frame_buttons.pack(pady=5)

        btn_start = tk.Button(frame_buttons, text="Start Deletion", command=self.start_deletion,
                              bg="#4CAF50", fg="white", padx=10, pady=5)
        btn_start.pack(side=tk.LEFT, padx=5)

        btn_clear = tk.Button(frame_buttons, text="Clear Log", command=self.clear_log,
                              bg="#f44336", fg="white", padx=10, pady=5)
        btn_clear.pack(side=tk.LEFT, padx=5)

        # Log area (scrolled text)
        self.log_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=25)
        self.log_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Initial message
        self.log("Ready. Select a directory and click 'Start Deletion'.")

    def browse_folder(self):
        folder_selected = filedialog.askdirectory(title="Select Directory to Scan")
        if folder_selected:
            self.path_var.set(folder_selected)

    def log(self, message):
        """Insert a message into the log area and scroll to the end."""
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.root.update_idletasks()

    def clear_log(self):
        self.log_area.delete(1.0, tk.END)

    def delete_pycache_folders(self, root_path):
        """Walk through root_path and delete every '__pycache__' directory."""
        deleted_count = 0
        error_count = 0

        for dirpath, dirnames, _ in os.walk(root_path):
            if '__pycache__' in dirnames:
                pycache_path = os.path.join(dirpath, '__pycache__')
                try:
                    shutil.rmtree(pycache_path)
                    self.log(f"Deleted: {pycache_path}")
                    deleted_count += 1
                except Exception as e:
                    self.log(f"ERROR deleting {pycache_path}: {e}")
                    error_count += 1

        return deleted_count, error_count

    def start_deletion(self):
        target = self.path_var.get().strip()
        if not target:
            messagebox.showwarning("No Directory", "Please select a directory first.")
            return

        if not os.path.isdir(target):
            messagebox.showerror("Invalid Path", f"'{target}' is not a valid directory.")
            return

        # Ask for confirmation
        if not messagebox.askyesno("Confirm Deletion",
                                   f"Are you sure you want to delete ALL '__pycache__' folders inside:\n\n{target}\n\nThis action cannot be undone."):
            self.log("Operation cancelled by user.")
            return

        self.log(f"\n--- Scanning: {target} ---")
        deleted, errors = self.delete_pycache_folders(target)
        self.log(f"--- Finished ---")
        self.log(f"Deleted {deleted} '__pycache__' folder(s).")
        if errors:
            self.log(f"Encountered {errors} error(s). Check log above.")

        if deleted == 0 and errors == 0:
            self.log("No '__pycache__' folders found.")
        elif deleted > 0:
            messagebox.showinfo("Completed", f"Successfully deleted {deleted} '__pycache__' folder(s).")

if __name__ == "__main__":
    root = tk.Tk()
    app = PycacheCleaner(root)
    root.mainloop()