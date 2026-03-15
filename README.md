# MASS Reproduction

This project reproduces the MASS multi-agent evaluation setup with Gemini models. It loads eight benchmarks, builds the paper's dataset-specific topologies, runs inference, and scores the outputs with task-appropriate evaluators.

## Requirements

- Python 3.10+
- A Gemini API key exposed as `GEMINI_API_KEY` or `GOOGLE_API_KEY`

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run one dataset:

```bash
python main.py --dataset math --model pro
```

Run a smaller sample for quick checks:

```bash
python main.py --dataset hotpotqa --model flash --num-samples 5
```

Run all datasets and save results:

```bash
python main.py --all --model pro --num-runs 3 --output results.json
```

## Notes

- Supported datasets: `math`, `drop`, `hotpotqa`, `musique`, `2wikimqa`, `mbpp`, `humaneval`, `livecodebench`
- `--prompt-mode` accepts `optimized` or `default`
- Optional model overrides are available through `GEMINI_MODEL`, `GEMINI_MODEL_PRO`, and `GEMINI_MODEL_FLASH`
- Results are printed to the terminal and can also be written as JSON with `--output`
