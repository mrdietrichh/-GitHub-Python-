from tkinter import ttk

from database import fetch_all
from tabs_trainings import TrainingViewWindow
from tabs_progress import AthleteProgressTab
from tabs_profile import ProfileTab


class AthleteTabs(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.user = parent.user

        nb = ttk.Notebook(self)
        nb.pack(fill='both', expand=True, padx=8, pady=8)
        nb.add(AthleteTrainingsTab(nb, self.user), text='Мои тренировки')
        nb.add(AthleteProgressTab(nb, self.user), text='Мой прогресс')
        nb.add(ProfileTab(nb, self.user), text='Профиль')


class AthleteTrainingsTab(ttk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, padding=10)
        self.user = user

        top = ttk.Frame(self)
        top.pack(fill='x', pady=(0, 8))
        ttk.Button(top, text="Открыть тренировку", command=self.open).pack(side='left')
        ttk.Button(top, text="Обновить", command=self.reload).pack(side='right')

        cols = ('id', 'title', 'trainer', 'date', 'status')
        self.tree = ttk.Treeview(self, columns=cols, show='headings')
        self.tree.heading('id', text='ID')
        self.tree.heading('title', text='Название')
        self.tree.heading('trainer', text='Тренер')
        self.tree.heading('date', text='Дата')
        self.tree.heading('status', text='Статус')
        self.tree.column('id', width=50, anchor='center')
        self.tree.column('title', width=300)
        self.tree.column('trainer', width=250)
        self.tree.column('date', width=120, anchor='center')
        self.tree.column('status', width=140, anchor='center')
        self.tree.pack(fill='both', expand=True)
        self.tree.bind('<Double-1>', lambda e: self.open())

        self.reload()

    def reload(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        rows = fetch_all("""
            SELECT t.id, t.title, t.date, t.status,
                   u.full_name AS trainer_name
            FROM trainings t
            LEFT JOIN users u ON u.id = t.trainer_id
            WHERE t.athlete_id=?
            ORDER BY t.date DESC, t.id DESC
        """, (self.user['id'],))
        for r in rows:
            self.tree.insert('', 'end', iid=str(r['id']),
                             values=(r['id'], r['title'],
                                     r['trainer_name'] or '—',
                                     r['date'] or '', r['status'] or ''))

    def open(self):
        sel = self.tree.selection()
        if not sel:
            return
        TrainingViewWindow(self, int(sel[0]), self.user)
        self.reload()
