import sys
import zip_util
import math

def normalize_zip(zip_str: str) -> str:
    zip_str = zip_str.strip()
    if zip_str.isdigit():
        return f"{int(zip_str):05d}"
    return zip_str

def decimal_to_dms(deg: float, coord_type: str) -> str:
    if coord_type == 'lat':
        direction = 'N' if deg >= 0 else 'S'
    else:
        direction = 'E' if deg >= 0 else 'W'

    deg_abs = abs(deg)
    degrees = int(deg_abs)
    minutes_float = (deg_abs - degrees) * 60
    minutes = int(minutes_float)
    seconds = (minutes_float - minutes) * 60
    seconds = round(seconds, 2)

    if seconds >= 60:
        seconds -= 60
        minutes += 1
        if minutes >= 60:
            minutes -= 60
            degrees += 1

    return f"{degrees:03d}∘{minutes:02d}'{seconds:05.2f}\"{direction}"

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 3959.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

print("Loading ZIP code data...", file=sys.stderr)
raw_data = zip_util.read_zip_all()
print("Data loaded.", file=sys.stderr)

zip_to_record = {}
city_state_to_zips = {}

for record in raw_data:
    zip_code = record[0]
    lat = record[1]
    lon = record[2]
    city = record[3]
    state = record[4]
    county = record[5]

    norm_zip = normalize_zip(zip_code)
    zip_to_record[norm_zip] = (zip_code, lat, lon, city, state, county)

    key = (city.lower(), state.lower())
    if key not in city_state_to_zips:
        city_state_to_zips[key] = (city, state, [])
    if norm_zip not in city_state_to_zips[key][2]:
        city_state_to_zips[key][2].append(norm_zip)

def main():
    while True:
        cmd = input("Command ('loc', 'zip', 'dist', 'end') => ").strip().lower()

        if cmd == 'end':
            print("Done")
            break

        elif cmd == 'loc':
            zip_input = input("Enter a ZIP Code to lookup => ").strip()
            norm_zip = normalize_zip(zip_input)
            record = zip_to_record.get(norm_zip)
            if record is None:
                print(f"Error: ZIP code {zip_input} not found.")
                continue

            orig_zip, lat, lon, city, state, county = record
            lat_dms = decimal_to_dms(lat, 'lat')
            lon_dms = decimal_to_dms(lon, 'lon')
            print(f"ZIP Code {orig_zip} is in {city}, {state}, {county} county,\ncoordinates: ({lat_dms}, {lon_dms})")

        elif cmd == 'zip':
            city_input = input("Enter a city name to lookup => ").strip()
            state_input = input("Enter the state name to lookup => ").strip()
            key = (city_input.lower(), state_input.lower())
            info = city_state_to_zips.get(key)
            if info is None:
                print(f"Error: no ZIP codes found for {city_input}, {state_input}.")
                continue

            orig_city, orig_state, zips = info
            zips_sorted = sorted(zips)
            zip_list_str = ', '.join(zips_sorted)
            print(f"The following ZIP Code(s) found for {orig_city}, {orig_state}: {zip_list_str}")

        elif cmd == 'dist':
            zip1_input = input("Enter the first ZIP Code => ").strip()
            zip2_input = input("Enter the second ZIP Code => ").strip()
            norm_zip1 = normalize_zip(zip1_input)
            norm_zip2 = normalize_zip(zip2_input)

            rec1 = zip_to_record.get(norm_zip1)
            if rec1 is None:
                print(f"Error: ZIP code {zip1_input} not found.")
                continue
            rec2 = zip_to_record.get(norm_zip2)
            if rec2 is None:
                print(f"Error: ZIP code {zip2_input} not found.")
                continue

            _, lat1, lon1, _, _, _ = rec1
            _, lat2, lon2, _, _, _ = rec2
            distance = haversine_distance(lat1, lon1, lat2, lon2)
            print(f"The distance between {norm_zip1} and {norm_zip2} is {distance:.2f} miles")

        else:
            print("Invalid command, ignoring")

if __name__ == "__main__":
    main()