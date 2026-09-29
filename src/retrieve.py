import argparse
import json
import sys
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import CrossEncoder, SentenceTransformer

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
STORAGE = ROOT / "storage"
RERANKER = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"


class Retriever:
    def __init__(self):
        self.config = json.loads(
            (STORAGE / "config.json").read_text(encoding="utf-8")
        )
        self.chunks = json.loads(
            (STORAGE / "chunks.json").read_text(encoding="utf-8")
        )
        self.index = faiss.read_index(str(STORAGE / "index.faiss"))

        if not self.chunks or self.index.ntotal != len(self.chunks):
            raise ValueError("İndeks və chunk məlumatları uyğun deyil.")

        self.model = SentenceTransformer(
            self.config["embedding_model"], device="cpu"
        )
        self.reranker = None

    def search(self, question, k=3, rerank=True):
        question = question.strip()
        if not question:
            raise ValueError("Sual boş ola bilməz.")
        if k < 1:
            raise ValueError("k ən azı 1 olmalıdır.")

        query = self.config["query_prefix"] + question
        tokens = self.model.tokenizer.encode(
            query, truncation=False
        )
        if len(tokens) > self.model.max_seq_length:
            raise ValueError("Sual embedding modelinin limitini keçir.")

        vector = self.model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        vector = np.ascontiguousarray(vector, dtype=np.float32)

        if vector.shape[1] != self.index.d:
            raise ValueError("Model və indeks ölçüləri uyğun deyil.")

        candidate_count = min(
            max(10, k) if rerank else k,
            len(self.chunks),
        )
        scores, positions = self.index.search(
            vector, candidate_count
        )

        results = [
            {
                **self.chunks[int(position)],
                "score": float(score),
            }
            for score, position in zip(scores[0], positions[0])
            if position >= 0
        ]

        if rerank and results:
            if self.reranker is None:
                print("Reranker yüklənir...", flush=True)
                self.reranker = CrossEncoder(
                    RERANKER, device="cpu", max_length=512
                )

            pairs = [
                [question, chunk["text"]]
                for chunk in results
            ]
            rerank_scores = np.asarray(
                self.reranker.predict(
                    pairs,
                    batch_size=4,
                    show_progress_bar=False,
                )
            ).reshape(-1)

            for chunk, score in zip(results, rerank_scores):
                chunk["rerank_score"] = float(score)

            results.sort(
                key=lambda chunk: chunk["rerank_score"],
                reverse=True,
            )

        return results[:k]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("question")
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--no-rerank", action="store_true")
    args = parser.parse_args()

    retriever = Retriever()
    results = retriever.search(
        args.question,
        k=args.k,
        rerank=not args.no_rerank,
    )

    for rank, chunk in enumerate(results, 1):
        print(f"\nNəticə {rank}: {chunk['chunk_id']}")
        print(f"Vektor oxşarlığı: {chunk['score']:.4f}")
        if "rerank_score" in chunk:
            print(f"Reranker balı: {chunk['rerank_score']:.4f}")
        print(f"Səhifə: {chunk['page']}")
        print(chunk["text"])
        print(chunk["source_url"])


if __name__ == "__main__":
    main()