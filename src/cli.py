import sys
from typing import List
from .config import CSV_PATH, PAGE_SIZE
from .market import load_markets, filter_by_city_state, filter_by_zip, filter_by_distance, Market
from .distance import haversine
from .reviews import get_reviews_for_market, add_review, get_average_rating
from .utils import paginate, sort_markets, format_market_short, format_market_full, validate_rating

class AppState:
    def __init__(self):
        self.all_markets: List[Market] = []
        self.current_list: List[Market] = []

state = AppState()

def load_initial_data():
    try:
        state.all_markets = load_markets(CSV_PATH)
        state.current_list = state.all_markets.copy()
        print(f"Загружено {len(state.all_markets)} рынков.")
    except FileNotFoundError:
        print(f"Ошибка: файл {CSV_PATH} не найден.")
        sys.exit(1)

def display_page(items: List[Market], page: int, page_size: int = PAGE_SIZE):
    page_items = paginate(items, page, page_size)
    if not page_items:
        print("Нет записей на этой странице.")
        return
    for i, m in enumerate(page_items, start=(page-1)*page_size + 1):
        print(format_market_short(m, i))
    total_pages = (len(items) + page_size - 1) // page_size
    print(f"\nСтраница {page} из {total_pages} (всего записей: {len(items)})")

def cmd_list(args: List[str]):
    page = 1
    if args:
        try:
            page = int(args[0])
        except ValueError:
            print("Некорректный номер страницы. Используйте list [номер]")
            return
    if page < 1:
        page = 1
    display_page(state.current_list, page)

def cmd_search(args: List[str]):
    if not args:
        print("Использование: search <city> [state] или search zip <zipcode> [distance]")
        return
    if args[0].lower() == "zip":
        if len(args) < 2:
            print("Укажите почтовый индекс: search zip 02108")
            return
        zipcode = args[1]
        distance = 0.0
        if len(args) >= 3:
            try:
                distance = float(args[2])
            except ValueError:
                print("Расстояние должно быть числом (в милях).")
                return
        filtered = filter_by_zip(state.all_markets, zipcode)
        if distance > 0 and filtered:
            lat = filtered[0].lat
            lon = filtered[0].lon
            filtered = filter_by_distance(filtered, lat, lon, distance)
        state.current_list = sorted(filtered, key=lambda m: m.name)
        print(f"Найдено {len(state.current_list)} рынков.")
    else:
        city = args[0]
        state_str = args[1] if len(args) > 1 else None
        filtered = filter_by_city_state(state.all_markets, city, state_str)
        state.current_list = sorted(filtered, key=lambda m: m.name)
        print(f"Найдено {len(state.current_list)} рынков.")
    display_page(state.current_list, 1)

def cmd_view(args: List[str]):
    if not args:
        print("Укажите ID рынка: view <id>")
        return
    try:
        market_id = int(args[0])
    except ValueError:
        print("ID должен быть числом.")
        return
    market = next((m for m in state.current_list if m.id == market_id), None)
    if not market:
        print(f"Рынок с ID {market_id} не найден в текущем списке.")
        return
    print(format_market_full(market))
    reviews = get_reviews_for_market(market_id)
    avg = get_average_rating(market_id)
    print(f"\nСредний рейтинг на основе рецензий: {avg:.1f}")
    if reviews:
        print("Рецензии:")
        for r in reviews:
            print(f"  {r['user_name']} – {r['rating']} звёзд: {r['text']} ({r['timestamp']})")
    else:
        print("Нет рецензий для этого рынка.")

def cmd_review(args: List[str]):
    if not args:
        print("Укажите ID рынка: review <id>")
        return
    try:
        market_id = int(args[0])
    except ValueError:
        print("ID должен быть числом.")
        return
    market = next((m for m in state.all_markets if m.id == market_id), None)
    if not market:
        print(f"Рынок с ID {market_id} не найден.")
        return
    print(f"Оставьте рецензию для рынка: {market.name}")
    name = input("Ваше имя и фамилия: ").strip()
    if not name:
        print("Имя обязательно.")
        return
    rating_str = input("Рейтинг (1-5): ").strip()
    try:
        rating = int(rating_str)
    except ValueError:
        print("Рейтинг должен быть числом.")
        return
    if not validate_rating(rating):
        print("Рейтинг должен быть от 1 до 5.")
        return
    text = input("Текст рецензии (необязательно): ").strip()
    add_review(market_id, name, rating, text)
    print("Рецензия добавлена!")

def cmd_sort(args: List[str]):
    if not args:
        print("Использование: sort <criterion> [asc|desc]")
        print("Критерии: rating, city, state")
        return
    criterion = args[0].lower()
    reverse = False
    if len(args) >= 2:
        if args[1].lower() == "desc":
            reverse = True
        elif args[1].lower() == "asc":
            reverse = False
        else:
            print("Направление должно быть asc или desc. Используется asc по умолчанию.")
    if criterion == "rating":
        state.current_list = sort_markets(state.current_list, lambda m: m.rating, reverse)
    elif criterion == "city":
        state.current_list = sort_markets(state.current_list, lambda m: m.city, reverse)
    elif criterion == "state":
        state.current_list = sort_markets(state.current_list, lambda m: m.state, reverse)
    else:
        print(f"Неизвестный критерий: {criterion}")
        return
    print("Список отсортирован.")
    display_page(state.current_list, 1)

def cmd_delete(args: List[str]):
    if not args:
        print("Укажите ID рынка для удаления: delete <id>")
        return
    try:
        market_id = int(args[0])
    except ValueError:
        print("ID должен быть числом.")
        return
    before = len(state.current_list)
    state.current_list = list(filter(lambda m: m.id != market_id, state.current_list))
    after = len(state.current_list)
    if after < before:
        print(f"Рынок с ID {market_id} удалён из текущего списка.")
        display_page(state.current_list, 1)
    else:
        print(f"Рынок с ID {market_id} не найден в текущем списке.")

def cmd_exit(args: List[str]):
    print("Выход из программы.")
    sys.exit(0)

def main():
    load_initial_data()
    print("\nДобро пожаловать в приложение Farmers Market CLI!")
    print("Доступные команды:")
    print("  list [page]                  - показать список рынков (постранично)")
    print("  search <city> [state]        - поиск по городу и штату")
    print("  search zip <zip> [distance]  - поиск по почтовому индексу с радиусом (мили)")
    print("  view <id>                    - подробная информация о рынке")
    print("  review <id>                  - добавить рецензию")
    print("  sort <criterion> [asc|desc]  - сортировка: rating, city, state")
    print("  delete <id>                  - удалить рынок из текущего списка")
    print("  exit                         - выход\n")

    while True:
        try:
            cmd_line = input("> ").strip()
            if not cmd_line:
                continue
            parts = cmd_line.split()
            command = parts[0].lower()
            args = parts[1:]
            if command == "list":
                cmd_list(args)
            elif command == "search":
                cmd_search(args)
            elif command == "view":
                cmd_view(args)
            elif command == "review":
                cmd_review(args)
            elif command == "sort":
                cmd_sort(args)
            elif command == "delete":
                cmd_delete(args)
            elif command == "exit":
                cmd_exit(args)
            else:
                print(f"Неизвестная команда: {command}")
        except KeyboardInterrupt:
            print("\nВыход.")
            sys.exit(0)
        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
