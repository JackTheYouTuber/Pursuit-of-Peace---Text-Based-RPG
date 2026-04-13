import tkinter as tk
from tkinter import ttk
import app.ui.simple.constants as const


class TextDisplay(ttk.Frame):
    def __init__(self, parent, content="", bg=None, fg=None, **kwargs):
        super().__init__(parent, **kwargs)
        self._bg = bg if bg is not None else const.CARD_BG
        self._font = const.FONT_BODY
        self._fg = fg if fg is not None else const.TEXT_FG

        self._scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self._text = tk.Text(
            self,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=self._font,
            fg=self._fg,
            bg=self._bg,
            yscrollcommand=self._scrollbar.set,
            relief=tk.FLAT,
            padx=const.PAD_SMALL,
            pady=const.PAD_SMALL,
            cursor="arrow",
            selectbackground=self._bg,
            borderwidth=0,
            highlightthickness=0,
        )
        self._scrollbar.config(command=self._text.yview)
        self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        if content:
            self.set_content(content)

    def set_content(self, content):
        self._text.config(state=tk.NORMAL)
        self._text.delete("1.0", tk.END)
        self._text.insert(tk.END, content)
        self._text.config(state=tk.DISABLED)
        self._text.see(tk.END)

    def append(self, text):
        self._text.config(state=tk.NORMAL)
        self._text.insert(tk.END, text)
        self._text.config(state=tk.DISABLED)
        self._text.see(tk.END)

    def clear(self):
        self.set_content("")