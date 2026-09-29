# Retrieval-Augmented Generation

A local, from-scratch Python RAG project for Week 4. It answers Azerbaijani
questions using a real AzTU examination-regulations PDF. The document title
is dated 2023; this project does not claim the policy is currently in force.
The source PDF and URL/download-date metadata are in `data/raw/`.

## Quick start (Windows PowerShell)

Tested with Python 3.13.9. Install Ollama separately, then:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
ollama pull llama3.2:latest
```

If Ollama is not running, start `ollama serve` in another terminal.
The first retrieval downloads the embedding and reranking models.
After models are cached, offline Hugging Face operation can be enabled:

```powershell
$env:HF_HUB_OFFLINE = "1"
$env:TRANSFORMERS_OFFLINE = "1"
```

Use the included persisted index:

```powershell
.\.venv\Scripts\python.exe src\ask.py "4.7-ci bolmede muraciet muddeti?" --mode rag --k 3
```

Use Azerbaijani letters in real questions; examples and exact evaluation
questions are in `evaluation/questions.json`. For example, copy a question
from that UTF-8 file rather than piping non-ASCII Python through PowerShell.

## Models and trade-offs

- Embeddings: `intfloat/multilingual-e5-small`, chosen for multilingual support
  and local operation without per-request API charges. Documents use `passage:`
  and questions use `query:` prefixes; embeddings are normalized.
- FAISS `IndexFlatIP`: exact cosine-similarity ranking of normalized vectors.
- Reranker: `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`.
- LLM: Ollama `llama3.2:latest`, selected after local trials. Its actual installed
  digest is recorded with final evaluation metadata when available.

Local inference trades API costs for RAM, disk space and latency. The final
answer mode is extractive: the LLM chooses one numbered source passage via a
JSON schema, then the program renders the original text with its citation.
This avoids rewriting numbers and negation. It is not free-form synthesis.
Labeled answers are never consulted by the production answering code.

## Chunking and indexing

`src/extract_text.py` extracts text with page provenance. `src/chunk_text.py`
splits it into at most 180 words with 30-word overlap, without crossing pages.
Overlap retains boundary context; page boundaries preserve reliable citations.
The title-only first page is excluded. The resulting index has 38 chunks.
Word counts are not token counts: `build_index.py` rejects over-limit chunks
rather than silently embedding truncated text.

```powershell
.\.venv\Scripts\python.exe src\extract_text.py
.\.venv\Scripts\python.exe src\chunk_text.py
.\.venv\Scripts\python.exe src\build_index.py
```

The FAISS index, ordered chunk mapping and embedding configuration are persisted
in `storage/`. Questions load them, not rebuild them. Rebuild after changing
source text, chunking or embedding model. Changing the LLM does not require it.

## Retrieval and grounded generation

1. Embed the question and retrieve 10 candidates from FAISS (or more if k > 10).
2. Cross-encode candidates with the question and retain configurable top-k.
3. Split only those chunks into evidence spans, preserving common abbreviations.
4. Recover section metadata from source pages; for explicit section questions,
   restrict evidence to that section. Page text supplies metadata, not extra
   answer passages. Candidate answer text always comes from retrieved chunks.
5. Rerank spans and inject at most six into the CONTEXT part of the prompt,
   separately from QUESTION.
6. The LLM selects one passage ID or zero for refusal. IDs are validated and
   rendered as exact source text, with chunk ID, document title, page and URL.

Document text is treated as untrusted data in the system prompt. Constrained
selection reduces fabricated quotations but is not a complete injection defense.
The model may still choose irrelevant evidence or refuse an answerable question.

## Baseline, evaluation and grounding proof

```powershell
.\.venv\Scripts\python.exe src\ask.py "your question" --mode baseline
.\.venv\Scripts\python.exe -u src\evaluate.py --k 3
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Baseline uses the same LLM with no documents, index or retrieved context.
Evaluation separately records ten labeled retrieval checks, five actual RAG vs
baseline outputs, two out-of-scope questions, and five same-prompt ablations.
The ablation disables the retrieval path before any index/document loading,
passes empty context to the same LLM/system prompt, and records its refusal.

See `evaluation/report.md` for results; raw data and a code/index fingerprint
are in the JSON files and `run_manifest.json`. `src/finish.py` only renders saved
results; it does not generate fabricated reviews. New evaluations clear manual
review fields, which must be assessed against source text again.

## Limitations and evaluation scope

The small question set was used during development, so scores are not held-out
accuracy. Earlier failed trials are retained. Section headings are parsed
heuristically; extraction retains occasional PDF spacing errors. The document
contains different late-arrival provisions (sections 4.3 and 4.8), so the final
late-arrival test explicitly asks about 4.8 instead of implying a universal rule.
Source context and currency must be checked before relying on policy answers.
The evidence selector chooses one rule; it does not reliably reconcile all
conflicting policies across a corpus. UI, chat memory and multiple input formats
are not implemented; these are optional bonuses. Reranking is implemented.

## Submission

See `SUBMISSION.md` for the requirement-to-file checklist. Commit `src`, `tests`,
`data`, `storage`, `evaluation`, requirements and documentation. Do not commit
`.venv`, cache directories, secrets or `work` scratch files. Model weights are
not bundled; dependencies and model identifiers allow them to be installed.

## Final measured results

Final run: see `evaluation/run_manifest.json` for timestamps, model digest and
code/index hashes. No model-call errors occurred.

- Retrieval Hit-rate@3: **10/10 (100%)**.
- Manual question-answer correctness: **5/5** on the five revised development questions.
- Selected passages and citations verified against persisted source chunks: **5/5**.
- Out-of-scope refusal: **2/2**.
- Same-prompt retrieval-disabled runs: **5/5 refuse and change the answer**.
- RAG vs parametric-only answers: four factual/content differences; the zero-point
  question is also answered correctly by the baseline. This coincidence is retained.
- Seven unit tests pass; dependency consistency and persisted index/mapping checks pass.

These results are extractive QA on a small development set, not proof of general
accuracy. The earlier unqualified late-arrival question was revised to name
section 4.8 explicitly; older failures are retained. Formatting artifacts from
the PDF (including occasional split words and a trailing list number) remain
in exact quotations rather than being silently rewritten.
