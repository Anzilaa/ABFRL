try:
    from google.adk.agents import Agent  # type: ignore
except Exception:
    Agent = None

from .agents.master import MasterSalesAgent

# Provide a simple master sales agent as the primary entrypoint for the app.
master_agent = MasterSalesAgent()

# If the Google ADK is available the original `root_agent` can be constructed
# (left as an optional integration point). For now expose `master_agent`.
