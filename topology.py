"""
Topology engine for MASS multi-agent systems.
Constructs the optimal topology for each dataset based on Fig 8 / Table 2.

Construction rule from Appendix B.3:
  Fixed order: [Summarize, Reflect, Debate, Aggregate]
  When multiple dimensions are active, Aggregate controls the number of
  parallel chains, and the chain length is defined by the predefined order.
"""

from building_blocks import (
    Predictor, Reflector, Refiner, Debator, Summarizer,
    Executor, Aggregator, extract_answer,
)
from prompts import get_prompts
from config import TOPOLOGY_CONFIGS


def build_topology(dataset: str, llm_client, prompt_mode: str = "optimized"):
    """
    Build the optimal MASS topology for a given dataset.

    Args:
        dataset: Dataset key (e.g., "math", "drop", "hotpotqa", ...)
        llm_client: GeminiClient instance
        prompt_mode: "optimized" (Appendix E + D fallback) or "default" (Appendix D only)

    Returns:
        A callable topology function: topology(sample) -> answer_str
    """
    cfg = TOPOLOGY_CONFIGS[dataset]
    prompts = get_prompts(dataset, mode=prompt_mode)
    Na, Nr, Nd, Ns, Nt = cfg["Na"], cfg["Nr"], cfg["Nd"], cfg["Ns"], cfg["Nt"]

    # Determine the task family for answer extraction
    task_family = _get_task_family(dataset)

    # Build the single-chain pipeline based on the construction rule:
    # [Summarize, Reflect, Debate, Aggregate]
    def run_single_chain(sample: dict) -> str:
        """Run one chain of the topology and return the final answer."""
        input_kwargs = _prepare_input(sample, dataset)

        # ── Step 0: Predictor ──
        predictor = Predictor(llm_client, prompts["predictor"])
        prediction = predictor.run(**input_kwargs)
        current_answer = extract_answer(prediction, dataset)

        # ── Summarize (if Ns > 0) ──
        if Ns > 0 and "summarizer" in prompts:
            summarizer = Summarizer(llm_client, prompts["summarizer"])
            for _ in range(Ns):
                summary = summarizer.run(**input_kwargs)
                # Update context with summary for subsequent steps
                input_kwargs["context"] = summary

            # Re-predict with summarized context
            prediction = predictor.run(**input_kwargs)
            current_answer = extract_answer(prediction, dataset)

        # ── Reflect (if Nr > 0) ──
        if Nr > 0 and "reflector" in prompts:
            reflector = Reflector(llm_client, prompts["reflector"])
            refiner_template = prompts.get("refiner", prompts.get("reflector"))
            refiner = Refiner(llm_client, refiner_template) if "refiner" in prompts else None

            for r in range(Nr):
                # Execute code if this is a coding task with executor
                exec_result = None
                if Nt and task_family == "coding":
                    executor = Executor()
                    test_code = sample.get("test", "")
                    exec_result = executor.run(current_answer, test_code)

                # Build reflector input
                reflect_kwargs = dict(input_kwargs)
                reflect_kwargs["text"] = prediction
                reflect_kwargs["previous_answer"] = current_answer
                reflect_kwargs["previous_solution"] = current_answer

                if exec_result:
                    reflect_kwargs["traceback"] = (
                        exec_result.get("traceback", "") or exec_result.get("output", "")
                    )
                    # For coding tasks, the reflector acts as the refiner too
                    if exec_result["correctness"] == "True":
                        break  # Early stop if correct

                reflection = reflector.run(**reflect_kwargs)

                # Refine the answer
                if refiner and "refiner" in prompts:
                    refine_kwargs = dict(input_kwargs)
                    refine_kwargs["previous_answer"] = current_answer
                    refine_kwargs["reflection"] = reflection["response"]
                    refine_kwargs["correctness"] = reflection["correctness"]
                    refine_kwargs["thinking"] = ""
                    prediction = refiner.run(**refine_kwargs)
                else:
                    # For coding tasks, the reflector's answer IS the refinement
                    prediction = reflection["response"]

                current_answer = extract_answer(prediction, dataset)

        # ── Debate (if Nd > 0) ──
        if Nd > 0 and "debator" in prompts:
            debator = Debator(llm_client, prompts["debator"])

            for d in range(Nd):
                # Generate multiple predictions for debate
                # In the minimum debate block: 2 Predictors + 1 Debator
                pred2 = Predictor(llm_client, prompts["predictor"])
                second_prediction = pred2.run(**input_kwargs)
                second_answer = extract_answer(second_prediction, dataset)

                # Debator examines both solutions
                debate_kwargs = dict(input_kwargs)
                debate_result = debator.run(
                    solutions=[current_answer, second_answer],
                    **debate_kwargs,
                )
                prediction = debate_result
                current_answer = extract_answer(prediction, dataset)

        return current_answer

    # ── Build the full topology with Aggregate ──
    def topology(sample: dict) -> str:
        """Run the full MASS-optimized topology for a single sample."""
        if Na <= 1:
            # Single chain, no aggregation needed
            return run_single_chain(sample)

        # Run Na parallel chains and aggregate
        predictions = []
        for chain_idx in range(Na):
            answer = run_single_chain(sample)
            predictions.append(answer)

        # Aggregate via majority vote
        return Aggregator.run(predictions)

    return topology


def _get_task_family(dataset: str) -> str:
    """Determine the task family for a dataset."""
    if dataset in ("math", "drop"):
        return "reasoning"
    elif dataset in ("hotpotqa", "musique", "2wikimqa"):
        return "multihop"
    elif dataset in ("mbpp", "humaneval", "livecodebench"):
        return "coding"
    return "unknown"


def _prepare_input(sample: dict, dataset: str) -> dict:
    """Prepare input kwargs for building blocks from a dataset sample."""
    task_family = _get_task_family(dataset)

    if task_family == "reasoning":
        if dataset == "math":
            return {
                "question": sample.get("problem", sample.get("question", "")),
                "answer": "",
                "thinking": "",
                "text": "",
            }
        else:  # DROP
            return {
                "question": sample.get("question", ""),
                "context": sample.get("passage", sample.get("context", "")),
                "thinking": "",
                "text": "",
                "answer": "",
            }

    elif task_family == "multihop":
        return {
            "question": sample.get("question", sample.get("input", "")),
            "context": sample.get("context", sample.get("input", "")),
            "text": "",
            "answer": "",
        }

    elif task_family == "coding":
        if dataset == "livecodebench":
            return {
                "question": sample.get("question", sample.get("question_content", "")),
                "thinking": "",
                "code": "",
                "answer": "",
                "previous_solution": "",
                "traceback": "",
            }
        else:  # MBPP, HumanEval
            return {
                "question": sample.get("text", sample.get("prompt", sample.get("question", ""))),
                "thinking": "",
                "answer": "",
                "previous_solution": "",
                "traceback": "",
            }

    return {"question": str(sample), "answer": "", "thinking": "", "text": ""}


def describe_topology(dataset: str) -> str:
    """Return a human-readable description of the optimal topology for a dataset."""
    cfg = TOPOLOGY_CONFIGS[dataset]
    Na, Nr, Nd, Ns, Nt = cfg["Na"], cfg["Nr"], cfg["Nd"], cfg["Ns"], cfg["Nt"]

    parts = []
    if Ns > 0:
        parts.append(f"Summarize×{Ns}")
    parts.append("Predictor")
    if Nt:
        parts.append("Executor")
    if Nr > 0:
        parts.append(f"Reflect×{Nr}")
    if Nd > 0:
        parts.append(f"Debate×{Nd}")
    chain = " → ".join(parts)

    if Na > 1:
        return f"[{chain}] × {Na} chains → Aggregator (majority vote)"
    return chain
