import tkinter as tk
from tkinter import ttk
from app.ui.style_manager import StyleManager
import app.ui.constants as const

class InputField(ttk.Frame):
    def __init__(self, parent, placeholder="", on_submit=None, **kwargs):
        super().__init__(parent, **kwargs)
        self._on_submit = on_submit
        self._var = tk.StringVar()

        # Use tk.Entry for custom foreground/background
        self._entry = tk.Entry(
            self,
            textvariable=self._var,
            font=const.FONT_BODY,
            bg=const.CARD_BG,
            fg=const.TEXT_FG,
            insertbackground=const.TEXT_FG,
            relief=tk.FLAT,
        )
        self._entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(const.PAD_SMALL, 2), pady=const.PAD_SMALL)
        self._entry.bind("<Return>", self._handle_submit)

        self._btn = tk.Button(self, text="▶", command=self._handle_submit)
        self._btn.pack(side=tk.LEFT, padx=(0, const.PAD_SMALL))

        if placeholder:
            self._entry.insert(0, placeholder)
            self._entry.config(fg=const.MUTED_FG)
            self._entry.bind("<FocusIn>", self._clear_placeholder)
            self._placeholder = placeholder
        else:
            self._placeholder = None

    def _clear_placeholder(self, _event=None):
        if self._var.get() == self._placeholder:
            self._entry.delete(0, tk.END)
            self._entry.config(fg=const.TEXT_FG)

    def _handle_submit(self, _event=None):
        text = self._var.get().strip()
        if text and text != self._placeholder:
            if self._on_submit:
                self._on_submit(text)
            self._var.set("")

    def get_value(self):
        return self._var.get()

    def clear(self):
        self._var.set("")