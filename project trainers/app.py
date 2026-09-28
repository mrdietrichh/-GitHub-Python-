import tkinter as tk
from tkinter import ttk

from constants import APP_TITLE, ROLES
from database import fetch_all, execute
from auth import LoginFrame, RegisterFrame
from tabs_trainer import TrainerTabs
from tabs_athlete import AthleteTabs
from tabs_admin import AdminTabs


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1150x720")
        self.minsize(1000, 620)
        self.current_user = None

        self._apply_style()
        self.show_login()

    def _apply_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass
        style.configure('TNotebook.Tab', padding=(14, 8), font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 10), padding=6)
        style.configure('TLabel', font=('Segoe UI', 10))
        style.configure('Header.TLabel', font=('Segoe UI', 16, 'bold'))
        style.configure('Sub.TLabel', font=('Segoe UI', 10), foreground='#555')
        style.configure('Treeview', font=('Segoe UI', 9), rowheight=24)
        style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'))

    def clear(self):
        for w in self.winfo_children():
            w.destroy()

    def show_login(self):
        self.current_user = None
        self.clear()
        LoginFrame(self).pack(fill='both', expand=True)

    def show_register(self):
        self.clear()
        RegisterFrame(self).pack(fill='both', expand=True)

    def show_main(self, user):
        self.current_user = user
        self.clear()
        MainFrame(self, user).pack(fill='both', expand=True)


class MainFrame(ttk.Frame):
    def __init__(self, app, user):
        super().__init__(app)
        self.app = app
        self.user = user

        top = ttk.Frame(self, padding=(10, 6))
        top.pack(fill='x')
        ttk.Label(top,
                  text=f"Пользователь: {user['full_name']}  ({ROLES.get(user['role'], user['role'])})",
                  style='Sub.TLabel').pack(side='left')
        ttk.Button(top, text="Выйти", command=self.app.show_login).pack(side='right')
        ttk.Button(top, text="Уведомления", command=self.open_notifications).pack(side='right', padx=6)

        ttk.Separator(self).pack(fill='x')

        role = user['role']
        if role == 'trainer':
            TrainerTabs(self).pack(fill='both', expand=True)
        elif role == 'athlete':
            AthleteTabs(self).pack(fill='both', expand=True)
        elif role == 'admin':
            AdminTabs(self).pack(fill='both', expand=True)
        else:
            ttk.Label(self, text="Неизвестная роль").pack(pady=40)

    def open_notifications(self):
        NotificationsWindow(self, self.user['id'])


class NotificationsWindow(tk.Toplevel):
    def __init__(self, parent, user_id):
        super().__init__(parent)
        self.title("Уведомления")
        self.geometry("620x420")
        self.transient(parent)

        cols = ('date', 'message', 'read')
        tree = ttk.Treeview(self, columns=cols, show='headings')
        tree.heading('date', text='Дата')
        tree.heading('message', text='Сообщение')
        tree.heading('read', text='Прочитано')
        tree.column('date', width=130)
        tree.column('message', width=380)
        tree.column('read', width=90, anchor='center')
        tree.pack(fill='both', expand=True, padx=10, pady=10)

        rows = fetch_all(
            "SELECT id, date, message, is_read FROM notifications "
            "WHERE user_id=? ORDER BY date DESC", (user_id,))
        for r in rows:
            tree.insert('', 'end', iid=str(r['id']),
                        values=(r['date'], r['message'],
                                'Да' if r['is_read'] else 'Нет'))

        def mark_read():
            sel = tree.selection()
            if not sel:
                return
            execute("UPDATE notifications SET is_read=1 WHERE id=?", (int(sel[0]),))
            tree.set(sel[0], 'read', 'Да')

        ttk.Button(self, text="Отметить прочитанным",
                   command=mark_read).pack(pady=(0, 10))
