import tkinter as tk


class StatBar(tk.Frame):
    """Labeled numeric stat display. Layer 1 — no project imports."""

    BG = "#16213e"
    LABEL_FG = "#7a8fa6"
    VALUE_FG = "#e2b96f"
    FONT_LABEL = ("Courier", 10)
    FONT_VALUE = ("Courier", 11, "bold")

    def __init__(self, parent, label="", value=0, **kwargs):
        bg = kwargs.pop('bg', self.BG)
        super().__init__(parent, bg=bg, **kwargs)

        self._label_var = tk.StringVar(value=label)
        self._value_var = tk.StringVar(value=str(value))

        tk.Label(
            self,
            textvariable=self._label_var,
            font=self.FONT_LABEL,
            fg=self.LABEL_FG,
            bg=self.BG,
            anchor=tk.W,
        ).pack(side=tk.LEFT, padx=(4, 2))

        tk.Label(
            self,
            textvariable=self._value_var,
            font=self.FONT_VALUE,
            fg=self.VALUE_FG,
            bg=self.BG,
            anchor=tk.W,
        ).pack(side=tk.LEFT, padx=(0, 8))

    def set_value(self, value):
        self._value_var.set(str(value))

    def set_label(self, label):
        self._label_var.set(label)
