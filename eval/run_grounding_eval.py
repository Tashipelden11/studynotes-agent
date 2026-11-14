import json
import time

from src.agent.llm import OllamaLLM
from src.tools.grounding import check_grounding

VERSION = "quote-check-v1"  # change this label when you change the checker


def main():
    with open("data/sample_lecture.txt", encoding="utf-8") as f:
        lecture = f.read()
    with open("eval/grounding_cases.json", encoding="utf-8") as f:
        cases = json.load(f)

    llm = OllamaLLM()
    results = []
    for i, case in enumerate(cases, start=1):
        start = time.time()
        predicted = check_grounding(case["claim"], lecture, llm)
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
        print(f"{i:2d}/{len(cases)} {'OK ' if correct else 'BAD'} {seconds:5.1f}s  {case['claim']}")

    tp = sum(r["expected"] and r["predicted"] for r in results)
    tn = sum(not r["expected"] and not r["predicted"] for r in results)
    fp = sum(not r["expected"] and r["predicted"] for r in results)
    fn = sum(r["expected"] and not r["predicted"] for r in results)
    accuracy = (tp + tn) / len(results)

    print("\nRESULTS:", VERSION)
    print(f"Accuracy: {accuracy:.0%} ({tp + tn}/{len(results)})")
    print(f"Caught supported claims (TP): {tp}   Wrongly rejected (FN): {fn}")
    print(f"Caught unsupported claims (TN): {tn}   Wrongly accepted (FP): {fp}")
    print(f"Average time per check: {sum(r['seconds'] for r in results) / len(results):.1f}s")

    with open(f"eval/results_{VERSION}.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "version": VERSION,
                "accuracy": accuracy,
                "tp": tp,
                "tn": tn,
                "fp": fp,
                "fn": fn,
                "cases": results,
            },
            f,
            indent=2,
        )


if __name__ == "__main__":
    main()