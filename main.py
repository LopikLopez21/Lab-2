import tkinter as tk
from tkinter import ttk, font, messagebox, filedialog, simpledialog
import json
from datetime import datetime
import os


class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Расширенные заметки")
        self.root.geometry("1200x800")

        # Данные
        self.notes = {}
        self.categories = ["Общее", "Работа", "Личное", "Покупки"]
        self.current_category = "Общее"
        self.current_font = ("Arial", 12)

        # Настройка стилей
        self.setup_styles()
        self.setup_gui()
        self.load_notes()

    def setup_styles(self):
        # Настройка шрифтов и стилей
        self.text_tags = {
            "bold": {"font": font.Font(weight="bold")},
            "italic": {"font": font.Font(slant="italic")},
            "underline": {"underline": True},
            "strikethrough": {"overstrike": True}
        }

    def setup_gui(self):
        # Создание главного меню
        self.create_menu()

        # Основной контейнер
        self.main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Создание левой панели
        self.create_left_panel()

        # Создание правой панели
        self.create_right_panel()

        # Создание контекстного меню
        self.create_context_menu()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Новая заметка", command=self.new_note)
        file_menu.add_command(label="Импорт", command=self.import_notes)
        file_menu.add_command(label="Экспорт", command=self.export_notes)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)

    def create_left_panel(self):
        self.left_panel = ttk.Frame(self.main_container)
        self.main_container.add(self.left_panel)

        # Категории
        self.category_frame = ttk.LabelFrame(self.left_panel, text="Категории")
        self.category_frame.pack(fill=tk.X, padx=5, pady=5)

        # Комбобокс для категорий
        self.category_var = tk.StringVar(value=self.categories[0])
        self.category_combo = ttk.Combobox(self.category_frame,
                                           textvariable=self.category_var,
                                           values=self.categories)
        self.category_combo.pack(fill=tk.X, padx=5, pady=5)
        self.category_combo.bind('<<ComboboxSelected>>', self.change_category)

        # Кнопка добавления категории
        ttk.Button(self.category_frame, text="Добавить категорию",
                   command=self.add_category).pack(fill=tk.X, padx=5, pady=2)

        # Кнопка удаления категории
        ttk.Button(self.category_frame, text="Удалить категорию",
                   command=self.delete_category).pack(fill=tk.X, padx=5, pady=2)

        # Список заметок
        self.notes_list_frame = ttk.LabelFrame(self.left_panel, text="Заметки")
        self.notes_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Список с прокруткой
        self.notes_listbox = tk.Listbox(self.notes_list_frame)
        scrollbar = ttk.Scrollbar(self.notes_list_frame, orient=tk.VERTICAL,
                                  command=self.notes_listbox.yview)
        self.notes_listbox.config(yscrollcommand=scrollbar.set)

        self.notes_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.notes_listbox.bind('<<ListboxSelect>>', self.load_note)

    def create_right_panel(self):
        self.right_panel = ttk.Frame(self.main_container)
        self.main_container.add(self.right_panel)

        # Панель инструментов
        self.create_toolbar()

        # Текстовый редактор
        self.text_editor = tk.Text(self.right_panel, wrap=tk.WORD, undo=True)
        self.text_editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Панель задач
        self.create_task_panel()
        self.task_panel.pack(fill=tk.X, padx=5, pady=5)
    def create_toolbar(self):
        self.toolbar = ttk.Frame(self.right_panel)
        self.toolbar.pack(fill=tk.X, padx=5, pady=5)

        # Выбор шрифта
        self.font_family = ttk.Combobox(self.toolbar, values=list(font.families()), width=20)
        self.font_family.set("Arial")
        self.font_family.pack(side=tk.LEFT, padx=2)
        self.font_family.bind('<<ComboboxSelected>>', self.change_font)

        # Размер шрифта
        self.font_size = ttk.Spinbox(self.toolbar, from_=8, to=72, width=5)
        self.font_size.set(12)
        self.font_size.pack(side=tk.LEFT, padx=2)
        self.font_size.bind('<Return>', self.change_font)

    def create_task_panel(self):
        self.task_panel = ttk.Frame(self.right_panel)
        self.task_panel.pack(fill=tk.X, padx=5, pady=5)

        # Чекбокс "Выполнено"
        self.completed_var = tk.BooleanVar()
        self.completed_checkbox = ttk.Checkbutton(self.task_panel, text="Выполнено",
                                                  variable=self.completed_var,
                                                  command=self.toggle_completed)
        self.completed_checkbox.pack(side=tk.LEFT, padx=5)

        # Кнопки управления
        ttk.Button(self.task_panel, text="Сохранить",
                   command=self.save_note).pack(side=tk.RIGHT, padx=2)
        ttk.Button(self.task_panel, text="Удалить",
                   command=self.delete_note).pack(side=tk.RIGHT, padx=2)

    def create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Вырезать", command=lambda: self.text_editor.event_generate("<<Cut>>"))
        self.context_menu.add_command(label="Копировать", command=lambda: self.text_editor.event_generate("<<Copy>>"))
        self.context_menu.add_command(label="Вставить", command=lambda: self.text_editor.event_generate("<<Paste>>"))
        self.text_editor.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def change_font(self, event=None):
        try:
            font_name = self.font_family.get()
            font_size = int(self.font_size.get())
            self.text_editor.config(font=(font_name, font_size))
            self.text_editor.tag_config("completed", font=(font_name, font_size, "overstrike"))
        except tk.TclError:
            pass
    def add_category(self):
        new_category = simpledialog.askstring("Новая категория",
                                               "Введите название категории:")
        if new_category and new_category not in self.categories:
            self.categories.append(new_category)
            self.category_combo['values'] = self.categories
            self.save_notes()

    def delete_category(self):
        current_category = self.category_var.get()
        if current_category in self.categories:
            if messagebox.askyesno("Подтверждение", "Удалить категорию?"):
                self.categories.remove(current_category)
                self.category_combo['values'] = self.categories
                self.save_notes()
                self.update_notes_list()

    def new_note(self):
        title = simpledialog.askstring("Новая заметка", "Введите название заметки")
        if title:
            self.notes[title] = {
                "content": "",
                "category": self.current_category,
                "completed": False,
                "tags": []
            }
            self.update_notes_list()
            self.notes_listbox.select_set(tk.END)
            self.load_note(None)

    def save_note(self):
        selection = self.notes_listbox.curselection()
        if selection:
            title = self.notes_listbox.get(selection[0])
            self.notes[title]["content"] = self.text_editor.get("1.0", tk.END)
            self.notes[title]["completed"] = self.completed_var.get()
            self.save_notes()
            messagebox.showinfo("Успех", "Заметка сохранена")

    def delete_note(self):
        selection = self.notes_listbox.curselection()
        if selection:
            title = self.notes_listbox.get(selection[0])
            if messagebox.askyesno("Подтверждение", "Удалить заметку?"):
                del self.notes[title]
                self.update_notes_list()
                self.text_editor.delete("1.0", tk.END)
                self.save_notes()

    def toggle_completed(self):
        selection = self.notes_listbox.curselection()
        if selection:
            title = self.notes_listbox.get(selection[0])
            self.notes[title]["completed"] = self.completed_var.get()
            if self.completed_var.get():
                self.text_editor.tag_config("completed", font=("Arial", 12, "overstrike"))
                self.text_editor.tag_add("completed", "1.0", tk.END)
            else:
                self.text_editor.tag_remove("completed", "1.0", tk.END)
                self.text_editor.tag_config("completed", font=("Arial", 12))
            self.save_notes()

    def change_category(self, event=None):
        self.current_category = self.category_var.get()
        self.update_notes_list()

    def update_notes_list(self):
        self.notes_listbox.delete(0, tk.END)
        for title, note in self.notes.items():
            if note["category"] == self.current_category:
                self.notes_listbox.insert(tk.END, title)

    def load_note(self, event):
        selection = self.notes_listbox.curselection()
        if selection:
            title = self.notes_listbox.get(selection[0])
            note = self.notes[title]
            self.text_editor.delete("1.0", tk.END)
            self.text_editor.insert("1.0", note["content"])
            self.completed_var.set(note["completed"])
            if note["completed"]:
                self.text_editor.tag_add("strikethrough", "1.0", tk.END)

    def save_notes(self):
        with open("notes.json", "w", encoding="utf-8") as f:
            json.dump({"notes": self.notes, "categories": self.categories}, f)

    def load_notes(self):
        try:
            with open("notes.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.notes = data.get("notes", {})
                self.categories = data.get("categories", self.categories)
                self.category_combo['values'] = self.categories
                self.update_notes_list()
        except FileNotFoundError:
            pass

    def import_notes(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                title = os.path.basename(file_path)
                self.notes[title] = {
                    "content": content,
                    "category": self.current_category,
                    "completed": False,
                    "tags": []
                }
                self.update_notes_list()
                self.save_notes()

    def export_notes(self):
        selection = self.notes_listbox.curselection()
        if selection:
            title = self.notes_listbox.get(selection[0])
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.notes[title]["content"])

if __name__ == "__main__":
    root = tk.Tk()
    app = NotesApp(root)
    root.mainloop()
