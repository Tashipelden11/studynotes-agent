import json

from src.agent.llm import OllamaLLM


def _parse_json_list(reply):
    """Extract a JSON list from the model's reply."""
    try:
        # Find the JSON list in the response.
        start = reply.find("[")
        end = reply.rfind("]")

        if start == -1 or end == -1 or end < start:
            return []

        data = json.loads(reply[start:end + 1])

    except (json.JSONDecodeError, TypeError):
        return []

    concepts = []

    for item in data:
        if (
            isinstance(item, dict)
            and isinstance(item.get("term"), str)
            and isinstance(item.get("definition"), str)
        ):
            concepts.append({
                "term": item["term"].strip(),
                "definition": item["definition"].strip()
            })

    return concepts


def extract_concepts(text, llm):
    """Extract important concepts from the lecture."""
    prompt = (
        "Identify the important concepts and technical terms in this lecture.\n\n"

        "Instructions:\n"
        "1. Include all important concepts mentioned in the lecture.\n"
        "2. Do not skip concepts just because they are briefly mentioned.\n"
        "3. Include named types, categories, and classifications.\n"
        "4. Use only information provided in the lecture.\n"
        "5. If a term is mentioned but not defined, use this exact definition: "
        "'Mentioned in the lecture, but no definition is provided.'\n"
        "6. Do not invent definitions using outside knowledge.\n"
        "7. Do not include duplicate concepts.\n\n"

        'Return ONLY a JSON list in this format:\n'
        '[{"term": "Concept name", "definition": "Definition or mention"}]\n\n'

        f"LECTURE TEXT:\n{text}"
    )

    reply = llm.generate(prompt)
    return _parse_json_list(reply)


if __name__ == "__main__":
    with open("data/sample_lecture.txt", encoding="utf-8") as f:
        lecture = f.read()

    for concept in extract_concepts(lecture, OllamaLLM()):
        print(f"- {concept['term']}: {concept['definition']}")