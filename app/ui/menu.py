import tkinter as tk


class GameMenu:
    def __init__(self, root: tk.Tk, callbacks: dict):
        self.root = root
        self.callbacks = callbacks
        self._build()

    def _build(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Game", command=self.callbacks.get("new_game"))
        file_menu.add_command(label="Save Game", command=self.callbacks.get("save_game"))
        file_menu.add_command(label="Load Game", command=self.callbacks.get("load_game"))
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.callbacks.get("quit"))