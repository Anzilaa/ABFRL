"""agents/first_agent.py

Make this module safe to run whether or not the real GADK (Google
Agent Development Kit) is installed. The module will attempt to import
real SDK classes but falls back to small local mocks so you can iterate
locally without external dependencies.
"""
import asyncio
from typing import Any, Callable, Dict, List


# --- Mock tool ---------------------------------------------------------
async def mock_google_search(query: str) -> Dict[str, Any]:
    """A tiny async mock to emulate a search tool. Replace with a real
    adapter before production."""
    await asyncio.sleep(0.05)
    return {"results": [f"(mock) Search result for: {query}"]}


# --- Agent / Runner imports with graceful fallback --------------------
try:
    # Try the official GADK import paths first (adjust as the SDK docs)
    from google.adk.agents import Agent  # type: ignore
    from google.adk.runners import InMemoryRunner  # type: ignore
    ToolAvailable = True
except Exception:
    # If the SDK isn't available, provide minimal local implementations
    ToolAvailable = False

    class Agent:
        def __init__(self, name: str, model: str, description: str, instruction: str, tools: List[Callable] = None):
            self.name = name
            self.model = model
            self.description = description
            self.instruction = instruction
            self.tools = tools or []

        async def handle(self, prompt: str) -> str:
            if self.tools:
                try:
                    res = await self.tools[0](prompt)
                    return f"[mocked agent response using tool] {res['results'][0]}"
                except Exception:
                    return "[mocked agent] Tool failed"
            return f"[mocked agent] I received: {prompt}"

    class InMemoryRunner:
        def __init__(self, agent: Agent):
            self.agent = agent

        async def run_debug(self, prompt: str) -> str:
            return await self.agent.handle(prompt)


# --- Create agent instance --------------------------------------------
# Use the real `google_search` if available, otherwise the local mock.
search_tool = None
if ToolAvailable:
    try:
        # Attempt to import the SDK-provided tool helper
        from google.adk.tools import google_search as sdk_google_search  # type: ignore
        search_tool = sdk_google_search
    except Exception:
        search_tool = mock_google_search
else:
    search_tool = mock_google_search


root_agent = Agent(
    name="helpful_assistant",
    model="gemini-2.5-flash-lite",
    description="A simple agent that can answer general questions.",
    instruction="You are a helpful assistant. Use Google Search for current info or if unsure.",
    tools=[search_tool],
)

print("✅ Root Agent defined.")

# Runner
runner = InMemoryRunner(agent=root_agent)

print("✅ Runner created.")


async def main():
    # Example debug run — change the prompt as needed
    response = await runner.run_debug("best phone brands")
    print("--- RUNNER DEBUG RESPONSE ---")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
