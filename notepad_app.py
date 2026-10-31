import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path


class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("My Notepad")
        self.root.geometry("900x600")
        self.root.minsize(500, 350)

        self.file_path = None
        self.modified = False

        self.create_menu()
        self.create_toolbar()
        self.create_editor()

        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)
        self.update_title()

    def create_menu(self):
        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(
            label="New", accelerator="Ctrl+N", command=self.new_file
        )
        file_menu.add_command(
            label="Open", accelerator="Ctrl+O", command=self.open_file
        )
        file_menu.add_command(
            label="Save", accelerator="Ctrl+S", command=self.save_file
        )
        file_menu.add_command(
            label="Save As", accelerator="Ctrl+Shift+S",
            command=self.save_as
        )
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app)

        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(
            label="Delete Text", command=self.delete_text
        )
        edit_menu.add_command(
            label="Select All", command=self.select_all
        )

        menu_bar.add_cascade(label="File", menu=file_menu)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)

        self.root.config(menu=menu_bar)

        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind(
            "<Control-Shift-S>", lambda e: self.save_as()
        )

    def create_toolbar(self):
        toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        buttons = [
            ("New", self.new_file),
            ("Open", self.open_file),
            ("Save", self.save_file),
            ("Save As", self.save_as),
            ("Delete", self.delete_text),
        ]

        for text, command in buttons:
            tk.Button(
                toolbar,
                text=text,
                command=command,
                padx=10,
                pady=5
            ).pack(side=tk.LEFT, padx=3, pady=3)

    def create_editor(self):
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.editor = tk.Text(
            frame,
            wrap=tk.WORD,
            undo=True,
            font=("Tahoma", 12),
            padx=10,
            pady=10,
            yscrollcommand=scrollbar.set
        )
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=self.editor.yview)
        self.editor.bind("<<Modified>>", self.on_modified)

        status = tk.Label(
            self.root,
            text="Ready",
            anchor=tk.W,
            bd=1,
            relief=tk.SUNKEN
        )
        status.pack(side=tk.BOTTOM, fill=tk.X)
        self.status = status

    def on_modified(self, event=None):
        if self.editor.edit_modified():
            self.modified = True
            self.update_title()
            self.editor.edit_modified(False)

    def update_title(self):
        name = Path(self.file_path).name if self.file_path else "Untitled"
        mark = "*" if self.modified else ""
        self.root.title(f"{mark}{name} - My Notepad")

    def ask_save_changes(self):
        if not self.modified:
            return True

        answer = messagebox.askyesnocancel(
            "Unsaved Changes",
            "Do you want to save your changes?"
        )

        if answer is None:
            return False

        if answer:
            return self.save_file()

        return True
    def new_file(self):
        if not self.ask_save_changes():
            return

        self.editor.delete("1.0", tk.END)
        self.file_path = None
        self.modified = False
        self.editor.edit_modified(False)
        self.update_title()
        self.status.config(text="New document")

    def open_file(self):
        if not self.ask_save_changes():
            return

        path = filedialog.askopenfilename(
            title="Open Text File",
            filetypes=[
                ("Text Files", "*.txt"),
                ("All Files", "*.*")
            ]
        )

        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8-sig") as file:
                content = file.read()

            self.editor.delete("1.0", tk.END)
            self.editor.insert("1.0", content)

            self.file_path = path
            self.modified = False
            self.editor.edit_modified(False)
            self.update_title()
            self.status.config(text=f"Opened: {path}")

        except (OSError, UnicodeError) as error:
            messagebox.showerror("Open Error", str(error))

    def save_file(self):
        if self.file_path is None:
            return self.save_as()

        return self.write_file(self.file_path)

    def save_as(self):
        path = filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=".txt",
            filetypes=[
                ("Text Files", "*.txt"),
                ("All Files", "*.*")
            ]
        )

        if not path:
            return False

        return self.write_file(path)

    def write_file(self, path):
        content = self.editor.get("1.0", "end-1c")

        try:
            with open(path, "w", encoding="utf-8") as file:
                file.write(content)

            self.file_path = path
            self.modified = False
            self.editor.edit_modified(False)
            self.update_title()
            self.status.config(text=f"Saved: {path}")
            return True

        except OSError as error:
            messagebox.showerror("Save Error", str(error))
            return False

    def delete_text(self):
        if not self.editor.get("1.0", "end-1c"):
            return

        answer = messagebox.askyesno(
            "Delete Text",
            "Are you sure you want to delete all text?"
        )

        if answer:
            self.editor.delete("1.0", tk.END)
            self.status.config(text="Text deleted")

    def select_all(self):
        self.editor.tag_add("sel", "1.0", "end-1c")
        self.editor.mark_set("insert", "1.0")
        self.editor.see("insert")
        return "break"

    def exit_app(self):
        if self.ask_save_changes():
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TextEditor(root)
    root.mainloop()