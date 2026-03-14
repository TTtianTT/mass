"""
Dataset loaders for all 8 benchmarks used in the MASS paper.
Uses HuggingFace `datasets` library. Samples random subsets matching Table 2 sizes.
"""

import random
from datasets import load_dataset
from config import DATASET_SPLITS


def load_math(split: str = "test", seed: int = 42) -> list:
    """Load Hendryck's MATH dataset."""
    ds = load_dataset("nlile/hendrycks-MATH-benchmark", split=split)
    samples = [{"problem": s["problem"], "solution": s["solution"],
                "level": s.get("level", ""), "type": s.get("type", s.get("subject", ""))} for s in ds]
    n = DATASET_SPLITS["math"].get(split, len(samples))
    random.seed(seed)
    return random.sample(samples, min(n, len(samples)))


def load_drop(split: str = "validation", seed: int = 42) -> list:
    """Load DROP dataset."""
    split_name = split if split == "validation" else ("train" if split == "train" else "validation")
    ds = load_dataset("parquet", data_files={split_name: f"hf://datasets/ucinlp/drop/data/{split_name}-*.parquet"}, split=split_name)
    samples = []
    for s in ds:
        # DROP has multiple valid answers per question
        answers = []
        if "answers_spans" in s:
            ans_obj = s["answers_spans"]
            if isinstance(ans_obj, dict) and "spans" in ans_obj:
                answers = ans_obj["spans"]
            elif isinstance(ans_obj, list):
                answers = ans_obj
        samples.append({
            "question": s["question"],
            "passage": s["passage"],
            "context": s["passage"],
            "answers": answers,
        })
    n = DATASET_SPLITS["drop"].get(split if split != "validation" else "val", len(samples))
    random.seed(seed)
    return random.sample(samples, min(n, len(samples)))


def load_hotpotqa(split: str = "test", seed: int = 42) -> list:
    """Load HotpotQA from LongBench."""
    ds = load_dataset("THUDM/LongBench", "hotpotqa", split=split, trust_remote_code=True)
    samples = [{"question": s["input"], "context": s["context"],
                "answer": s["answers"][0] if s["answers"] else "",
                "all_answers": s["answers"]} for s in ds]
    n = DATASET_SPLITS["hotpotqa"].get(split, len(samples))
    random.seed(seed)
    return random.sample(samples, min(n, len(samples)))


def load_musique(split: str = "test", seed: int = 42) -> list:
    """Load MuSiQue from LongBench."""
    ds = load_dataset("THUDM/LongBench", "musique", split=split, trust_remote_code=True)
    samples = [{"question": s["input"], "context": s["context"],
                "answer": s["answers"][0] if s["answers"] else "",
                "all_answers": s["answers"]} for s in ds]
    n = DATASET_SPLITS["musique"].get(split, len(samples))
    random.seed(seed)
    return random.sample(samples, min(n, len(samples)))


def load_2wikimqa(split: str = "test", seed: int = 42) -> list:
    """Load 2WikiMultiHopQA from LongBench."""
    ds = load_dataset("THUDM/LongBench", "2wikimqa", split=split, trust_remote_code=True)
    samples = [{"question": s["input"], "context": s["context"],
                "answer": s["answers"][0] if s["answers"] else "",
                "all_answers": s["answers"]} for s in ds]
    n = DATASET_SPLITS["2wikimqa"].get(split, len(samples))
    random.seed(seed)
    return random.sample(samples, min(n, len(samples)))


def load_mbpp(split: str = "test", seed: int = 42) -> list:
    """Load MBPP dataset."""
    split_name = split if split in ["train", "test", "validation", "prompt"] else "test"
    ds = load_dataset("parquet", data_files={split_name: f"hf://datasets/google-research-datasets/mbpp/full/{split_name}-*.parquet"}, split=split_name)
    samples = [{"text": s["text"], "code": s["code"],
                "test": "\n".join(s["test_list"]),
                "question": s["text"]} for s in ds]
    n = DATASET_SPLITS["mbpp"].get(split, len(samples))
    random.seed(seed)
    return random.sample(samples, min(n, len(samples)))


def load_humaneval(split: str = "test", seed: int = 42) -> list:
    """Load HumanEval dataset."""
    ds = load_dataset("openai/openai_humaneval", split=split)
    samples = [{"prompt": s["prompt"], "canonical_solution": s["canonical_solution"],
                "test": s["test"], "entry_point": s["entry_point"],
                "question": s["prompt"], "task_id": s["task_id"]} for s in ds]
    n = DATASET_SPLITS["humaneval"].get(split, len(samples))
    random.seed(seed)
    return random.sample(samples, min(n, len(samples)))


def load_livecodebench(split: str = "test", seed: int = 42) -> list:
    """Load LiveCodeBench dataset (test output prediction)."""
    try:
        ds = load_dataset("livecodebench/code_generation_lite", split=split, trust_remote_code=True)
        samples = [{"question": s.get("question_content", s.get("question", "")),
                     "question_content": s.get("question_content", ""),
                     "test": s.get("test", ""),
                     "input_output": s.get("input_output", "")} for s in ds]
    except Exception:
        # Fallback: try alternative dataset name
        try:
            ds = load_dataset("livecodelabs/livecodebench", split=split, trust_remote_code=True)
            samples = [{"question": s.get("question_content", s.get("question", "")),
                         "question_content": s.get("question_content", ""),
                         "test": s.get("test", ""),
                         "input_output": s.get("input_output", "")} for s in ds]
        except Exception as e:
            print(f"Warning: Could not load LiveCodeBench: {e}")
            return []

    n = DATASET_SPLITS["livecodebench"].get(split, len(samples))
    random.seed(seed)
    return random.sample(samples, min(n, len(samples)))


# ── Unified Loader ──

LOADERS = {
    "math": load_math,
    "drop": load_drop,
    "hotpotqa": load_hotpotqa,
    "musique": load_musique,
    "2wikimqa": load_2wikimqa,
    "mbpp": load_mbpp,
    "humaneval": load_humaneval,
    "livecodebench": load_livecodebench,
}


def load_dataset_samples(dataset: str, split: str = "test",
                         seed: int = 42, num_samples: int = None) -> list:
    """
    Load samples for a given dataset.

    Args:
        dataset: Dataset key.
        split: "test" or "validation" / "val".
        seed: Random seed for subset sampling.
        num_samples: Override number of samples (None = use paper's Table 2 sizes).

    Returns:
        List of sample dicts.
    """
    loader = LOADERS.get(dataset)
    if loader is None:
        raise ValueError(f"Unknown dataset: {dataset}. Available: {list(LOADERS.keys())}")

    # Map "val" to the appropriate split name per dataset
    if split == "val":
        if dataset == "drop":
            split = "validation"
        elif dataset in ("math",):
            split = "train"  # MATH uses train split for validation subset
        # For LongBench datasets, they only have "test" split usually

    samples = loader(split=split, seed=seed)

    if num_samples is not None:
        samples = samples[:num_samples]

    return samples
