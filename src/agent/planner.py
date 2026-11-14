import json
import re

from src.agent.llm import OllamaLLM
from src.tools.registry import TOOLS

DEFAULT_PLAN = ["segment_topics", "extract_concepts"]


def make_plan(goal, llm):
    """Ask the LLM which tools to run, in order. Falls back to a default plan."""
    tool_list = "\n".join(
        f"- {name}: {info['description']}" for name, info in TOOLS.items()
    )
    prompt = (
        "You are the planner of a lecture-notes agent. Choose which tools to run, "
        "in order, to achieve the goal. Use only tools from this list:\n"
        f"{tool_list}\n\n"
        f"Goal: {goal}\n\n"
        'Reply ONLY with a JSON list of tool names, for example ["segment_topics"].'
    )
    reply = llm.generate(prompt)

    match = re.search(r"\[.*?\]", reply, re.DOTALL)
    if match:
        try:
            steps = json.loads(match.group(0))
            steps = [s for s in steps if s in TOOLS]
            if steps:
                return {"steps": steps, "source": "llm"}
        except json.JSONDecodeError:
            pass
    return {"steps": DEFAULT_PLAN, "source": "fallback"}


if __name__ == "__main__":
    llm = OllamaLLM()
    goals = [
        "Turn this lecture into structured study notes",
        "Check whether this claim is supported by the lecture",
    ]
    for goal in goals:
        print(goal, "->", make_plan(goal, llm))