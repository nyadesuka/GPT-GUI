from tkinter import Tk, Text, Scrollbar
from tkinter import ttk
import pyperclip
from tkinter import simpledialog
from g4f.client import Client
from tkinter import Menu
import logging

logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)
class MyButton:
    def __init__(self, color, font, size):
        self.color = color
        self.font = font
        self.size = size

    def create_button(self, root, text, command, style_name, width=None):
        button = ttk.Button(
            root,
            text=text,
            command=command,
            style=style_name,
            width=width
        )
        return button
class Functionality:
    def __init__(self, editor, entry):
        self.editor = editor
        self.entry = entry

    def on_text_change(self, event):
        lines = self.entry.get("1.0", "end-1c").count('\n') + 1
        if lines <= 6:
            self.entry.config(height=lines)
        else:
            # Limiting the scrollbar to scroll only up to 4 lines down
            self.entry.yview_scroll(lines - 4, "units")

    def paste_text_entry(self, event):
        clipboard_text = pyperclip.paste()
        self.entry.insert("end", clipboard_text)

    def paste_text_editor(self, event):
        clipboard_text = pyperclip.paste()
        self.editor.insert("end", clipboard_text)

    def send_message(self, event=None):
        query = self.entry.get("1.0", "end-1c")
        self.entry.delete("1.0", "end")

        self.editor.insert("end", "Пользователь: " + query + "\n", "user")
        self.editor.see("end")

        client = Client()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"{query}"}]
        )
        response_text = response.choices[0].message.content


        self.editor.insert("end", "Бот: " + response_text + "\n", "bot")
        self.editor.see("end")


class Binds:
    def __init__(self, root, functionality):
        self.root = root
        self.functionality = functionality

        self.root.bind_all("<Control-v>", self.functionality.paste_text_entry)
        self.root.bind_all("<Control-V>", self.functionality.paste_text_editor)
        self.root.bind('<Shift-Return>', self.functionality.send_message)


class ChatTab:
    def __init__(self, notebook):
        self.notebook = notebook
        self.functionality = Functionality(None, None)  # Placeholder
        self.create_chat_tab()

    def create_chat_tab(self):
        self.frame = ttk.Frame(self.notebook)
        self.notebook.add(self.frame, text="FurryPorn" + str(self.notebook.index("end") + 1))
        editor = Text(self.frame, wrap="word", bg="black", fg="white", font=(font, 14))
        editor.grid(column=0, row=0, sticky="NSEW")

        ys = Scrollbar(self.frame, orient="vertical", command=editor.yview)
        ys.grid(column=1, row=0, sticky="NS")
        xs = Scrollbar(self.frame, orient="horizontal", command=editor.xview)
        xs.grid(column=0, row=1, sticky="EW")

        editor["yscrollcommand"] = ys.set
        editor["xscrollcommand"] = xs.set

        entry_frame = ttk.Frame(self.frame)
        entry_frame.grid(column=0, row=2, sticky="EW")

        entry = Text(entry_frame, wrap="word", height=2, font=(font, 16), bg="black", fg="white", insertbackground="white")

        entry.grid(column=0, row=0, sticky="EW")

        # Add scrollbars to the entry widget
        entry_ys = Scrollbar(entry_frame, orient="vertical", command=entry.yview)
        entry_ys.grid(column=1, row=0, sticky="NS")
        entry["yscrollcommand"] = entry_ys.set

        self.functionality = Functionality(editor, entry)
        entry.bind("<Key>", self.functionality.on_text_change)

        my_button = MyButton(color='black', font=font, size=16)

        style = ttk.Style()
        style.configure('my.TButton', foreground=my_button.color, background=my_button.color,
                        font=(my_button.font, my_button.size, 'bold'))


        send_button = my_button.create_button(
            entry_frame,
            text="Отправить",
            command=self.functionality.send_message,
            style_name='my.TButton',
            width=10
        )
        send_button.grid(column=1, row=0, sticky="EW", padx=(5, 0))

        editor.tag_config("user", foreground="white", font=(font, 16, "bold"))
        editor.tag_config("bot", foreground="#16C60C", font=(font, 16, "bold"))


        entry_frame.grid_columnconfigure(1, minsize=100)
    def rename_chat(self, new_name):
        index = self.notebook.index(self.frame)
        self.notebook.tab(index, text=new_name)

font = "Times New Roman"
root = Tk()
root.title("Directed by NyaDesuKa (and the Circus.team)")
root.iconbitmap('gachi.ico')
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

notebook = ttk.Notebook(root)
notebook.grid(column=0, row=0, sticky="NSEW")

initial_chat = ChatTab(notebook)

menu_bar = Menu(root)
root.config(menu=menu_bar)
tab_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Меню", menu=tab_menu)

def rename_tab(chat_tab):
    new_name = simpledialog.askstring("Переименовать вкладку", "Введите новое имя для вкладки:")
    if new_name:
        chat_tab.rename_chat(new_name)

def add_tab_menu(tab):
    tab_menu.add_command(label=f"Переименовать {tab.notebook.tab(tab.frame, 'text')}", command=lambda: rename_tab(tab))

add_tab_menu(initial_chat)


def create_new_chat_tab():
    new_chat = ChatTab(notebook)
    add_tab_menu(new_chat)

my_button = MyButton(color='black', font=font, size=16)
style = ttk.Style()
style.configure('my.TButton', foreground=my_button.color, background=my_button.color,
                font=(my_button.font, my_button.size, 'bold'))
new_tab_button = my_button.create_button(root, text="Новый чат", command=create_new_chat_tab, style_name='my.TButton', width=5)
new_tab_button.grid(column=0, row=1, sticky='EW')

binds = Binds(root, initial_chat.functionality)

root.mainloop()
