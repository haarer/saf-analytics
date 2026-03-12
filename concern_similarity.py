#!/usr/bin/env python3
"""
concern_similarity_llm_gpu.py
-----------------------------
Compute cosine similarity between concern names using a pre‑trained
sentence‑transformer on the GPU (if available).
"""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# --------------------------------------------------------------------------- #
def load_names(json_path: Path) -> pd.Series:
    with json_path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    return pd.Series([item.get("Name", "") for item in data])

def embed_texts(texts, model_name="all-MiniLM-L6-v2"):
    # Detect GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    # Load the model once, move to device
    model = SentenceTransformer(model_name, device=device)
    return model.encode(texts, convert_to_numpy=True)

def report_similar_pairs(names, sims, threshold=0.85):
    n = len(names)
    for i in range(n):
        for j in range(i+1, n):
            if sims[i, j] >= threshold:
                print(f"[{sims[i, j]:.3f}] \"{names[i]}\" <=> \"{names[j]}\"")

# --------------------------------------------------------------------------- #
def main():
    parser = argparse.ArgumentParser(
        description="Cosine similarity of concern names using LLM embeddings (GPU‑aware)"
    )
    parser.add_argument("json_file", type=Path, help="Path to concerns.json")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.85,
        help="Similarity threshold (default 0.85)",
    )
    parser.add_argument(
        "--model",
        type=str,
#        default="all-MiniLM-L6-v2",
        default="all-roberta-large-v1",
        help="Sentence‑Transformers model name or path",
    )
    args = parser.parse_args()

    names = load_names(args.json_file)
    if len(names) < 2:
        print("Need at least two concerns.")
        return

    embeddings = embed_texts(names.tolist(), args.model)
    sims = cosine_similarity(embeddings)
    report_similar_pairs(names, sims, args.threshold)

if __name__ == "__main__":
    main()
