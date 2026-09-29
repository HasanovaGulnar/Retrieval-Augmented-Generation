import hashlib
import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parent.parent
CHUNKS_PATH = ROOT / "data" / "processed" / "chunks.json"
STORAGE = ROOT / "storage"
MODEL_NAME = "intfloat/multilingual-e5-small"


def main():
    chunks_bytes = CHUNKS_PATH.read_bytes()
    chunks = json.loads(chunks_bytes.decode("utf-8"))

    if not chunks:
        raise ValueError("chunks.json boşdur.")

    print("Embedding modeli yüklənir...")
    model = SentenceTransformer(MODEL_NAME, device="cpu")

    # E5 sənəd hissələri üçün bu prefiksi tələb edir.
    texts = ["passage: " + chunk["text"] for chunk in chunks]

    # Söz sayı token sayı deyil. Mətnin səssizcə kəsilməsinə yol vermirik.
    token_counts = [
        len(model.tokenizer.encode(text, truncation=False))
        for text in texts
    ]

    oversized = [
        chunks[i]["chunk_id"]
        for i, count in enumerate(token_counts)
        if count > model.max_seq_length
    ]

    print(f"Ən uzun chunk: {max(token_counts)} token")
    print(f"Modelin limiti: {model.max_seq_length} token")

    if oversized:
        raise ValueError(
            f"{len(oversized)} chunk modelin token limitini keçir. "
            "chunk_text.py faylında CHUNK_SIZE = 100 et, "
            "chunking-i yenidən işə sal və indeks yaratmağı təkrarla. "
            f"İlk nümunələr: {oversized[:3]}"
        )

    print(f"{len(chunks)} chunk üçün embedding yaradılır...")
    vectors = model.encode(
        texts,
        batch_size=8,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=True,
    )
    vectors = np.ascontiguousarray(vectors, dtype=np.float32)

    # Normallaşdırılmış vektorlarda inner product cosine similarity-dir.
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)

    STORAGE.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(STORAGE / "index.faiss"))

    # FAISS nəticəsinin sıra nömrəsini chunk-a bağlamaq üçün saxlayırıq.
    (STORAGE / "chunks.json").write_text(
        json.dumps(chunks, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    config = {
        "embedding_model": MODEL_NAME,
        "dimension": int(vectors.shape[1]),
        "chunk_count": len(chunks),
        "normalize_embeddings": True,
        "document_prefix": "passage: ",
        "query_prefix": "query: ",
        "similarity": "cosine",
        "chunks_sha256": hashlib.sha256(chunks_bytes).hexdigest(),
    }
    (STORAGE / "config.json").write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Yazılmış indeksi yenidən açaraq saxlanmanı yoxlayırıq.
    saved_index = faiss.read_index(str(STORAGE / "index.faiss"))
    if saved_index.ntotal != len(chunks):
        raise RuntimeError("Saxlanmış indeksin ölçüsü uyğun gəlmir.")

    print(f"\nSaxlanmış vektor sayı: {saved_index.ntotal}")
    print(f"Vektor ölçüsü: {saved_index.d}")
    print("İndeks diskə yazıldı və yenidən oxunması yoxlanıldı.")


if __name__ == "__main__":
    main()