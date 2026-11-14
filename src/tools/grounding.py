from src.agent.llm import OllamaLLM
from src.tools.concepts import extract_concepts


def check_grounding(claim, source_text, llm):
    """Ask the LLM whether a claim is supported by the source text.

    Returns True (supported) or False (unsupported or unclear).
    """
    prompt = (
        "Read the source text and the claim. "
        "Answer SUPPORTED only if the source text clearly states the claim. "
        "Otherwise answer NOT_SUPPORTED. Reply with one word only.\n\n"
        f"SOURCE TEXT:\n{source_text}\n\nCLAIM:\n{claim}"
    )
    reply = llm.generate(prompt).strip().upper()
    return reply.startswith("SUPPORTED")


if __name__ == "__main__":
    llm = OllamaLLM()
    with open("data/sample_lecture.txt", encoding="utf-8") as f:
        lecture = f.read()
    for c in extract_concepts(lecture, llm):
        claim = f"{c['term']}: {c['definition']}"
        verdict = "SUPPORTED" if check_grounding(claim, lecture, llm) else "NOT SUPPORTED"
        print(f"[{verdict}] {claim}")