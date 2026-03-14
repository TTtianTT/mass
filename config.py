"""
Configuration for MASS paper reproduction.
Contains model configs, per-dataset topology configs (from Table 2 / Fig 8),
and experiment settings matching the paper exactly.
"""

import os

# ──────────────────────────────────────────────
# Gemini API
# ──────────────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY", "")
GEMINI_API_VERSION = os.environ.get("GEMINI_API_VERSION", "v1")

MODEL_CONFIGS = {
    "pro": {
        "label": "Gemini 2.5 Pro",
        "candidates": [
            os.environ.get("GEMINI_MODEL_PRO"),
            os.environ.get("GEMINI_MODEL"),
            "gemini-2.5-pro",
        ],
    },
    "flash": {
        "label": "Gemini 2.5 Flash",
        "candidates": [
            os.environ.get("GEMINI_MODEL_FLASH"),
            os.environ.get("GEMINI_MODEL"),
            "gemini-2.5-flash",
            "gemini-2.0-flash",
        ],
    },
}

# Paper settings (Section 4)
TEMPERATURE = 0.7
MAX_OUTPUT_TOKENS = 4096

# ──────────────────────────────────────────────
# Dataset split sizes (Table 2)
# ──────────────────────────────────────────────
DATASET_SPLITS = {
    "math":        {"val": 60,  "test": 100},
    "drop":        {"val": 60,  "test": 200},
    "hotpotqa":    {"val": 50,  "test": 100},
    "musique":     {"val": 50,  "test": 100},
    "2wikimqa":    {"val": 50,  "test": 100},
    "mbpp":        {"val": 60,  "test": 200},
    "humaneval":   {"val": 50,  "test": 100},
    "livecodebench": {"val": 50, "test": 100},
}

# ──────────────────────────────────────────────
# MASS-optimized topologies (Table 2 / Fig 8, Gemini 1.5 Pro)
# Format: {Ns, Na, Nr, Nd, Nt}
#   Ns = rounds of summarization
#   Na = number of parallel agents (aggregate width)
#   Nr = rounds of self-reflection
#   Nd = rounds of debating
#   Nt = use of code executor (0 or 1)
# ──────────────────────────────────────────────
TOPOLOGY_CONFIGS = {
    "math": {
        "search_space": ["aggregate", "reflect", "debate"],
        "Ns": 0, "Na": 9, "Nr": 0, "Nd": 0, "Nt": 0,
    },
    "drop": {
        "search_space": ["aggregate", "reflect", "debate"],
        "Ns": 0, "Na": 5, "Nr": 0, "Nd": 0, "Nt": 0,
    },
    "hotpotqa": {
        "search_space": ["summarize", "aggregate", "reflect", "debate"],
        "Ns": 0, "Na": 5, "Nr": 0, "Nd": 1, "Nt": 0,
    },
    "musique": {
        "search_space": ["summarize", "aggregate", "reflect", "debate"],
        "Ns": 0, "Na": 3, "Nr": 0, "Nd": 2, "Nt": 0,
    },
    "2wikimqa": {
        "search_space": ["summarize", "aggregate", "reflect", "debate"],
        "Ns": 0, "Na": 3, "Nr": 0, "Nd": 1, "Nt": 0,
    },
    "mbpp": {
        "search_space": ["aggregate", "reflect", "debate", "executor"],
        "Ns": 0, "Na": 1, "Nr": 4, "Nd": 0, "Nt": 1,
    },
    "humaneval": {
        "search_space": ["aggregate", "reflect", "debate", "executor"],
        "Ns": 0, "Na": 1, "Nr": 3, "Nd": 0, "Nt": 1,
    },
    "livecodebench": {
        "search_space": ["aggregate", "reflect", "debate", "executor"],
        "Ns": 0, "Na": 3, "Nr": 1, "Nd": 1, "Nt": 1,
    },
}
