import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from database import fetch_all, fetch_one, execute, notify


class TrainingsTab(ttk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, padding=10)
        self.user = user

        top = ttk.Frame(self)
        top.pack(fill='x', pady=(0, 8))
        ttk.Button(top, text="Создать тренировку", command=self.create).pack(side='left')
        ttk.Button(top, text="Просмотреть", command=self.view).pack(side='left', padx=6)
        ttk.Button(top, text="Удалить", command=self.delete).pack(side='left')
        ttk.Button(top, text="Обновить", command=self.reload).pack(side='right')

        cols = ('id', 'title', 'athlete', 'date', 'status')
        self.tree = ttk.Treeview(self, columns=cols, show='headings')
        self.tree.heading('id', text='ID')
        self.tree.heading('title', text='Название')
        self.tree.heading('athlete', text='Спортсмен')
        self.tree.heading('date', text='Дата')
        self.tree.heading('status', text='Статус')
        self.tree.column('id', width=50, anchor='center')
        self.tree.column('title', width=300)
        self.tree.column('athlete', width=250)
        self.tree.column('date', width=120, anchor='center')
        self.tree.column('status', width=140, anchor='center')
        self.tree.pack(fill='both', expand=True)
        self.tree.bind('<Double-1>', lambda e: self.view())

        self.reload()

    def reload(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        rows = fetch_all("""
            SELECT t.id, t.title, t.date, t.status,
                   u.full_name AS athlete_name
            FROM trainings t
            LEFT JOIN users u ON u.id = t.athlete_id
            WHERE t.trainer_id = ?
            ORDER BY t.date DESC, t.id DESC
        """, (self.user['id'],))
        for r in rows:
            self.tree.insert('', 'end', iid=str(r['id']),
                             values=(r['id'], r['title'],
                                     r['athlete_name'] or '—',
                                     r['date'] or '', r['status'] or ''))

    def create(self):
        TrainingDialog(self, self.user, self.reload)

    def view(self):
        sel = self.tree.selection()
        if not sel:
            return
        TrainingViewWindow(self, int(sel[0]), self.user)

    def delete(self):
        sel = self.tree.selection()
        if not sel:
            return
        if not messagebox.askyesno("Подтверждение", "Удалить выбранную тренировку?"):
            return
        execute("DELETE FROM trainings WHERE id=?", (int(sel[0]),))
        self.reload()


class TrainingDialog(tk.Toplevel):
    def __init__(self, parent, user, on_save):
        super().__init__(parent)
        self.title("Создание тренировки")
        self.geometry("720x620")
        self.transient(parent)
        self.grab_set()

        self.user = user
        self.on_save = on_save
        self.exercises_buffer = []

        frm = ttk.Frame(self, padding=12)
        frm.pack(fill='both', expand=True)

        meta = ttk.LabelFrame(frm, text="Параметры тренировки", padding=10)
        meta.pack(fill='x')

        self.title_var = tk.StringVar(value=f"Тренировка от {datetime.now():%d.%m.%Y}")
        self.date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        self.athlete_var = tk.StringVar()

        ttk.Label(meta, text="Название:").grid(row=0, column=0, sticky='e', pady=4)
        ttk.Entry(meta, textvariable=self.title_var, width=42).grid(
            row=0, column=1, columnspan=3, sticky='w', pady=4)

        ttk.Label(meta, text="Дата (ГГГГ-ММ-ДД):").grid(row=1, column=0, sticky='e', pady=4)
        ttk.Entry(meta, textvariable=self.date_var, width=18).grid(
            row=1, column=1, sticky='w', pady=4)

        ttk.Label(meta, text="Спортсмен:").grid(row=2, column=0, sticky='e', pady=4)
        athletes = fetch_all(
            "SELECT u.id, u.full_name FROM users u WHERE u.role='athlete' ORDER BY u.full_name")
        self.athletes_list = [(a['id'], a['full_name']) for a in athletes]
        combo = ttk.Combobox(meta, textvariable=self.athlete_var,
                             values=[a[1] for a in self.athletes_list],
                             state='readonly', width=39)
        combo.grid(row=2, column=1, columnspan=3, sticky='w', pady=4)

        ttk.Label(meta, text="Комментарий:").grid(row=3, column=0, sticky='ne', pady=4)
        self.comment = tk.Text(meta, width=48, height=3, wrap='word')
        self.comment.grid(row=3, column=1, columnspan=3, sticky='w', pady=4)

        exf = ttk.LabelFrame(frm, text="Упражнения тренировки", padding=10)
        exf.pack(fill='both', expand=True, pady=(10, 0))

        add_row = ttk.Frame(exf)
        add_row.pack(fill='x')

        ttk.Label(add_row, text="Упражнение:").grid(row=0, column=0, sticky='e')
        self.ex_var = tk.StringVar()
        self.exercises_list = [
            (r['id'], r['name']) for r in fetch_all(
                "SELECT id, name FROM exercises ORDER BY name")
        ]
        self.ex_combo = ttk.Combobox(add_row, textvariable=self.ex_var,
                                     values=[e[1] for e in self.exercises_list],
                                     state='readonly', width=32)
        self.ex_combo.grid(row=0, column=1, padx=6, sticky='w')

        ttk.Label(add_row, text="Подходы:").grid(row=0, column=2, sticky='e')
        self.sets_var = tk.StringVar(value='3')
        ttk.Entry(add_row, textvariable=self.sets_var, width=5).grid(row=0, column=3, padx=4)

        ttk.Label(add_row, text="Повторы:").grid(row=0, column=4, sticky='e')
        self.reps_var = tk.StringVar(value='10')
        ttk.Entry(add_row, textvariable=self.reps_var, width=5).grid(row=0, column=5, padx=4)

        ttk.Label(add_row, text="Вес, кг:").grid(row=0, column=6, sticky='e')
        self.weight_var = tk.StringVar(value='0')
        ttk.Entry(add_row, textvariable=self.weight_var, width=6).grid(row=0, column=7, padx=4)

        ttk.Button(add_row, text="Добавить",
                   command=self.add_exercise).grid(row=0, column=8, padx=6)

        cols = ('name', 'sets', 'reps', 'weight')
        self.tree = ttk.Treeview(exf, columns=cols, show='headings', height=10)
        self.tree.heading('name', text='Упражнение')
        self.tree.heading('sets', text='Подходы')
        self.tree.heading('reps', text='Повторы')
        self.tree.heading('weight', text='Вес, кг')
        self.tree.column('name', width=340)
        self.tree.column('sets', width=90, anchor='center')
        self.tree.column('reps', width=90, anchor='center')
        self.tree.column('weight', width=100, anchor='center')
        self.tree.pack(fill='both', expand=True, pady=(8, 0))

        ttk.Button(exf, text="Удалить выбранное",
                   command=self.remove_exercise).pack(anchor='e', pady=(6, 0))

        btns = ttk.Frame(frm)
        btns.pack(pady=10)
        ttk.Button(btns, text="Сохранить тренировку",
                   command=self.save, width=24).pack(side='left', padx=5)
        ttk.Button(btns, text="Отмена",
                   command=self.destroy, width=14).pack(side='left', padx=5)

    def add_exercise(self):
        name = self.ex_var.get().strip()
        if not name:
            messagebox.showwarning("Внимание", "Выберите упражнение.")
            return
        ex_id = next((e[0] for e in self.exercises_list if e[1] == name), None)
        try:
            sets = int(self.sets_var.get())
            reps = int(self.reps_var.get())
            weight = float(self.weight_var.get().replace(',', '.'))
        except ValueError:
            messagebox.showwarning("Внимание", "Подходы/повторы — целые, вес — число.")
            return
        item = {'exercise_id': ex_id, 'name': name,
                'sets': sets, 'reps': reps, 'weight': weight}
        self.exercises_buffer.append(item)
        self.tree.insert('', 'end',
                         values=(name, sets, reps, f"{weight:g}"))

    def remove_exercise(self):
        sel = self.tree.selection()
        if not sel:
            return
        idx = self.tree.index(sel[0])
        self.tree.delete(sel[0])
        del self.exercises_buffer[idx]

    def save(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("Внимание", "Введите название тренировки.")
            return
        if not self.exercises_buffer:
            messagebox.showwarning("Внимание", "Добавьте хотя бы одно упражнение.")
            return
        athlete_name = self.athlete_var.get().strip()
        athlete_id = next((a[0] for a in self.athletes_list if a[1] == athlete_name), None)

        status = 'Назначена' if athlete_id else 'Черновик'
        date = self.date_var.get().strip() or datetime.now().strftime('%Y-%m-%d')
        comment = self.comment.get('1.0', 'end').strip()

        training_id = execute(
            "INSERT INTO trainings (trainer_id, athlete_id, title, date, status, comment) "
            "VALUES (?,?,?,?,?,?)",
            (self.user['id'], athlete_id, title, date, status, comment)
        )
        for i, ex in enumerate(self.exercises_buffer, start=1):
            execute(
                "INSERT INTO training_exercises "
                "(training_id, exercise_id, sets, reps, weight, duration, order_num, completed) "
                "VALUES (?,?,?,?,?,?,?,0)",
                (training_id, ex['exercise_id'], ex['sets'], ex['reps'],
                 ex['weight'], 0, i)
            )
        if athlete_id:
            notify(athlete_id, f"Вам назначена тренировка: «{title}» ({date})", training_id)

        self.on_save()
        self.destroy()


class TrainingViewWindow(tk.Toplevel):
    def __init__(self, parent, training_id, user):
        super().__init__(parent)
        self.title("Тренировка")
        self.geometry("720x540")
        self.transient(parent)
        self.training_id = training_id
        self.user = user

        t = fetch_one("""
            SELECT t.*, u.full_name AS athlete_name
            FROM trainings t
            LEFT JOIN users u ON u.id = t.athlete_id
            WHERE t.id=?
        """, (training_id,))

        info = ttk.LabelFrame(self, text="Информация", padding=10)
        info.pack(fill='x', padx=10, pady=10)
        ttk.Label(info, text=f"Название: {t['title']}").pack(anchor='w')
        ttk.Label(info, text=f"Дата: {t['date'] or '—'}").pack(anchor='w')
        ttk.Label(info, text=f"Статус: {t['status'] or '—'}").pack(anchor='w')
        ttk.Label(info, text=f"Спортсмен: {t['athlete_name'] or '—'}").pack(anchor='w')
        if t['comment']:
            ttk.Label(info, text=f"Комментарий: {t['comment']}").pack(anchor='w')

        cols = ('name', 'sets', 'reps', 'weight', 'done')
        self.tree = ttk.Treeview(self, columns=cols, show='headings')
        self.tree.heading('name', text='Упражнение')
        self.tree.heading('sets', text='Подходы')
        self.tree.heading('reps', text='Повторы')
        self.tree.heading('weight', text='Вес, кг')
        self.tree.heading('done', text='Выполнено')
        self.tree.column('name', width=320)
        self.tree.column('sets', width=90, anchor='center')
        self.tree.column('reps', width=90, anchor='center')
        self.tree.column('weight', width=90, anchor='center')
        self.tree.column('done', width=100, anchor='center')
        self.tree.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        self.reload()

        btns = ttk.Frame(self)
        btns.pack(pady=(0, 12))
        if self.user['role'] == 'athlete':
            ttk.Button(btns, text="Отметить выполнение",
                       command=self.mark_complete).pack(side='left', padx=5)
            ttk.Button(btns, text="Отметить все",
                       command=self.mark_all).pack(side='left', padx=5)
        ttk.Button(btns, text="Закрыть",
                   command=self.destroy).pack(side='left', padx=5)

    def reload(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        rows = fetch_all("""
            SELECT te.id, e.name, te.sets, te.reps, te.weight, te.completed
            FROM training_exercises te
            JOIN exercises e ON e.id = te.exercise_id
            WHERE te.training_id=?
            ORDER BY te.order_num, te.id
        """, (self.training_id,))
        for r in rows:
            self.tree.insert('', 'end', iid=str(r['id']),
                             values=(r['name'], r['sets'], r['reps'],
                                     f"{r['weight']:g}" if r['weight'] is not None else '',
                                     'Да' if r['completed'] else 'Нет'))

    def mark_complete(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Внимание", "Выберите упражнение.")
            return
        execute("UPDATE training_exercises SET completed=1 WHERE id=?", (int(sel[0]),))
        self._update_training_status()
        self.reload()

    def mark_all(self):
        execute("UPDATE training_exercises SET completed=1 WHERE training_id=?",
                (self.training_id,))
        self._update_training_status()
        self.reload()

    def _update_training_status(self):
        row = fetch_one(
            "SELECT COUNT(*) AS total, SUM(completed) AS done "
            "FROM training_exercises WHERE training_id=?",
            (self.training_id,))
        if row and row['total']:
            status = 'Завершена' if row['done'] == row['total'] else 'Выполняется'
            execute("UPDATE trainings SET status=? WHERE id=?",
                    (status, self.training_id))
