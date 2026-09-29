"""Evidence spans and section metadata; no question-specific answers."""
import json
import re
from pathlib import Path


def normalize(text):
    return " ".join(text.split())


class SectionMap:
    def __init__(self, path):
        self.pages = {}
        current = {}
        for page in json.loads(Path(path).read_text(encoding="utf-8")):
            doc = page["document_id"]
            raw = page["text"]
            headings = [(0, current.get(doc, ""))]
            for match in re.finditer(
                r"(?m)^\s*(\d+(?:\.\d+)*)\.?(?=\s)\s+([^\n]+)", raw
            ):
                number, title = match.group(1), match.group(2).strip()
                # Numbered subclauses and standalone section titles.
                if "." in number or (title and title[0].isupper()):
                    position = len(normalize(raw[:match.start()]))
                    headings.append((position, number))
                    current[doc] = number
            self.pages[(doc, page["page"])] = (normalize(raw), headings)

    def section(self, chunk, text):
        page, headings = self.pages.get(
            (chunk["document_id"], chunk["page"]), ("", [])
        )
        # Anchor to the chunk first to avoid repeated-text ambiguity.
        anchor = max(page.find(normalize(chunk["text"])), 0)
        position = page.find(normalize(text), anchor)
        if position < 0:
            return ""
        section = ""
        for offset, number in headings:
            if offset <= position:
                section = number
        return section


def requested_section(question):
    match = re.search(
        r"(\d+(?:\.\d+)*)(?:-(?:ci|cı|cu|cü))?\s+bölm", question
    )
    return match.group(1) if match else None


def candidates(chunks, section_map, question):
    requested = requested_section(question)
    result, seen = [], set()
    for chunk in chunks:
        # Preserve abbreviations such as 'və s. texniki'; keep negation.
        parts = re.split(
            r"[•\uf0b7]\s*|(?<=[;!?])\s+|(?<=\.)\s+(?=[A-ZƏÖÜĞÇŞİ-])",
            normalize(chunk["text"]),
        )
        for part in parts:
            part = part.strip()
            if len(part.split()) < 5:
                continue
            section = section_map.section(chunk, part)
            if requested and not (
                section == requested or section.startswith(requested + ".")
            ):
                continue
            key = (chunk["document_id"], section, part)
            if key in seen:
                continue
            seen.add(key)
            result.append({
                "chunk_id": chunk["chunk_id"], "page": chunk["page"],
                "section": section, "text": part,
            })
    return result
