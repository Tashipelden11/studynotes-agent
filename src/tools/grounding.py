from src.agent.llm import OllamaLLM
from src.tools.concepts import extract_concepts

MIN_QUOTE_LENGTH = 25


def _normalize(text):
    """Lowercase and collapse whitespace so quotes can be compared reliably."""
    return " ".join(text.lower().split())


def check_grounding(claim, source_text, llm):
    """Check whether a claim is supported by the source text.

    The LLM must quote a sentence from the source. The code then verifies the
    quote really appears in the source, so an invented quote counts as unsupported.
    Returns True (supported) or False (unsupported).
    """
    prompt = (
        "Find ONE sentence in the source text that clearly states the claim. "
        "If no sentence states it, reply exactly NONE. "
        "Otherwise copy that sentence exactly as written, with nothing else.\n\n"
        f"SOURCE TEXT:\n{source_text}\n\nCLAIM:\n{claim}"
    )
    reply = llm.generate(prompt).strip().strip('"')

    if not reply or reply.upper().startswith("NONE"):
        return False
    if len(reply) < MIN_QUOTE_LENGTH:
        return False
    return _normalize(reply) in _normalize(source_text)


if __name__ == "__main__":
    llm = OllamaLLM()
    with open("data/sample_lecture.txt", encoding="utf-8") as f:
        lecture = f.read()
    for c in extract_concepts(lecture, llm):
        claim = f"{c['term']}: {c['definition']}"
        verdict = "SUPPORTED" if check_grounding(claim, lecture, llm) else "NOT SUPPORTED"
        print(f"[{verdict}] {claim}")