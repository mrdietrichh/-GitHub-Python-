import os
import sys


def get_base_dir() -> str:
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


DB_PATH = os.path.join(get_base_dir(), 'fitness_assistant.db')

APP_TITLE = "Приложение-ассистент для тренеров и тренирующихся"

ROLES = {
    'trainer': 'Тренер',
    'athlete': 'Тренирующийся',
    'admin':   'Администратор',
}

TRAINING_STATUSES = ['Черновик', 'Назначена', 'Выполняется', 'Завершена', 'Отменена']
