import argparse
import os
from PIL import Image, ImageDraw

def read_initial_state(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    if not lines:
        raise ValueError("Файл пуст или не содержит данных")

    rows = len(lines)
    cols = max(len(line) for line in lines)
    state = [[False] * cols for _ in range(rows)]

    for r, line in enumerate(lines):
        for c, ch in enumerate(line):
            if ch == '#':
                state[r][c] = True
    return state, rows, cols


def save_state_to_file(file_handle, state, step, is_first=False):
    if not is_first:
        file_handle.write("\n")
    file_handle.write(f"# Step {step}\n")
    for row in state:
        line = ''.join('#' if cell else '.' for cell in row)
        file_handle.write(line + "\n")


def count_neighbors(state, r, c, rows, cols):
    neighbors = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and state[nr][nc]:
                neighbors += 1
    return neighbors


def next_generation(state, age, rows, cols):
    new_state = [[False] * cols for _ in range(rows)]
    new_age = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            live_neighbors = count_neighbors(state, r, c, rows, cols)
            if state[r][c]:
                if live_neighbors in (2, 3):
                    new_state[r][c] = True
                    new_age[r][c] = age[r][c] + 1
            else:
                if live_neighbors == 3:
                    new_state[r][c] = True
                    new_age[r][c] = 1
    return new_state, new_age


def color_for_age(age, max_age, base_rgb):
    if age <= 0:
        return (0, 0, 0)
    factor = min(age, max_age) / max_age
    r = int(255 + (base_rgb[0] - 255) * factor)
    g = int(255 + (base_rgb[1] - 255) * factor)
    b = int(255 + (base_rgb[2] - 255) * factor)
    return (r, g, b)


def save_image(state, age, step, base_color, cell_size, max_age, out_dir):

    rows = len(state)
    cols = len(state[0])
    width = cols * cell_size
    height = rows * cell_size
    img = Image.new('RGB', (width, height), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    for r in range(rows):
        for c in range(cols):
            if state[r][c]:
                color = color_for_age(age[r][c], max_age, base_color)
                x1 = c * cell_size
                y1 = r * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                draw.rectangle([x1, y1, x2, y2], fill=color)

    os.makedirs(out_dir, exist_ok=True)
    filename = os.path.join(out_dir, f"step_{step:04d}.png")
    img.save(filename)
    print(f"Сохранён снимок: {filename}")


def parse_color(color_str):
    if color_str.startswith('(') and color_str.endswith(')'):
        parts = color_str[1:-1].split(',')
        return tuple(int(p.strip()) for p in parts)
    try:
        return Image.new('RGB', (1,1), color_str).getpixel((0,0))
    except:
        raise ValueError(f"Не удалось распознать цвет: {color_str}")


def main():
    parser = argparse.ArgumentParser(description="Conway's Game of Life с визуализацией возраста")
    parser.add_argument("input_file", help="файл с начальной конфигурацией")
    parser.add_argument("output_file", help="файл для записи всех поколений")
    parser.add_argument("--steps", type=int, required=True, help="количество шагов моделирования")
    parser.add_argument("--color", default="#FF0000", help="базовый цвет живых клеток (red, #RRGGBB, (r,g,b))")
    parser.add_argument("--png-dir", default="png_out", help="папка для PNG-снимков")
    parser.add_argument("--cell-size", type=int, default=10, help="размер ячейки в пикселях")
    parser.add_argument("--max-age", type=int, default=10, help="максимальный возраст для оттенков")
    args = parser.parse_args()

    try:
        state, rows, cols = read_initial_state(args.input_file)
    except Exception as e:
        print(f"Ошибка чтения входного файла: {e}")
        return

    age = [[0] * cols for _ in range(rows)]

    try:
        base_rgb = parse_color(args.color)
    except ValueError as e:
        print(e)
        return

    with open(args.output_file, 'w') as out_f:
        save_state_to_file(out_f, state, 0, is_first=True)
        save_image(state, age, 0, base_rgb, args.cell_size, args.max_age, args.png_dir)
        for step in range(1, args.steps + 1):
            state, age = next_generation(state, age, rows, cols)
            save_state_to_file(out_f, state, step, is_first=False)
            save_image(state, age, step, base_rgb, args.cell_size, args.max_age, args.png_dir)
    print(f"Моделирование завершено. Результаты в {args.output_file} и {args.png_dir}")

if __name__ == "__main__":
    main()