import tkinter as tk


class InputField(tk.Frame):
    """Single-line text entry. Returns string on submit via callback. Layer 1."""

    BG = "#16213e"
    ENTRY_BG = "#0d1b2a"
    FG = "#d4c9a8"
    FONT = ("Courier", 11)

    def __init__(self, parent, placeholder="", on_submit=None, **kwargs):
        """
        on_submit — callback(text: str)
        """
        bg = kwargs.pop('bg', self.BG)
        super().__init__(parent, bg=bg, **kwargs)
        self._on_submit = on_submit

        self._var = tk.StringVar()
        self._entry = tk.Entry(
            self,
            textvariable=self._var,
            font=self.FONT,
            bg=self.ENTRY_BG,
            fg=self.FG,
            insertbackground=self.FG,
            relief=tk.FLAT,
        )
        self._entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 2), pady=4)
        self._entry.bind("<Return>", self._handle_submit)

        self._btn = tk.Button(
            self,
            text="▶",
            font=self.FONT,
            bg="#0f3460",
            fg=self.FG,
            activebackground="#e94560",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=6,
            cursor="hand2",
            command=self._handle_submit,
        )
        self._btn.pack(side=tk.LEFT, padx=(0, 4))

        if placeholder:
            self._entry.insert(0, placeholder)
            self._entry.config(fg="#555")
            self._entry.bind("<FocusIn>", self._clear_placeholder)
            self._placeholder = placeholder
        else:
            self._placeholder = None

    def _clear_placeholder(self, _event=None):
        if self._var.get() == self._placeholder:
            self._entry.delete(0, tk.END)
            self._entry.config(fg=self.FG)

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
