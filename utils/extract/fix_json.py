import json

with open("lot_cords.json") as f:
    data = json.load(f)

# flatten any nested lists regardless of how deep
cleaned = []
for lot in data["parking_lots"]:
    if isinstance(lot, list):
        cleaned.extend(lot)
    else:
        cleaned.append(lot)

data["parking_lots"] = cleaned

with open("lot_cords.json", "w") as f:
    json.dump(data, f, indent=2)

print(f"Done! {len(cleaned)} lots saved.")