import sys
from typing import List
from .config import CSV_PATH, REVIEWS_PATH, PAGE_SIZE
from .market import MarketManager
from .reviews import ReviewManager
from .utils import paginate, validate_rating, format_market_short, format_market_full

class App:
    def __init__(self):
        self.market_manager = MarketManager()
        self.review_manager = ReviewManager(REVIEWS_PATH)

    def load_data(self):
        try:
            self.market_manager.load(CSV_PATH)
            print(f"Загружено {len(self.market_manager.all_markets)} рынков.")
        except FileNotFoundError as e:
            print(e)
            sys.exit(1)

    def list_markets(self, page: int = 1):
        items = self.market_manager.current_list
        page_items = paginate(items, page, PAGE_SIZE)
        if not page_items:
            print("Нет записей на этой странице.")
            return
        for i, m in enumerate(page_items, start=(page-1)*PAGE_SIZE + 1):
            print(format_market_short(m, i))
        total_pages = (len(items) + PAGE_SIZE - 1) // PAGE_SIZE
        print(f"\nСтраница {page} из {total_pages} (всего записей: {len(items)})")

    def search_by_city_state(self, city: str, state: str = None):
        self.market_manager.filter_by_city_state(city, state)
        print(f"Найдено {len(self.market_manager.current_list)} рынков.")
        self.list_markets(1)

    def search_by_zip(self, zipcode: str, distance: float = 0.0):
        self.market_manager.filter_by_zip(zipcode)
        if distance > 0 and self.market_manager.current_list:
            first = self.market_manager.current_list[0]
            self.market_manager.filter_by_distance(first.lat, first.lon, distance)
        print(f"Найдено {len(self.market_manager.current_list)} рынков.")
        self.list_markets(1)

    def view_market(self, market_id: int):
        market = self.market_manager.get_by_id(market_id)
        if not market:
            print(f"Рынок с ID {market_id} не найден в текущем списке.")
            return
        print(format_market_full(market))
        reviews = self.review_manager.get_for_market(market_id)
        avg = self.review_manager.average_rating(market_id)
        print(f"\nСредний рейтинг на основе рецензий: {avg:.1f}")
        if reviews:
            print("Рецензии:")
            for r in reviews:
                print(f"  {r['user_name']} – {r['rating']} звёзд: {r['text']} ({r['timestamp']})")
        else:
            print("Нет рецензий для этого рынка.")

    def add_review(self, market_id: int, user_name: str, rating: int, text: str = ""):
        # проверяем существование рынка
        if not any(m.id == market_id for m in self.market_manager.all_markets):
            print(f"Рынок с ID {market_id} не найден.")
            return False
        self.review_manager.add(market_id, user_name, rating, text)
        print("Рецензия добавлена!")
        return True

    def sort_markets(self, criterion: str, reverse: bool = False):
        if criterion == "rating":
            self.market_manager.sort(lambda m: m.rating, reverse)
        elif criterion == "city":
            self.market_manager.sort(lambda m: m.city, reverse)
        elif criterion == "state":
            self.market_manager.sort(lambda m: m.state, reverse)
        else:
            print(f"Неизвестный критерий: {criterion}")
            return
        print("Список отсортирован.")
        self.list_markets(1)

    def delete_market(self, market_id: int):
        if self.market_manager.delete(market_id):
            print(f"Рынок с ID {market_id} удалён из текущего списка.")
            self.list_markets(1)
        else:
            print(f"Рынок с ID {market_id} не найден в текущем списке.")

    def exit(self):
        print("Выход из программы.")
        sys.exit(0)


class CLI:
    def __init__(self):
        self.app = App()

    def run(self):
        self.app.load_data()
        print("\nДобро пожаловать в приложение Farmers Market CLI (ООП версия)!")
        print("Доступные команды:")
        print("  list [page]                  - показать список рынков (постранично)")
        print("  search <city> [state]        - поиск по городу и штату")
        print("  search zip <zip> [distance]  - поиск по почтовому индексу с радиусом (мили)")
        print("  view <id>                    - подробная информация о рынке")
        print("  review <id>                  - добавить рецензию (интерактивно)")
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
                    page = 1
                    if args:
                        try:
                            page = int(args[0])
                        except ValueError:
                            print("Некорректный номер страницы.")
                            continue
                    self.app.list_markets(page)

                elif command == "search":
                    if not args:
                        print("Использование: search <city> [state] или search zip <zipcode> [distance]")
                        continue
                    if args[0].lower() == "zip":
                        if len(args) < 2:
                            print("Укажите почтовый индекс: search zip 02108")
                            continue
                        zipcode = args[1]
                        distance = 0.0
                        if len(args) >= 3:
                            try:
                                distance = float(args[2])
                            except ValueError:
                                print("Расстояние должно быть числом (в милях).")
                                continue
                        self.app.search_by_zip(zipcode, distance)
                    else:
                        city = args[0]
                        state = args[1] if len(args) > 1 else None
                        self.app.search_by_city_state(city, state)

                elif command == "view":
                    if not args:
                        print("Укажите ID рынка: view <id>")
                        continue
                    try:
                        market_id = int(args[0])
                    except ValueError:
                        print("ID должен быть числом.")
                        continue
                    self.app.view_market(market_id)

                elif command == "review":
                    if not args:
                        print("Укажите ID рынка: review <id>")
                        continue
                    try:
                        market_id = int(args[0])
                    except ValueError:
                        print("ID должен быть числом.")
                        continue
                    # Проверяем существование
                    market = next((m for m in self.app.market_manager.all_markets if m.id == market_id), None)
                    if not market:
                        print(f"Рынок с ID {market_id} не найден.")
                        continue
                    print(f"Оставьте рецензию для рынка: {market.name}")
                    name = input("Ваше имя и фамилия: ").strip()
                    if not name:
                        print("Имя обязательно.")
                        continue
                    rating_str = input("Рейтинг (1-5): ").strip()
                    try:
                        rating = int(rating_str)
                    except ValueError:
                        print("Рейтинг должен быть числом.")
                        continue
                    if not validate_rating(rating):
                        print("Рейтинг должен быть от 1 до 5.")
                        continue
                    text = input("Текст рецензии (необязательно): ").strip()
                    self.app.add_review(market_id, name, rating, text)

                elif command == "sort":
                    if not args:
                        print("Использование: sort <criterion> [asc|desc]")
                        print("Критерии: rating, city, state")
                        continue
                    criterion = args[0].lower()
                    reverse = False
                    if len(args) >= 2:
                        if args[1].lower() == "desc":
                            reverse = True
                        elif args[1].lower() == "asc":
                            reverse = False
                        else:
                            print("Направление должно быть asc или desc. Используется asc по умолчанию.")
                    self.app.sort_markets(criterion, reverse)

                elif command == "delete":
                    if not args:
                        print("Укажите ID рынка для удаления: delete <id>")
                        continue
                    try:
                        market_id = int(args[0])
                    except ValueError:
                        print("ID должен быть числом.")
                        continue
                    self.app.delete_market(market_id)

                elif command == "exit":
                    self.app.exit()

                else:
                    print(f"Неизвестная команда: {command}")

            except KeyboardInterrupt:
                print("\nВыход.")
                sys.exit(0)
            except Exception as e:
                print(f"Ошибка: {e}")
