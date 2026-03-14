#!/usr/bin/env python3
"""
Main runner for MASS paper reproduction.
Runs the optimal MASS topology for a given dataset using Gemini models.

Usage:
    python main.py --dataset math --model pro
    python main.py --dataset math --model flash --num-samples 5
    python main.py --dataset math --model pro --prompt-mode default
    python main.py --all --model pro --num-samples 3
"""

import argparse
import json
import os
import sys
import time

from config import TOPOLOGY_CONFIGS, DATASET_SPLITS
from llm_client import GeminiClient
from topology import build_topology, describe_topology
from datasets_loader import load_dataset_samples
from evaluator import evaluate
from tqdm import tqdm


DATASETS = list(TOPOLOGY_CONFIGS.keys())


def format_model_banner(client: GeminiClient) -> str:
    """Return a readable model label for logs and summaries."""
    return f"{client.display_name} ({client.model_name})"


def run_dataset(dataset: str, model_key: str, prompt_mode: str,
                num_samples: int = None, num_runs: int = 1,
                seed: int = 42) -> dict:
    """
    Run the MASS optimal topology on a dataset and evaluate.

    Args:
        dataset: Dataset key (e.g., "math", "drop", ...)
        model_key: "pro" or "flash"
        prompt_mode: "optimized" or "default"
        num_samples: Number of test samples (None = use paper sizes)
        num_runs: Number of runs for averaging (paper uses 3)
        seed: Random seed

    Returns:
        Dict with results summary.
    """
    client = GeminiClient(model_key=model_key)

    print(f"\n{'='*60}")
    print(f"  Dataset: {dataset.upper()}")
    print(f"  Model: {format_model_banner(client)}")
    print(f"  Prompt mode: {prompt_mode}")
    print(f"  Topology: {describe_topology(dataset)}")
    print(f"{'='*60}")

    # Load dataset
    print(f"\n📦 Loading {dataset} dataset...")
    try:
        samples = load_dataset_samples(dataset, split="test", seed=seed,
                                        num_samples=num_samples)
    except Exception as e:
        print(f"  ⚠️ Error loading dataset: {e}")
        print(f"  Trying alternative split...")
        try:
            samples = load_dataset_samples(dataset, split="validation", seed=seed,
                                            num_samples=num_samples)
        except Exception as e2:
            print(f"  ❌ Could not load dataset: {e2}")
            return {"dataset": dataset, "error": str(e2)}

    print(f"  Loaded {len(samples)} samples")

    # Initialize topology
    topology = build_topology(dataset, client, prompt_mode=prompt_mode)

    # Run evaluation
    all_run_results = []
    for run_idx in range(num_runs):
        if num_runs > 1:
            print(f"\n🔄 Run {run_idx + 1}/{num_runs}")

        scores = []
        results = []

        for i, sample in enumerate(tqdm(samples, desc=f"  Evaluating")):
            try:
                # Run topology
                prediction = topology(sample)

                # Evaluate
                eval_result = evaluate(prediction, sample, dataset)
                scores.append(eval_result["score"])

                results.append({
                    "index": i,
                    "prediction": prediction[:200],
                    "score": eval_result["score"],
                    "correct": eval_result["correct"],
                    "details": eval_result["details"][:100],
                })

            except Exception as e:
                print(f"\n  ⚠️ Error on sample {i}: {e}")
                scores.append(0.0)
                results.append({
                    "index": i,
                    "prediction": "",
                    "score": 0.0,
                    "correct": False,
                    "details": str(e)[:100],
                })

        avg_score = sum(scores) / len(scores) if scores else 0.0
        accuracy = sum(1 for s in scores if s >= 0.8) / len(scores) if scores else 0.0
        all_run_results.append({"avg_score": avg_score, "accuracy": accuracy})

        print(f"\n  📊 Results: Avg Score = {avg_score:.4f}, Accuracy = {accuracy:.4f}")

    # Average across runs
    final_score = sum(r["avg_score"] for r in all_run_results) / len(all_run_results)
    final_accuracy = sum(r["accuracy"] for r in all_run_results) / len(all_run_results)

    summary = {
        "dataset": dataset,
        "model": client.model_name,
        "prompt_mode": prompt_mode,
        "topology": describe_topology(dataset),
        "num_samples": len(samples),
        "num_runs": num_runs,
        "avg_score": round(final_score, 4),
        "accuracy": round(final_accuracy, 4),
        "per_run": all_run_results,
    }

    print(f"\n✅ Final: Score={final_score:.4f}, Accuracy={final_accuracy:.4f}")
    return summary


def main():
    parser = argparse.ArgumentParser(
        description="MASS Paper Reproduction: Run optimal topologies with Gemini"
    )
    parser.add_argument(
        "--dataset", type=str, choices=DATASETS,
        help=f"Dataset to evaluate. Choices: {DATASETS}"
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Run all datasets"
    )
    parser.add_argument(
        "--model", type=str, default="pro", choices=["pro", "flash"],
        help="Gemini model preset: pro or flash (default: pro)"
    )
    parser.add_argument(
        "--prompt-mode", type=str, default="optimized",
        choices=["optimized", "default"],
        help="Prompt mode: optimized (Appendix E) or default (Appendix D)"
    )
    parser.add_argument(
        "--num-samples", type=int, default=None,
        help="Number of test samples (default: use paper sizes from Table 2)"
    )
    parser.add_argument(
        "--num-runs", type=int, default=1,
        help="Number of runs for averaging (paper uses 3)"
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed (default: 42)"
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Output JSON file for results"
    )

    args = parser.parse_args()

    # Validate
    if not args.dataset and not args.all:
        parser.error("Either --dataset or --all must be specified")

    if not (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")):
        print("❌ Error: GEMINI_API_KEY or GOOGLE_API_KEY environment variable not set")
        print("  Please set one of them before running this script")
        sys.exit(1)

    banner_client = GeminiClient(model_key=args.model)

    # Determine which datasets to run
    datasets_to_run = DATASETS if args.all else [args.dataset]

    print(f"\n🚀 MASS Paper Reproduction")
    print(f"   Model: {format_model_banner(banner_client)}")
    print(f"   Prompt Mode: {args.prompt_mode}")
    print(f"   Datasets: {datasets_to_run}")
    print(f"   Runs per dataset: {args.num_runs}")

    all_results = []
    for ds in datasets_to_run:
        result = run_dataset(
            dataset=ds,
            model_key=args.model,
            prompt_mode=args.prompt_mode,
            num_samples=args.num_samples,
            num_runs=args.num_runs,
            seed=args.seed,
        )
        all_results.append(result)

    # Print summary table
    print(f"\n{'='*70}")
    print(f"  SUMMARY — {format_model_banner(banner_client)} — {args.prompt_mode} prompts")
    print(f"{'='*70}")
    print(f"  {'Dataset':<15} {'Score':>8} {'Accuracy':>10} {'Topology'}")
    print(f"  {'-'*60}")
    for r in all_results:
        if "error" in r:
            print(f"  {r['dataset']:<15} {'ERROR':>8} {'':>10} {r.get('error', '')[:40]}")
        else:
            print(f"  {r['dataset']:<15} {r['avg_score']:>8.4f} {r['accuracy']:>10.4f} {r['topology'][:40]}")

    avg_all = sum(r.get("avg_score", 0) for r in all_results if "error" not in r)
    count = sum(1 for r in all_results if "error" not in r)
    if count:
        print(f"\n  Average Score: {avg_all / count:.4f}")

    # Save results
    if args.output:
        with open(args.output, "w") as f:
            json.dump(all_results, f, indent=2)
        print(f"\n💾 Results saved to {args.output}")


if __name__ == "__main__":
    main()
