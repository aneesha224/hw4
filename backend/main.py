from pathlib import Path
import sqlite3
import asyncio
import base64
import hashlib
import hmac
import secrets
from pydantic import BaseModel, EmailStr
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from models import ChatRequest, ChatReply, ChatMessage
from agent import answer, local_answer, AgentDeps

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
DB = ROOT / "data" / "campus_customs.db"
app = FastAPI(title="Campus Customs API")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])
app.mount("/images", StaticFiles(directory=ROOT / "data"), name="images")

class AccountIn(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return "pbkdf2_sha256$310000$" + base64.urlsafe_b64encode(salt).decode() + "$" + base64.urlsafe_b64encode(digest).decode()

def verify_password(password: str, stored: str) -> bool:
    try:
        parts = stored.split("$")
        if len(parts) == 3:  # seeded Homework 4 test account format
            algorithm, salt_text, digest_text = parts
            rounds, encoded = 120_000, "hex"
        else:
            algorithm, rounds_text, salt_text, digest_text = parts
            rounds, encoded = int(rounds_text), "base64"
        if algorithm != "pbkdf2_sha256": return False
        salt = salt_text.encode() if encoded == "hex" else base64.urlsafe_b64decode(salt_text.encode())
        expected = bytes.fromhex(digest_text) if encoded == "hex" else base64.urlsafe_b64decode(digest_text.encode())
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, rounds)
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False

def product(row):
    item = dict(row)
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        item["inventory"] = [dict(r) for r in conn.execute("SELECT size, quantity FROM inventory WHERE product_id = ? ORDER BY size", (item["product_id"],))]
    return item

@app.get("/api/products")
def products():
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        return [product(r) for r in conn.execute("SELECT * FROM catalogue ORDER BY name")]

@app.get("/api/products/{product_id}")
def one_product(product_id: str):
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
    if not row: raise HTTPException(status_code=404, detail="Product not found")
    return product(row)

@app.post("/api/auth/register", status_code=201)
def register(account: AccountIn):
    if len(account.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    with sqlite3.connect(DB) as conn:
        try:
            cursor = conn.execute("INSERT INTO users (name, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)", (f"{account.first_name} {account.last_name}", str(account.email).lower(), hash_password(account.password), account.first_name, account.last_name))
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=409, detail="An account with that email already exists")
    return {"id": cursor.lastrowid, "first_name": account.first_name, "email": str(account.email).lower()}

@app.post("/api/auth/login")
def login(credentials: LoginIn):
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        user = conn.execute("SELECT id, first_name, email, password_hash FROM users WHERE email = ?", (str(credentials.email).lower(),)).fetchone()
    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"id": user["id"], "first_name": user["first_name"], "email": user["email"]}

@app.post("/api/chat", response_model=ChatReply)
async def chat(request: ChatRequest):
    user = None
    history: list[ChatMessage] = []
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        if request.user_id is not None:
            user = conn.execute("SELECT id, name, email FROM users WHERE id = ?", (request.user_id,)).fetchone()
            if user:
                history = [ChatMessage(**dict(row)) for row in conn.execute("SELECT role, content, created_at FROM chat_messages WHERE user_id = ? ORDER BY id DESC LIMIT 20", (request.user_id,)).fetchall()][::-1]
    deps = AgentDeps(user_id=user["id"] if user else None, name=user["name"] if user else None, email=user["email"] if user else None, page_context=request.page_context)
    prompt = request.message
    if request.page_context:
        prompt = f"[Page context: {request.page_context}]\n{request.message}"
    try:
        result = await asyncio.wait_for(answer(prompt, deps), timeout=4.0)
    except Exception:
        result = local_answer(request.message)
    if user:
        with sqlite3.connect(DB) as conn:
            conn.execute("INSERT INTO chat_messages (user_id, role, content) VALUES (?, 'user', ?)", (user["id"], request.message))
            conn.execute("INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, 'assistant', ?, ?)", (user["id"], result.reply, str([product.model_dump() for product in result.products])))
            conn.commit()
        history.extend([ChatMessage(role="user", content=request.message, created_at="now"), ChatMessage(role="assistant", content=result.reply, created_at="now")])
    result.history = history
    return result

@app.get("/api/chat/history/{user_id}", response_model=list[ChatMessage])
def chat_history(user_id: int):
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(row) for row in conn.execute("SELECT role, content, created_at FROM chat_messages WHERE user_id = ? ORDER BY id DESC LIMIT 50", (user_id,)).fetchall()][::-1]
