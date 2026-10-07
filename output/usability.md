# Problem 9: Usability improvements

This document is written before implementation and records the four improvements planned for the running Campus Customs app.

## Front-end improvements

### 1. Catalogue search and category filtering

Add a search box and garment-type filter above the Products grid. Shoppers can quickly narrow a large catalogue to a name, color, team, or type such as hoodies. This helps a customer find relevant campus merchandise without scrolling through every item.

### 2. Price sorting

Add a sort control for featured order, lowest price, and highest price. This supports different shopping goals, including finding an affordable gift or comparing premium pieces.

## Agent/backend improvements

### 3. Natural-language product resolution

Add a database-backed `resolve_product` tool that converts a product name or phrase into exact catalogue products and IDs. This makes follow-up questions such as “what sizes does the Yale hoodie have?” more accurate because later detail and stock lookups use database identifiers instead of guessed names. The tool is registered with the agent and required by the system prompt.

### 4. Safe chat failure handling

Make the chat endpoint return a clear, non-sensitive service-unavailable response when the model configuration or provider is unavailable. The frontend shows that message instead of a broken panel, while the API avoids exposing credentials, stack traces, or internal details.

## Final implemented behavior

The delivered standalone build preserves the two catalogue controls above and makes the concierge immediately usable without a live provider: its compact in-chat cards show real names, photos, and prices from the packaged catalogue, and they keep the same product-detail links. On detail pages, shoppers can choose an in-stock size, add it to the bag, and see that item’s thumbnail in the bag, completing the core browse-to-bag flow.
