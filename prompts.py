"""
Prompt templates from the MASS paper.
- Appendix D: Default prompt templates for each building block per dataset.
- Appendix E: Best prompts discovered by MASS (shown for selected datasets).

All prompts are reproduced 1:1 from the paper.
Use `get_prompts(dataset, mode)` to retrieve the right set.
  mode="default"  → Appendix D templates
  mode="optimized" → Appendix E best-found prompts (falls back to D if not available)
"""

# ═══════════════════════════════════════════════
# APPENDIX D — Default Prompt Templates
# ═══════════════════════════════════════════════

APPENDIX_D = {}

# ── MATH ──────────────────────────────────────
APPENDIX_D["math"] = {
    "predictor": (
        "Let's think step by step.\n"
        "---\n"
        "Question: ${question}\n"
        "Reasoning: Let's think step by step in order to ${produce the answer}. We ...\n"
        "Answer: ${answer}"
    ),
    "reflector": (
        "Please review the answer above and criticize on where might be wrong. "
        "If you are absolutely sure it is correct, output 'True' in 'correctness'.\n"
        "\n"
        "---\n"
        "Question: ${question}\n"
        "Text: ${text}\n"
        "Reasoning: Let's think step by step in order to ${produce the correctness}. We ...\n"
        "Feedback: ${feedback}\n"
        "Correctness: True/False indicating if answer is correct given the question."
    ),
    "refiner": (
        "Given previous attempts and feedback, carefully consider where you could go wrong "
        "in your latest attempt. Using insights from previous attempts, try to solve the task better. "
        "Show your final answer bracketed between <answer> and </answer> at the end.\n"
        "\n"
        "---\n"
        "Question: ${question}\n"
        "Previous answer: ${previous_answer}\n"
        "Reflection: ${reflection}\n"
        "Correctness: ${correctness}\n"
        "Thinking: ${thinking}\n"
        "Answer: ${answer}"
    ),
    "debator": (
        "These are the solutions to the question from other agents. "
        "Examine the solutions from other agents in your rationale, "
        "finish by giving an updated answer. "
        "Show your final answer bracketed between <answer> and </answer> at the end.\n"
        "\n"
        "---\n"
        "Question: ${question}\n"
        "Solutions: the solutions to the question from other agents\n"
        "Reasoning: Let's think step by step in order to ${Examine the solutions from other agents}. We ...\n"
        "Answer: The updated answer for the question. Do not repeat Answer:"
    ),
}

# ── DROP ──────────────────────────────────────
APPENDIX_D["drop"] = {
    "predictor": (
        "Please think step by step and then solve the task. # Your Task:\n"
        "Please answer the following question based on the given context.\n"
        "---\n"
        "Question: ${question}\n"
        "Context: ${context}\n"
        "Thinking: ${thinking}\n"
        "Answer: Directly answer the question. Keep it very concise."
    ),
    "reflector": (
        "Verify that the answer is based on the provided context. "
        "Give your reflection in the rationale.\n"
        "\n"
        "---\n"
        "Question: ${question}\n"
        "Context: ${context}\n"
        "Text: ${text}\n"
        "Reasoning: Let's think step by step in order to ${produce the correctness}. We ...\n"
        "Correctness: True/False indicating if answer is correct given the observations and question."
    ),
    "refiner": (
        "Please think step by step and then solve the task. # Your Task:\n"
        "Based on the reflection, correctness of the previous answer, "
        "and the context again, give an updated answer.\n"
        "\n"
        "---\n"
        "Question: ${question}\n"
        "Context: ${context}\n"
        "Previous answer: ${previous_answer}\n"
        "Reflection: ${reflection}\n"
        "Correctness: ${correctness}\n"
        "Thinking: ${thinking}\n"
        "Answer: Directly answer the question. Keep it very concise."
    ),
    "debator": (
        "These are the solutions to the question from other agents. "
        "Based on the context, examine the solutions from other agents in your rationale, "
        "finish by giving an updated answer.\n"
        "\n"
        "---\n"
        "Question: ${question}\n"
        "Context: ${context}\n"
        "Solutions: the solutions to the question from other agents\n"
        "Reasoning: Let's think step by step in order to ${Examine the solutions from other agents}. We ...\n"
        "Answer: The updated answer for the question. Do not repeat Answer:"
    ),
}

# ── HotpotQA / MuSiQue / 2WikiMQA (shared templates) ───
_multihop_template = {
    "predictor": (
        "Answer the question with information based on the context. "
        "Only return the answer as your output.\n"
        "---\n"
        "Question: ${question}\n"
        "Context: ${context}\n"
        "Answer: Only give me the answer. Do not output any other words."
    ),
    "summarizer": (
        "Based on the question, retrieve relevant information from context "
        "that is ONLY helpful in answering the question. "
        "Include all key information. Do not repeat context.\n"
        "---\n"
        "Question: ${question}\n"
        "Context: ${context}\n"
        "Summary: Only generate the summary. Start with Summary:"
    ),
    "reflector": (
        "Verify that the answer is based on the provided context.\n"
        "\n"
        "---\n"
        "Question: ${question}\n"
        "Context: ${context}\n"
        "Text: ${text}\n"
        "Reasoning: Let's think step by step in order to ${produce the correctness}. We ...\n"
        "Correctness: True/False indicating if answer is correct given the observations and question."
    ),
    "debator": (
        "These are the solutions to the question from other agents. "
        "Based on the context, examine the solutions from other agents in your rationale, "
        "finish by giving an updated answer.\n"
        "\n"
        "---\n"
        "Question: ${question}\n"
        "Context: ${context}\n"
        "Solutions: the solutions to the question from other agents\n"
        "Reasoning: Let's think step by step in order to ${Examine the solutions from other agents}. We ...\n"
        "Answer: The updated answer for the question. Do not repeat Answer:"
    ),
}
APPENDIX_D["hotpotqa"] = dict(_multihop_template)
APPENDIX_D["musique"] = dict(_multihop_template)
APPENDIX_D["2wikimqa"] = dict(_multihop_template)

# ── MBPP ──────────────────────────────────────
APPENDIX_D["mbpp"] = {
    "predictor": (
        "Let's think step by step. "
        "Provide a complete and correct code implementation in python.\n"
        "---\n"
        "Question: ${question}\n"
        "Thinking: ${thinking}\n"
        "Answer: Only the code implementation. Do not include example usage or explainations."
    ),
    "reflector": (
        "Please determine the correctness of the solution in passing all test cases. "
        "If it fails, based on the error message and trackback, think step by step, "
        "carefully propose an updated solution in the answer output with a correct "
        "code implementation in python.\n"
        "\n"
        "---\n"
        "Question: ${question}\n"
        "Previous solution: ${previous_solution}\n"
        "Traceback: It contains the test cases, execution results, and ground truth. "
        "If there is an error, the relevant traceback is given.\n"
        "Correctness: 'True/False' based on the correctness of executive feedback. "
        "If there is an error message, output 'False'\n"
        "Thinking: ${thinking}\n"
        "Answer: ${answer}"
    ),
    "debator": (
        "These are the solutions to the question from other agents. "
        "Examine the solutions from other agents in your rationale, "
        "finish by giving an updated answer. "
        "Let's think step by step. "
        "Provide a complete and correct code implementation in python.\n"
        "\n"
        "---\n"
        "Question: ${question}\n"
        "Solutions: the solutions to the question from other agents\n"
        "Reasoning: Let's think step by step in order to ${Examine the solutions from other agents}. We ...\n"
        "Answer: ${answer}"
    ),
}

# ── HumanEval ─────────────────────────────────
APPENDIX_D["humaneval"] = {
    "predictor": (
        "Let's think step by step. "
        "Provide a complete and correct code implementation in python.\n"
        "---\n"
        "Question: ${question}\n"
        "Thinking: ${thinking}\n"
        "Answer: ${answer}"
    ),
    "reflector": (
        "Please determine the correctness of the solution in passing all test cases. "
        "If it fails, based on the error message and trackback, think step by step, "
        "carefully propose an updated solution in the answer output with a correct "
        "code implementation in python.\n"
        "\n"
        "---\n"
        "Question: ${question}\n"
        "Previous solution: ${previous_solution}\n"
        "Traceback: ${traceback}\n"
        "Thinking: ${thinking}\n"
        "Answer: ${answer}"
    ),
    "debator": (
        "These are the solutions to the question from other agents. "
        "Examine the solutions from other agents in your rationale, "
        "finish by giving an updated answer. "
        "Let's think step by step. "
        "Provide a complete and correct code implementation in python.\n"
        "\n"
        "---\n"
        "Question: ${question}\n"
        "Solutions: the solutions to the question from other agents\n"
        "Reasoning: Let's think step by step in order to ${Examine the solutions from other agents}. We ...\n"
        "Answer: ${answer}"
    ),
}

# ── LiveCodeBench ─────────────────────────────
APPENDIX_D["livecodebench"] = {
    "predictor": (
        "You are a helpful programming assistant and an expert Python programmer. "
        "The user has written a input for the testcase. Think step by step. "
        "You will generate the code based on the problem requirepement. "
        "You will calculate the output of the testcase and write the whole assertion "
        "statement in the markdown code block with the correct output.\n"
        "---\n"
        "Question: ${question}\n"
        "Thinking: ${thinking}\n"
        "Code: ${code}\n"
        "Answer: complete the testcase with assertion."
    ),
    "reflector": (
        "If there is an executive output in the traceback, "
        "parse the output into an assertion in the answer given the executive output.\n"
        "\n"
        "---\n"
        "Question: ${question}\n"
        "Previous solution: ${previous_solution}\n"
        "Traceback: It contains the test cases, execution results, and ground truth. "
        "If there is an error, the relevant traceback is given.\n"
        "Correctness: 'True/False' based on the correctness of executive feedback. "
        "If there is an error message, output 'False'\n"
        "Thinking: ${thinking}\n"
        "Answer: ${answer}"
    ),
    "debator": (
        "These are the solutions to the question from other agents. "
        "Examine the solutions from other agents in your rationale, "
        "finish by giving an updated answer.\n"
        "\n"
        "---\n"
        "Question: ${question}\n"
        "Solutions: the solutions to the question from other agents\n"
        "Reasoning: Let's think step by step in order to ${Examine the solutions from other agents}. We ...\n"
        "Answer: assert ${function(input)} == {executive_output}"
    ),
}


# ═══════════════════════════════════════════════
# APPENDIX E — Best Prompts Discovered by MASS
# (Only shown for selected datasets/agents in the paper)
# ═══════════════════════════════════════════════

APPENDIX_E = {}

# ── MATH (Predictor) ──────────────────────────
APPENDIX_E["math"] = {
    "predictor": (
        "Let's think step by step to solve the given problem. "
        "Clearly explain your reasoning process, showing all intermediate calculations "
        "and justifications.  Express your final answer as a single numerical value or "
        "simplified expression enclosed within <answer></answer> tags.  "
        "Avoid extraneous text or explanations outside of the core reasoning and final answer.\n"
        "\n"
        "---\n"
        "\n"
        "Follow the following format.\n"
        "\n"
        "Question: ${question}\n"
        "Reasoning: Let's think step by step in order to ${produce the answer}. We ...\n"
        "Answer: ${answer}\n"
        "\n"
        "---\n"
        "\n"
        "Question: What is the average of the two smallest positive integer solutions "
        "to the congruence $$14u \\equiv 46 \\pmod{100}~?$$\n"
        "Reasoning: Let's think step by step in order to find the average of the two "
        "smallest positive integer solutions to the congruence $14u \\equiv 46 \\pmod{100}$. "
        "We are looking for solutions to $14u \\equiv 46 \\pmod{100}$. We can divide the "
        "congruence by 2 to get $7u \\equiv 23 \\pmod{50}$. We want to find the inverse of "
        "7 modulo 50. We use the Euclidean Algorithm: \\begin{align*} 50 &= 7 \\cdot 7 + 1 "
        "\\\\ 1 &= 50 - 7 \\cdot 7 \\end{align*} Thus, $7(-7) \\equiv 1 \\pmod{50}$, so "
        "$7^{-1} \\equiv -7 \\equiv 43 \\pmod{50}$. Multiplying $7u \\equiv 23 \\pmod{50}$ "
        "by 43 gives $u \\equiv 23 \\cdot 43 \\pmod{50}$. $23 \\cdot 43 = 989 = 50 \\cdot 19 + 39$, "
        "so $23 \\cdot 43 \\equiv 39 \\pmod{50}$. Therefore, $u \\equiv 39 \\pmod{50}$. "
        "The two smallest positive integer solutions are $u = 39$ and $u = 39+50=89$. "
        "The average of these two solutions is $\\frac{39+89}{2} = \\frac{128}{2} = 64$.\n"
        "Answer: 64\n"
        "\n"
        "---"
    ),
}

# ── DROP (Predictor) ──────────────────────────
APPENDIX_E["drop"] = {
    "predictor": (
        "This dataset is designed for extractive question answering, focusing on retrieving "
        "concise, factual answers from short texts. Many questions involve extracting numerical "
        "information and performing simple calculations, suggesting applications in areas like "
        "sports analytics or financial data analysis. However, the dataset's Western cultural bias "
        "and lack of complex reasoning questions limit its generalizability and real-world applicability.\n"
        "\n"
        "TASK DEMO(S):\n"
        "<example_1>\n"
        "Question: How many more points did the Spurs win by in Game 4 against the Mavericks?\n"
        "\n"
        "Context:\n"
        'The Mavericks finished 49-33, one game ahead of Phoenix for the eighth and final playoff spot, '
        'which meant that they would once again have to face their in-state rivals, the San Antonio Spurs, '
        'who were the top seed in the Western Conference with a 62-20 record. In Game 1 in San Antonio, '
        'Dallas had an 81-71 lead in the fourth quarter, but the Spurs rallied back and took Game 1, 85-90. '
        'However, the Mavs forced 22 turnovers in Game 2 to rout the Spurs 113-92, splitting the first two games '
        'before the series went to Dallas. In Game 3, Manu Gin\u00f3bili hit a shot that put the Spurs up 108-106 '
        'with 1.7 seconds left, but a buzzer-beater by Vince Carter gave the Mavs the victory, putting them '
        'up 2-1 in the series. The Spurs took Game 4 in Dallas 93-89 despite a late Dallas comeback after '
        'the Spurs at one point had a 20-point lead and later won Game 5 at home, 109-103, giving them a 3-2 '
        'series lead. The Mavs avoided elimination in Game 6 at home by rallying in the fourth quarter, '
        'winning 111-113. Game 7 was on the Spurs home court, and the Spurs beat the Mavericks 119-96, '
        'putting an end to the Mavericks season.\n'
        "\n"
        "Thinking:\n"
        "The Spurs scored 93 points in Game 4. The Mavericks scored 89 points in Game 4.  "
        "The difference is 93 - 89 = 4.\n"
        "Answer: 4\n"
        "\n"
        "\n"
        "BASIC INSTRUCTION:\n"
        "```\n"
        "You are a highly specialized AI tasked with extracting critical numerical information "
        "for an urgent news report.  A live broadcast is relying on your accuracy and speed. "
        "Think step-by-step, focusing on the numerical information provided in the context.  "
        "Then, answer the question concisely with the extracted numerical answer. "
        "Failure to provide the correct numerical information will result in the broadcast being interrupted.\n"
        "\n"
        "Question: {question}\n"
        "Context: {context}\n"
        "```\n"
        "\n"
        "TIP: Keep the instruction clear and concise.\n"
        "\n"
        "PROPOSED INSTRUCTION:\n"
        "\n"
        "```\n"
        "Extract the numerical answer to the following question. Show your reasoning by "
        "identifying the relevant numbers from the provided context and performing any "
        "necessary calculations.  Respond with only the final numerical answer.\n"
        "\n"
        "Question: {question}\n"
        "Context: {context}\n"
        "```"
    ),
}

# ── HotpotQA (Predictor + Debator) ────────────
APPENDIX_E["hotpotqa"] = {
    "predictor": (
        "This multi-passage question answering dataset focuses on complex questions requiring "
        "synthesis of information from multiple Wikipedia-like sources, often involving named "
        "entities and temporal reasoning. It emphasizes integrating information, handling ambiguity, "
        "and leveraging real-world knowledge, posing a significant challenge for models relying "
        "solely on provided text. The dataset appears well-suited for evaluating advanced language "
        "models' reasoning abilities across diverse domains and varying complexity levels.\n"
        "\n"
        "TASK DEMO(S):\n"
        'Question: The actor that plays Phileas Fogg in "Around the World in 80 Days", '
        "co-starred with Gary Cooper in a 1939 Goldwyn Productions film based on a novel "
        "by what author?\n"
        "Context: Provided in prompt\n"
        "Answer: Charles L. Clifford\n"
        "\n"
        "\n"
        "BASIC INSTRUCTION: From the provided text, extract the answer to the question.  "
        "Output *only* the answer.\n"
        "\n"
        "TIP: Keep the instruction clear and concise.  Emphasize reliance *only* on the provided text.\n"
        "\n"
        "PROPOSED INSTRUCTION: Answer the question using only the provided context.  "
        "Do not use external knowledge.\n"
        "\n"
        "---\n"
        "<example_1>"
    ),
    "debator": (
        "This multi-passage question answering dataset focuses on complex questions requiring "
        "synthesis of information from multiple Wikipedia-like sources, often involving named "
        "entities and temporal reasoning. It emphasizes integrating information, handling ambiguity, "
        "and leveraging real-world knowledge, posing a significant challenge for models relying "
        "solely on provided text. The dataset appears well-suited for evaluating advanced language "
        "models' reasoning abilities across diverse domains and varying complexity levels.\n"
        "\n"
        "TASK DEMO(S):\n"
        "Provided above.\n"
        "\n"
        "BASIC INSTRUCTION: These are the solutions to the question from other agents. "
        "Based on the context, examine the solutions from other agents in your rationale, "
        "finish by giving an updated answer.\n"
        "\n"
        "TIP: Don't be afraid to be creative when creating the new instruction!\n"
        "\n"
        "PROPOSED INSTRUCTION: You are an expert fact-checker for a major publication. "
        "Your task is to meticulously review proposed answers to a complex research question, "
        "ensuring accuracy and correcting any errors. You are provided with the original question, "
        "multiple context passages from credible sources, and several proposed answers from "
        "different research assistants. Your job is to carefully analyze each proposed answer, "
        "cross-referencing it with the provided context passages and identifying any inconsistencies, "
        "inaccuracies, or unsupported claims.\n"
        "\n"
        "**Question:** [Insert Question Here]\n"
        "\n"
        "**Context Passages:**\n"
        "[Insert Passages Here]\n"
        "\n"
        "**Proposed Answers:**\n"
        "* Assistant 1: [Insert Assistant 1's Answer]\n"
        "* Assistant 2: [Insert Assistant 2's Answer]\n"
        "...\n"
        "* Assistant N: [Insert Assistant N's Answer]\n"
        "\n"
        "\n"
        "**Instructions:**\n"
        "\n"
        '1. **Fact-Check & Analyze:** Evaluate each proposed answer individually.  For each answer:\n'
        '* **Verdict:**  Indicate whether the answer is "Correct," "Incorrect," '
        '"Partially Correct," or "Not Supported by Context."\n'
        "* **Evidence:** Provide specific quotes and passage numbers from the context to support "
        "your verdict. Explain how the evidence supports or refutes the proposed answer.  "
        "Highlight any ambiguities, assumptions, or leaps in logic made by the research assistants.\n"
        "* **Corrections/Improvements (if applicable):**  Suggest specific corrections or "
        "improvements to partially correct or incorrect answers. Explain how these changes "
        "align with the context.\n"
        "\n"
        "2. **Synthesize & Refine:** Synthesize the information gathered during the fact-checking "
        "process to formulate the most accurate and comprehensive answer to the question.  "
        "This may involve:\n"
        "* Selecting the most accurate proposed answer.\n"
        "* Combining elements from multiple proposed answers.\n"
        "* Developing a completely new answer based on your analysis of the evidence.\n"
        "\n"
        "3. **Final Answer:** Clearly state your final, verified answer to the question.\n"
        "\n"
        '4. **Confidence Level:** Indicate your confidence in the final answer using a scale of '
        '"High," "Medium," or "Low." Briefly explain the factors influencing your confidence level.\n'
        "\n"
        "\n"
        "This revised instruction emphasizes a more rigorous fact-checking process, encouraging "
        "the LM to critically evaluate each proposed answer and provide detailed justifications "
        "for its assessments.  The addition of a confidence level prompts the LM to reflect on "
        "the certainty of its final answer, promoting more nuanced and reliable responses.  "
        'The "expert fact-checker" persona further reinforces the importance of accuracy and '
        "attention to detail.\n"
        "\n"
        "---\n"
        "<example_1>\n"
        "<example_2>"
    ),
}

# ── MBPP (Predictor + Reflector) ──────────────
APPENDIX_E["mbpp"] = {
    "predictor": (
        "You are a highly skilled Python programmer tasked with generating a correct and efficient "
        "Python function based on the given natural language problem description.  Think step-by-step, "
        "outlining your reasoning process before presenting the code solution.  Your response should "
        "adhere to the following structure:\n"
        "\n"
        "**Thinking:**  Provide a clear and concise breakdown of your thought process, including the "
        "steps you'll take to solve the problem.  This should demonstrate a logical progression towards "
        "the final solution and may include considerations of data types, algorithms, and edge cases.  "
        "For example:\n"
        "\n"
        "1. Identify the input data type and expected output.\n"
        "2. Determine the core logic or algorithm required.\n"
        "3. Consider potential edge cases or special scenarios.\n"
        "4. Outline the steps for implementing the solution in Python.\n"
        "\n"
        "**Answer:**  Present your complete and correct Python code implementation within a code block "
        "(using triple backticks). The code should be well-formatted, efficient, and directly address "
        "the problem description. Ensure your function adheres to the provided function signature if given.  "
        "For example:\n"
        "\n"
        "```python\n"
        "def function_name(input_arguments):\n"
        "# Code implementation here\n"
        "# ...\n"
        "return output\n"
        "```\n"
        "\n"
        "Focus on producing functional code that accurately solves the problem. Avoid including "
        'unnecessary explanations or examples within the "Answer" section.  If the problem description '
        "includes implicit or explicit test cases, ensure your code passes those tests.  Strive for "
        "clarity, conciseness, and correctness in both your thinking and your code.\n"
        "\n"
        "---\n"
        "<example_1>\n"
        "<example_2>\n"
        "<example_3>"
    ),
    "reflector": (
        "This dataset is designed for Python code generation, translating natural language problem "
        "descriptions into simple functions and their corresponding test cases. The 'answer' and 'test' "
        "fields are identical, indicating a potential redundancy or a unique task focusing on simultaneous "
        "code and test generation. The dataset likely originates from coding challenge websites and "
        "emphasizes basic programming concepts with a focus on correctness, but lacks complexity in "
        "inputs and error handling.\n"
        "\n"
        "TASK DEMO(S):\n"
        "Question: Write a function that takes in two numbers and returns a tuple with the second number "
        "and then the first number.\n"
        "\n"
        "def swap_numbers(a,b):\n"
        "Previous Solution: def swap_numbers(a,b):\n"
        "    return (b, a)\n"
        "\n"
        "Traceback: Test case: print(swap_numbers(10,20))\n"
        "Output: (20, 10)\n"
        "Ground Truth: (20,10)\n"
        "Correctness: True\n"
        "Thinking: The provided solution correctly swaps the order of the two input numbers and returns "
        "them as a tuple. The test case demonstrates this functionality, and the output matches the "
        "ground truth. Therefore, no changes are required.\n"
        "Answer: ```python\n"
        "def swap_numbers(a,b):\n"
        "    return (b, a)\n"
        "```\n"
        "<example_2>\n"
        "<example_3>\n"
        "\n"
        "\n"
        "BASIC INSTRUCTION: Please determine the correctness of the solution in passing all test cases. "
        "If it fails, based on the error message and trackback, think step by step, carefully propose "
        "an updated solution in the answer output with a correct code implementation in python.\n"
        "\n"
        "TIP: The instruction should include a high stakes scenario in which the LM must solve the task!\n"
        "\n"
        "PROPOSED INSTRUCTION:\n"
        "\n"
        "You are an automated code reviewer for a mission-critical satellite control system.  "
        "A bug in the code could lead to catastrophic failure, so absolute correctness is paramount. "
        "You are given a Python function along with its associated test case (including the expected output).  "
        "Analyze the provided\n"
        "\n"
        "<example_1>\n"
        "<example_2>"
    ),
}


# ═══════════════════════════════════════════════
# Public API
# ═══════════════════════════════════════════════

def get_prompts(dataset: str, mode: str = "optimized") -> dict:
    """
    Retrieve prompt templates for a given dataset.

    Args:
        dataset: One of the 8 dataset keys (e.g., "math", "drop", "hotpotqa", ...).
        mode: "optimized" for Appendix E best-found prompts (with fallback to D),
              "default" for Appendix D templates only.

    Returns:
        Dict mapping agent type → prompt template string.
    """
    dataset = dataset.lower()
    default = APPENDIX_D.get(dataset, {})

    if mode == "default":
        return dict(default)

    # "optimized" mode: overlay Appendix E on top of D
    optimized = APPENDIX_E.get(dataset, {})
    merged = dict(default)
    merged.update(optimized)  # E overrides D where available
    return merged
