import tkinter as tk
from .theme import CARD_BG, TEXT_FG, ACCENT_FG, ACTIVE_BG, ACTIVE_FG, FONT_TITLE, FONT_BODY, FONT_BOLD, PAD_MEDIUM, PAD_LARGE

class DialogBox(tk.Toplevel):
    def __init__(self, parent, title="", body="", on_dismiss=None, **kwargs):
        bg = kwargs.pop('bg', CARD_BG)
        super().__init__(parent, bg=bg, **kwargs)
        self.title(title)
        self.configure(bg=bg)
        self.resizable(False, False)
        self.grab_set()
        self._on_dismiss = on_dismiss

        tk.Label(
            self,
            text=title,
            font=FONT_TITLE,
            fg=ACCENT_FG,
            bg=bg,
        ).pack(padx=PAD_LARGE, pady=(PAD_LARGE, PAD_MEDIUM))

        tk.Label(
            self,
            text=body,
            font=FONT_BODY,
            fg=TEXT_FG,
            bg=bg,
            wraplength=340,
            justify=tk.LEFT,
        ).pack(padx=PAD_LARGE, pady=(PAD_MEDIUM, PAD_LARGE))

        tk.Button(
            self,
            text="Dismiss",
            font=FONT_BOLD,
            bg=ACTIVE_BG,
            fg=ACTIVE_FG,
            activebackground=ACTIVE_BG,
            activeforeground=ACTIVE_FG,
            relief=tk.FLAT,
            padx=BUTTON_PADX,
            pady=BUTTON_PADY,
            cursor="hand2",
            command=self._handle_dismiss,
        ).pack(pady=(0, PAD_LARGE))

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