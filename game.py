import random
from copy import deepcopy

class Ship:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.coords = self.get_coords()
        self.hits = set()

    def get_coords(self):
        x1, y1 = self.start
        x2, y2 = self.end
        coords = []
        if x1 == x2:
            for y in range(min(y1, y2), max(y1, y2) + 1):
                coords.append((x1, y))
        else:
            for x in range(min(x1, x2), max(x1, x2) + 1):
                coords.append((x, y1))
        return coords

    def hit(self, coord):
        if coord in self.coords and coord not in self.hits:
            self.hits.add(coord)
            return True
        return False

    def is_sunk(self):
        return len(self.hits) == len(self.coords)

class Board:
    def __init__(self, size):
        self.size = size
        self.grid = [[" " for _ in range(size)] for _ in range(size)]
        self.ships = []
        self.hits = set()
        self.misses = set()

    def place_ship(self, ship):
        for x, y in ship.coords:
            self.grid[x][y] = "S"
        self.ships.append(ship)

    def can_place(self, ship):
        for x, y in ship.coords:
            if not (0 <= x < self.size and 0 <= y < self.size):
                return False
            if self.grid[x][y] != " ":
                return False
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.size and 0 <= ny < self.size:
                        if self.grid[nx][ny] == "S":
                            return False
        return True

    def receive_shot(self, coord):
        x, y = coord
        if coord in self.hits or coord in self.misses:
            return None
        if self.grid[x][y] == "S":
            self.hits.add(coord)
            for ship in self.ships:
                if ship.hit(coord):
                    if ship.is_sunk():
                        return "sunk"
                    return "hit"
        else:
            self.misses.add(coord)
            return "miss"
        return None

    def all_sunk(self):
        return all(ship.is_sunk() for ship in self.ships)

class AI:
    def __init__(self, level, board_size):
        self.level = level
        self.board_size = board_size
        self.shots = set()
        self.hits_stack = []
        self.last_hit = None
        self.directions = [(0,1),(0,-1),(1,0),(-1,0)]

    def get_shot(self):
        if self.level == "easy":
            return self.random_shot()
        else:
            return self.smart_shot()

    def random_shot(self):
        while True:
            x = random.randint(0, self.board_size - 1)
            y = random.randint(0, self.board_size - 1)
            if (x, y) not in self.shots:
                self.shots.add((x, y))
                return (x, y)

    def smart_shot(self):
        if self.hits_stack:
            return self.hits_stack.pop()
        if self.last_hit:
            x, y = self.last_hit
            for dx, dy in self.directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.board_size and 0 <= ny < self.board_size and (nx, ny) not in self.shots:
                    self.shots.add((nx, ny))
                    return (nx, ny)
            self.last_hit = None
            return self.random_shot()
        return self.random_shot()

    def register_result(self, coord, result):
        self.shots.add(coord)
        if result in ("hit", "sunk"):
            self.last_hit = coord
            if result == "sunk":
                self.last_hit = None
                self.hits_stack.clear()
            else:
                x, y = coord
                for dx, dy in self.directions:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.board_size and 0 <= ny < self.board_size and (nx, ny) not in self.shots:
                        self.hits_stack.append((nx, ny))

class Game:
    def __init__(self, config):
        self.size = config["grid_size"]
        self.ship_sizes = config["ship_sizes"]
        self.ai_level = config["ai_level"]
        self.player_board = Board(self.size)
        self.ai_board = Board(self.size)
        self.ai = AI(self.ai_level, self.size)
        self.player_ships_placed = False
        self.ai_ships_placed = False
        self.turn = "player"

    def place_ships_randomly(self, board):
        ships_to_place = sorted(self.ship_sizes, reverse=True)
        for size in ships_to_place:
            placed = False
            attempts = 0
            while not placed and attempts < 1000:
                attempts += 1
                if random.choice([True, False]):
                    x = random.randint(0, self.size - 1)
                    y = random.randint(0, self.size - size)
                    end = (x, y + size - 1)
                else:
                    x = random.randint(0, self.size - size)
                    y = random.randint(0, self.size - 1)
                    end = (x + size - 1, y)
                ship = Ship((x, y), end)
                if board.can_place(ship):
                    board.place_ship(ship)
                    placed = True
            if not placed:
                raise RuntimeError("Не удалось разместить корабли")

    def setup(self):
        self.place_ships_randomly(self.player_board)
        self.place_ships_randomly(self.ai_board)
        self.player_ships_placed = True
        self.ai_ships_placed = True

    def player_shot(self, coord):
        if self.turn != "player":
            return None
        result = self.ai_board.receive_shot(coord)
        if result is None:
            return None
        if self.ai_board.all_sunk():
            self.turn = "player_wins"
            return "win"
        self.turn = "ai"
        return result

    def ai_shot(self):
        if self.turn != "ai":
            return None
        coord = self.ai.get_shot()
        result = self.player_board.receive_shot(coord)
        if result is None:
            return self.ai_shot()
        self.ai.register_result(coord, result)
        if self.player_board.all_sunk():
            self.turn = "ai_wins"
            return "lose"
        if result in ("hit", "sunk"):
            self.turn = "ai"
        else:
            self.turn = "player"
        return coord, result
