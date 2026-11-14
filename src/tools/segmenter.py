from src.agent.llm import OllamaLLM


def segment_topics(text, llm=None):
    """Split a lecture into sections (by blank lines) and optionally title each one."""
    chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
    segments = []
    for i, chunk in enumerate(chunks, start=1):
        title = f"Section {i}"
        if llm is not None:
            prompt = (
                "Give a short title (maximum 6 words) for this lecture section. "
                "Reply with the title only.\n\n" + chunk
            )
            title = llm.generate(prompt).strip().strip('"')
        segments.append({"id": i, "title": title, "text": chunk})
    return segments


if __name__ == "__main__":
    with open("data/sample_lecture.txt", encoding="utf-8") as f:
        lecture = f.read()
    for seg in segment_topics(lecture, llm=OllamaLLM()):
        print(f"{seg['id']}. {seg['title']}")