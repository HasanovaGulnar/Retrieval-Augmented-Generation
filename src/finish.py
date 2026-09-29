"""Render real saved results; never invent scores or overwrite manual reviews."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "evaluation"

def read(name):
    return json.loads((OUT/name).read_text(encoding="utf-8"))

def cell(value):
    return str(value).replace("|", "&#124;").replace("\n", "<br>")

def render_report():
    retrieval=read("retrieval_results.json")
    grounding=read("grounding_results.json")
    oos=read("out_of_scope_results.json")
    disabled=read("retrieval_disabled_results.json")
    lines=["# Retrieval-Augmented Generation: evaluation", "",
        f"Retrieval Hit-rate@{retrieval['k']}: {retrieval['hit_rate']:.0%}", "",
        "## Actual model outputs", "",
        "| Question | With retrieval | LLM alone |", "|---|---|---|"]
    for row in grounding:
        lines.append("| "+" | ".join(cell(x) for x in [row["question"],
            row["rag"].get("answer",row["rag"].get("error")),
            row["baseline"].get("answer",row["baseline"].get("error"))])+" |")
    lines += ["", "## Out-of-scope checks", ""]
    for row in oos:
        lines.append(f"- {row['question']}: declined={row['declined']}")
    lines += ["", "## Same-prompt retrieval-disabled test", "",
        f"Changed answers: {sum(r['changed'] for r in disabled)}/{len(disabled)}.",
        "Same LLM and system prompt; no FAISS or document loading in disabled mode.",
        "The LLM receives empty CONTEXT. Raw selections are saved.",
        "", "## Separate generation review", ""]
    for i,row in enumerate(grounding,1):
        lines.append(f"- Q{i}: {json.dumps(row.get('review',{}),ensure_ascii=False)}")
    lines += ["", "These are development-set results, not held-out accuracy.",
        "The late-arrival question explicitly names section 4.8 because section 4.3",
        "contains a different late-arrival provision. Historical results are retained."]
    (OUT/"report.md").write_text("\n".join(lines),encoding="utf-8")

if __name__ == "__main__":
    render_report()
