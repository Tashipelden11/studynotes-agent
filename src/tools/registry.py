from src.tools.segmenter import segment_topics
from src.tools.concepts import extract_concepts
from src.tools.grounding import check_grounding

TOOLS = {
    "segment_topics": {
        "description": "Split a lecture into titled sections. Use first on long lecture text.",
        "parameters": {"text": "the lecture text"},
        "function": segment_topics,
    },
    "extract_concepts": {
        "description": "Extract key terms and definitions from lecture text.",
        "parameters": {"text": "the lecture text or one section of it"},
        "function": extract_concepts,
    },
    "check_grounding": {
        "description": "Check whether a claim is supported by the source lecture text.",
        "parameters": {"claim": "the claim to verify", "source_text": "the lecture text"},
        "function": check_grounding,
    },
}


def run_tool(name, args, llm):
    """Run a tool by name. Never crashes: returns an ok/error result instead."""
    if name not in TOOLS:
        return {"ok": False, "error": f"Unknown tool: {name}"}
    try:
        result = TOOLS[name]["function"](llm=llm, **args)
        return {"ok": True, "result": result}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


if __name__ == "__main__":
    # llm=None, so this test does not need the model
    print(run_tool("does_not_exist", {}, None))
    print(run_tool("segment_topics", {"wrong_arg": "x"}, None))
    print(run_tool("segment_topics", {"text": "Hello.\n\nWorld."}, None))