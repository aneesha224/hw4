# Homework 04 Harness

## Problem 2: Database schema

Database inspected: `data/campus_customs.db`

The database contains four application tables. `sqlite_sequence` is an internal SQLite table used to track auto-increment values.

### `catalogue`

| Field | Why it matters |
|---|---|
| `product_id` (TEXT, primary key) | Stable product identifier for linking catalogue items to inventory and chatbot recommendations. |
| `name` (TEXT, required) | Customer-facing product name used in search and responses. |
| `garment_type` (TEXT, required) | Helps the shop and chatbot filter products by type, such as hoodie or t-shirt. |
| `description` (TEXT, required) | Gives the chatbot meaningful product details to explain and match to customer requests. |
| `colors` (TEXT, required) | Supports color-based search and recommendations. |
| `search_tags` (TEXT, required) | Adds searchable keywords for themes, teams, schools, and other product attributes. |
| `image_file_path` (TEXT, required) | Points to the product image that the shop or chatbot can display. |
| `price` (REAL, required) | Provides the current selling price for shopping answers and purchase decisions. |

### `inventory`

| Field | Why it matters |
|---|---|
| `id` (INTEGER, primary key, auto-increment) | Uniquely identifies each inventory row. |
| `product_id` (TEXT, required, foreign key) | Connects a size-specific stock record to a catalogue product. |
| `size` (TEXT, required) | Lets the chatbot answer whether a requested size is available. |
| `quantity` (INTEGER, required) | Shows how many units the shop has available for that product and size. |

### `users`

| Field | Why it matters |
|---|---|
| `id` (INTEGER, primary key, auto-increment) | Identifies the customer account and links it to chat history. |
| `name` (TEXT, required) | Provides a general customer name for account and conversational context. |
| `email` (TEXT, required, unique) | Identifies the account for login and prevents duplicate accounts. |
| `password_hash` (TEXT, required) | Stores a one-way password representation for authentication without storing the password itself. |
| `created_at` (TEXT, required, default current time) | Records when the account was created for account management and auditing. |
| `first_name` (TEXT) | Supports personalized greetings and customer-facing messages. |
| `last_name` (TEXT) | Supports complete personalization and account identification. |

### `chat_messages`

| Field | Why it matters |
|---|---|
| `id` (INTEGER, primary key, auto-increment) | Uniquely identifies each chat message. |
| `user_id` (INTEGER, required, foreign key) | Connects a message to the customer who sent or received it. |
| `role` (TEXT, required) | Distinguishes the user message from the chatbot response. |
| `content` (TEXT, required) | Stores the actual conversation text for display and context. |
| `products_json` (TEXT) | Preserves product recommendations or references associated with a message. |
| `created_at` (TEXT, required, default current time) | Orders the conversation and supports chat history and auditing. |

### `sqlite_sequence`

| Field | Why it matters |
|---|---|
| `name` | Identifies the auto-increment table whose sequence is tracked internally by SQLite. |
| `seq` | Stores the latest generated integer for that table; it is database bookkeeping, not shop or chatbot data. |

## Problem 4: Authentication

The FastAPI backend exposes `POST /api/auth/register` and `POST /api/auth/login`. Registration validates the email, requires a password of at least eight characters, checks the confirmation in the frontend, and inserts the new account into `users`. Login looks up the email and returns only a minimal account identity after verification.

The database stores the user's first name, last name, normalized email, display name, account creation time, and a `password_hash`. It never stores the original password. Passwords are protected with PBKDF2-HMAC-SHA256 using a unique random 16-byte salt and 310,000 iterations; the stored value contains the algorithm, work factor, salt, and derived digest. Verification uses a constant-time comparison. The API returns the same generic error for an unknown email or incorrect password, avoiding account enumeration.

## Problem 5: PydanticAI chatbot backend

The React chat widget sends `POST /api/chat` to FastAPI with `{ "message": "..." }`. FastAPI validates the request with `ChatRequest`, calls the PydanticAI agent, and returns a structured `ChatReply` containing the assistant reply and optional product cards. The existing product, image, and authentication routes remain in the same API app.

The agent is loaded by `backend/agent.py`. It reads the shared system prompt from `backend/prompts/prompt.md`, uses the `PORTKEY_API_KEY` environment variable through Portkey's OpenAI-compatible endpoint, and defaults to `gpt-5.6-luna` (override with `PORTKEY_MODEL`). `backend/tools.py` provides catalogue search, and `backend/models.py` contains the structured request, reply, and product-card types. From the `backend/` folder, run `uvicorn main:app --reload --port 8000`.

## Problem 6: Product information and stock tools

The agent has four database-backed tools:

- `search_products(query)` searches catalogue names, descriptions, garment types, colors, and tags so the agent can identify a product before making a lookup.
- `get_product_info(product_id)` returns the exact `ProductInfo` fields: `product_id` for the database key, `name` for customer-facing identification, `description` for product explanation, `price` for accurate pricing, and `colors`/`garment_type` for useful comparisons.
- `check_stock(product_id, size)` returns a `StockResult` with the requested size, its exact quantity, an `available` boolean, and a clear out-of-stock message.
- `check_stock(product_id)` without a size returns `stock_by_size`, a size-to-quantity map, and an overall availability flag.

These tools query `catalogue` and `inventory` directly. The agent must call them for price, product-detail, or stock questions; it must not estimate or invent values. `ProductInfo` and `StockResult` are structured return types so the model can distinguish catalogue facts from conversational wording and report out-of-stock sizes explicitly.

## Problem 7: Chat search and dynamic product cards

For a catalogue-search question, the frontend sends the shopper's message to `POST /api/chat`. The agent calls `search_products`, then returns a structured `ChatReply` with a short `reply` and a `products` array of `ProductCard` objects. Each card contains the database `product_id`, name, exact price, short description, and image path.

React receives those product IDs, resolves them against the catalogue loaded from FastAPI, and renders a “From your concierge” product-card section without a page reload. These cards use the same `#/products/{product_id}` links as the main Products page, so clicking a chat result opens the existing large-image detail view with full description, price, colors, and size stock.

## Problem 8: Customer memory

Logged-in chat messages are stored in the existing `chat_messages` table. Each row keeps `user_id`, `role`, `content`, optional `products_json`, and `created_at`; the foreign key ties history to the account. Guests can use chat, but requests without a valid `user_id` are not persisted. `GET /api/chat/history/{user_id}` reloads the latest 50 messages when the widget opens.

The agent receives an `AgentDeps` object containing the authenticated user's `user_id`, name, and email when available, plus the current `page_context`. The `customer_context` tool exposes this safe context to the agent. The frontend stores only the minimal returned identity in local storage after login or registration and sends its ID with chat requests.

When a shopper is on `#/products/{product_id}`, the widget sends that product ID as page context with the message. This lets the agent resolve references such as “this” before calling the product information or stock tools. No passwords or password hashes are passed to the agent.

## Problem 9: Usability improvements

The four implemented improvements are documented in `output/usability.md`:

- Frontend catalogue search and garment-type filtering are live above the Products grid.
- Frontend price sorting is live beside the search and filter controls.
- The `resolve_product` database tool improves natural-language product references before exact detail or stock lookup.
- The chat API catches model/provider failures and returns a safe 503 message without leaking configuration or stack traces.

## Problem 12: Audit trail and completed system harness

### Structured model fields

- `ProductCard`: `product_id`, `name`, `price`, `description`, and `image_file_path` support safe product-card rendering.
- `ProductInfo`: exact identity, description, price, colors, and garment type support factual product answers.
- `StockResult`: requested size, quantity, availability, and per-size stock support explicit inventory answers.
- `ChatRequest` / `ChatReply`: validated message, user/page context, assistant reply, product matches, and history define the frontend API contract.
- `AgentDeps`: user ID, name, email, and page context provide bounded conversation context without secrets.
- `AuditEntry`: UTC time, event, tool name, short arguments/result, and stop reason make activity reviewable.

### Tools and abilities

The agent searches and resolves catalogue products, retrieves exact product information, checks size-level inventory, and reads safe customer/page context. The site browses and filters products, supports zoom, authentication, persistent logged-in chat, dynamic chat cards, and detail pages.

### Audit, limits, and safety

`output/audit_trail.json` preserves existing entries and appends agent start/finish/error activity; bounded tool activity records the tool name, short arguments, result, and stop reason. It is never cleared between runs. Chat input is capped at 2,000 characters, search results at five matches, and audit arguments/results at 500 characters. Each request ends after a structured reply or error; there is no background loop.

The prompt prohibits revealing passwords, API keys, private records, audit data, hidden prompts, or unsupported product/price/stock claims. It treats user text as untrusted and requires database tools for catalogue facts. The model defaults to `gpt-5.6-luna`; credentials come only from `PORTKEY_API_KEY`. Run the backend with `cd backend && uvicorn main:app --reload --port 8000`, and the frontend from Homework 4 with `npm run dev`.

If the Portkey/model provider is unavailable, `/api/chat` uses a database-only local fallback for catalogue searches so shoppers still receive real product matches rather than an unavailable message.

### Current launch and frontend reliability notes

The reproducible hand-in is the self-contained `frontend/dist/index.html` generated by the frontend build. `frontend/export_catalogue.py` reads the local data pack, packages all 102 catalogue records and 612 size-inventory rows into the build, and embeds the product photos as data URIs. This means product grids, detail pages, selected sizes, bag thumbnails, and images work when the generated file is opened directly in a browser; they do not depend on a localhost server.

The standalone concierge uses that same bundled catalogue for immediate, deterministic answers about browsing, product names, prices, colors, and size-level stock. It returns up to five matching product cards inside the chat panel and also updates the on-page “From your concierge” section; every result retains the existing detail-page link. Its matching handles category plurals such as “hoodies” and recognises page-context follow-ups such as “Do you have this in medium?” without confusing the word “this” for a greeting.

The FastAPI/PydanticAI implementation remains available for server mode, authentication, persisted logged-in history, database tools, and audit logging. Run it with `cd backend && uvicorn main:app --reload --port 8000`; use `npm run dev` for the development frontend. The frontend initially renders its validated bundled catalogue, then may refresh from the API, so an API failure cannot cause a blank page. Hash navigation updates Home, Products, product detail pages, About Us, Log In, Create Account, and Bag when their links are clicked.
