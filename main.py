import tkinter as tk
from tkinter import messagebox, simpledialog, font

class NoteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Приложение для заметок")
        self.root.geometry("500x500")

        self.notes = []
        self.current_font = "Arial" # Начальный шрифт
        self.font_size = 12

        # Создаем меню
        menubar = tk.Menu(root)
        root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Добавить заметку", command=self.add_note)
        file_menu.add_command(label="Удалить заметку", command=self.delete_note)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=root.quit)

        # Создаем текстовое поле для заметок
        self.text_area = tk.Text(root, wrap='word', font=(self.current_font, self.font_size))
        self.text_area.pack(expand=True, fill='both')

        # Отключаем возможность ввода текста в текстовом поле
        self.text_area.config(state=tk.DISABLED) 

        # Создаем кнопку "Добавить заметку"
        self.add_button = tk.Button(root, text="Добавить заметку", command=self.add_note)
        self.add_button.pack(pady=10)

        # Создаем меню шрифтов
        font_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Шрифт", menu=font_menu)
        font_menu.add_command(label="Arial", command=lambda: self.change_font("Arial"))
        font_menu.add_command(label="Times New Roman", command=lambda: self.change_font("Times New Roman"))
        font_menu.add_command(label="Courier New", command=lambda: self.change_font("Courier New"))

    def add_note(self):
        try:
            note = simpledialog.askstring("Добавить заметку", "Введите текст заметки:")
            if note and note.strip():
                self.notes.append(note)
                self.update_text_area()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def delete_note(self):
        try:
            selected_note_index = self.text_area.index(tk.SEL_FIRST) # Получаем индекс выделенного текста
            selected_note = self.text_area.get(selected_note_index, tk.SEL_LAST)
            if selected_note in self.notes:
                self.notes.remove(selected_note)
                self.update_text_area()
            else:
                messagebox.showwarning("Предупреждение", "Выделенная заметка не найдена.")
        except tk.TclError:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выделите заметку для удаления.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def update_text_area(self):
        self.text_area.config(state=tk.NORMAL) # Включаем редактирование
        self.text_area.delete(1.0, tk.END) # Очищаем текстовое поле
        for note in self.notes:
            self.text_area.insert(tk.END, note + "\n") # Добавляем заметки в текстовое поле
        self.text_area.config(state=tk.DISABLED) # Выключаем редактирование

    def change_font(self, new_font):
        self.current_font = new_font
        self.text_area.config(font=(self.current_font, self.font_size))
        self.update_text_area() # Обновляем текстовое поле после смены шрифта

if __name__ == "__main__":
    root = tk.Tk()
    app = NoteApp(root)
    root.mainloop()