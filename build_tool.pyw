#!/usr/bin/env python3
# build_tool.pyw - GUI for packaging Pursuit of Peace with external data folder

import os
import sys
import subprocess
import shutil
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def check_pyinstaller():
    """Return True if pyinstaller is available, else False."""
    try:
        subprocess.run(["pyinstaller", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def install_pyinstaller(parent_window):
    """Install pyinstaller via pip, show progress in a simple dialog."""
    def install_thread():
        proc = subprocess.Popen(
            [sys.executable, "-m", "pip", "install", "pyinstaller"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        output = ""
        for line in proc.stdout:
            output += line
            # Update a simple label inside the progress window
            if progress_label.winfo_exists():
                progress_label.config(text=line.strip()[:80])
                progress_window.update()
        proc.wait()
        progress_window.destroy()
        if proc.returncode == 0:
            messagebox.showinfo("Success", "PyInstaller installed successfully.\nYou can now build the game.")
        else:
            messagebox.showerror("Installation Failed", f"Could not install PyInstaller.\n\n{output[:500]}")
        # Re-enable build button if needed
        build_btn.config(state="normal")

    # Create a small popup
    progress_window = tk.Toplevel(parent_window)
    progress_window.title("Installing PyInstaller")
    progress_window.geometry("500x100")
    progress_label = tk.Label(progress_window, text="Installing... please wait")
    progress_label.pack(pady=20)
    tk.Label(progress_window, text="This may take a minute.").pack()
    # Disable build button during install
    build_btn.config(state="disabled")
    threading.Thread(target=install_thread, daemon=True).start()

# ----------------------------------------------------------------------
# Main Build GUI
# ----------------------------------------------------------------------
class BuildTool:
    def __init__(self, root):
        self.root = root
        root.title("Pursuit of Peace - Game Builder")
        root.geometry("800x600")
        root.resizable(True, True)

        # Variables
        self.main_script = tk.StringVar(value=os.path.abspath("main.pyw"))
        self.output_name = tk.StringVar(value="PursuitOfPeace")
        self.icon_path = tk.StringVar(value="")
        self.console_mode = tk.BooleanVar(value=False)  # --windowed by default, so console off
        self.copy_data = tk.BooleanVar(value=True)
        self.clean_before = tk.BooleanVar(value=True)

        # Create UI
        self.create_widgets()

        # Check pyinstaller on startup
        self.check_pyinstaller_status()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Main script selection ---
        ttk.Label(main_frame, text="Main script:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.main_script, width=60).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        ttk.Button(main_frame, text="Browse...", command=self.browse_main).grid(row=0, column=2, padx=5, pady=5)

        # --- Output name ---
        ttk.Label(main_frame, text="Executable name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_name, width=30).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(main_frame, text="(.exe will be added automatically on Windows)").grid(row=1, column=2, sticky=tk.W, padx=5)

        # --- Icon file (optional) ---
        ttk.Label(main_frame, text="Icon file (.ico):").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.icon_path, width=60).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        ttk.Button(main_frame, text="Browse...", command=self.browse_icon).grid(row=2, column=2, padx=5, pady=5)

        # --- Options ---
        options_frame = ttk.LabelFrame(main_frame, text="Build Options", padding="5")
        options_frame.grid(row=3, column=0, columnspan=3, sticky=tk.W+tk.E, pady=10)
        ttk.Checkbutton(options_frame, text="One-file executable (--onefile)", state="disabled", variable=tk.BooleanVar(value=True)).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Windowed mode (no console) (--windowed)", variable=self.console_mode, onvalue=False, offvalue=True).grid(row=0, column=1, sticky=tk.W, padx=20)
        ttk.Checkbutton(options_frame, text="Copy 'data/' folder next to executable after build", variable=self.copy_data).grid(row=1, column=0, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Remove previous 'build/' and 'dist/' folders before building", variable=self.clean_before).grid(row=1, column=1, sticky=tk.W, padx=20)

        # --- Build button and status ---
        self.build_btn = ttk.Button(main_frame, text="BUILD GAME", command=self.start_build, width=20)
        self.build_btn.grid(row=4, column=0, columnspan=3, pady=15)

        self.status_label = ttk.Label(main_frame, text="Ready", foreground="gray")
        self.status_label.grid(row=5, column=0, columnspan=3, sticky=tk.W)

        # --- Output log ---
        ttk.Label(main_frame, text="Build Output:").grid(row=6, column=0, sticky=tk.W, pady=(10,0))
        self.log_text = scrolledtext.ScrolledText(main_frame, height=18, width=90, wrap=tk.WORD)
        self.log_text.grid(row=7, column=0, columnspan=3, pady=5, sticky=tk.W+tk.E+tk.N+tk.S)

        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(7, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def check_pyinstaller_status(self):
        if not check_pyinstaller():
            self.status_label.config(text="PyInstaller not found. Click 'Install PyInstaller' first.", foreground="orange")
            install_btn = ttk.Button(self.root, text="Install PyInstaller", command=lambda: install_pyinstaller(self.root))
            install_btn.place(relx=0.5, rely=0.9, anchor=tk.CENTER)
            self.build_btn.config(state="disabled")
            self.install_btn = install_btn
        else:
            self.status_label.config(text="PyInstaller is ready.", foreground="green")
            self.build_btn.config(state="normal")

    def browse_main(self):
        filename = filedialog.askopenfilename(
            title="Select main script",
            filetypes=[("Python files", "*.py *.pyw"), ("All files", "*.*")]
        )
        if filename:
            self.main_script.set(filename)

    def browse_icon(self):
        filename = filedialog.askopenfilename(
            title="Select icon file (.ico)",
            filetypes=[("Icon files", "*.ico"), ("All files", "*.*")]
        )
        if filename:
            self.icon_path.set(filename)

    def log(self, message):
        """Append message to log text widget."""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def start_build(self):
        """Run build in a separate thread."""
        if not check_pyinstaller():
            messagebox.showerror("Missing Dependency", "PyInstaller is not installed.\nClick 'Install PyInstaller' first.")
            return

        main_script = self.main_script.get().strip()
        if not os.path.isfile(main_script):
            messagebox.showerror("Error", f"Main script not found:\n{main_script}")
            return

        output_name = self.output_name.get().strip()
        if not output_name:
            messagebox.showerror("Error", "Please enter an executable name.")
            return

        # Clean previous builds if requested
        if self.clean_before.get():
            for folder in ["build", "dist"]:
                if os.path.exists(folder):
                    try:
                        shutil.rmtree(folder)
                        self.log(f"Removed existing '{folder}/' folder.")
                    except Exception as e:
                        self.log(f"Warning: could not remove {folder}: {e}")

        # Prepare pyinstaller command
        cmd = ["pyinstaller", "--onefile", "--noconfirm"]

        if not self.console_mode.get():
            cmd.append("--windowed")  # no console

        # Add icon if provided
        icon = self.icon_path.get().strip()
        if icon and os.path.isfile(icon):
            cmd.append(f"--icon={icon}")

        # Output name
        cmd.append(f"--name={output_name}")

        # Add the main script
        cmd.append(main_script)

        self.log("=== Starting build ===")
        self.log(f"Command: {' '.join(cmd)}")
        self.status_label.config(text="Building... please wait", foreground="blue")
        self.build_btn.config(state="disabled")

        # Run in thread
        threading.Thread(target=self.run_build, args=(cmd,), daemon=True).start()

    def run_build(self, cmd):
        """Execute pyinstaller and capture output."""
        try:
            # Use CREATE_NO_WINDOW on Windows to avoid a flash of console
            creationflags = 0
            if sys.platform == "win32":
                creationflags = subprocess.CREATE_NO_WINDOW
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                creationflags=creationflags
            )
            for line in iter(proc.stdout.readline, ""):
                if line:
                    self.log(line.rstrip())
            proc.wait()
            if proc.returncode == 0:
                self.log("\n=== Build completed successfully ===")
                self.status_label.config(text="Build successful!", foreground="green")
                # Copy data folder after successful build
                if self.copy_data.get():
                    self.copy_data_folder()
            else:
                self.log(f"\n=== Build failed with error code {proc.returncode} ===")
                self.status_label.config(text="Build failed. See output above.", foreground="red")
        except Exception as e:
            self.log(f"Exception during build: {e}")
            self.status_label.config(text="Build error occurred.", foreground="red")
        finally:
            self.build_btn.config(state="normal")

    def copy_data_folder(self):
        """Copy the 'data/' folder from the main script's directory to the 'dist/' folder."""
        main_dir = os.path.dirname(self.main_script.get())
        source_data = os.path.join(main_dir, "data")
        if not os.path.isdir(source_data):
            self.log(f"Warning: data folder not found at '{source_data}'. Skipping copy.")
            return

        # dist folder is created by pyinstaller in the current working directory
        dest_dir = os.path.join(os.getcwd(), "dist")
        dest_data = os.path.join(dest_dir, "data")

        try:
            if os.path.exists(dest_data):
                shutil.rmtree(dest_data)
                self.log(f"Removed existing '{dest_data}'.")
            shutil.copytree(source_data, dest_data)
            self.log(f"Successfully copied 'data/' folder to '{dest_data}'.")
            self.log("Your game executable is ready in the 'dist' folder.")
        except Exception as e:
            self.log(f"Error copying data folder: {e}")

# ----------------------------------------------------------------------
# Main entry point
# ----------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = BuildTool(root)
    root.mainloop()