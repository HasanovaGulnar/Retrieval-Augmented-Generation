import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"

CHUNK_SIZE = 180
OVERLAP = 30

if not 0 <= OVERLAP < CHUNK_SIZE:
    raise ValueError("Overlap chunk ölçüsündən kiçik olmalıdır.")

pages = json.loads(
    (PROCESSED / "pages.json").read_text(encoding="utf-8")
)

chunks = []

for page in pages:
    if (
        page["document_id"] == "imtahan_qaydalari"
        and page["page"] == 1
    ):
        continue

    words = page["text"].split()
    start = 0
    chunk_number = 1

    while start < len(words):
        end = min(start + CHUNK_SIZE, len(words))
        chunk_words = words[start:end]

        chunks.append({
            "chunk_id": (
                f"{page['document_id']}"
                f"_p{page['page']:03d}"
                f"_c{chunk_number:03d}"
            ),
            "document_id": page["document_id"],
            "title": page["title"],
            "source_url": page["source_url"],
            "page": page["page"],
            "word_start": start,
            "word_end": end,
            "word_count": len(chunk_words),
            "text": " ".join(chunk_words),
        })

        if end == len(words):
            break

        start = end - OVERLAP
        chunk_number += 1

if not chunks:
    raise RuntimeError("Chunk yaranmadı. pages.json mətnlərini yoxla.")

output = PROCESSED / "chunks.json"
output.write_text(
    json.dumps(chunks, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

print(f"Chunk sayı: {len(chunks)}")
print(f"Ölçü: maksimum {CHUNK_SIZE} söz; overlap: {OVERLAP} söz")
print(f"Ən kiçik chunk: {min(c['word_count'] for c in chunks)} söz")
print(f"Ən böyük chunk: {max(c['word_count'] for c in chunks)} söz")
print("\nİlk chunk:")
print(json.dumps(chunks[0], ensure_ascii=False, indent=2))