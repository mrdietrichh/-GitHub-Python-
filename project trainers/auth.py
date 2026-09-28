import tkinter as tk
from tkinter import ttk, messagebox

from constants import APP_TITLE
from database import fetch_one, execute, hash_password


class LoginFrame(ttk.Frame):
    def __init__(self, app):
        super().__init__(app, padding=40)
        self.app = app

        header = ttk.Frame(self)
        header.pack(pady=(30, 20))
        ttk.Label(header, text=APP_TITLE, style='Header.TLabel').pack()
        ttk.Label(header, text="Пожалуйста, войдите в систему",
                  style='Sub.TLabel').pack(pady=(6, 0))

        box = ttk.LabelFrame(self, text="Авторизация", padding=20)
        box.pack(ipadx=10, ipady=10)

        ttk.Label(box, text="Логин:").grid(row=0, column=0, sticky='e', padx=6, pady=8)
        self.login_var = tk.StringVar()
        ttk.Entry(box, textvariable=self.login_var, width=30).grid(
            row=0, column=1, padx=6, pady=8)

        ttk.Label(box, text="Пароль:").grid(row=1, column=0, sticky='e', padx=6, pady=8)
        self.pw_var = tk.StringVar()
        pw_entry = ttk.Entry(box, textvariable=self.pw_var, show='*', width=30)
        pw_entry.grid(row=1, column=1, padx=6, pady=8)
        pw_entry.bind('<Return>', lambda e: self.do_login())

        btns = ttk.Frame(box)
        btns.grid(row=2, column=0, columnspan=2, pady=(15, 0))
        ttk.Button(btns, text="Войти", command=self.do_login, width=18).pack(side='left', padx=5)
        ttk.Button(btns, text="Регистрация", command=self.app.show_register, width=18).pack(side='left', padx=5)

        hint = ttk.LabelFrame(self, text="Демо-доступы", padding=12)
        hint.pack(pady=(20, 0), fill='x')

        demo_data = [
            ("admin / admin", "администратор"),
            ("trainer / trainer", "тренер"),
            ("athlete / athlete", "тренирующийся"),
        ]

        for i, (cred, role) in enumerate(demo_data):
            ttk.Label(hint, text=cred, style='Sub.TLabel').grid(row=i, column=0, sticky='w')
            ttk.Label(hint, text="—", style='Sub.TLabel').grid(row=i, column=1, padx=12)
            ttk.Label(hint, text=role, style='Sub.TLabel').grid(row=i, column=2, sticky='w')

    def do_login(self):
        login = self.login_var.get().strip()
        password = self.pw_var.get().strip()
        if not login or not password:
            messagebox.showwarning("Внимание", "Введите логин и пароль.")
            return
        row = fetch_one(
            "SELECT * FROM users WHERE login=? AND password_hash=?",
            (login, hash_password(password))
        )
        if row is None:
            messagebox.showerror("Ошибка", "Неверный логин или пароль.")
            return
        self.app.show_main(dict(row))


class RegisterFrame(ttk.Frame):
    def __init__(self, app):
        super().__init__(app, padding=30)
        self.app = app

        ttk.Label(self, text="Регистрация нового пользователя",
                  style='Header.TLabel').pack(pady=(10, 20))

        box = ttk.LabelFrame(self, text="Данные пользователя", padding=20)
        box.pack(ipadx=10, ipady=10)

        self.role_var = tk.StringVar(value='athlete')
        self.login_var = tk.StringVar()
        self.pw_var = tk.StringVar()
        self.pw2_var = tk.StringVar()
        self.fio_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()

        def row(label, var, show=None, r=0):
            ttk.Label(box, text=label).grid(row=r, column=0, sticky='e', padx=6, pady=6)
            e = ttk.Entry(box, textvariable=var, width=34, show=show)
            e.grid(row=r, column=1, padx=6, pady=6, sticky='w')
            return e

        ttk.Label(box, text="Роль:").grid(row=0, column=0, sticky='e', padx=6, pady=6)
        role_frame = ttk.Frame(box)
        role_frame.grid(row=0, column=1, sticky='w', padx=6, pady=6)
        ttk.Radiobutton(role_frame, text="Тренирующийся",
                        variable=self.role_var, value='athlete').pack(side='left')
        ttk.Radiobutton(role_frame, text="Тренер",
                        variable=self.role_var, value='trainer').pack(side='left', padx=(12, 0))

        row("Логин:", self.login_var, r=1)
        row("Пароль:", self.pw_var, show='*', r=2)
        row("Повтор пароля:", self.pw2_var, show='*', r=3)
        row("ФИО:", self.fio_var, r=4)
        row("E-mail:", self.email_var, r=5)
        row("Телефон:", self.phone_var, r=6)

        btns = ttk.Frame(self)
        btns.pack(pady=20)
        ttk.Button(btns, text="Зарегистрироваться",
                   command=self.do_register, width=22).pack(side='left', padx=5)
        ttk.Button(btns, text="Назад",
                   command=self.app.show_login, width=18).pack(side='left', padx=5)

    def do_register(self):
        login = self.login_var.get().strip()
        pw = self.pw_var.get().strip()
        pw2 = self.pw2_var.get().strip()
        fio = self.fio_var.get().strip()
        email = self.email_var.get().strip()
        phone = self.phone_var.get().strip()
        role = self.role_var.get()

        if not (login and pw and fio):
            messagebox.showwarning("Внимание", "Заполните логин, пароль и ФИО.")
            return
        if pw != pw2:
            messagebox.showwarning("Внимание", "Пароли не совпадают.")
            return
        if len(pw) < 4:
            messagebox.showwarning("Внимание", "Пароль должен содержать не менее 4 символов.")
            return
        if fetch_one("SELECT 1 FROM users WHERE login=?", (login,)) is not None:
            messagebox.showerror("Ошибка", "Пользователь с таким логином уже существует.")
            return

        uid = execute(
            "INSERT INTO users (login, password_hash, role, full_name, email, phone) "
            "VALUES (?,?,?,?,?,?)",
            (login, hash_password(pw), role, fio, email, phone)
        )
        if role == 'trainer':
            execute("INSERT INTO trainers (user_id, specialization, experience) VALUES (?,?,?)",
                    (uid, '', 0))
        else:
            execute("INSERT INTO athletes (user_id, birth_date, goal) VALUES (?,?,?)",
                    (uid, '', ''))
        messagebox.showinfo("Успех", "Регистрация завершена. Теперь вы можете войти.")
        self.app.show_login()
