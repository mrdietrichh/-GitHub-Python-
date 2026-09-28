import tkinter as tk
from tkinter import ttk, messagebox

from database import fetch_all, fetch_one, execute


class ExercisesTab(ttk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, padding=10)
        self.user = user

        top = ttk.Frame(self)
        top.pack(fill='x', pady=(0, 8))
        ttk.Button(top, text="Добавить", command=self.add).pack(side='left')
        ttk.Button(top, text="Редактировать", command=self.edit).pack(side='left', padx=6)
        ttk.Button(top, text="Удалить", command=self.delete).pack(side='left')
        ttk.Button(top, text="Обновить", command=self.reload).pack(side='right')

        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill='x', pady=(0, 6))
        ttk.Label(filter_frame, text="Поиск:").pack(side='left')
        self.search_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.search_var, width=30).pack(side='left', padx=6)
        self.search_var.trace_add('write', lambda *_: self.reload())

        cols = ('id', 'name', 'muscle', 'desc')
        self.tree = ttk.Treeview(self, columns=cols, show='headings')
        self.tree.heading('id', text='ID')
        self.tree.heading('name', text='Название')
        self.tree.heading('muscle', text='Группа мышц')
        self.tree.heading('desc', text='Описание')
        self.tree.column('id', width=50, anchor='center')
        self.tree.column('name', width=240)
        self.tree.column('muscle', width=140)
        self.tree.column('desc', width=520)
        self.tree.pack(fill='both', expand=True)
        self.tree.bind('<Double-1>', lambda e: self.edit())

        self.reload()

    def reload(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        q = f"%{self.search_var.get().strip()}%"
        rows = fetch_all(
            "SELECT id, name, muscle_group, description FROM exercises "
            "WHERE name LIKE ? OR muscle_group LIKE ? ORDER BY name",
            (q, q))
        for r in rows:
            self.tree.insert('', 'end', iid=str(r['id']),
                             values=(r['id'], r['name'], r['muscle_group'] or '', r['description'] or ''))

    def add(self):
        ExerciseDialog(self, None, self.user['id'], self.reload)

    def edit(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Внимание", "Выберите упражнение.")
            return
        ExerciseDialog(self, int(sel[0]), self.user['id'], self.reload)

    def delete(self):
        sel = self.tree.selection()
        if not sel:
            return
        if not messagebox.askyesno("Подтверждение", "Удалить выбранное упражнение?"):
            return
        ex_id = int(sel[0])
        used = fetch_one("SELECT 1 FROM training_exercises WHERE exercise_id=?", (ex_id,))
        if used:
            messagebox.showerror("Ошибка",
                                 "Упражнение используется в тренировках и не может быть удалено.")
            return
        execute("DELETE FROM exercises WHERE id=?", (ex_id,))
        self.reload()


class ExerciseDialog(tk.Toplevel):
    def __init__(self, parent, ex_id, user_id, on_save):
        super().__init__(parent)
        self.title("Упражнение")
        self.geometry("480x360")
        self.transient(parent)
        self.grab_set()

        self.ex_id = ex_id
        self.user_id = user_id
        self.on_save = on_save

        self.name_var = tk.StringVar()
        self.muscle_var = tk.StringVar()
        self.url_var = tk.StringVar()

        frm = ttk.Frame(self, padding=15)
        frm.pack(fill='both', expand=True)

        ttk.Label(frm, text="Название:").grid(row=0, column=0, sticky='e', pady=6)
        ttk.Entry(frm, textvariable=self.name_var, width=40).grid(row=0, column=1, pady=6)

        ttk.Label(frm, text="Группа мышц:").grid(row=1, column=0, sticky='e', pady=6)
        ttk.Entry(frm, textvariable=self.muscle_var, width=40).grid(row=1, column=1, pady=6)

        ttk.Label(frm, text="Ссылка на видео:").grid(row=2, column=0, sticky='e', pady=6)
        ttk.Entry(frm, textvariable=self.url_var, width=40).grid(row=2, column=1, pady=6)

        ttk.Label(frm, text="Описание:").grid(row=3, column=0, sticky='ne', pady=6)
        self.desc = tk.Text(frm, width=40, height=6, wrap='word')
        self.desc.grid(row=3, column=1, pady=6)

        if ex_id:
            row = fetch_one("SELECT * FROM exercises WHERE id=?", (ex_id,))
            if row:
                self.name_var.set(row['name'])
                self.muscle_var.set(row['muscle_group'] or '')
                self.url_var.set(row['video_url'] or '')
                self.desc.insert('1.0', row['description'] or '')

        btns = ttk.Frame(self)
        btns.pack(pady=10)
        ttk.Button(btns, text="Сохранить", command=self.save).pack(side='left', padx=5)
        ttk.Button(btns, text="Отмена", command=self.destroy).pack(side='left', padx=5)

    def save(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Внимание", "Введите название упражнения.")
            return
        muscle = self.muscle_var.get().strip()
        url = self.url_var.get().strip()
        desc = self.desc.get('1.0', 'end').strip()

        if self.ex_id:
            execute(
                "UPDATE exercises SET name=?, description=?, muscle_group=?, video_url=? WHERE id=?",
                (name, desc, muscle, url, self.ex_id)
            )
        else:
            execute(
                "INSERT INTO exercises (name, description, muscle_group, video_url, created_by) "
                "VALUES (?,?,?,?,?)",
                (name, desc, muscle, url, self.user_id)
            )
        self.on_save()
        self.destroy()
