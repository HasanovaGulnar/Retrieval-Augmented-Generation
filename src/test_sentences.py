import json
import re
import sys
from pathlib import Path

import numpy as np
from sentence_transformers import CrossEncoder
from retrieve import Retriever, RERANKER

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
tests = json.loads(
    (ROOT / "evaluation" / "retrieval_results.json")
    .read_text(encoding="utf-8")
)["results"]

retriever = Retriever()
ranker = CrossEncoder(RERANKER, device="cpu", max_length=512)

# Eyni ümumi üsulu ilk 5 suala tətbiq edirik.
for test in tests[:5]:
    question = test["question"]
    chunks = retriever.search(question, k=10, rerank=False)

    candidates = []
    seen = set()

    for chunk in chunks:
        text = " ".join(chunk["text"].split())
        sentences = re.split(r"(?<=[.!?;])\s+|[•]\s*", text)

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence.split()) < 5 or sentence in seen:
                continue
            seen.add(sentence)
            candidates.append((chunk["chunk_id"], sentence))

    scores = np.asarray(
        ranker.predict(
            [[question, sentence] for _, sentence in candidates],
            batch_size=4,
            show_progress_bar=False,
        )
    ).reshape(-1)

    order = np.argsort(-scores)[:3]

    print(f"\nSUAL: {question}", flush=True)
    for position, index in enumerate(order, 1):
        chunk_id, sentence = candidates[int(index)]
        print(f"{position}. [{chunk_id}] {sentence}", flush=True)