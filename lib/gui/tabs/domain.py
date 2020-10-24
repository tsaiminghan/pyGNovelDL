import tkinter as tk
from tkinter import ttk
from ..table import Table
from ..menu import Util
from ...websites import _mod


def create_table(parent):
    return Table(parent, columns=[{
        'id': 'host',
        'text': '域名'
    }, {
        'id': 'mod',
        'text': '模組',
        'anchor': 'center'
    }], tv_opt={'show': 'headings'})


class DomainTab(ttk.Frame):
    def __init__(self, main_window, master=None, **kw):
        super().__init__(master, **kw)
        self.main = main_window
        self.create_view()

    def create_view(self):
        self.table = create_table(self)
        for m in _mod.mod_list:
            self.table.add({
                'host': m.NETLOC,
                'mod': m.NAME
            })

    def bind_event(self):
        def open_url(event):
            from ...cmds.browser import Command
            tv = event.widget
            if iid := tv.identify_row(event.y):
                tv.selection_set(iid)
                url = tv.set(iid, 'host')
                menu = tk.Menu(tv, tearoff=0)
                menu.add_command(label='開啟網頁',
                                 command=lambda: Command.open(url))
                menu.post(event.x_root, event.y_root)
        self.table.bind('<Button-3>', open_url)



