from dataclasses import dataclass
from pydantic import BaseModel, Field

@dataclass
class AgentDeps:
    user_id: int | None = None
    name: str | None = None
    email: str | None = None
    page_context: str | None = None

class ProductCard(BaseModel):
    product_id: str
    name: str
    price: float
    description: str
    image_file_path: str

class ProductInfo(BaseModel):
    product_id: str
    name: str
    description: str
    price: float
    colors: str
    garment_type: str

class StockResult(BaseModel):
    product_id: str
    product_name: str
    requested_size: str | None = None
    quantity: int | None = None
    available: bool
    stock_by_size: dict[str, int] = Field(default_factory=dict)
    message: str

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2_000)
    user_id: int | None = None
    page_context: str | None = Field(default=None, max_length=500)

class ChatMessage(BaseModel):
    role: str
    content: str
    created_at: str

class AuditEntry(BaseModel):
    time: str
    event: str
    tool_name: str
    arguments: str
    result: str
    stop_reason: str | None = None

class ChatReply(BaseModel):
    reply: str
    products: list[ProductCard] = Field(default_factory=list)
    history: list[ChatMessage] = Field(default_factory=list)
