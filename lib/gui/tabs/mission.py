import tkinter as tk
import re
from tkinter import ttk
from ..table import Table
from ..menu import Util, disable_menu
from ...mission import State


def create_table(parent):
    return Table(
        parent,
        columns=[{
            'id': '#0',
            'text': '#',
            'width': 25
        }, {
            'id': 'name',
            'text': '任務'
        }, {
            'id': 'host',
            'text': '主機',
            'width': 50,
            'anchor': 'center'
        }, {
            'id': 'state',
            'text': '狀態',
            'width': 70,
            'anchor': 'center'
        }, {
            'id': 'last_update',
            'text': '更新',
            'width': 100,
            'anchor': 'center',
            'sort': 'DESC'
        }])


def bind_menu(tab):
    """ TODO """
    util = Util(tab.table.tv, always_show=True)
    table = tab.table

    def create_menu():

        def callback(tv, menu, label):
            if not tv.selection():
                disable_menu(menu, label)

        def parent_item(tv, menu, label):
            selected = tv.selection()
            if not selected:
                disable_menu(menu, label)
            else:
                if len(selected) != 1:
                    disable_menu(menu, label)
                else:
                    iid = selected[0]
                    if tv.parent(iid):
                        disable_menu(menu, label)

        @util.bind_menu_set(parent_item)
        @util.bind_menu('移動到', '上一列')
        def _():
            tv = table.tv
            selected = tv.selection()
            iid = selected[0]
            index = tv.index(iid)
            if index > 0:
                tv.move(iid, '', index-1)

        @util.bind_menu_set(parent_item)
        @util.bind_menu('移動到', '下一列')
        def _():
            tv = table.tv
            selected = tv.selection()
            iid = selected[0]
            index = tv.index(iid)
            if index != len(tv.get_children()):
                tv.move(iid, '', index+1)

        @util.bind_menu_set(parent_item)
        @util.bind_menu('移動到', '第一列')
        def _():
            tv = table.tv
            selected = tv.selection()
            iid = selected[0]
            tv.move(iid, '', 0)

        @util.bind_menu_set(parent_item)
        @util.bind_menu('移動到', '最後列')
        def _():
            tv = table.tv
            selected = tv.selection()
            iid = selected[0]
            tv.move(iid, '', len(tv.get_children())-1)

        @util.bind_menu_set(callback)
        @util.bind_menu('清除任務')
        def _():
            for key in table.selected():
                tab.main.current.put_normal('MISSION_REMOVE', key)

        @util.bind_menu('清除所有任務')
        def _():
            for key in table.get_children():
                tab.main.current.put_normal('MISSION_REMOVE', key)

        @util.bind_menu('清除所有已完成')
        def _():
            """ TODO: update parent count and total and mission """
            for parent in table.get_children():
                for tree_key in parent.usage['OK'].copy():
                    tab.main.mgr.remove(parent, key=tree_key)

                state = table.set(parent, 'state')
                if state in [State.FINISHED, State.OK]:
                    tab.main.mgr.remove(parent, key=parent)
                else:
                    tab.main.current.put_normal('UPDATE_PARENT', parent)

    util.register(create_menu)


class MissionTab(ttk.Frame):
    def __init__(self, main_window, master=None, **kw):
        super().__init__(master, **kw)
        self.main = main_window
        self.create_view()

    def create_view(self):
        self.table = create_table(self)

    def bind_menu(self):
        bind_menu(self)

    def bind_event(self):
        self.bind_menu()
