
import json
import re

from src.agent.llm import OllamaLLM
from src.tools.registry import TOOLS

DEFAULT_PLAN = ["segment_topics", "extract_concepts"]


def make_plan(goal, llm):
    """Use a fast default plan for normal study-note generation."""

    normalized_goal = goal.lower()

    if "study notes" in normalized_goal or "structured notes" in normalized_goal:
        return {
            "steps": DEFAULT_PLAN,
            "source": "default"
        }

    tool_list = "\n".join(
        f"- {name}: {info['description']}"
        for name, info in TOOLS.items()
    )

    prompt = (
        "You are the planner of a lecture-notes agent. "
        "Choose which tools to run, in order, to achieve the goal. "
        "Use only tools from this list:\n"
        f"{tool_list}\n\n"
        f"Goal: {goal}\n\n"
        'Reply ONLY with a JSON list of tool names, '
        'for example ["segment_topics"].'
    )

    try:
        reply = llm.generate(prompt)
        match = re.search(r"\[.*?\]", reply, re.DOTALL)

        if match:
            steps = json.loads(match.group(0))
            steps = [step for step in steps if step in TOOLS]

            if steps:
                return {
                    "steps": steps,
                    "source": "llm"
                }

    except Exception:
        pass

    return {
        "steps": DEFAULT_PLAN,
        "source": "fallback"
    }


if __name__ == "__main__":
    llm = OllamaLLM()

    goals = [
        "Turn this lecture into structured study notes",
        "Check whether this claim is supported by the lecture",
    ]

    for goal in goals:
        print(goal, "->", make_plan(goal, llm))
