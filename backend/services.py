"""Deterministic scoring and bounded source retrieval used by the AI service."""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any, Iterable

PRIORITY_WEIGHTS = {"frequency": .25, "marks": .20, "recency": .15,
                    "teachingPlan": .15, "diversity": .10, "weakness": .15}


def bounded(value: Any, default: float = 0) -> float:
    try:
        number = float(value)
        return min(100, max(0, number)) if math.isfinite(number) else default
    except (TypeError, ValueError):
        return default


def priority_score(topic: dict[str, Any]) -> float:
    """A transparent weighted score, not a fitted logistic regression.

    An unobserved mastery has neutral weakness 50. Zero mastery must remain zero.
    """
    mastery = topic.get("mastery")
    weakness = 50 if mastery is None else 100 - bounded(mastery)
    return round(sum(weight * (weakness if key == "weakness" else bounded(topic.get(key)))
                     for key, weight in PRIORITY_WEIGHTS.items()), 1)


def update_mastery(prior: float | None, score: float, max_score: float) -> float:
    """MVP evidence update: 70% prior + 30% latest observed mark percentage."""
    if max_score <= 0:
        raise ValueError("Maximum score must be positive")
    observation = bounded(score / max_score * 100)
    return round(observation if prior is None else .7 * bounded(prior) + .3 * observation, 1)


def next_topic_id(topics: list[dict[str, Any]], current_id: str | None = None) -> str | None:
    candidates = [t for t in topics if t.get("mastery") is None or bounded(t.get("mastery")) < 60]
    candidates = candidates or topics
    if not candidates:
        return None
    best = max(candidates, key=lambda t: (priority_score(t), t.get("id") != current_id))
    return str(best["id"])


@dataclass(frozen=True)
class SourceContext:
    sources: list[dict[str, str]]
    allowed_ids: frozenset[str]
    included_chars: int
    total_chars: int
    total_sources: int

    @property
    def truncated(self) -> bool:
        return self.included_chars < self.total_chars

    @property
    def coverage(self) -> str:
        if not self.total_chars:
            return "No readable course source text is available."
        fraction = 100 * self.included_chars / self.total_chars
        if self.truncated:
            return (f"Context coverage: {fraction:.0f}% of source text ({len(self.sources)}/{self.total_sources} "
                    "documents). Long documents were excerpted; counts and trends apply only to the included excerpts.")
        return f"Context coverage: full extracted text of {len(self.sources)} document(s)."

    def payload(self) -> dict[str, Any]:
        return {"coverage": self.coverage, "sources": self.sources}


def build_source_context(materials: Iterable[dict[str, Any]], query: str = "", max_chars: int = 90000) -> SourceContext:
    """Include full extraction when possible, otherwise a fair share per source.

    For large documents page/paragraph excerpts are ranked by query tokens. Every
    excerpt retains its supplied page label and offset. Only actually included
    documents are allowable citations. This is a local MVP retrieval method.
    """
    if max_chars <= 0:
        raise ValueError("Source context limit must be positive")
    docs: list[tuple[dict[str, Any], str]] = []
    seen: set[str] = set()
    for material in materials:
        sid = str(material.get("id") or "")
        value = material.get("text")
        if value is None:
            value = material.get("excerpt", "")
        text = str(value or "").strip()
        if sid and sid not in seen and text:
            docs.append((material, text))
            seen.add(sid)
    total_chars = sum(len(text) for _, text in docs)
    terms = set(re.findall(r"[\w\u4e00-\u9fff]{2,}", query.lower()))
    remaining = max_chars
    included_chars = 0
    sources: list[dict[str, str]] = []
    for index, (material, full_text) in enumerate(docs):
        if remaining <= 0:
            break
        quota = max(1, remaining // (len(docs) - index))
        used = min(len(full_text), quota)
        if len(full_text) <= quota:
            excerpt = full_text
        else:
            # Label offsets even for DOCX/txt, which do not have stable page numbers.
            spans = [(m.start(), m.group(0)) for m in re.finditer(r"[\s\S]{1,1800}", full_text)]
            ranked = sorted(spans, key=lambda item: (-sum(item[1].lower().count(term) for term in terms), item[0]))
            picked: list[tuple[int, str]] = []
            budget = quota
            for offset, chunk in ranked:
                if not budget:
                    break
                piece = chunk[:budget]
                picked.append((offset, piece))
                budget -= len(piece)
            used = sum(len(piece) for _, piece in picked)
            labeled = []
            for offset, piece in sorted(picked):
                preceding = list(re.finditer(r"\[Page\s+\d+[^\]]*\]", full_text[:offset], re.IGNORECASE))
                page = preceding[-1].group(0) + " " if preceding else ""
                labeled.append(f"{page}[Extracted text offset {offset}]\n{piece}")
            excerpt = "\n\n".join(labeled)
        sources.append({"sourceId": str(material["id"]), "name": str(material.get("name", "Source")),
                        "kind": str(material.get("kind", "document")), "text": excerpt})
        included_chars += used
        remaining -= used
    return SourceContext(sources, frozenset(source["sourceId"] for source in sources),
                         included_chars, total_chars, len(docs))


def validate_source_ids(ids: Iterable[str], allowed: Iterable[str], required: bool = False) -> list[str]:
    """Reject hallucinated and cross-course citations, even in structured output."""
    result = list(dict.fromkeys(ids))
    permitted = set(allowed)
    if any(sid not in permitted for sid in result):
        raise ValueError("Generated output cited a source outside the supplied course context")
    if required and not result:
        raise ValueError("Generated output lacks required course source citations")
    return result


def source_copy_overlap(prompt: str, sources: list[dict[str, str]]) -> float:
    """Max contiguous normalized 5-word overlap; language-neutral character fallback."""
    normalized = re.findall(r"\w+", prompt.lower())
    if len(normalized) < 10:
        normalized = list(re.sub(r"\s+", "", prompt.lower()))
    width = 5
    grams = {tuple(normalized[i:i+width]) for i in range(max(0, len(normalized)-width+1))}
    if not grams:
        return 0
    maximum = 0.0
    for source in sources:
        tokens = re.findall(r"\w+", source["text"].lower())
        if len(re.findall(r"\w+", prompt.lower())) < 10:
            tokens = list(re.sub(r"\s+", "", source["text"].lower()))
        other = {tuple(tokens[i:i+width]) for i in range(max(0, len(tokens)-width+1))}
        maximum = max(maximum, len(grams & other) / len(grams))
    return maximum
