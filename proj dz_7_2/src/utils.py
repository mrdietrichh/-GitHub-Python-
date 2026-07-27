from typing import List, TypeVar, Callable
from .market import Market

T = TypeVar('T')

def paginate(items: List[T], page: int, page_size: int = 10) -> List[T]:
    start = (page - 1) * page_size
    end = start + page_size
    return items[start:end]

def validate_rating(rating: int) -> bool:
    return 1 <= rating <= 5

def format_market_short(market: Market, idx: int) -> str:
    return f"{idx}. {market.name} ({market.city}, {market.state}) - Рейтинг: {market.rating:.1f}"

def format_market_full(market: Market) -> str:
    return (f"ID: {market.id}\n"
            f"Название: {market.name}\n"
            f"Адрес: {market.address}\n"
            f"Город: {market.city}\n"
            f"Штат: {market.state}\n"
            f"Индекс: {market.zipcode}\n"
            f"Широта: {market.lat}, Долгота: {market.lon}\n"
            f"Средний рейтинг: {market.rating:.1f}")
