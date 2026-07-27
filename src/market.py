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

def load_markets(csv_path: str) -> List[Market]:
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
        return markets

def filter_by_city_state(markets: List[Market], city: Optional[str] = None, state: Optional[str] = None) -> List[Market]:
    if city is None and state is None:
        return markets
    return list(filter(
        lambda m: (city is None or m.city.lower() == city.lower()) and
                  (state is None or m.state.lower() == state.lower()),
        markets
    ))

def filter_by_zip(markets: List[Market], zipcode: str) -> List[Market]:
    return list(filter(lambda m: m.zipcode.startswith(zipcode), markets))

def filter_by_distance(markets: List[Market], lat: float, lon: float, max_miles: float) -> List[Market]:
    from .distance import haversine
    return list(filter(
        lambda m: haversine(lat, lon, m.lat, m.lon) <= max_miles,
        markets
    ))
