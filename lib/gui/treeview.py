import tkinter as tk
from tkinter import ttk


# https://www.itread01.com/content/1549184437.html
# https://docs.python.org/3/library/tkinter.ttk.html
#

master = tk.Tk()
master.title('測試')

master.resizable(width=1, height=1)
# master.geometry('500x280')

tree = ttk.Treeview(master)
# tree = ttk.Treeview(master, show='headings')
tree.pack(side=tk.LEFT, expand=True, fill='both')


# tree.pack(side=tk.TOP,fill=tk.X)


def rightClickMenu(event):
    def hello():
        print("hello!")
        # create a popup menu

    rowID = tree.identify('item', event.x, event.y)
    _iid = tree.identify_row(event.y)
    tree.selection_set(_iid)
    print(event.x, event.y, rowID)
    if rowID:
        menu = tk.Menu(master, tearoff=0)
        menu.add_command(label="Undo", command=hello)
        menu.add_command(label="Redo", command=hello)
        menu.post(event.x_root, event.y_root)


tree.bind('<3>', rightClickMenu)

verscrlbar = ttk.Scrollbar(master,
                           orient="vertical",
                           command=tree.yview)
# verscrlbar.pack(side =tk.RIGHT, fill=tk.X)
# verscrlbar.pack(side =tk.RIGHT, fill=tk.BOTH)
verscrlbar.pack(side=tk.RIGHT, fill=tk.Y)
tree.configure(yscrollcommand=verscrlbar.set)

# stretch=tk.NO ，用戶無法修改列的寬度。
tree["columns"] = ("one", "two", "three")
tree.column("#0", width=270, minwidth=270, stretch=tk.NO)
tree.column("one", width=150, minwidth=150, stretch=tk.NO)
tree.column("two", width=400, minwidth=200)
tree.column("three", width=80, minwidth=50, stretch=tk.NO)

tree.heading("#0", text="Name", anchor=tk.W)
tree.heading("one", text="Date modified", anchor=tk.W)
tree.heading("two", text="Type", anchor=tk.W)
tree.heading("three", text="Size", anchor=tk.W)

# Level 1
folder1 = tree.insert("", 0, text="Folder 1", values=("23-Jun-17 11:05", "File folder", ""))
tree.insert("", 1, text="text_file.txt", values=("23-Jun-17 11:25", "TXT file", "1 KB"))

for i in range(100):
    tree.insert("", i + 1, text=f"{i}.txt", values=("23-Jun-17 11:25", "TXT file", "1 KB"))

# Level 2
tree.insert(folder1, "end", text="photo1.png", values=("23-Jun-17 11:28", "PNG file", "2.6 KB"))
tree.insert(folder1, "end", text="photo2.png", values=("23-Jun-17 11:29", "PNG file", "3.2 KB"))
iid3 = tree.insert(folder1, "end", text="photo3.png", values=("23-Jun-17 11:30", "PNG file", "3.1 KB"))

print('iid3 next=', tree.next(iid3))

kwargs = {
   #'#0': '0000',
   'one': '1111',
   'two': '2222',
   'three': '33333'
}
iid = tree.insert('', tk.END)
for column, value in kwargs.items():
    tree.set(iid, column, value)
r = tree.item(iid)
tree.item(iid, text='aaa', tags=('red',))


master.mainloop()
