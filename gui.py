import tkinter as tk
from tkinter import ttk, messagebox
import random
from game import Game
from config_manager import ConfigManager
from constants import *

class BattleshipGUI:
    def __init__(self, root):
        self.root = root
        self.config_mgr = ConfigManager()
        self.config = self.config_mgr.config
        self.root.title("Морской Бой")
        self.root.geometry(f"{self.config['window_width']}x{self.config['window_height']}")
        self.root.configure(bg=self.config["bg_color"])
        self.game = None
        self.selected_cell = None
        self.player_name = tk.StringVar(value="Игрок")
        self.create_menu()
        self.create_widgets()
        self.new_game()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Новая игра", command=self.new_game)
        file_menu.add_command(label="Настройки", command=self.open_settings)
        file_menu.add_command(label="Рекорды", command=self.open_scores)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        menubar.add_cascade(label="Меню", menu=file_menu)
        self.root.config(menu=menubar)

    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg=self.config["bg_color"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        left_frame = tk.Frame(main_frame, bg=self.config["bg_color"])
        left_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(left_frame, text="Ваше поле", font=self.config["font"], bg=self.config["bg_color"], fg="white").pack()
        self.player_canvas = tk.Canvas(left_frame, width=300, height=300, bg=self.config["cell_color"])
        self.player_canvas.pack()

        right_frame = tk.Frame(main_frame, bg=self.config["bg_color"])
        right_frame.pack(side=tk.RIGHT, padx=10)
        tk.Label(right_frame, text="Поле противника", font=self.config["font"], bg=self.config["bg_color"], fg="white").pack()
        self.ai_canvas = tk.Canvas(right_frame, width=300, height=300, bg=self.config["cell_color"])
        self.ai_canvas.pack()

        info_frame = tk.Frame(self.root, bg=self.config["bg_color"])
        info_frame.pack(pady=10)
        self.status_label = tk.Label(info_frame, text="Ваш ход", font=self.config["font"], bg=self.config["bg_color"], fg="white")
        self.status_label.pack(side=tk.LEFT, padx=10)
        tk.Label(info_frame, text="Имя игрока:", font=self.config["font"], bg=self.config["bg_color"], fg="white").pack(side=tk.LEFT)
        tk.Entry(info_frame, textvariable=self.player_name, font=self.config["font"]).pack(side=tk.LEFT, padx=5)

        self.ai_canvas.bind("<Button-1>", self.on_ai_click)

    def new_game(self):
        self.config = self.config_mgr.config
        self.game = Game(self.config)
        self.game.setup()
        self.draw_boards()
        self.status_label.config(text="Ваш ход")
        self.game.turn = "player"

    def draw_boards(self):
        self.draw_board(self.player_canvas, self.game.player_board, show_ships=True)
        self.draw_board(self.ai_canvas, self.game.ai_board, show_ships=False)

    def draw_board(self, canvas, board, show_ships):
        canvas.delete("all")
        size = board.size
        cell_size = 300 // size
        for i in range(size):
            for j in range(size):
                x1, y1 = j * cell_size, i * cell_size
                x2, y2 = x1 + cell_size, y1 + cell_size
                color = self.config["cell_color"]
                if (i, j) in board.hits:
                    color = self.config["hit_color"]
                elif (i, j) in board.misses:
                    color = self.config["miss_color"]
                elif show_ships and board.grid[i][j] == "S":
                    color = self.config["ship_color"]
                canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
                if (i, j) in board.hits and board.grid[i][j] == "S":
                    canvas.create_text(x1 + cell_size//2, y1 + cell_size//2, text="X", font=("Arial", 14, "bold"), fill="white")
                elif (i, j) in board.misses:
                    canvas.create_text(x1 + cell_size//2, y1 + cell_size//2, text="·", font=("Arial", 14, "bold"), fill="black")

    def on_ai_click(self, event):
        if self.game is None or self.game.turn != "player":
            return
        x = event.y // (300 // self.game.size)
        y = event.x // (300 // self.game.size)
        if not (0 <= x < self.game.size and 0 <= y < self.game.size):
            return
        result = self.game.player_shot((x, y))
        if result is None:
            return
        self.draw_boards()
        if result == "win":
            self.status_label.config(text="Вы победили!")
            self.config_mgr.add_score(self.player_name.get(), 1, 0)
            messagebox.showinfo("Победа", "Вы уничтожили все корабли противника!")
            return
        self.status_label.config(text="Ход противника...")
        self.root.after(500, self.ai_turn)

    def ai_turn(self):
        if self.game is None or self.game.turn != "ai":
            return
        result = self.game.ai_shot()
        if result is None:
            return
        if result == "lose":
            self.draw_boards()
            self.status_label.config(text="Вы проиграли")
            self.config_mgr.add_score(self.player_name.get(), 0, 1)
            messagebox.showinfo("Поражение", "Все ваши корабли уничтожены!")
            return
        coord, res = result
        self.draw_boards()
        if res == "sunk":
            self.status_label.config(text="Противник потопил корабль!")
        elif res == "hit":
            self.status_label.config(text="Противник попал!")
        else:
            self.status_label.config(text="Ваш ход")
        if self.game.turn == "player":
            self.status_label.config(text="Ваш ход")
        else:
            self.root.after(500, self.ai_turn)

    def open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("Настройки")
        win.geometry("400x500")
        win.configure(bg=self.config["bg_color"])
        frame = ttk.Frame(win)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(frame, text="Размер поля:").grid(row=0, column=0, sticky="w")
        size_var = tk.IntVar(value=self.config["grid_size"])
        ttk.Spinbox(frame, from_=6, to=12, textvariable=size_var).grid(row=0, column=1)

        ttk.Label(frame, text="Корабли (через запятую):").grid(row=1, column=0, sticky="w")
        ships_var = tk.StringVar(value=",".join(map(str, self.config["ship_sizes"])))
        ttk.Entry(frame, textvariable=ships_var).grid(row=1, column=1)

        ttk.Label(frame, text="Сложность ИИ:").grid(row=2, column=0, sticky="w")
        ai_var = tk.StringVar(value=self.config["ai_level"])
        ttk.Combobox(frame, textvariable=ai_var, values=["easy", "hard"]).grid(row=2, column=1)

        ttk.Label(frame, text="Цвет фона:").grid(row=3, column=0, sticky="w")
        bg_var = tk.StringVar(value=self.config["bg_color"])
        ttk.Entry(frame, textvariable=bg_var).grid(row=3, column=1)

        ttk.Label(frame, text="Цвет клетки:").grid(row=4, column=0, sticky="w")
        cell_var = tk.StringVar(value=self.config["cell_color"])
        ttk.Entry(frame, textvariable=cell_var).grid(row=4, column=1)

        ttk.Label(frame, text="Цвет корабля:").grid(row=5, column=0, sticky="w")
        ship_var = tk.StringVar(value=self.config["ship_color"])
        ttk.Entry(frame, textvariable=ship_var).grid(row=5, column=1)

        ttk.Label(frame, text="Цвет попадания:").grid(row=6, column=0, sticky="w")
        hit_var = tk.StringVar(value=self.config["hit_color"])
        ttk.Entry(frame, textvariable=hit_var).grid(row=6, column=1)

        ttk.Label(frame, text="Цвет промаха:").grid(row=7, column=0, sticky="w")
        miss_var = tk.StringVar(value=self.config["miss_color"])
        ttk.Entry(frame, textvariable=miss_var).grid(row=7, column=1)

        def save_settings():
            try:
                size = size_var.get()
                ships = [int(s.strip()) for s in ships_var.get().split(",") if s.strip()]
                if not ships:
                    raise ValueError
                self.config["grid_size"] = size
                self.config["ship_sizes"] = ships
                self.config["ai_level"] = ai_var.get()
                self.config["bg_color"] = bg_var.get()
                self.config["cell_color"] = cell_var.get()
                self.config["ship_color"] = ship_var.get()
                self.config["hit_color"] = hit_var.get()
                self.config["miss_color"] = miss_var.get()
                self.config_mgr.config = self.config
                self.config_mgr.save_config()
                win.destroy()
                self.root.configure(bg=self.config["bg_color"])
                self.new_game()
            except:
                messagebox.showerror("Ошибка", "Некорректные данные")

        ttk.Button(frame, text="Сохранить", command=save_settings).grid(row=8, columnspan=2, pady=10)

    def open_scores(self):
        win = tk.Toplevel(self.root)
        win.title("Рекорды")
        win.geometry("400x300")
        win.configure(bg=self.config["bg_color"])
        tree = ttk.Treeview(win, columns=("Имя", "Победы", "Поражения"), show="headings")
        tree.heading("Имя", text="Имя")
        tree.heading("Победы", text="Победы")
        tree.heading("Поражения", text="Поражения")
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        for score in self.config_mgr.scores:
            tree.insert("", tk.END, values=(score["name"], score["wins"], score["losses"]))
        ttk.Button(win, text="Закрыть", command=win.destroy).pack(pady=5)
