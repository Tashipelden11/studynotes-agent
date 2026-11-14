
import json

from src.agent.llm import OllamaLLM
from src.agent.notes import DETAIL_INSTRUCTIONS


def _parse_json_list(reply):
    """Extract a JSON list from the model's reply."""
    try:
        start = reply.find("[")
        end = reply.rfind("]")

        if start == -1 or end == -1:
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
        "Identify the important concepts and technical terms "
        "in this lecture.\n\n"
        "Use only information provided in the lecture.\n"
        "Do not invent definitions.\n"
        "If a term is mentioned but not defined, use this exact "
        "definition: 'Mentioned in the lecture, but no definition "
        "is provided.'\n\n"
        'Return ONLY a JSON list in this format:\n'
        '[{"term": "Concept name", '
        '"definition": "Definition or mention"}]\n\n'
        f"LECTURE TEXT:\n{text}"
    )

    reply = llm.generate(prompt)
    return _parse_json_list(reply)


def analyze_section(text, detail, llm):
    """Generate study notes and extract concepts in one AI request."""

    instruction = DETAIL_INSTRUCTIONS.get(
        detail,
        DETAIL_INSTRUCTIONS["normal"]
    )

    prompt = (
        "You are a lecture study assistant.\n"
        "Analyze the lecture section and produce study notes "
        "and key concepts.\n\n"

        "STRICT RULES:\n"
        "1. Use only information stated in the lecture.\n"
        "2. Do not add outside knowledge or assumptions.\n"
        "3. Do not invent definitions.\n"
        "4. Include examples actually given in the lecture.\n"
        "5. Keep the original meaning.\n"
        "6. Use clear headings and simple language.\n"
        "7. Avoid unnecessary repetition.\n\n"

        f"NOTE DETAIL LEVEL: {instruction}\n\n"

        "Return one JSON object with exactly these two keys:\n"
        "1. notes: structured study notes in Markdown format.\n"
        "2. concepts: a list of important concepts and their "
        "lecture-based definitions.\n\n"

        "If a concept is mentioned but not defined, use this exact "
        "definition: 'Mentioned in the lecture, but no definition "
        "is provided.'\n\n"

        'Required format:\n'
        '{"notes": "Study notes here", '
        '"concepts": [{"term": "Concept", '
        '"definition": "Definition"}]}\n\n'

        "Return valid JSON only. Do not use a Markdown code block.\n\n"
        f"LECTURE SECTION:\n{text}"
    )

    try:
        reply = llm.chat(
            [{"role": "user", "content": prompt}],
            format="json"
        )["content"].strip()

        start = reply.find("{")

        if start == -1:
            return None

        result, _ = json.JSONDecoder().raw_decode(reply[start:])

        if not isinstance(result, dict):
            return None

        notes = result.get("notes")
        concepts = result.get("concepts")

        if not isinstance(notes, str):
            return None

        if not isinstance(concepts, list):
            return None

        valid_concepts = []

        for item in concepts:
            if (
                isinstance(item, dict)
                and isinstance(item.get("term"), str)
                and isinstance(item.get("definition"), str)
            ):
                valid_concepts.append({
                    "term": item["term"].strip(),
                    "definition": item["definition"].strip()
                })

        return {
            "notes": notes.strip(),
            "concepts": valid_concepts
        }

    except Exception:
        return None


if __name__ == "__main__":
    llm = OllamaLLM()

    with open("data/sample_lecture.txt", encoding="utf-8") as f:
        lecture = f.read()

    result = analyze_section(lecture, "normal", llm)

    if result:
        print("\nSTUDY NOTES\n")
        print(result["notes"])

        print("\nKEY CONCEPTS\n")
        for concept in result["concepts"]:
            print(
                f"- {concept['term']}: "
                f"{concept['definition']}"
            )
    else:
        print("Could not analyze the lecture.")
