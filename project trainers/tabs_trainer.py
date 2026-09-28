from tkinter import ttk

from tabs_exercises import ExercisesTab
from tabs_trainings import TrainingsTab
from tabs_progress import TrainerProgressTab
from tabs_profile import ProfileTab


class TrainerTabs(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.user = parent.user

        nb = ttk.Notebook(self)
        nb.pack(fill='both', expand=True, padx=8, pady=8)

        nb.add(ExercisesTab(nb, self.user), text='Упражнения')
        nb.add(TrainingsTab(nb, self.user), text='Тренировки')
        nb.add(TrainerProgressTab(nb, self.user), text='Прогресс спортсменов')
        nb.add(ProfileTab(nb, self.user), text='Профиль')
