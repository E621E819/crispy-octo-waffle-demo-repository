# Exam Radar AI design

The live course path uses the server-side OpenAI Responses API with the exact
`gpt-5` model. `AIService` accepts only extracted course material supplied by
the FastAPI layer; source text is placed in a clearly delimited untrusted-data
section. The service validates every returned `sourceId` against the material
IDs in that request, rejects hallucinated citations, and reports the proportion
of source text included when context had to be bounded. Public question payloads
never include the private solution or rubric.

`generate_question` runs a real LangGraph state graph:

```text
START → generate → critic → verify → END (pass, or fail after two drafts)
          ↑                   │
          └──── retry ─────────┘ (first draft failed)
```

The generator changes context, data or assumptions, and wording while retaining
the reasoning structure. The critic checks those transformation invariants,
grounding, difficulty, and a similarity threshold. The verifier independently
checks solvability, the private solution and rubric consistency before a draft is
accepted. Failure is returned to the caller; a failed live model call never turns
into a fabricated answer.

The Responses API structured-output call follows OpenAI's documented
`client.responses.parse(..., text_format=PydanticModel)` interface and reads
`output_parsed`: [GPT-5 models](https://developers.openai.com/api/docs/models/gpt-5)
and [Structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs).

The client allows one transport retry and a 90-second request timeout; question
regeneration is bounded to two drafts. Requests use `store=False`. Errors are
mapped to actionable messages without reflecting SDK response bodies into the UI.
Source context is capped at 90,000 extracted characters. Small documents are read
in full; large documents share the budget, with query-matching excerpts selected
and the original page markers and text offsets preserved. This MVP uses local
lexical retrieval, without a vector database or embeddings.

The seeded Machine Learning course is deliberately separate: it is marked
`isDemo: true`, uses authored deterministic fixtures, and labels those outputs in
the API. Demo grading accepts an explicit multiple-choice selection only. A real
course without `OPENAI_API_KEY` returns an actionable 503 instead of silently
pretending to be AI generated. Live grading reveals the rubric only after a
submission and updates mastery with the MVP evidence rule: 70% prior mastery +
30% latest score percentage.

Priority is an inspectable weighted score (not logistic regression):

`0.25 frequency + 0.20 marks + 0.15 recency + 0.15 teachingPlan + 0.10 diversity + 0.15 weakness`.

Unknown mastery uses neutral weakness 50. When mastery is present, weakness is
`100 - mastery`. The UI should show these contributions and the supplied sample
size/year range; a score is study guidance rather than an exam guarantee.

Validation: `python -m pytest backend/test_ai.py -q` runs credential-free tests
covering live-path failure isolation, invalid citations, all six authored demo
topics, private question data, deterministic grading, numerical scoring, and the
actual LangGraph transitions plus a real OpenAI SDK `MockTransport` serialization
check. These tests verify
the integration contract; live GPT-5 quality and account access require an API key.

Material limits are deliberate for this local MVP: uploads are limited to 15 MB
and 500 pages/slides, extracted text to one million characters per file, and the
model context to 90,000 characters per request. PDF text extraction requires
selectable text (scanned PDFs should be OCRed first); DOCX pagination is reported
as unavailable; PPTX text is extracted per slide. Tables in DOCX are included as
plain cell text and images, handwriting, diagrams, formulas embedded only as
pixels, and speaker notes are not OCRed by the local parser. Split large source
sets into several files and check the reported coverage before treating a trend
as complete.

Historical exam analysis is a separate explicit action:
`await AIService.exam_analysis(course, materials=None, language="en")`.
It selects only materials typed as past papers/exams and extracts up to 40
question records per run with concept, dominant task, cognitive level, stated
marks, printed year, source IDs, and concise reasoning skills. Unstated marks and
years remain null. All citations are validated against the selected exam
sources; duplicate source-question identifiers and years not present in cited
excerpts are rejected. Task distribution counts and percentages are computed
locally from accepted records. These figures describe the extracted sample,
without claiming teacher identity, complete historical coverage, or future exam
probability. The demo parses four actual authored question lines across three
sample papers (2024–2026) and labels them synthetic. Five focused tests cover
demo counts, missing papers, wrong-source citations, deterministic distribution,
missing metadata, duplicate records, and unprinted years.
