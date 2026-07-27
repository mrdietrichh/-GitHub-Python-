import json
import os
from constants import *

class ConfigManager:
    def __init__(self):
        self.config = self.load_config()
        self.scores = self.load_scores()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        return {
            "grid_size": DEFAULT_GRID_SIZE,
            "ship_sizes": DEFAULT_SHIP_SIZES,
            "ai_level": DEFAULT_AI_LEVEL,
            "window_width": DEFAULT_WINDOW_WIDTH,
            "window_height": DEFAULT_WINDOW_HEIGHT,
            "bg_color": DEFAULT_BG_COLOR,
            "cell_color": DEFAULT_CELL_COLOR,
            "ship_color": DEFAULT_SHIP_COLOR,
            "hit_color": DEFAULT_HIT_COLOR,
            "miss_color": DEFAULT_MISS_COLOR,
            "font": DEFAULT_FONT
        }

    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)

    def load_scores(self):
        if os.path.exists(SCORES_FILE):
            with open(SCORES_FILE, "r") as f:
                return json.load(f)
        return []

    def save_scores(self):
        with open(SCORES_FILE, "w") as f:
            json.dump(self.scores, f, indent=4)

    def add_score(self, name, wins, losses):
        self.scores.append({"name": name, "wins": wins, "losses": losses})
        self.scores.sort(key=lambda x: x["wins"], reverse=True)
        if len(self.scores) > 10:
            self.scores = self.scores[:10]
        self.save_scores()
