import tkinter as tk
import app.ui.simple.constants as const

class DialogBox(tk.Toplevel):
    def __init__(self, parent, title="", body="", on_dismiss=None, **kwargs):
        bg = kwargs.pop('bg', const.CARD_BG)
        super().__init__(parent, bg=bg, **kwargs)
        self.title(title)
        self.configure(bg=bg)
        self.resizable(False, False)
        self.grab_set()
        self._on_dismiss = on_dismiss

        tk.Label(
            self,
            text=title,
            font=const.FONT_TITLE,
            fg=const.ACCENT_FG,
            bg=bg,
        ).pack(padx=const.PAD_LARGE, pady=(const.PAD_LARGE, const.PAD_MEDIUM))

        tk.Label(
            self,
            text=body,
            font=const.FONT_BODY,
            fg=const.TEXT_FG,
            bg=bg,
            wraplength=340,
            justify=tk.LEFT,
        ).pack(padx=const.PAD_LARGE, pady=(const.PAD_MEDIUM, const.PAD_LARGE))

        tk.Button(
            self,
            text="Dismiss",
            font=const.FONT_BOLD,
            bg=const.ACTIVE_BG,
            fg=const.ACTIVE_FG,
            activebackground=const.ACTIVE_BG,
            activeforeground=const.ACTIVE_FG,
            relief=tk.FLAT,
            padx=const.BUTTON_PADX,
            pady=const.BUTTON_PADY,
            cursor="hand2",
            command=self._handle_dismiss,
        ).pack(pady=(0, const.PAD_LARGE))

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