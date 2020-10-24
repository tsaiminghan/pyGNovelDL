import tkinter as tk


def noop(*_, **__):
    pass


def enable_menu(menu, label):
    menu.entryconfig(label, state=tk.NORMAL)


def disable_menu(menu, label):
    menu.entryconfig(label, state=tk.DISABLED)


class Util(object):
    def __init__(self, treeview, **kw):
        self.tv = treeview
        self.always_show = kw.get('always_show', False)

        def handle(event):
            """ iid maybe be empty """
            tv = event.widget
            iid = tv.identify_row(event.y)
            if len(tv.selection()) < 2:
                tv.selection_set(iid)
            if iid or self.always_show:
                menu = self.gen_menu()
                menu.post(event.x_root, event.y_root)
        treeview.bind('<Button-3>', handle)

    def register(self, create_menu):
        self.create_menu = create_menu

    def gen_menu(self):
        def gen(d):
            menu = tk.Menu(self.tv, tearoff=False)
            for k, v in d.items():
                if callable(v):
                    menu.add_command(label=k, command=v)
                    self.change_state.get(v, noop)(self.tv, menu, k)
                else:
                    menu.add_cascade(label=k, menu=gen(v))
            return menu
        self.menu = {}
        self.change_state = {}
        self.create_menu()
        return gen(self.menu)

    def bind_menu_set(self, callback):
        def inner(func):
            self.change_state[func] = callback
            return func
        return inner

    def bind_menu(self, *args):
        def inner(func):
            def gen(d, arg0, *args):
                if arg0:
                    d1 = d.get(arg0, {})
                    assert isinstance(d1, dict), f'{arg0} already set a command'
                    d[arg0] = gen(d1, *args, None)
                    return d
                return func

            gen(self.menu, *args)
            return func
        return inner


