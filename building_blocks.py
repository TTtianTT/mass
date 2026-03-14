"""
Building blocks for MASS multi-agent systems.
Each block corresponds to a topology component from Section 2.2:
  - Predictor: generates an answer
  - Reflector: verifies / criticizes a previous answer
  - Refiner: improves answer based on feedback
  - Debator: synthesizes answers from multiple agents
  - Summarizer: extracts relevant context (for long-context tasks)
  - Executor: runs Python code and captures output/traceback
  - Aggregator: majority vote over multiple predictions
"""

import re
import subprocess
import tempfile
import os
from collections import Counter
from string import Template


def _fill_template(template: str, **kwargs) -> str:
    """Fill ${variable} placeholders in a prompt template."""
    # Use a simple approach: replace ${var} patterns
    result = template
    for key, value in kwargs.items():
        result = result.replace(f"${{{key}}}", str(value))
    return result


class Predictor:
    """Generates an answer to a question using a prompt template."""

    def __init__(self, llm_client, prompt_template: str):
        self.llm = llm_client
        self.template = prompt_template

    def run(self, **kwargs) -> str:
        prompt = _fill_template(self.template, **kwargs)
        return self.llm.generate(prompt)


class Reflector:
    """Verifies / criticizes a previous answer and outputs correctness + feedback."""

    def __init__(self, llm_client, prompt_template: str):
        self.llm = llm_client
        self.template = prompt_template

    def run(self, **kwargs) -> dict:
        prompt = _fill_template(self.template, **kwargs)
        response = self.llm.generate(prompt)

        # Parse correctness from response
        correctness = "False"
        if "True" in response:
            correctness = "True"

        return {
            "response": response,
            "correctness": correctness,
            "feedback": response,
        }


class Refiner:
    """Improves an answer based on reflection feedback."""

    def __init__(self, llm_client, prompt_template: str):
        self.llm = llm_client
        self.template = prompt_template

    def run(self, **kwargs) -> str:
        prompt = _fill_template(self.template, **kwargs)
        return self.llm.generate(prompt)


class Debator:
    """Synthesizes answers from multiple agents into an updated answer."""

    def __init__(self, llm_client, prompt_template: str):
        self.llm = llm_client
        self.template = prompt_template

    def run(self, solutions: list, **kwargs) -> str:
        solutions_text = "\n".join(
            f"Agent {i+1}: {sol}" for i, sol in enumerate(solutions)
        )
        prompt = _fill_template(
            self.template,
            **kwargs,
        )
        # Replace the solutions placeholder
        prompt = prompt.replace(
            "the solutions to the question from other agents",
            solutions_text,
        )
        return self.llm.generate(prompt)


class Summarizer:
    """Extracts relevant context information (for long-context tasks)."""

    def __init__(self, llm_client, prompt_template: str):
        self.llm = llm_client
        self.template = prompt_template

    def run(self, **kwargs) -> str:
        prompt = _fill_template(self.template, **kwargs)
        return self.llm.generate(prompt)


class Executor:
    """Runs Python code in a sandboxed subprocess and captures output/traceback."""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def run(self, code: str, test_code: str = "") -> dict:
        """Execute code + optional test_code. Returns dict with output/traceback."""
        full_code = code + "\n" + test_code if test_code else code

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write(full_code)
            tmp_path = f.name

        try:
            result = subprocess.run(
                ["python3", tmp_path],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            output = result.stdout.strip()
            error = result.stderr.strip()

            if result.returncode == 0:
                return {
                    "success": True,
                    "output": output,
                    "traceback": "",
                    "correctness": "True",
                }
            else:
                return {
                    "success": False,
                    "output": output,
                    "traceback": error,
                    "correctness": "False",
                }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "traceback": "TimeoutError: Execution exceeded time limit.",
                "correctness": "False",
            }
        finally:
            os.unlink(tmp_path)


class Aggregator:
    """Majority vote aggregation over multiple predictions."""

    @staticmethod
    def run(predictions: list) -> str:
        """Return the most common prediction (majority vote)."""
        if not predictions:
            return ""

        # Normalize predictions for voting
        normalized = [_normalize_answer(p) for p in predictions]
        counter = Counter(normalized)
        most_common = counter.most_common(1)[0][0]

        # Return the original (non-normalized) prediction that matches
        for pred, norm in zip(predictions, normalized):
            if norm == most_common:
                return pred
        return predictions[0]


def _normalize_answer(text: str) -> str:
    """Normalize answer for majority voting comparison."""
    text = text.strip().lower()
    # Remove common answer prefixes
    for prefix in ["answer:", "the answer is", "final answer:"]:
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
    # Extract from <answer> tags if present
    match = re.search(r"<answer>(.*?)</answer>", text, re.DOTALL)
    if match:
        text = match.group(1).strip()
    return text


def extract_answer(text: str, dataset: str = "") -> str:
    """Extract the final answer from a model response based on dataset type."""
    if not text:
        return ""

    # Try <answer> tags first
    match = re.search(r"<answer>(.*?)</answer>", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # For coding tasks, extract code from markdown blocks
    if dataset in ("mbpp", "humaneval", "livecodebench"):
        code_match = re.search(r"```python\n(.*?)```", text, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        code_match = re.search(r"```\n(.*?)```", text, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()

    # Look for "Answer:" patterns
    lines = text.strip().split("\n")
    for line in reversed(lines):
        line = line.strip()
        if line.lower().startswith("answer:"):
            return line[len("answer:"):].strip()

    # For assertion tasks (LiveCodeBench)
    if dataset == "livecodebench":
        for line in reversed(lines):
            if line.strip().startswith("assert"):
                return line.strip()

    # Fallback: return the last non-empty line
    for line in reversed(lines):
        if line.strip():
            return line.strip()

    return text.strip()
