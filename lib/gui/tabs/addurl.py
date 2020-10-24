import tkinter as tk
from tkinter import ttk
import pyperclip
from ..common import set_text, set_enable


class AddTab(ttk.Frame):
    def __init__(self, main_window, master=None, **kw):
        super().__init__(master, **kw)
        self.main = main_window
        self.create_view()

    def create_view(self):
        self.btn_analysis = ttk.Button(self, text='開始分析')
        self.btn_analysis.pack(anchor=tk.W)
        tk.Label(self, text='在此處貼上連結︰').pack(anchor=tk.W)
        text = tk.Text(self)
        text.pack(expand=True, fill=tk.BOTH)
        self.text = text

    def bind_event(self):
        @self.main.current.register('ANALYSIS_START')
        def _():
            set_enable(self.btn_analysis, False)

        @self.main.current.register('ANALYSIS_FINISH')
        def _():
            set_enable(self.btn_analysis, True)

        def paste(event):
            widget = event.widget
            menu = tk.Menu(widget, tearoff=0)
            menu.add_command(label='貼上',
                             command=lambda: set_text(
                                 widget, pyperclip.paste()))
            menu.post(event.x_root, event.y_root)
        self.text.bind('<Button-3>', paste)

        def analysis():
            pyperclip.copy('')
            text = self.text.get('1.0', 'end-1c')
            if text:
                set_text(self.text, '')
                self.main.analyzer.put_normal('ANALYSIS', text)
        self.btn_analysis['command'] = analysis

        def focus_in(event):
            widget = event.widget
            set_text(widget, pyperclip.paste())
        self.text.bind("<FocusIn>", focus_in)
