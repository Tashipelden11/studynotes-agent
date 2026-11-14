
def segment_topics(text, llm=None):
    """Split lecture text into smaller sections."""

    paragraphs = [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]

    segments = []
    current_text = []
    current_length = 0
    section_number = 1

    # Keep sections to a manageable size.
    max_length = 2500

    for paragraph in paragraphs:

        # Split exceptionally long paragraphs.
        if len(paragraph) > max_length:
            if current_text:
                segments.append({
                    "id": section_number,
                    "title": f"Section {section_number}",
                    "text": "\n\n".join(current_text)
                })
                section_number += 1
                current_text = []
                current_length = 0

            for start in range(0, len(paragraph), max_length):
                chunk = paragraph[start:start + max_length]

                segments.append({
                    "id": section_number,
                    "title": f"Section {section_number}",
                    "text": chunk
                })
                section_number += 1

            continue

        # Start a new section when the current one gets too large.
        if current_length + len(paragraph) > max_length and current_text:
            segments.append({
                "id": section_number,
                "title": f"Section {section_number}",
                "text": "\n\n".join(current_text)
            })

            section_number += 1
            current_text = []
            current_length = 0

        current_text.append(paragraph)
        current_length += len(paragraph)

    # Save the remaining text.
    if current_text:
        segments.append({
            "id": section_number,
            "title": f"Section {section_number}",
            "text": "\n\n".join(current_text)
        })

    return segments
