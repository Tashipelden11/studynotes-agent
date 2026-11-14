import json
import re

from src.agent.llm import OllamaLLM


def _parse_json_list(reply):
    """Pull a JSON list out of the model's reply; return [] if it is malformed."""
    match = re.search(r"\[.*\]", reply, re.DOTALL)
    if not match:
        return []
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return []
    return [
        item for item in data
        if isinstance(item, dict) and "term" in item and "definition" in item
    ]


def extract_concepts(text, llm):
    """Ask the LLM for key terms and definitions that are supported by the text."""
    prompt = (
        "List the key concepts in this lecture text. "
        'Reply ONLY with JSON in this form: [{"term": "...", "definition": "..."}]. '
        "Only use definitions that are supported by the text.\n\n" + text
    )
    reply = llm.generate(prompt)
    return _parse_json_list(reply)


if __name__ == "__main__":
    with open("data/sample_lecture.txt", encoding="utf-8") as f:
        lecture = f.read()
    for concept in extract_concepts(lecture, OllamaLLM()):
        print(f"- {concept['term']}: {concept['definition']}")