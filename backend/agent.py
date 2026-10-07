import os
from pathlib import Path
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from models import AgentDeps, ChatReply
from audit import audit
from tools import search_products, resolve_product, get_product_info, check_stock, customer_context


PROMPT = (Path(__file__).parent / "prompts" / "prompts.md").read_text()

def build_agent() -> Agent[AgentDeps, ChatReply]:
    api_key = os.environ.get("PORTKEY_API_KEY")
    if not api_key:
        raise RuntimeError("PORTKEY_API_KEY is required for the Campus Customs agent")
    provider = OpenAIProvider(api_key=api_key, base_url="https://api.portkey.ai/v1")
    model = OpenAIChatModel(os.environ.get("PORTKEY_MODEL", "gpt-5.6-luna"), provider=provider)
    agent = Agent(model, system_prompt=PROMPT, output_type=ChatReply)
    agent.tool(search_products)
    agent.tool(resolve_product)
    agent.tool(get_product_info)
    agent.tool(check_stock)
    agent.tool(customer_context)
    return agent

async def answer(message: str, deps: AgentDeps, message_history=None) -> ChatReply:
    audit("start", "agent_loop", {"user_id": deps.user_id, "page_context": deps.page_context}, "started")
    try:
        result = await build_agent().run(message, deps=deps, message_history=message_history)
        audit("finish", "agent_loop", {"user_id": deps.user_id}, result.output.reply, "structured_result")
        return result.output
    except Exception:
        audit("finish", "agent_loop", {"user_id": deps.user_id}, "service unavailable", "error")
        raise

def local_answer(message: str) -> ChatReply:
    """Reliable database-only fallback for catalogue questions when the model provider is unavailable."""
    matches = search_products(None, message)
    if matches:
        return ChatReply(reply=f"I found {len(matches)} Campus Customs pieces that match your question.", products=matches)
    return ChatReply(reply="I couldn't find a matching catalogue item. Try asking about hoodies, Yale sports, colors, or a product name.")
