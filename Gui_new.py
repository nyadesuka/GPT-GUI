import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk
import g4f.models
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
            # provider=Blackbox
        )
        response_text = response.choices[0].message.content

        self.editor.insert("end", "Бот: " + response_text + "\n", "bot")
        self.editor.see("end")

class ChatTab:
    def __init__(self, notebook):
        self.notebook = notebook
        self.create_chat_tab()

    def create_chat_tab(self):
        self.frame = ttk.Frame(self.notebook)
        self.notebook.add(self.frame, text="FurryPorn" + str(self.notebook.index("end") + 1))

        self.editor = tk.Text(self.frame, wrap="word", bg="black", fg="white", font=self.get_font())
        self.editor.grid(column=0, row=0, sticky="NSEW")

        ys = tk.Scrollbar(self.frame, orient="vertical", command=self.editor.yview)
        ys.grid(column=1, row=0, sticky="NS")
        xs = tk.Scrollbar(self.frame, orient="horizontal", command=self.editor.xview)
        xs.grid(column=0, row=1, sticky="EW")

        self.editor["yscrollcommand"] = ys.set
        self.editor["xscrollcommand"] = xs.set

        entry_frame = ttk.Frame(self.frame)
        entry_frame.grid(column=0, row=2, sticky="EW")

        self.entry = tk.Text(entry_frame, wrap="word", bg="black", fg="white", font=self.get_font())
        self.entry.grid(column=0, row=0, sticky="NSEW")

        ys = tk.Scrollbar(entry_frame, orient="vertical", command=self.entry.yview)
        ys.grid(column=1, row=0, sticky="NS")
        xs = tk.Scrollbar(entry_frame, orient="horizontal", command=self.entry.xview)
        xs.grid(column=0, row=1, sticky="EW")

        self.entry["yscrollcommand"] = ys.set
        self.entry["xscrollcommand"] = xs.set

        send_button = MyButton(None, None, None).create_button(self.frame, "Отправить", self.send_message, "TButton")
        send_button.grid(column=0, row=3, sticky="EW")

        self.functionality = Functionality(self.editor, self.entry)

        self.entry.bind("<Return>", self.functionality.send_message)
        self.entry.bind("<Control-v>", self.functionality.paste_text_entry)
        self.editor.bind("<Control-v>", self.functionality.paste_text_editor)
        self.entry.bind("<Control-y>", lambda event: self.editor.insert("end", self.editor.get("1.0", "end-1c")))
        self.entry.bind("<Key>", self.functionality.on_text_change)

    def get_font(self):
        font = tkFont.Font(family="Times New Roman", size=14)
        return font

    def send_message(self, event=None):
        query = self.entry.get("1.0", "end-1c")
        self.entry.delete("1.0", "end")

        self.editor.insert("end", "Пользователь: " + query + "\n", "user")
        self.editor.see("end")

        client = Client()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"{query}"}]
            # provider=Blackbox
        )
        response_text = response.choices[0].message.content

        self.editor.insert("end", "Бот: " + response_text + "\n", "bot")
        self.editor.see("end")
        self.editor.tag_config("user", foreground="white", font=self.get_font())
        self.editor.tag_config("bot", foreground="#16C60C", font=self.get_font())


class FurryPornApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Directed by NyaDesuKa")
        self.root.iconbitmap('gachi.ico')
        self.create_notebook()
        self.create_menu()

    def create_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=5)
        self.create_new_chat_tab()

    def create_menu(self):
        menu = Menu(self.root)
        self.root.config(menu=menu)
        self.create_file_menu(menu)
        self.create_help_menu(menu)

    def create_file_menu(self, menu: Menu):
        file_menu = Menu(menu)
        menu.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Новая вкладка", command=self.create_new_chat_tab)
        file_menu.add_command(label="Переименовать вкладку", command=self.rename_tab)
        file_menu.add_command(label="Закрыть вкладку", command=self.close_tab)

    def create_help_menu(self, menu: Menu):
        help_menu = Menu(menu)
        menu.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.open_about_window)

    def rename_tab(self):
        tab_index = self.notebook.index("current")
        self.rename_tab_dialog(tab_index)

    def rename_tab_dialog(self, tab_index: int):
        def on_rename():
            new_name = entry.get()
            if new_name:
                self.notebook.tab(tab_index, text=new_name)
                rename_window.destroy()

        rename_window = tk.Toplevel(self.root)
        rename_window.title("Переименовать вкладку")

        label = tk.Label(rename_window, text="Введите новое имя для вкладки:")
        label.pack(pady=5)

        entry = tk.Entry(rename_window)
        entry.pack(pady=5)

        button = tk.Button(rename_window, text="Переименовать", command=on_rename)
        button.pack(pady=5)

    def close_tab(self):
        self.notebook.forget(self.notebook.select())

    def create_new_chat_tab(self):
        chat_tab = ChatTab(self.notebook)
        chat_tab.functionality = Functionality(chat_tab.editor, chat_tab.entry)

    def open_about_window(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("О программе")

        about_label = tk.Label(about_window, text="ГЫГ")
        about_label.pack(pady=5)

        ok_button = tk.Button(about_window, text="ОК", command=about_window.destroy)
        ok_button.pack(pady=5)

def main():
    root = tk.Tk()
    FurryPornApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()