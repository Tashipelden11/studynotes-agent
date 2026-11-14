import json
import time

from src.agent.llm import OllamaLLM
from src.tools.grounding import check_grounding, check_grounding_yesno

CHECKERS = {
    "yesno-v0": check_grounding_yesno,
    "quote-check-v1": check_grounding,
}


def evaluate(name, checker, lecture, cases, llm):
    results = []
    for i, case in enumerate(cases, start=1):
        start = time.time()
        predicted = checker(case["claim"], lecture, llm)
        seconds = round(time.time() - start, 1)
        correct = predicted == case["supported"]
        results.append(
            {
                "claim": case["claim"],
                "expected": case["supported"],
                "predicted": predicted,
                "correct": correct,
                "seconds": seconds,
            }
        )
        print(f"[{name}] {i:2d}/{len(cases)} {'OK ' if correct else 'BAD'} {seconds:5.1f}s  {case['claim']}")

    tp = sum(r["expected"] and r["predicted"] for r in results)
    tn = sum(not r["expected"] and not r["predicted"] for r in results)
    fp = sum(not r["expected"] and r["predicted"] for r in results)
    fn = sum(r["expected"] and not r["predicted"] for r in results)
    summary = {
        "version": name,
        "accuracy": (tp + tn) / len(results),
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "avg_seconds": round(sum(r["seconds"] for r in results) / len(results), 1),
        "cases": results,
    }
    with open(f"eval/results_{name}.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    return summary


def main():
    with open("data/sample_lecture.txt", encoding="utf-8") as f:
        lecture = f.read()
    with open("eval/grounding_cases.json", encoding="utf-8") as f:
        cases = json.load(f)

    llm = OllamaLLM()
    summaries = [evaluate(n, c, lecture, cases, llm) for n, c in CHECKERS.items()]

    print("\nCOMPARISON")
    print(f"{'version':16s} {'accuracy':>9s} {'TP':>3s} {'FN':>3s} {'TN':>3s} {'FP':>3s} {'avg s':>6s}")
    for s in summaries:
        print(
            f"{s['version']:16s} {s['accuracy']:>9.0%} {s['tp']:>3d} {s['fn']:>3d} "
            f"{s['tn']:>3d} {s['fp']:>3d} {s['avg_seconds']:>6.1f}"
        )


if __name__ == "__main__":
    main()