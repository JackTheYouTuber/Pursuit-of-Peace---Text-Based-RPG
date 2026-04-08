import tkinter as tk


class DialogBox(tk.Toplevel):
    """Modal overlay: title, body text, dismiss button. Layer 1."""

    BG = "#1a1a2e"
    FG = "#d4c9a8"
    TITLE_FG = "#e2b96f"
    BTN_BG = "#0f3460"
    BTN_ACTIVE_BG = "#e94560"
    FONT_TITLE = ("Courier", 13, "bold")
    FONT_BODY = ("Courier", 11)
    FONT_BTN = ("Courier", 11, "bold")

    def __init__(self, parent, title="", body="", on_dismiss=None, **kwargs):
        bg = kwargs.pop('bg', self.BG)
        super().__init__(parent, bg=bg, **kwargs)
        self.title(title)
        self.configure(bg=self.BG)
        self.resizable(False, False)
        self.grab_set()  # modal

        self._on_dismiss = on_dismiss

        tk.Label(
            self,
            text=title,
            font=self.FONT_TITLE,
            fg=self.TITLE_FG,
            bg=self.BG,
        ).pack(padx=20, pady=(16, 4))

        tk.Label(
            self,
            text=body,
            font=self.FONT_BODY,
            fg=self.FG,
            bg=self.BG,
            wraplength=340,
            justify=tk.LEFT,
        ).pack(padx=20, pady=(4, 12))

        tk.Button(
            self,
            text="Dismiss",
            font=self.FONT_BTN,
            bg=self.BTN_BG,
            fg=self.FG,
            activebackground=self.BTN_ACTIVE_BG,
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self._handle_dismiss,
        ).pack(pady=(0, 16))

        self._center(parent)

    def _center(self, parent):
        self.update_idletasks()
        px = parent.winfo_rootx() + parent.winfo_width() // 2
        py = parent.winfo_rooty() + parent.winfo_height() // 2
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{px - w // 2}+{py - h // 2}")

    def _handle_dismiss(self):
        if self._on_dismiss:
            self._on_dismiss()
        self.destroy()
