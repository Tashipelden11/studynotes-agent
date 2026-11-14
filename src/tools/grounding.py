
import json

from src.agent.llm import OllamaLLM


def _normalize(text):
    """Lowercase and collapse whitespace."""
    return " ".join(text.lower().split())


def check_grounding(claim, source_text, llm):
    """Check one claim using exact supporting evidence."""

    prompt = (
        "You are a lecture information checker.\n"
        "Decide whether the source supports the claim.\n"
        "Use only the source. Do not use outside knowledge.\n"
        "If supported, copy an exact phrase from the source.\n\n"
        'Return ONLY this JSON format: '
        '{"supported": true, "evidence": "exact quote"}\n\n'
        f"SOURCE TEXT:\n{source_text}\n\n"
        f"CLAIM:\n{claim}"
    )

    try:
        reply = llm.generate(prompt).strip()
        start = reply.find("{")

        if start == -1:
            return None

        result, _ = json.JSONDecoder().raw_decode(reply[start:])

        if not isinstance(result, dict):
            return None

        supported = result.get("supported")
        evidence = result.get("evidence", "")

        if supported is False:
            return False

        if (
            supported is True
            and isinstance(evidence, str)
            and evidence.strip()
            and _normalize(evidence) in _normalize(source_text)
        ):
            return True

        return None

    except Exception:
        return None


def check_grounding_batch(claims, source_text, llm):
    """Check multiple claims in one AI request."""

    if not claims:
        return []

    prompt = (
        "You are a careful lecture information checker.\n"
        "Check every claim using only the source lecture.\n"
        "Return exactly one result for each claim.\n"
        "Keep the same order as the claims.\n"
        "For supported claims, provide an exact quotation.\n"
        "For unsupported claims, use an empty evidence string.\n"
        "Do not add explanations or extra results.\n\n"
        "Return ONLY a JSON list in this format:\n"
        '[{"supported": true, "evidence": "exact quote"}]\n\n'
        f"SOURCE TEXT:\n{source_text}\n\n"
        f"CLAIMS:\n{json.dumps(claims, ensure_ascii=False)}"
    )

    try:
        reply = llm.generate(prompt).strip()
        start = reply.find("[")

        if start == -1:
            return [None] * len(claims)

        results, _ = json.JSONDecoder().raw_decode(reply[start:])

        if not isinstance(results, list) or len(results) != len(claims):
            return [None] * len(claims)

        verdicts = []

        for result in results:
            if not isinstance(result, dict):
                return [None] * len(claims)

            supported = result.get("supported")
            evidence = result.get("evidence", "")

            if not isinstance(supported, bool):
                return [None] * len(claims)

            if supported is False:
                verdicts.append(False)

            elif (
                isinstance(evidence, str)
                and evidence.strip()
                and _normalize(evidence) in _normalize(source_text)
            ):
                verdicts.append(True)

            else:
                verdicts.append(None)

        return verdicts

    except Exception:
        return [None] * len(claims)


def check_grounding_yesno(claim, source_text, llm):
    """Compatibility checker using a one-word verdict."""

    try:
        prompt = (
            "Read the source text and the claim. "
            "Answer SUPPORTED only if the source clearly supports it. "
            "Otherwise answer NOT_SUPPORTED. Reply with one word only.\n\n"
            f"SOURCE TEXT:\n{source_text}\n\n"
            f"CLAIM:\n{claim}"
        )

        reply = llm.generate(prompt).strip().upper()

        if reply.startswith("NOT_SUPPORTED"):
            return False

        if reply.startswith("SUPPORTED"):
            return True

        return None

    except Exception:
        return None


if __name__ == "__main__":
    llm = OllamaLLM()

    with open("data/sample_lecture.txt", encoding="utf-8") as f:
        lecture = f.read()

    test_claims = [
        "An intelligent agent perceives its environment through sensors and acts through actuators.",
        "A thermostat is an example of a simple agent.",
        "Chess is fully observable and deterministic.",
    ]

    print("\nBATCH GROUNDING TESTS\n")

    results = check_grounding_batch(test_claims, lecture, llm)

    for claim, result in zip(test_claims, results):
        verdict = (
            "SUPPORTED" if result is True
            else "NOT SUPPORTED" if result is False
            else "UNKNOWN"
        )
        print(f"[{verdict}] {claim}")
