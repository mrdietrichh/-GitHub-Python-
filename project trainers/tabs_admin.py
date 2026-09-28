import tkinter as tk
from tkinter import ttk, messagebox

from constants import ROLES
from database import fetch_all, fetch_one, execute, hash_password
from tabs_exercises import ExercisesTab
from tabs_profile import ProfileTab


class AdminTabs(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.user = parent.user

        nb = ttk.Notebook(self)
        nb.pack(fill='both', expand=True, padx=8, pady=8)
        nb.add(UsersTab(nb, self.user), text='Пользователи')
        nb.add(ExercisesTab(nb, self.user), text='Упражнения')
        nb.add(AdminTrainingsTab(nb, self.user), text='Все тренировки')
        nb.add(ProfileTab(nb, self.user), text='Профиль')


class UsersTab(ttk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, padding=10)
        self.user = user

        top = ttk.Frame(self)
        top.pack(fill='x', pady=(0, 8))
        ttk.Button(top, text="Добавить", command=self.add).pack(side='left')
        ttk.Button(top, text="Удалить", command=self.delete).pack(side='left', padx=6)
        ttk.Button(top, text="Обновить", command=self.reload).pack(side='right')

        cols = ('id', 'login', 'role', 'fio', 'email', 'phone')
        self.tree = ttk.Treeview(self, columns=cols, show='headings')
        for c, t, w in [('id', 'ID', 50), ('login', 'Логин', 140),
                        ('role', 'Роль', 130), ('fio', 'ФИО', 260),
                        ('email', 'E-mail', 200), ('phone', 'Телефон', 150)]:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor='w')
        self.tree.pack(fill='both', expand=True)

        self.reload()

    def reload(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        rows = fetch_all("SELECT * FROM users ORDER BY id")
        for r in rows:
            self.tree.insert('', 'end', iid=str(r['id']),
                             values=(r['id'], r['login'],
                                     ROLES.get(r['role'], r['role']),
                                     r['full_name'], r['email'] or '',
                                     r['phone'] or ''))

    def add(self):
        RegisterAdminDialog(self, self.reload)

    def delete(self):
        sel = self.tree.selection()
        if not sel:
            return
        uid = int(sel[0])
        if uid == self.user['id']:
            messagebox.showerror("Ошибка", "Нельзя удалить самого себя.")
            return
        if not messagebox.askyesno("Подтверждение", "Удалить пользователя?"):
            return
        execute("DELETE FROM users WHERE id=?", (uid,))
        self.reload()


class RegisterAdminDialog(tk.Toplevel):
    def __init__(self, parent, on_save):
        super().__init__(parent)
        self.title("Новый пользователь")
        self.geometry("420x420")
        self.transient(parent)
        self.grab_set()
        self.on_save = on_save

        self.role_var = tk.StringVar(value='athlete')
        self.login_var = tk.StringVar()
        self.pw_var = tk.StringVar()
        self.fio_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()

        frm = ttk.Frame(self, padding=15)
        frm.pack(fill='both', expand=True)

        ttk.Label(frm, text="Роль:").grid(row=0, column=0, sticky='e', pady=6)
        rf = ttk.Frame(frm)
        rf.grid(row=0, column=1, sticky='w', pady=6)
        ttk.Radiobutton(rf, text="Спортсмен", variable=self.role_var, value='athlete').pack(side='left')
        ttk.Radiobutton(rf, text="Тренер", variable=self.role_var, value='trainer').pack(side='left', padx=6)
        ttk.Radiobutton(rf, text="Админ", variable=self.role_var, value='admin').pack(side='left')

        def row(r, label, var, show=None):
            ttk.Label(frm, text=label).grid(row=r, column=0, sticky='e', pady=6)
            ttk.Entry(frm, textvariable=var, width=32, show=show).grid(row=r, column=1, pady=6)

        row(1, "Логин:", self.login_var)
        row(2, "Пароль:", self.pw_var, show='*')
        row(3, "ФИО:", self.fio_var)
        row(4, "E-mail:", self.email_var)
        row(5, "Телефон:", self.phone_var)

        btns = ttk.Frame(self)
        btns.pack(pady=10)
        ttk.Button(btns, text="Создать", command=self.save).pack(side='left', padx=5)
        ttk.Button(btns, text="Отмена", command=self.destroy).pack(side='left', padx=5)

    def save(self):
        login = self.login_var.get().strip()
        pw = self.pw_var.get().strip()
        fio = self.fio_var.get().strip()
        if not (login and pw and fio):
            messagebox.showwarning("Внимание", "Заполните логин, пароль, ФИО.")
            return
        if fetch_one("SELECT 1 FROM users WHERE login=?", (login,)):
            messagebox.showerror("Ошибка", "Логин занят.")
            return
        role = self.role_var.get()
        uid = execute(
            "INSERT INTO users (login, password_hash, role, full_name, email, phone) "
            "VALUES (?,?,?,?,?,?)",
            (login, hash_password(pw), role, fio,
             self.email_var.get().strip(), self.phone_var.get().strip())
        )
        if role == 'trainer':
            execute("INSERT INTO trainers (user_id, specialization, experience) VALUES (?,?,?)",
                    (uid, '', 0))
        elif role == 'athlete':
            execute("INSERT INTO athletes (user_id, birth_date, goal) VALUES (?,?,?)",
                    (uid, '', ''))
        self.on_save()
        self.destroy()


class AdminTrainingsTab(ttk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, padding=10)
        self.user = user

        top = ttk.Frame(self)
        top.pack(fill='x', pady=(0, 8))
        ttk.Button(top, text="Обновить", command=self.reload).pack(side='right')

        cols = ('id', 'title', 'trainer', 'athlete', 'date', 'status')
        self.tree = ttk.Treeview(self, columns=cols, show='headings')
        for c, t, w in [('id', 'ID', 50), ('title', 'Название', 260),
                        ('trainer', 'Тренер', 220), ('athlete', 'Спортсмен', 220),
                        ('date', 'Дата', 110), ('status', 'Статус', 120)]:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor='w')
        self.tree.pack(fill='both', expand=True)
        self.reload()

    def reload(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        rows = fetch_all("""
            SELECT t.id, t.title, t.date, t.status,
                   tr.full_name AS trainer_name,
                   at.full_name AS athlete_name
            FROM trainings t
            LEFT JOIN users tr ON tr.id = t.trainer_id
            LEFT JOIN users at ON at.id = t.athlete_id
            ORDER BY t.id DESC
        """)
        for r in rows:
            self.tree.insert('', 'end', iid=str(r['id']),
                             values=(r['id'], r['title'],
                                     r['trainer_name'] or '—',
                                     r['athlete_name'] or '—',
                                     r['date'] or '',
                                     r['status'] or ''))
