import tkinter as tk
from tkinter import ttk, messagebox


def is_disabled(widget):
    return str(widget['state']) == tk.DISABLED


def set_enable(widget, enable):
    widget['state'] = tk.NORMAL if enable else tk.DISABLED


def set_text(widget, text):
    if isinstance(widget, ttk.Combobox):
        widget.current(widget['values'].index(text))
    elif isinstance(widget, tk.Text):
        widget.delete('1.0', tk.END)
        widget.insert('1.0', text)
    elif isinstance(widget, tk.Entry):
        widget.delete(0, tk.END)
        widget.insert(tk.END, text)
    elif isinstance(widget, (ttk.Label, tk.Label)):
        widget['text'] = text


def message_box(type, *args, **kwargs):
    """Pause the loop when using messagebox"""
    if type in ("okcancel", "yesno", "yesnocancel", "retrycancel"):
        name = "ask" + type
    else:
        name = "show" + type
    func = getattr(messagebox, name)
    return func(*args, **kwargs)
