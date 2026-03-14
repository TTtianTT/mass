"""
Evaluation metrics for MASS paper reproduction.
Each dataset uses a specific metric as in the paper:
  - MATH: Exact match (after answer normalization)
  - DROP: F1 score
  - HotpotQA / MuSiQue / 2WikiMQA: F1 score
  - MBPP / HumanEval: pass@1 (code execution)
  - LiveCodeBench: Assertion match
"""

import re
import string
from collections import Counter


def evaluate(prediction: str, sample: dict, dataset: str) -> dict:
    """
    Evaluate a single prediction against the ground truth.

    Returns:
        {"correct": bool, "score": float, "details": str}
    """
    evaluator = EVALUATORS.get(dataset)
    if evaluator is None:
        return {"correct": False, "score": 0.0, "details": f"No evaluator for {dataset}"}
    return evaluator(prediction, sample)


# ── MATH ──────────────────────────────────────

def _eval_math(prediction: str, sample: dict) -> dict:
    """Exact match on MATH after LaTeX normalization."""
    gold = _extract_math_answer(sample.get("solution", ""))
    pred = _normalize_math(prediction)
    gold = _normalize_math(gold)

    correct = pred == gold
    return {"correct": correct, "score": 1.0 if correct else 0.0,
            "details": f"pred={pred} gold={gold}"}


def _extract_math_answer(solution: str) -> str:
    """Extract the final boxed answer from a MATH solution."""
    # Look for \boxed{...}
    match = re.search(r"\\boxed\{(.*)\}", solution)
    if match:
        return match.group(1)
    # Fallback: last line
    lines = solution.strip().split("\n")
    return lines[-1].strip() if lines else ""


def _normalize_math(text: str) -> str:
    """Normalize a math answer for comparison."""
    text = text.strip()
    # Remove <answer> tags
    m = re.search(r"<answer>(.*?)</answer>", text, re.DOTALL)
    if m:
        text = m.group(1).strip()
    # Remove dollar signs, spaces, \text{}
    text = text.replace("$", "").replace(" ", "")
    text = re.sub(r"\\text\{(.*?)\}", r"\1", text)
    text = text.replace("\\,", "").replace("\\;", "")
    text = text.lower()
    return text


# ── DROP ──────────────────────────────────────

def _eval_drop(prediction: str, sample: dict) -> dict:
    """F1 score for DROP."""
    gold_answers = sample.get("answers", [])
    if not gold_answers:
        return {"correct": False, "score": 0.0, "details": "No gold answers"}

    best_f1 = 0.0
    best_gold = ""
    for gold in gold_answers:
        if isinstance(gold, dict):
            gold = gold.get("text", str(gold))
        f1 = _token_f1(prediction, str(gold))
        if f1 > best_f1:
            best_f1 = f1
            best_gold = str(gold)

    return {"correct": best_f1 >= 0.8, "score": best_f1,
            "details": f"F1={best_f1:.3f} best_gold={best_gold}"}


# ── Multi-hop QA (HotpotQA, MuSiQue, 2WikiMQA) ──

def _eval_multihop(prediction: str, sample: dict) -> dict:
    """F1 score for multi-hop QA tasks."""
    gold = sample.get("answer", "")
    all_answers = sample.get("all_answers", [gold] if gold else [])

    if not all_answers:
        return {"correct": False, "score": 0.0, "details": "No gold answers"}

    best_f1 = 0.0
    for ans in all_answers:
        f1 = _token_f1(prediction, str(ans))
        best_f1 = max(best_f1, f1)

    return {"correct": best_f1 >= 0.8, "score": best_f1,
            "details": f"F1={best_f1:.3f}"}


# ── Coding (MBPP, HumanEval) ──────────────────

def _eval_code(prediction: str, sample: dict) -> dict:
    """pass@1 for coding tasks: run code + tests."""
    from building_blocks import Executor
    executor = Executor(timeout=15)

    test_code = sample.get("test", "")
    entry_point = sample.get("entry_point", "")

    # For HumanEval, prepend the prompt (function signature) if prediction
    # doesn't include it
    prompt = sample.get("prompt", "")
    if prompt and not prediction.strip().startswith("def "):
        code = prompt + prediction
    else:
        code = prediction

    # For HumanEval, test code often calls check(candidate) where candidate
    # is the function. We need to wrap it.
    if entry_point and f"def {entry_point}" in code:
        full_test = test_code
        if "candidate" in test_code and entry_point:
            full_test = f"candidate = {entry_point}\n" + test_code
        result = executor.run(code, full_test)
    else:
        result = executor.run(code, test_code)

    correct = result["success"]
    return {"correct": correct, "score": 1.0 if correct else 0.0,
            "details": result.get("traceback", "")[:200]}


# ── LiveCodeBench ─────────────────────────────

def _eval_livecodebench(prediction: str, sample: dict) -> dict:
    """Assertion match for LiveCodeBench test output prediction."""
    # For test output prediction, check if the assertion is correct
    from building_blocks import Executor
    executor = Executor(timeout=15)

    result = executor.run(prediction)
    correct = result["success"]
    return {"correct": correct, "score": 1.0 if correct else 0.0,
            "details": result.get("traceback", "")[:200]}


# ── Shared helpers ────────────────────────────

def _token_f1(prediction: str, gold: str) -> float:
    """Compute token-level F1 score."""
    pred_tokens = _tokenize(prediction)
    gold_tokens = _tokenize(gold)

    if not gold_tokens:
        return 1.0 if not pred_tokens else 0.0
    if not pred_tokens:
        return 0.0

    common = Counter(pred_tokens) & Counter(gold_tokens)
    num_same = sum(common.values())

    if num_same == 0:
        return 0.0

    precision = num_same / len(pred_tokens)
    recall = num_same / len(gold_tokens)
    f1 = 2 * precision * recall / (precision + recall)
    return f1


def _tokenize(text: str) -> list:
    """Simple whitespace + punctuation tokenization."""
    text = text.lower().strip()
    # Remove articles
    text = re.sub(r"\b(a|an|the)\b", " ", text)
    # Remove punctuation
    text = "".join(ch for ch in text if ch not in string.punctuation)
    return text.split()


# ── Registry ──────────────────────────────────

EVALUATORS = {
    "math": _eval_math,
    "drop": _eval_drop,
    "hotpotqa": _eval_multihop,
    "musique": _eval_multihop,
    "2wikimqa": _eval_multihop,
    "mbpp": _eval_code,
    "humaneval": _eval_code,
    "livecodebench": _eval_livecodebench,
}
