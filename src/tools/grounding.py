
import json

from src.agent.llm import OllamaLLM
from src.tools.concepts import extract_concepts


def _normalize(text):
    """Lowercase and collapse whitespace."""
    return " ".join(text.lower().split())


def check_grounding(claim, source_text, llm):
    """Check whether the lecture directly supports a claim."""

    prompt = (
        "You are a lecture information checker.\n\n"
        "Decide whether the source supports the meaning of the claim.\n\n"
        "Rules:\n"
        "1. Use only information from the source.\n"
        "2. A paraphrase is allowed if it has the same meaning.\n"
        "3. Do not use outside knowledge.\n"
        "4. Do not invent missing definitions.\n"
        "5. A term being mentioned does not mean it is defined.\n"
        "6. An example can support a claim about that example.\n"
        "7. Evidence must be copied exactly from the source.\n\n"
        "Return ONLY one JSON object:\n"
        '{"supported": true, "evidence": "exact source quotation"}\n'
        "or\n"
        '{"supported": false, "evidence": ""}\n\n'
        f"SOURCE TEXT:\n{source_text}\n\n"
        f"CLAIM:\n{claim}"
    )

    try:
        reply = llm.generate(prompt).strip()
        start = reply.find("{")

        if start == -1:
            return False

        result, _ = json.JSONDecoder().raw_decode(reply[start:])

        if not isinstance(result, dict):
            return False

        supported = result.get("supported")
        evidence = result.get("evidence", "")

        if not isinstance(supported, bool):
            return False

        if supported is False:
            return False

        if not isinstance(evidence, str) or not evidence.strip():
            return False

        if _normalize(evidence) not in _normalize(source_text):
            return False

        return True

    except Exception:
        return False


def check_grounding_yesno(claim, source_text, llm):
    """Keep the original function name for compatibility."""
    return check_grounding(claim, source_text, llm)


if __name__ == "__main__":
    llm = OllamaLLM()

    with open("data/sample_lecture.txt", encoding="utf-8") as f:
        lecture = f.read()

    print("\nGROUNDING TESTS\n")

    test_claims = [
        "An intelligent agent perceives its environment through sensors and acts through actuators.",
        "A thermostat is an example of a simple agent.",
        "PEAS stands for Performance measure, Environment, Actuators and Sensors.",
        "A static environment does not change over time.",
        "Chess is fully observable and deterministic.",
    ]

    for claim in test_claims:
        result = check_grounding(claim, lecture, llm)
        verdict = "SUPPORTED" if result else "NOT SUPPORTED"
        print(f"[{verdict}] {claim}")

    print("\nEXTRACTED CONCEPTS\n")

    for concept in extract_concepts(lecture, llm):
        claim = f"{concept['term']}: {concept['definition']}"
        result = check_grounding(claim, lecture, llm)
        verdict = "SUPPORTED" if result else "NOT SUPPORTED"
        print(f"[{verdict}] {claim}")
