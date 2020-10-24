import tkinter as tk
from tkinter import ttk
from functools import partial


class Table(object):

    def __init__(self, parent, tv_opt={}, columns=[]):
        self.sort_mode = None
        self.sort_on = None
        self.cols = {c['id']: c for c in columns}
        self.listeners = {}

        # scrollbar
        scrbar = ttk.Scrollbar(parent, orient=tk.VERTICAL)
        scrbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrbar = scrbar

        # treeview
        tv = ttk.Treeview(
            parent,
            columns=[c["id"] for c in columns if c["id"] != "#0"],
            yscrollcommand=scrbar.set,
            **tv_opt
        )
        for c in columns:
            tv.heading(c["id"], text=c["text"], command=partial(self.sort_table, id=c["id"]))
            tv.column(c["id"], **{k: v for k, v in c.items() if k in ("width", "anchor")})
        tv.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.tv = tv
        scrbar.config(command=tv.yview)

        self.key_index = {}
        self.iid_index = {}

    def add(self, row, *, parent='', key=None):
        if key and key in self.key_index:
            return
        parent_iid = self.key_index.get(parent, '')

        iid = self.tv.insert(parent_iid, tk.END)
        if not key:
            key = iid
        self.key_index[key] = iid
        self.iid_index[iid] = key
        self.update(key, **row)
        return key

    def update(self, key, **kwargs):
        if key not in self.key_index:
            return
        iid = self.key_index[key]
        for column, value in kwargs.items():
            if column == '#0':
                self.tv.item(iid, text=value)
            else:
                self.tv.set(iid, column, value)

    def remove(self, *rows):
        self.tv.delete(*[self.key_index[k] for k in rows])
        for key in rows:
            if key not in self.key_index:
                continue
            iid = self.key_index[key]
            del self.key_index[key]
            del self.iid_index[iid]

    def sort_table(self, id=None):
        if id == '#0':
            return
        if self.sort_on == id:
            if self.sort_mode == 'ASC':
                self.sort_mode = 'DESC'
            else:
                self.sort_mode = 'ASC'
        else:
            if self.sort_on:
                # reset text
                self.tv.heading(self.sort_on, text=self.cols[self.sort_on]['text'])
            self.sort_mode = self.cols[id].get('sort', 'ASC')
            self.sort_on = id

        if self.sort_mode == 'ASC':
            arrow = '▲'
        else:
            arrow = '▼'
        self.tv.heading(id, text=self.cols[id]['text'] + arrow)

        if listener := self.listeners.get('on_sort', self.on_sort):
            listener(self)

    def on(self, event_name, listener):
        self.listeners['on_' + event_name] = listener

    @staticmethod
    def on_sort(table, key=lambda t: t[0]):
        l = [(table.tv.set(iid, table.sort_on), iid) for iid in table.tv.get_children()]
        l.sort(key=key, reverse=table.sort_mode == 'DESC')
        # rearrange items in sorted positions
        for idx, (_, iid) in enumerate(l):
            table.tv.move(iid, '', idx)

    def identify_row(self, y):
        iid = self.tv.identify_row(y)
        return self.iid_index.get(iid, None)

    def selection_set(self, key):
        if key in self.key_index:
            iid = self.key_index.get(key)
            return self.tv.selection_set(iid)

    def item(self, key, *args, **kwargs):
        if key in self.key_index:
            iid = self.key_index.get(key)
            return self.tv.item(iid, *args, **kwargs)

    def get_children(self, key=None):
        if key in self.key_index:
            iid = self.key_index.get(key)
            return [self.iid_index[i] for i in self.tv.get_children(iid)]
        if key is None:
            return [self.iid_index[i] for i in self.tv.get_children(key)]

    def set(self, key, column=None, value=None):
        if key in self.key_index:
            iid = self.key_index.get(key)
            return self.tv.set(iid, column, value)

    def parent(self, key):
        if key in self.key_index:
            iid = self.key_index.get(key)
            if parent_iid := self.tv.parent(iid):
                return self.iid_index[parent_iid]

    def exists(self, key):
        if key in self.key_index:
            iid = self.key_index.get(key)
            return self.tv.exists(iid)

    def index(self, key):
        if key in self.key_index:
            iid = self.key_index.get(key)
            return self.tv.index(iid)

    def selected(self):
        return [self.iid_index[i] for i in self.tv.selection()]

    def bind(self, event, handler):
        self.tv.bind(event, handler)
