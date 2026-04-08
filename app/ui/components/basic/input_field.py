import tkinter as tk
from .theme import PANEL_BG, CARD_BG, TEXT_FG, ACTIVE_BG, ACTIVE_FG, FONT_BODY, PAD_SMALL

class InputField(tk.Frame):
    def __init__(self, parent, placeholder="", on_submit=None, **kwargs):
        bg = kwargs.pop('bg', PANEL_BG)
        super().__init__(parent, bg=bg, **kwargs)
        self._on_submit = on_submit
        self._var = tk.StringVar()
        self._entry = tk.Entry(
            self,
            textvariable=self._var,
            font=FONT_BODY,
            bg=CARD_BG,
            fg=TEXT_FG,
            insertbackground=TEXT_FG,
            relief=tk.FLAT,
        )
        self._entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(PAD_SMALL, 2), pady=PAD_SMALL)
        self._entry.bind("<Return>", self._handle_submit)

        self._btn = tk.Button(
            self,
            text="▶",
            font=FONT_BODY,
            bg=ACTIVE_BG,
            fg=ACTIVE_FG,
            activebackground=ACTIVE_BG,
            activeforeground=ACTIVE_FG,
            relief=tk.FLAT,
            padx=PAD_SMALL,
            cursor="hand2",
            command=self._handle_submit,
        )
        self._btn.pack(side=tk.LEFT, padx=(0, PAD_SMALL))

        if placeholder:
            self._entry.insert(0, placeholder)
            self._entry.config(fg=MUTED_FG)
            self._entry.bind("<FocusIn>", self._clear_placeholder)
            self._placeholder = placeholder
        else:
            self._placeholder = None

    def _clear_placeholder(self, _event=None):
        if self._var.get() == self._placeholder:
            self._entry.delete(0, tk.END)
            self._entry.config(fg=TEXT_FG)

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