
import time

from src.agent.llm import OllamaLLM
from src.agent.planner import make_plan
from src.memory.student_memory import RATINGS, StudentMemory
from src.tools.segmenter import segment_topics
from src.tools.concepts import analyze_section


def normalize(text):
    """Lowercase text and remove extra whitespace."""
    return " ".join(text.lower().split())


class LectureAgent:
    def __init__(self, llm=None, memory=None):
        self.llm = llm or OllamaLLM()
        self.memory = memory or StudentMemory()
        self.trace = []

    def _log(self, step, status, seconds, detail=""):
        self.trace.append({
            "step": step,
            "status": status,
            "seconds": round(seconds, 1),
            "detail": detail
        })

    def _notify_progress(
        self, callback, completed, total, title, status
    ):
        """Send progress information to the application."""
        if callback is not None:
            try:
                callback(completed, total, title, status)
            except Exception as error:
                print(f"Progress display error: {error}")

    def _reflect(self, state):
        """Label concepts based on exact text matching."""
        start = time.time()
        final_notes = []
        exact_matches = 0
        mentioned = 0

        for item in state["verified"]:
            if item["supported"]:
                final_notes.append({
                    "term": item["term"],
                    "definition": item["definition"],
                    "status": "verified"
                })
                exact_matches += 1
            else:
                final_notes.append({
                    "term": item["term"],
                    "definition": item["definition"],
                    "status": "mentioned"
                })
                mentioned += 1

        state["final_notes"] = final_notes

        self._log(
            "reflect",
            "ok",
            time.time() - start,
            f"exact_matches={exact_matches}, "
            f"not_exact_matches={mentioned}"
        )

    def _analyze_sections(self, state, progress_callback=None):
        """Generate notes and concepts one section at a time."""
        start = time.time()
        detail = self.memory.profile["detail"]

        seen = set()
        failures = 0
        retries = 0
        failed_sections = []

        total = len(state["sections"])

        for index, section in enumerate(
            state["sections"], start=1
        ):
            title = section["title"]

            self._notify_progress(
                progress_callback,
                index - 1,
                total,
                title,
                "processing"
            )

            try:
                result = None
                notes = ""
                last_error = None

                placeholder_phrases = [
                    "study notes here",
                    "notes here",
                    "study notes will appear here",
                    "insert notes here",
                    "no notes"
                ]

                # Try at most two times.
                for attempt in range(2):
                    try:
                        result = analyze_section(
                            section["text"],
                            detail,
                            self.llm
                        )

                        if result is None:
                            raise ValueError(
                                "The model did not return valid analysis."
                            )

                        notes = result["notes"].strip()
                        notes_lower = notes.lower()

                        if (
                            not notes
                            or any(
                                phrase in notes_lower
                                for phrase in placeholder_phrases
                            )
                        ):
                            raise ValueError(
                                "The model returned empty or placeholder notes."
                            )

                        if attempt == 1:
                            retries += 1

                        last_error = None
                        break

                    except Exception as error:
                        last_error = error

                        if attempt == 0:
                            print(
                                f"Retrying {title}: {error}"
                            )

                if last_error is not None:
                    raise last_error

                state["notes"].append({
                    "title": title,
                    "notes": notes
                })

                source = normalize(section["text"])

                for concept in result["concepts"]:
                    term = concept["term"].strip()
                    definition = concept["definition"].strip()
                    key = term.casefold()

                    if not key or key in seen:
                        continue

                    seen.add(key)
                    state["concepts"].append(concept)

                    supported = (
                        bool(definition)
                        and normalize(definition) in source
                    )

                    state["verified"].append({
                        "term": term,
                        "definition": definition,
                        "supported": supported,
                        "source": section["text"]
                    })

                self._notify_progress(
                    progress_callback,
                    index,
                    total,
                    title,
                    "completed"
                )

            except Exception as error:
                failures += 1
                failed_sections.append(f"{title}: {error}")

                print(f"Analysis error in {title}: {error}")

                state["notes"].append({
                    "title": title,
                    "notes": (
                        "Notes could not be generated for this "
                        "section. Please try processing it again."
                    )
                })

                self._notify_progress(
                    progress_callback,
                    index,
                    total,
                    title,
                    "failed"
                )

        status = "ok" if failures == 0 else "partial"

        details = (
            f"detail={detail}, "
            f"concepts={len(state['concepts'])}, "
            f"failures={failures}, "
            f"retries={retries}, "
            f"sections={total}"
        )

        if failed_sections:
            details += "; " + "; ".join(failed_sections)

        self._log(
            "analyze_sections",
            status,
            time.time() - start,
            details
        )

    def give_feedback(self, rating, comment=""):
        """Save student feedback."""
        self.memory.record_feedback(rating, comment)

    def run(
        self, goal, lecture_text, progress_callback=None
    ):
        """Run the lecture assistant."""
        self.trace = []

        state = {
            "lecture_text": lecture_text,
            "sections": [],
            "concepts": [],
            "verified": [],
            "final_notes": [],
            "notes": []
        }

        start = time.time()
        plan = make_plan(goal, self.llm)

        self._log(
            "plan",
            "ok",
            time.time() - start,
            f"{plan['steps']} ({plan['source']})"
        )

        if "segment_topics" in plan["steps"]:
            start = time.time()

            try:
                state["sections"] = segment_topics(lecture_text)

                self._log(
                    "segment_topics",
                    "ok",
                    time.time() - start,
                    f"sections={len(state['sections'])}"
                )

            except Exception as error:
                self._log(
                    "segment_topics",
                    "error",
                    time.time() - start,
                    str(error)
                )
                return state, self.trace

        if state["sections"]:
            self._analyze_sections(
                state,
                progress_callback
            )
            self._reflect(state)

        return state, self.trace


if __name__ == "__main__":
    with open("data/sample_lecture.txt", encoding="utf-8") as f:
        lecture = f.read()

    agent = LectureAgent()

    print(
        "Current detail level:",
        agent.memory.profile["detail"]
    )

    state, trace = agent.run(
        "Turn this lecture into structured study notes",
        lecture
    )

    print("\nSTUDY NOTES")

    for note in state["notes"]:
        print(f"\n## {note['title']}")
        print(note["notes"])

    print("\nKEY CONCEPTS")

    for item in state["final_notes"]:
        print(
            f"[{item['status']}] "
            f"{item['term']}: {item['definition']}"
        )

    print("\nTRACE")

    for item in trace:
        print(item)

    answer = input(
        "\nWere the notes too_short, good, or too_long? "
        "(press Enter to skip): "
    ).strip()

    if answer in RATINGS:
        agent.give_feedback(answer)

        print(
            "Detail level is now:",
            agent.memory.profile["detail"]
        )

    elif answer:
        print("Not recognised, feedback skipped.")
