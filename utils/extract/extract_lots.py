import requests
import json
from collections import defaultdict

KEY = "0001085cc708b9cef47080f064612ca5"
MAP = "562"
PARKING_CAT_IDS = {27985, 27987}

r = requests.get(f"https://api.concept3d.com/locations?map={MAP}&key={KEY}")
data = r.json()
parking = [loc for loc in data if loc.get('catId') in PARKING_CAT_IDS]

cat_lots = defaultdict(list)
for loc in parking:
    shape = loc.get('shape')
    if shape and isinstance(shape, dict) and shape.get('paths'):
        polygon = [list(p) for p in shape['paths']]  # lists instead of tuples for JSON
        if polygon[0] != polygon[-1]:
            polygon.append(polygon[0])
        cat_lots[loc['catId']].append((loc['name'], polygon))

lots_output = []
counter = 1
for cat_id, lots in cat_lots.items():
    for name, coords in lots:
        lots_output.append({
            "id": f"vis{counter}",
            "name": name,
            "permit": "Visitor",        # adjust per lot/category as needed
            "color": [0.42, 0, 0.588, 0.45],  # default white — change per lot
            "coordinates": coords
        })
        counter += 1

with open("parking_lots.json", "w") as f:
    json.dump(lots_output, f, indent=2)

print(f"Saved {counter - 1} lots to parking_lots.json")