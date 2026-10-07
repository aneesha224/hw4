from pathlib import Path
import sqlite3
from pydantic_ai import RunContext
from models import AgentDeps
from models import ProductCard, ProductInfo, StockResult
from audit import audit

DB = Path(__file__).resolve().parents[1] / "data" / "campus_customs.db"

def search_products(ctx: RunContext[None], query: str) -> list[ProductCard]:
    """Search the catalogue by name, garment type, description, colors, or tags."""
    terms = [term for term in query.lower().split() if len(term) > 1]
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT product_id, name, price, description, image_file_path, garment_type, colors, search_tags FROM catalogue").fetchall()
    scored = []
    for row in rows:
        haystack = " ".join(str(row[key]).lower() for key in ("name", "description", "garment_type", "colors", "search_tags"))
        score = sum(term in haystack for term in terms)
        if score: scored.append((score, row))
    scored.sort(key=lambda pair: (-pair[0], pair[1]["name"]))
    matches = [ProductCard(**{key: row[key] for key in ("product_id", "name", "price", "description", "image_file_path")}) for _, row in scored[:5]]
    audit("tool", "search_products", {"query": query}, f"{len(matches)} matches")
    return matches

def resolve_product(ctx: RunContext[AgentDeps], product_phrase: str) -> list[ProductCard]:
    """Resolve a shopper's product phrase to exact catalogue records before detail or stock lookups."""
    return search_products(ctx, product_phrase)

def get_product_info(ctx: RunContext[None], product_id: str) -> ProductInfo | None:
    """Return exact catalogue description, price, colors, and garment type for one product."""
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT product_id, name, description, price, colors, garment_type FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
    return ProductInfo(**dict(row)) if row else None

def check_stock(ctx: RunContext[None], product_id: str, size: str | None = None) -> StockResult:
    """Look up real inventory, by requested size when supplied; never estimate stock."""
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        product = conn.execute("SELECT product_id, name FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
        if not product:
            return StockResult(product_id=product_id, product_name="Unknown product", requested_size=size, available=False, message="I could not find that product in the catalogue.")
        rows = conn.execute("SELECT size, quantity FROM inventory WHERE product_id = ? ORDER BY size", (product_id,)).fetchall()
    stock = {row["size"]: row["quantity"] for row in rows}
    if size is not None:
        quantity = stock.get(size)
        available = quantity is not None and quantity > 0
        message = f"{size} is available ({quantity} left)." if available else f"{size} is out of stock."
        return StockResult(product_id=product_id, product_name=product["name"], requested_size=size, quantity=quantity or 0, available=available, stock_by_size=stock, message=message)
    return StockResult(product_id=product_id, product_name=product["name"], available=any(quantity > 0 for quantity in stock.values()), stock_by_size=stock, message="Here is the current stock by size from the inventory database.")

def customer_context(ctx: RunContext[AgentDeps]) -> str:
    """Provide safe identity and page context for the current conversation."""
    if ctx.deps.user_id is None:
        identity = "The shopper is a guest."
    else:
        identity = f"The logged-in shopper is {ctx.deps.name} ({ctx.deps.email})."
    page = f" They are currently viewing: {ctx.deps.page_context}." if ctx.deps.page_context else ""
    return identity + page
