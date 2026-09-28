import tkinter as tk
from tkinter import ttk, messagebox

from constants import ROLES
from database import fetch_one, execute


class ProfileTab(ttk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, padding=20)
        self.user = user

        ttk.Label(self, text="Профиль пользователя",
                  style='Header.TLabel').pack(anchor='w', pady=(0, 15))

        self.fio_var = tk.StringVar(value=user['full_name'])
        self.email_var = tk.StringVar(value=user['email'] or '')
        self.phone_var = tk.StringVar(value=user['phone'] or '')

        box = ttk.LabelFrame(self, text="Данные", padding=15)
        box.pack(fill='x')

        ttk.Label(box, text="Логин:").grid(row=0, column=0, sticky='e', pady=6)
        ttk.Label(box, text=user['login']).grid(row=0, column=1, sticky='w', pady=6)
        ttk.Label(box, text="Роль:").grid(row=1, column=0, sticky='e', pady=6)
        ttk.Label(box, text=ROLES.get(user['role'], user['role'])).grid(
            row=1, column=1, sticky='w', pady=6)
        ttk.Label(box, text="ФИО:").grid(row=2, column=0, sticky='e', pady=6)
        ttk.Entry(box, textvariable=self.fio_var, width=42).grid(row=2, column=1, sticky='w', pady=6)
        ttk.Label(box, text="E-mail:").grid(row=3, column=0, sticky='e', pady=6)
        ttk.Entry(box, textvariable=self.email_var, width=42).grid(row=3, column=1, sticky='w', pady=6)
        ttk.Label(box, text="Телефон:").grid(row=4, column=0, sticky='e', pady=6)
        ttk.Entry(box, textvariable=self.phone_var, width=42).grid(row=4, column=1, sticky='w', pady=6)

        # ---- дополнительные поля по роли ----
        self.birth_var = tk.StringVar()
        self.goal_var = tk.StringVar()
        self.spec_var = tk.StringVar()
        self.exp_var = tk.StringVar()

        if user['role'] == 'athlete':
            row = fetch_one("SELECT * FROM athletes WHERE user_id=?", (user['id'],))
            if row:
                self.birth_var.set(row['birth_date'] or '')
                self.goal_var.set(row['goal'] or '')

            ttk.Label(box, text="Дата рождения:").grid(row=5, column=0, sticky='e', pady=6)
            ttk.Entry(box, textvariable=self.birth_var, width=42).grid(
                row=5, column=1, sticky='w', pady=6)

            ttk.Label(box, text="Цель:").grid(row=6, column=0, sticky='e', pady=6)
            ttk.Entry(box, textvariable=self.goal_var, width=42).grid(
                row=6, column=1, sticky='w', pady=6)

            ttk.Label(box,
                      text="Дата в формате ГГГГ-ММ-ДД, например 1995-05-15",
                      style='Sub.TLabel').grid(row=7, column=1, sticky='w')

        elif user['role'] == 'trainer':
            row = fetch_one("SELECT * FROM trainers WHERE user_id=?", (user['id'],))
            if row:
                self.spec_var.set(row['specialization'] or '')
                self.exp_var.set(str(row['experience'] or 0))

            ttk.Label(box, text="Специализация:").grid(row=5, column=0, sticky='e', pady=6)
            ttk.Entry(box, textvariable=self.spec_var, width=42).grid(
                row=5, column=1, sticky='w', pady=6)

            ttk.Label(box, text="Стаж (лет):").grid(row=6, column=0, sticky='e', pady=6)
            ttk.Entry(box, textvariable=self.exp_var, width=42).grid(
                row=6, column=1, sticky='w', pady=6)

        ttk.Button(self, text="Сохранить", command=self.save).pack(pady=15, anchor='w')

    def save(self):
        execute("UPDATE users SET full_name=?, email=?, phone=? WHERE id=?",
                (self.fio_var.get().strip(),
                 self.email_var.get().strip(),
                 self.phone_var.get().strip(),
                 self.user['id']))

        if self.user['role'] == 'athlete':
            execute("UPDATE athletes SET birth_date=?, goal=? WHERE user_id=?",
                    (self.birth_var.get().strip(),
                     self.goal_var.get().strip(),
                     self.user['id']))
            self.user['birth_date'] = self.birth_var.get().strip()
            self.user['goal'] = self.goal_var.get().strip()

        elif self.user['role'] == 'trainer':
            try:
                exp = int(self.exp_var.get().strip() or 0)
            except ValueError:
                messagebox.showwarning("Внимание", "Стаж должен быть числом.")
                return
            execute("UPDATE trainers SET specialization=?, experience=? WHERE user_id=?",
                    (self.spec_var.get().strip(), exp, self.user['id']))

        messagebox.showinfo("Готово", "Профиль сохранён.")
        self.user['full_name'] = self.fio_var.get().strip()
        self.user['email'] = self.email_var.get().strip()
        self.user['phone'] = self.phone_var.get().strip()
