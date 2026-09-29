import json
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUTPUT = ROOT / "data" / "processed"
OUTPUT.mkdir(parents=True, exist_ok=True)

# utf-8-sig PowerShell-in əlavə edə bildiyi BOM işarəsini də oxuyur.
metadata = json.loads(
    (RAW / "imtahan_qaydalari.metadata.json").read_text(
        encoding="utf-8-sig"
    )
)

reader = PdfReader(RAW / "imtahan_qaydalari.pdf")
pages = []
empty_pages = []

for page_number, page in enumerate(reader.pages, start=1):
    text = (page.extract_text() or "").strip()

    if not text:
        empty_pages.append(page_number)

    pages.append({
        "document_id": metadata["document_id"],
        "title": metadata["title"],
        "source_url": metadata["source_url"],
        "page": page_number,
        "text": text,
    })

if not any(page["text"] for page in pages):
    raise RuntimeError(
        "PDF-dən mətn çıxmadı. Sənədə OCR tətbiq etmək lazım ola bilər."
    )

# Sonrakı mərhələlər üçün strukturlaşdırılmış məlumat.
(OUTPUT / "pages.json").write_text(
    json.dumps(pages, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

# Özümüzün oxuyub yoxlaması üçün mətn faylı.
preview = "\n\n".join(
    f"--- Səhifə {page['page']} ---\n{page['text']}"
    for page in pages
)

(OUTPUT / "preview.txt").write_text(preview, encoding="utf-8")

print(f"Səhifə sayı: {len(pages)}")
print(f"Çıxarılan simvol sayı: {sum(len(p['text']) for p in pages)}")
print("Nəticələr: data/processed/pages.json və preview.txt")

if empty_pages:
    print(f"Diqqət: bu səhifələrdən mətn çıxmadı: {empty_pages}")