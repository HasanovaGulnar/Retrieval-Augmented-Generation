# Submission checklist

- Chunking: `src/chunk_text.py`; 180 words, 30-word overlap, page boundaries.
- Embedding: local multilingual E5-small; `src/build_index.py`.
- Persisted FAISS index: `storage/index.faiss`, mapping and model config alongside it.
- Configurable top-k: `python src/ask.py "question" --k 3`.
- Retrieval-only context: `src/ask.py` builds CONTEXT from retrieved evidence spans.
- Five actual RAG/LLM-alone comparisons: `evaluation/report.md` and raw JSON.
- Two out-of-scope checks: `evaluation/out_of_scope_results.json`.
- Ten labeled question/chunk pairs: `evaluation/questions.json`.
- Separate generation assessment: reviews in `evaluation/grounding_results.json`.
- Retrieval gate: `evaluation/retrieval_disabled_results.json`; same RAG system
  prompt and model with empty context, without loading the vector store.
- Citations: exact selected evidence maps to chunk ID, PDF page and original URL.
- Bonus: multilingual cross-encoder reranking of 10 vector-search candidates.

The answer generator is **extractive**: an LLM selects a source passage using
constrained JSON, and Python renders that exact passage. It does not perform
unrestricted paraphrasing. Baseline answers are real unrestricted model output.
No question-to-answer lookup is used in the runtime pipeline.

Scores on these development questions do not guarantee unseen-question quality.
PDF section labels are heuristic, and source policies may be outdated. Original
and revised evaluation outputs are retained for transparency.
