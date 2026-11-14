from src.agent.llm import OllamaLLM

DETAIL_INSTRUCTIONS = {
    "brief": "Write exactly 1 short sentence.",
    "normal": "Write 2 to 3 sentences.",
    "detailed": (
        "Write a short paragraph of 4 to 6 sentences and "
        "include the examples the section gives."
    ),
}


def write_section_notes(section_text, detail, llm):
    """Write study notes for one lecture section, sized to the student's detail level."""
    instruction = DETAIL_INSTRUCTIONS.get(detail, DETAIL_INSTRUCTIONS["normal"])
    prompt = (
        "Write study notes for the lecture section below. "
        f"{instruction} Use ONLY information stated in the section. "
        "Reply with the notes only.\n\n"
        f"SECTION:\n{section_text}"
    )
    return llm.generate(prompt).strip()


if __name__ == "__main__":
    llm = OllamaLLM()
    with open("data/sample_lecture.txt", encoding="utf-8") as f:
        section = f.read().split("\n\n")[1]  # the PEAS section

    for detail in ["brief", "normal", "detailed"]:
        print(f"\n[{detail}]")
        print(write_section_notes(section, detail, llm))