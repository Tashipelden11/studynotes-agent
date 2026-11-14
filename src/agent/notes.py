
import re

from src.agent.llm import OllamaLLM

DETAIL_INSTRUCTIONS = {
    "brief": "Write exactly 1 short sentence.",
    "normal": "Write 2 to 3 sentences.",
    "detailed": (
        "Write 4 to 6 sentences using only information explicitly stated "
        "in the section. Expand on the lecture's actual points and examples, "
        "but do not create new definitions, explanations, or conclusions."
    ),
}


def write_section_notes(section_text, detail, llm):
    """Write study notes using only information from the lecture section."""
    instruction = DETAIL_INSTRUCTIONS.get(
        detail, DETAIL_INSTRUCTIONS["normal"]
    )

    prompt = (
        "Create structured study notes from the lecture section below.\n\n"
        f"DETAIL LEVEL: {instruction}\n\n"
        "STRICT RULES:\n"
        "1. Use ONLY facts and information stated in the lecture.\n"
        "2. Do not add outside knowledge or assumptions.\n"
        "3. Do not add unsupported explanations or conclusions.\n"
        "4. Do not use general knowledge to expand a concept.\n"
        "5. Keep the original meaning of every statement.\n"
        "6. Do not invent definitions for mentioned terms.\n"
        "7. Include examples actually given in the lecture.\n"
        "8. Use clear headings and simple language.\n"
        "9. Do not add introductory phrases.\n"
        "10. Do not repeat information unnecessarily.\n\n"
        f"LECTURE SECTION:\n{section_text}\n\n"
        "Write the study notes now."
    )

    return llm.generate(prompt).strip()


def split_claims(notes_text):
    """Split notes into checkable sentences, skipping headings and chatter."""
    claims = []

    for line in notes_text.splitlines():
        line = line.strip().lstrip("*-•").strip()
        line = re.sub(r"^\d+\.\s*", "", line)

        if not line:
            continue

        for sentence in re.split(r"(?<=[.!?])\s+", line):
            sentence = sentence.strip()

            if len(sentence.split()) >= 4 and not sentence.endswith(":"):
                claims.append(sentence)

    return claims


def mark_unverified(notes_text, section_text, check, batch_check=None):
    """Check claims individually or together and tag unsupported claims."""

    claims = split_claims(notes_text)

    if batch_check is not None:
        results = batch_check(claims, section_text)
    else:
        results = [check(claim, section_text) for claim in claims]

    if len(results) != len(claims):
        results = [None] * len(claims)

    marked = notes_text
    unverified = 0

    for claim, result in zip(claims, results):
        if result is False:
            unverified += 1
            marked = marked.replace(
                claim, claim + " [unverified]", 1
            )

    return marked, {
        "checked": len(claims),
        "unverified": unverified
    }


if __name__ == "__main__":
    llm = OllamaLLM()

    with open("data/sample_lecture.txt", encoding="utf-8") as f:
        section = f.read().split("\n\n")[1]

    for detail in ["brief", "normal", "detailed"]:
        print(f"\n[{detail}]")
        print(write_section_notes(section, detail, llm))
