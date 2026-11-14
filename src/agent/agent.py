import time

from src.agent.llm import OllamaLLM
from src.agent.planner import make_plan
from src.tools.registry import run_tool


class LectureAgent:
    def __init__(self, llm=None):
        self.llm = llm or OllamaLLM()
        self.trace = []

    def _log(self, step, status, seconds, detail=""):
        self.trace.append(
            {"step": step, "status": status, "seconds": round(seconds, 1), "detail": detail}
        )

    def run(self, goal, lecture_text):
        self.trace = []
        state = {"sections": [], "concepts": [], "verified": []}

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
                    check = run_tool(
                        "check_grounding",
                        {"claim": claim, "source_text": lecture_text},
                        self.llm,
                    )
                    state["verified"].append(
                        {"claim": claim, "supported": check["result"] if check["ok"] else None}
                    )
                out = {"ok": True}

            else:
                out = {"ok": False, "error": f"No handler for step {step}"}

            status = "ok" if out["ok"] else "error"
            self._log(step, status, time.time() - start, out.get("error", ""))

        return state, self.trace


if __name__ == "__main__":
    with open("data/sample_lecture.txt", encoding="utf-8") as f:
        lecture = f.read()

    agent = LectureAgent()
    state, trace = agent.run("Turn this lecture into structured study notes", lecture)

    print("\nSECTIONS")
    for s in state["sections"]:
        print(f"{s['id']}. {s['title']}")

    print("\nCONCEPTS (with grounding check)")
    for v in state["verified"]:
        mark = {True: "SUPPORTED", False: "NOT SUPPORTED", None: "CHECK FAILED"}[v["supported"]]
        print(f"[{mark}] {v['claim']}")

    print("\nTRACE")
    for t in trace:
        print(t)