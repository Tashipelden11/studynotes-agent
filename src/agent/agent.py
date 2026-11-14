import time

from src.agent.llm import OllamaLLM
from src.agent.planner import make_plan
from src.tools.registry import run_tool

MAX_REVISIONS = 1


class LectureAgent:
    def __init__(self, llm=None):
        self.llm = llm or OllamaLLM()
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

    def _revise(self, term, lecture_text):
        """Ask for a definition that uses ONLY the lecture. Returns None if there is none."""
        prompt = (
            f"Using ONLY information stated in the lecture text below, write a one-sentence "
            f"definition of '{term}'. If the lecture text does not define or explain "
            f"'{term}', reply exactly NONE. Reply with the definition only.\n\n"
            f"LECTURE TEXT:\n{lecture_text}"
        )
        try:
            reply = self.llm.generate(prompt).strip().strip('"')
        except Exception:
            return None
        if not reply or reply.upper().startswith("NONE"):
            return None
        return reply

    def _reflect(self, state, lecture_text):
        """Review unsupported concepts: try one grounded rewrite, otherwise drop them."""
        start = time.time()
        notes = []
        revised = dropped = 0
        for v in state["verified"]:
            if v["supported"]:
                notes.append(
                    {"term": v["term"], "definition": v["definition"], "status": "verified"}
                )
                continue

            accepted = False
            for _ in range(MAX_REVISIONS):
                new_def = self._revise(v["term"], lecture_text)
                if new_def is None:
                    break
                if self._check(f"{v['term']}: {new_def}", lecture_text):
                    notes.append(
                        {"term": v["term"], "definition": new_def, "status": "revised"}
                    )
                    revised += 1
                    accepted = True
                    break
            if not accepted:
                dropped += 1
                notes.append(
                    {"term": v["term"], "definition": v["definition"], "status": "dropped"}
                )

        state["final_notes"] = notes
        self._log("reflect", "ok", time.time() - start, f"revised={revised}, dropped={dropped}")

    def run(self, goal, lecture_text):
        self.trace = []
        state = {"sections": [], "concepts": [], "verified": [], "final_notes": []}

        # 1. Plan
        start = time.time()
        plan = make_plan(goal, self.llm)
        self._log("plan", "ok", time.time() - start, f"{plan['steps']} ({plan['source']})")

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
                    state["verified"].append(
                        {
                            "term": concept["term"],
                            "definition": concept["definition"],
                            "supported": self._check(claim, lecture_text),
                        }
                    )
                out = {"ok": True}

            else:
                out = {"ok": False, "error": f"No handler for step {step}"}

            status = "ok" if out["ok"] else "error"
            self._log(step, status, time.time() - start, out.get("error", ""))

        # 3. Reflect: act on what the grounding check found
        if state["verified"]:
            self._reflect(state, lecture_text)

        return state, self.trace


if __name__ == "__main__":
    with open("data/sample_lecture.txt", encoding="utf-8") as f:
        lecture = f.read()

    agent = LectureAgent()
    state, trace = agent.run("Turn this lecture into structured study notes", lecture)

    print("\nSECTIONS")
    for s in state["sections"]:
        print(f"{s['id']}. {s['title']}")

    print("\nFINAL NOTES")
    for n in state["final_notes"]:
        if n["status"] == "dropped":
            print(f"[dropped] {n['term']} (not supported by the lecture)")
        else:
            print(f"[{n['status']}] {n['term']}: {n['definition']}")

    print("\nTRACE")
    for t in trace:
        print(t)