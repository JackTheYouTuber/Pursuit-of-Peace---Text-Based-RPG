import tkinter as tk
from .theme import CARD_BG, TEXT_FG, FONT_BODY, PAD_SMALL

class TextDisplay(tk.Frame):
    def __init__(self, parent, content="", **kwargs):
        bg = kwargs.pop('bg', CARD_BG)
        super().__init__(parent, bg=bg, **kwargs)
        self._bg = bg
        self._font = FONT_BODY
        self._fg = TEXT_FG

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
            padx=PAD_SMALL,
            pady=PAD_SMALL,
            cursor="arrow",
            selectbackground=self._bg,
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