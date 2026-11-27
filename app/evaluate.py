"""Score onHelio's answers with RAGAS.

Input:  data/eval/test_questions.csv   (question + correct reference answer)
Output: scores on screen + data/eval/results.csv (one row per question)

Run:    python app/evaluate.py
Cost:   a few cents (onHelio answers 8 questions, then Claude acts as the RAGAS judge).
"""
from pathlib import Path

import pandas as pd
from langchain_anthropic import ChatAnthropic
from ragas import EvaluationDataset, evaluate
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import Faithfulness, LLMContextPrecisionWithReference, LLMContextRecall

from ask import MODEL, ask, split_header

class JudgeClaude(ChatAnthropic):
    """Claude as the RAGAS judge.

    RAGAS always sets a `temperature`, but newer Claude models reject that setting,
    so remove it from every request before it is sent.
    """

    def _get_request_payload(self, *args, **kwargs):
        payload = super()._get_request_payload(*args, **kwargs)
        payload.pop("temperature", None)
        return payload


ROOT = Path(__file__).resolve().parent.parent
TESTS = ROOT / "data" / "eval" / "test_questions.csv"
RESULTS = ROOT / "data" / "eval" / "results.csv"


def collect_answers():
    """Ask onHelio every test question and keep what RAGAS needs."""
    tests = pd.read_csv(TESTS)
    samples = []
    for _, row in tests.iterrows():
        print(f"  Asking #{row['id']}: {row['question'][:60]}...")
        raw, excerpts = ask(row["question"], row["role"])
        _, _, answer = split_header(raw)
        samples.append({
            "user_input": row["question"],                         # the question
            "response": answer,                                    # onHelio's answer
            "retrieved_contexts": [doc for doc, _ in excerpts],    # pages search found
            "reference": row["reference_answer"],                  # the correct answer
        })
    return tests, samples


def main():
    print("Step 1/2: onHelio answers the test questions")
    tests, samples = collect_answers()

    print("\nStep 2/2: RAGAS scores the answers (Claude is the judge)")
    judge = LangchainLLMWrapper(JudgeClaude(model=MODEL, max_tokens=2000))
    metrics = [
        Faithfulness(),                      # did the answer stick to the documents?
        LLMContextRecall(),                  # did search find the pages with the right answer?
        LLMContextPrecisionWithReference(),  # were the pages found actually relevant?
    ]
    result = evaluate(dataset=EvaluationDataset.from_list(samples), metrics=metrics, llm=judge)

    scores = result.to_pandas()
    scores.insert(0, "id", tests["id"].values)
    scores.to_csv(RESULTS, index=False)

    # Guardrail questions (expected_source starts with "none") have no correct pages by design,
    # so they are left out of the search scores (recall and precision).
    has_source = ~tests["expected_source"].astype(str).str.lower().str.startswith("none")
    search_scores = scores[has_source.values]

    print("\n=== onHelio RAGAS scores (0 = poor, 1 = perfect) ===")
    if "faithfulness" in scores:
        print(f"  {'faithfulness':40s} {scores['faithfulness'].mean():.2f}   (all {len(scores)} questions)")
    for column in ["context_recall", "llm_context_precision_with_reference"]:
        if column in scores:
            print(f"  {column:40s} {search_scores[column].mean():.2f}   "
                  f"({len(search_scores)} questions with a source)")
    print(f"\nPer-question details saved to: {RESULTS}")


if __name__ == "__main__":
    main()
