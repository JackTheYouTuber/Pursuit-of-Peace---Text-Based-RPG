import tkinter as tk
from tkinter import font as tkfont


class TextDisplay(tk.Frame):
    """Scrollable read-only text block. Layer 1 — no project imports."""

    DEFAULT_FONT = ("Courier", 11)
    DEFAULT_FG = "#d4c9a8"
    DEFAULT_BG = "#1a1a2e"

    def __init__(self, parent, content="", font=None, fg=None, bg=None, **kwargs):
        theme_bg = kwargs.pop('bg', None)
        final_bg = bg or theme_bg or self.DEFAULT_BG
        super().__init__(parent, bg=final_bg, **kwargs)
        self._bg = final_bg

        self._font = font or self.DEFAULT_FONT
        self._fg = fg or self.DEFAULT_FG

        self._scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self._text = tk.Text(
            self,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=self._font,
            fg=self._fg,
            bg=self._bg,
            yscrollcommand=self._scrollbar.set,
            relief=tk.FLAT,
            padx=6,
            pady=6,
            cursor="arrow",
            selectbackground=self._bg,
        )
        self._scrollbar.config(command=self._text.yview)
        self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        if content:
            self.set_content(content)

    def set_content(self, content):
        """Replace the displayed text."""
        self._text.config(state=tk.NORMAL)
        self._text.delete("1.0", tk.END)
        self._text.insert(tk.END, content)
        self._text.config(state=tk.DISABLED)
        self._text.see(tk.END)

    def append(self, text):
        """Append text without clearing existing content."""
        self._text.config(state=tk.NORMAL)
        self._text.insert(tk.END, text)
        self._text.config(state=tk.DISABLED)
        self._text.see(tk.END)

    def clear(self):
        self.set_content("")
