import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from database import fetch_all, execute


class TrainerProgressTab(ttk.Frame):
    """Вкладка «Прогресс спортсменов» для тренера."""

    def __init__(self, parent, user):
        super().__init__(parent, padding=10)
        self.user = user

        top = ttk.Frame(self)
        top.pack(fill='x', pady=(0, 8))
        ttk.Label(top, text="Спортсмен:").pack(side='left')
        self.athlete_var = tk.StringVar()
        athletes = fetch_all(
            "SELECT id, full_name FROM users WHERE role='athlete' ORDER BY full_name")
        self.athletes_list = [(a['id'], a['full_name']) for a in athletes]
        combo = ttk.Combobox(top, textvariable=self.athlete_var,
                             values=[a[1] for a in self.athletes_list],
                             state='readonly', width=32)
        combo.pack(side='left', padx=6)
        combo.bind('<<ComboboxSelected>>', lambda e: self.reload())
        ttk.Button(top, text="Обновить", command=self.reload).pack(side='right')

        cols = ('date', 'exercise', 'weight', 'reps', 'notes')
        self.tree = ttk.Treeview(self, columns=cols, show='headings')
        self.tree.heading('date', text='Дата')
        self.tree.heading('exercise', text='Упражнение')
        self.tree.heading('weight', text='Вес, кг')
        self.tree.heading('reps', text='Повторы')
        self.tree.heading('notes', text='Заметки')
        self.tree.column('date', width=110, anchor='center')
        self.tree.column('exercise', width=260)
        self.tree.column('weight', width=100, anchor='center')
        self.tree.column('reps', width=100, anchor='center')
        self.tree.column('notes', width=380)
        self.tree.pack(fill='both', expand=True)

    def reload(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        name = self.athlete_var.get().strip()
        if not name:
            return
        athlete_id = next((a[0] for a in self.athletes_list if a[1] == name), None)
        if athlete_id is None:
            return
        rows = fetch_all("""
            SELECT p.date, e.name AS exercise_name, p.weight, p.reps, p.notes
            FROM progress_records p
            LEFT JOIN exercises e ON e.id = p.exercise_id
            WHERE p.athlete_id=?
            ORDER BY p.date DESC, p.id DESC
        """, (athlete_id,))
        for r in rows:
            self.tree.insert('', 'end', values=(
                r['date'] or '',
                r['exercise_name'] or '—',
                f"{r['weight']:g}" if r['weight'] is not None else '',
                r['reps'] if r['reps'] is not None else '',
                r['notes'] or ''
            ))


class AthleteProgressTab(ttk.Frame):
    """Вкладка «Мой прогресс» для спортсмена."""

    def __init__(self, parent, user):
        super().__init__(parent, padding=10)
        self.user = user

        top = ttk.Frame(self)
        top.pack(fill='x', pady=(0, 8))
        ttk.Button(top, text="Добавить запись", command=self.add).pack(side='left')
        ttk.Button(top, text="Удалить", command=self.delete).pack(side='left', padx=6)
        ttk.Button(top, text="Обновить", command=self.reload).pack(side='right')

        cols = ('id', 'date', 'exercise', 'weight', 'reps', 'notes')
        self.tree = ttk.Treeview(self, columns=cols, show='headings')
        self.tree.heading('id', text='ID')
        self.tree.heading('date', text='Дата')
        self.tree.heading('exercise', text='Упражнение')
        self.tree.heading('weight', text='Вес, кг')
        self.tree.heading('reps', text='Повторы')
        self.tree.heading('notes', text='Заметки')
        self.tree.column('id', width=50, anchor='center')
        self.tree.column('date', width=110, anchor='center')
        self.tree.column('exercise', width=260)
        self.tree.column('weight', width=100, anchor='center')
        self.tree.column('reps', width=100, anchor='center')
        self.tree.column('notes', width=380)
        self.tree.pack(fill='both', expand=True)

        self.reload()

    def reload(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        rows = fetch_all("""
            SELECT p.id, p.date, e.name AS exercise_name,
                   p.weight, p.reps, p.notes
            FROM progress_records p
            LEFT JOIN exercises e ON e.id = p.exercise_id
            WHERE p.athlete_id=?
            ORDER BY p.date DESC, p.id DESC
        """, (self.user['id'],))
        for r in rows:
            self.tree.insert('', 'end', iid=str(r['id']),
                             values=(r['id'],
                                     r['date'] or '',
                                     r['exercise_name'] or '—',
                                     f"{r['weight']:g}" if r['weight'] is not None else '',
                                     r['reps'] if r['reps'] is not None else '',
                                     r['notes'] or ''))

    def add(self):
        ProgressDialog(self, self.user['id'], self.reload)

    def delete(self):
        sel = self.tree.selection()
        if not sel:
            return
        if not messagebox.askyesno("Подтверждение", "Удалить запись?"):
            return
        execute("DELETE FROM progress_records WHERE id=?", (int(sel[0]),))
        self.reload()


class ProgressDialog(tk.Toplevel):
    def __init__(self, parent, athlete_id, on_save):
        super().__init__(parent)
        self.title("Новая запись прогресса")
        self.geometry("440x340")
        self.transient(parent)
        self.grab_set()

        self.athlete_id = athlete_id
        self.on_save = on_save

        frm = ttk.Frame(self, padding=15)
        frm.pack(fill='both', expand=True)

        self.ex_var = tk.StringVar()
        self.exercises_list = [
            (r['id'], r['name']) for r in fetch_all(
                "SELECT id, name FROM exercises ORDER BY name")
        ]
        self.date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        self.weight_var = tk.StringVar()
        self.reps_var = tk.StringVar()

        ttk.Label(frm, text="Упражнение:").grid(row=0, column=0, sticky='e', pady=6)
        ttk.Combobox(frm, textvariable=self.ex_var,
                     values=[e[1] for e in self.exercises_list],
                     state='readonly', width=32).grid(row=0, column=1, pady=6)

        ttk.Label(frm, text="Дата:").grid(row=1, column=0, sticky='e', pady=6)
        ttk.Entry(frm, textvariable=self.date_var, width=32).grid(row=1, column=1, pady=6)

        ttk.Label(frm, text="Вес, кг:").grid(row=2, column=0, sticky='e', pady=6)
        ttk.Entry(frm, textvariable=self.weight_var, width=32).grid(row=2, column=1, pady=6)

        ttk.Label(frm, text="Повторы:").grid(row=3, column=0, sticky='e', pady=6)
        ttk.Entry(frm, textvariable=self.reps_var, width=32).grid(row=3, column=1, pady=6)

        ttk.Label(frm, text="Заметки:").grid(row=4, column=0, sticky='ne', pady=6)
        self.notes = tk.Text(frm, width=32, height=5, wrap='word')
        self.notes.grid(row=4, column=1, pady=6)

        btns = ttk.Frame(self)
        btns.pack(pady=10)
        ttk.Button(btns, text="Сохранить", command=self.save).pack(side='left', padx=5)
        ttk.Button(btns, text="Отмена", command=self.destroy).pack(side='left', padx=5)

    def save(self):
        name = self.ex_var.get().strip()
        if not name:
            messagebox.showwarning("Внимание", "Выберите упражнение.")
            return
        ex_id = next((e[0] for e in self.exercises_list if e[1] == name), None)
        try:
            weight = float(self.weight_var.get().replace(',', '.')) if self.weight_var.get().strip() else None
            reps = int(self.reps_var.get()) if self.reps_var.get().strip() else None
        except ValueError:
            messagebox.showwarning("Внимание", "Вес — число, повторы — целое.")
            return
        execute(
            "INSERT INTO progress_records (athlete_id, exercise_id, date, weight, reps, notes) "
            "VALUES (?,?,?,?,?,?)",
            (self.athlete_id, ex_id, self.date_var.get().strip(),
             weight, reps, self.notes.get('1.0', 'end').strip())
        )
        self.on_save()
        self.destroy()
