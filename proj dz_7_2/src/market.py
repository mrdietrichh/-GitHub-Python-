from dataclasses import dataclass
import csv
from typing import List, Optional

@dataclass(frozen=True)
class Market:
    id: int
    name: str
    address: str
    city: str
    state: str
    zipcode: str
    lat: float
    lon: float
    rating: float

class MarketManager:
    def __init__(self):
        self.all_markets: List[Market] = []
        self.current_list: List[Market] = []

    def load(self, csv_path: str) -> None:
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                markets = []
                for row in reader:
                    try:
                        rating = float(row.get('rating', 0)) if row.get('rating') else 0.0
                    except ValueError:
                        rating = 0.0
                    market = Market(
                        id=int(row['id']),
                        name=row.get('marketname', ''),
                        address=row.get('street', ''),
                        city=row.get('city', ''),
                        state=row.get('state', ''),
                        zipcode=row.get('zip', ''),
                        lat=float(row.get('lat', 0)),
                        lon=float(row.get('lon', 0)),
                        rating=rating
                    )
                    markets.append(market)
                self.all_markets = markets
                self.current_list = markets.copy()
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл {csv_path} не найден.")

    def filter_by_city_state(self, city: Optional[str] = None, state: Optional[str] = None) -> None:
        if city is None and state is None:
            self.current_list = self.all_markets.copy()
            return
        self.current_list = list(filter(
            lambda m: (city is None or m.city.lower() == city.lower()) and
                      (state is None or m.state.lower() == state.lower()),
            self.all_markets
        ))

    def filter_by_zip(self, zipcode: str) -> None:
        self.current_list = list(filter(lambda m: m.zipcode.startswith(zipcode), self.all_markets))

    def filter_by_distance(self, lat: float, lon: float, max_miles: float) -> None:
        from .distance import haversine
        self.current_list = list(filter(
            lambda m: haversine(lat, lon, m.lat, m.lon) <= max_miles,
            self.current_list if self.current_list else self.all_markets
        ))

    def sort(self, key_func, reverse: bool = False) -> None:
        self.current_list = sorted(self.current_list, key=key_func, reverse=reverse)

    def delete(self, market_id: int) -> bool:
        before = len(self.current_list)
        self.current_list = list(filter(lambda m: m.id != market_id, self.current_list))
        return len(self.current_list) < before

    def get_by_id(self, market_id: int) -> Optional[Market]:
        return next((m for m in self.current_list if m.id == market_id), None)

    def get_all(self) -> List[Market]:
        return self.all_markets.copy()
