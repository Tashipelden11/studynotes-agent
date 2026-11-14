
import time

from src.agent.llm import OllamaLLM
from src.agent.notes import write_section_notes, mark_unverified
from src.agent.planner import make_plan
from src.memory.student_memory import RATINGS, StudentMemory
from src.tools.registry import run_tool


class LectureAgent:
    def __init__(self, llm=None, memory=None):
        self.llm = llm or OllamaLLM()
        self.memory = memory or StudentMemory()
        self.trace = []

    def _log(self, step, status, seconds, detail=""):
        self.trace.append(
            {"step": step, "status": status, "seconds": round(seconds, 1), "detail": detail}
        )

    def _check(self, claim, lecture_text):
        """Run the grounding tool; return True/False, or None if the tool failed."""
        out = run_tool(
            "check_grounding", {"claim": claim, "source_text": lecture_text}, self.llm
        )
        return out["result"] if out["ok"] else None

    def _reflect(self, state, lecture_text):
        """Keep verified concepts and preserve mentioned concepts without inventing definitions."""
        start = time.time()
        notes = []
        mentioned = 0
        dropped = 0

        for v in state["verified"]:

            if v["supported"] is True:
                notes.append({
                    "term": v["term"],
                    "definition": v["definition"],
                    "status": "verified"
                })
                continue

            if v["term"].casefold() in lecture_text.casefold():
                notes.append({
                    "term": v["term"],
                    "definition": "Mentioned in the lecture, but no verified definition is available.",
                    "status": "mentioned"
                })
                mentioned += 1
                continue

            dropped += 1
            notes.append({
                "term": v["term"],
                "definition": v["definition"],
                "status": "dropped"
            })

        state["final_notes"] = notes

        self._log(
            "reflect",
            "ok",
            time.time() - start,
            f"mentioned={mentioned}, dropped={dropped}"
        )

    def _write_notes(self, state):
        """Write and verify notes using the complete original lecture."""
        start = time.time()
        detail = self.memory.profile["detail"]
        failures = 0
        total_checked = 0
        total_unverified = 0

        for section in state["sections"]:
            try:
                notes_text = write_section_notes(
                    section["text"], detail, self.llm
                )

                # Check claims against the complete lecture, not just one section.
                marked_notes, stats = mark_unverified(
                    notes_text, state["lecture_text"], self._check
                )

                total_checked += stats["checked"]
                total_unverified += stats["unverified"]

                state["notes"].append({
                    "title": section["title"],
                    "notes": marked_notes
                })

            except Exception as e:
                print(f"Notes error in {section['title']}: {e}")
                failures += 1

                state["notes"].append({
                    "title": section["title"],
                    "notes": "(could not write or verify notes for this section)"
                })

        status = "ok" if failures == 0 else "error"

        self._log(
            "write_notes",
            status,
            time.time() - start,
            f"detail={detail}, failures={failures}, "
            f"checked={total_checked}, unverified={total_unverified}"
        )

    def give_feedback(self, rating, comment=""):
        """Pass the student's feedback to memory, which adapts the detail level."""
        self.memory.record_feedback(rating, comment)

    def run(self, goal, lecture_text):
        self.trace = []
        state = {
            "lecture_text": lecture_text,
            "sections": [],
            "concepts": [],
            "verified": [],
            "final_notes": [],
            "notes": [],
        }

        # 1. Plan
        start = time.time()
        plan = make_plan(goal, self.llm)
        self._log(
            "plan",
            "ok",
            time.time() - start,
            f"{plan['steps']} ({plan['source']})"
        )

        # 2. Act: run each planned step
        for step in plan["steps"]:
            start = time.time()

            if step == "segment_topics":
                out = run_tool("segment_topics", {"text": lecture_text}, self.llm)
                if out["ok"]:
                    state["sections"] = out["result"]

            elif step == "extract_concepts":
                out = run_tool("extract_concepts", {"text": lecture_text}, self.llm)
                if out["ok"]:
                    state["concepts"] = out["result"]

            elif step == "check_grounding":
                if not state["concepts"]:
                    self._log(step, "skipped", 0, "no concepts to verify yet")
                    continue

                for concept in state["concepts"]:
                    claim = f"{concept['term']}: {concept['definition']}"
                    state["verified"].append({
                        "term": concept["term"],
                        "definition": concept["definition"],
                        "supported": self._check(claim, lecture_text),
                    })

                out = {"ok": True}

            else:
                out = {"ok": False, "error": f"No handler for step {step}"}

            status = "ok" if out["ok"] else "error"
            self._log(step, status, time.time() - start, out.get("error", ""))

        # 3. Reflect
        if state["verified"]:
            self._reflect(state, lecture_text)

        # 4. Write and verify notes
        if state["sections"]:
            self._write_notes(state)

        return state, self.trace


if __name__ == "__main__":
    with open("data/sample_lecture.txt", encoding="utf-8") as f:
        lecture = f.read()

    agent = LectureAgent()
    print(f"Current detail level: {agent.memory.profile['detail']}")
    state, trace = agent.run(
        "Turn this lecture into structured study notes",
        lecture
    )

    print("\nSTUDY NOTES")
    for n in state["notes"]:
        print(f"\n## {n['title']}")
        print(n["notes"])

    print("\nKEY CONCEPTS")
    for n in state["final_notes"]:
        if n["status"] == "dropped":
            print(f"[dropped] {n['term']} (not supported by the lecture)")
        else:
            print(f"[{n['status']}] {n['term']}: {n['definition']}")

    print("\nTRACE")
    for t in trace:
        print(t)

    answer = input(
        "\nWere the notes too_short, good, or too_long? (press Enter to skip): "
    ).strip()

    if answer in RATINGS:
        agent.give_feedback(answer)
        print("Detail level is now:", agent.memory.profile["detail"])
    elif answer:
        print("Not recognised, feedback skipped.")
