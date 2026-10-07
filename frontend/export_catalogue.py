import json
import base64
import shutil
import sqlite3
from pathlib import Path

FRONTEND_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = FRONTEND_ROOT.parent
with sqlite3.connect(PROJECT_ROOT / "data" / "campus_customs.db") as db:
    db.row_factory = sqlite3.Row
    products = []
    for row in db.execute("SELECT * FROM catalogue ORDER BY name"):
        item = dict(row)
        item["inventory"] = [dict(stock) for stock in db.execute("SELECT size, quantity FROM inventory WHERE product_id = ? ORDER BY size", (item["product_id"],))]
        image = PROJECT_ROOT / "data" / item["image_file_path"]
        item["image_data_uri"] = "data:image/jpeg;base64," + base64.b64encode(image.read_bytes()).decode()
        products.append(item)
(FRONTEND_ROOT / "src" / "catalogue.json").write_text(json.dumps(products, indent=2) + "\n")
target = FRONTEND_ROOT / "public" / "data" / "products"
target.mkdir(parents=True, exist_ok=True)
for image in (PROJECT_ROOT / "data" / "products").glob("*"):
    shutil.copy2(image, target / image.name)
print(f"Exported {len(products)} products")
