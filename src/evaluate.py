"""Run retrieval, generation, out-of-scope and same-prompt ablation tests."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from ask import answer_question, MODEL
from retrieve import Retriever, RERANKER

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "evaluation"

def save(name, data):
    (OUT/name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=3)
    args = parser.parse_args()
    tests = json.loads((OUT/"questions.json").read_text(encoding="utf-8"))
    oos = json.loads((OUT/"out_of_scope_questions.json").read_text(encoding="utf-8"))
    manifest = {"model": MODEL, "reranker": RERANKER, "k": args.k,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "index_sha256": hashlib.sha256((ROOT/"storage/index.faiss").read_bytes()).hexdigest(),
        "code_sha256": {p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in (ROOT/"src").glob("*.py")}}
    save("run_manifest.json",manifest)
    retriever = Retriever()
    rows=[]
    for question, expected in tests:
        found=retriever.search(question,k=args.k)
        ids=[x["chunk_id"] for x in found]
        rows.append({"question":question,"expected_chunk":expected,
                     "retrieved_chunks":ids,"hit":expected in ids})
    hits=sum(r["hit"] for r in rows)
    save("retrieval_results.json",{"k":args.k,"hit_rate":hits/len(rows),"results":rows})
    print(f"Retrieval Hit-rate@{args.k}: {hits}/{len(rows)}",flush=True)
    errors=[]
    def run(question,mode="rag",enabled=True):
        try:
            return answer_question(question,k=args.k,mode=mode,
                retriever=retriever if enabled else None,retrieval_enabled=enabled)
        except Exception as exc:
            errors.append(str(exc))
            return {"error":str(exc)}
    comparisons=[]
    disabled_rows=[]
    for i,(question,_) in enumerate(tests[:5],1):
        print(f"{i}/5 RAG",flush=True)
        rag=run(question)
        print(f"{i}/5 baseline",flush=True)
        baseline=run(question,"baseline")
        print(f"{i}/5 same-prompt retrieval disabled",flush=True)
        disabled=run(question,enabled=False)
        comparisons.append({"question":question,"rag":rag,"baseline":baseline,
            "review":{"answer_correct":None,"citations_correct":None,
                      "meaningful_difference":None}})
        disabled_rows.append({"question":question,"result":disabled,
            "changed": bool(rag.get("answer") and disabled.get("answer") and
                            rag["answer"] != disabled["answer"])})
        save("grounding_results.json",comparisons)
        save("retrieval_disabled_results.json",disabled_rows)
    oos_rows=[]
    for question in oos:
        print("Out of scope:",question,flush=True)
        result=run(question)
        oos_rows.append({"question":question,"result":result,
                         "declined":result.get("status")=="not_found"})
        save("out_of_scope_results.json",oos_rows)
    manifest["completed_at"]=datetime.now(timezone.utc).isoformat()
    manifest["errors"]=errors
    save("run_manifest.json",manifest)
    from finish import render_report
    render_report()
    print("Saved evaluation/report.md",flush=True)
    if errors:
        raise SystemExit(f"{len(errors)} calls failed; see run_manifest.json")

if __name__ == "__main__":
    main()
