"""Deterministic source classification and per-message task routing."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class SourceClassification:
    sourceType: str
    sourceConfidence: float


@dataclass(frozen=True)
class RoutingDecision:
    sourceType: str
    sourceConfidence: float
    taskIntent: str
    intentConfidence: float
    route: str
    needsClarification: bool


SOURCE_KINDS = {
    "past_exam": {"past_paper", "past paper", "exam", "exam_paper", "mock_exam"},
    "review_material": {"notes", "review", "revision", "study_material"},
    "textbook": {"textbook", "book"},
    "slides": {"slides", "ppt", "lecture_slides"},
    "question_bank": {"question_bank", "question bank", "practice"},
}

SOURCE_EVIDENCE = {
    "past_exam": (
        "历年试卷", "往年试题", "往年真题", "真题", "考试卷", "期中考试", "期末考试",
        "模拟卷", "测试卷", "past paper", "previous exam", "exam paper", "mock exam", "practice test",
    ),
    "review_material": ("复习资料", "复习提纲", "课堂笔记", "复习建议", "revision notes", "study guide"),
    "textbook": ("教材", "电子书", "本章介绍", "课后习题", "textbook", "chapter"),
    "slides": ("课件", "幻灯片", "lecture slides", "powerpoint"),
    "question_bank": ("题库", "练习题集合", "question bank", "exercise bank"),
}

EXAM_STRUCTURE = (
    r"考试时间\s*[：:]", r"满分\s*[：:]", r"答题要求", r"参考答案", r"评分标准",
    r"(?:选择|填空|判断|简答|计算|综合)题", r"\bq(?:uestion)?\s*\d+", r"\d+\s*(?:分|marks?)",
)


def _count_phrases(text: str, phrases: Iterable[str]) -> int:
    return sum(1 for phrase in phrases if phrase in text)


def classify_source(material: dict[str, Any]) -> SourceClassification:
    """Classify one source from independent metadata and content evidence."""
    name = str(material.get("name") or "").casefold()
    text = str(material.get("text") or material.get("excerpt") or "").casefold()
    kind = str(material.get("kind") or "").strip().casefold()
    combined = f"{name}\n{text}"
    scores = {key: 0.0 for key in SOURCE_EVIDENCE}

    for source_type, kinds in SOURCE_KINDS.items():
        if kind in kinds:
            scores[source_type] += 4.0
    for source_type, phrases in SOURCE_EVIDENCE.items():
        scores[source_type] += min(3, _count_phrases(name, phrases)) * 1.6
        scores[source_type] += min(4, _count_phrases(text, phrases)) * 0.9

    extension = Path(name).suffix.lower()
    if extension == ".pptx":
        scores["slides"] += 2.5
    exam_features = sum(bool(re.search(pattern, combined, re.IGNORECASE)) for pattern in EXAM_STRUCTURE)
    scores["past_exam"] += min(5, exam_features) * 0.9
    if exam_features >= 3:
        scores["past_exam"] += 2.0
    if re.search(r"(?:^|\n)\s*(?:一[、.]|1[、.)]|q1\b)", text, re.IGNORECASE):
        scores["past_exam"] += 0.8
    if scores["question_bank"] and exam_features >= 2:
        scores["question_bank"] += 0.8

    source_type, score = max(scores.items(), key=lambda item: item[1])
    if score < 1.8:
        return SourceClassification("unknown", round(min(0.49, score / 4), 2))
    ordered = sorted(scores.values(), reverse=True)
    margin = score - ordered[1]
    confidence = min(0.99, 0.55 + score / 18 + max(0, margin) / 20)
    return SourceClassification(source_type, round(confidence, 2))


INTENT_EVIDENCE = {
    "generate_mock_exam": (
        "生成一份新的模拟考试卷", "生成一份模拟考试卷", "生成模拟考试卷", "生成一套类似的考试卷",
        "生成一份新的考试卷", "生成一份新的考试题", "重新出题", "举一反三", "帮我出", "给我出",
        "生成考试题", "生成试题", "模拟卷", "模拟考试卷", "类似题目", "练习题",
        "generate a new mock exam", "generate a mock exam", "create a new mock exam", "make a practice test",
        "generate similar questions", "create similar questions", "mock exam", "practice test",
    ),
    "extract_key_points": ("高频考点", "提取重点", "总结考点", "分析考点", "重点是什么", "key points", "exam topics"),
    "create_review_plan": ("复习计划", "学习计划", "怎么复习", "安排复习", "review plan", "study plan"),
    "create_flashcards": ("生成闪卡", "制作闪卡", "做成卡片", "flashcards", "flash cards"),
    "explain_questions": ("讲解题目", "讲解这道题", "解释这道题", "解析题目", "explain this question", "explain the questions"),
    "answer_questions": ("回答题目", "解答题目", "帮我做题", "给出答案", "answer the question", "solve this question"),
    "summarize": ("总结资料", "总结本章", "总结这份", "概括", "摘要", "summarize", "summary"),
}

ROUTES = {
    "generate_mock_exam": "exam_generation",
    "extract_key_points": "review_or_analysis",
    "create_review_plan": "review_plan",
    "create_flashcards": "flashcards",
    "explain_questions": "question_explanation",
    "answer_questions": "question_answering",
    "summarize": "summary",
}


def _classify_intent(message: str) -> tuple[str, float]:
    query = " ".join(message.casefold().split())
    scores = {intent: 0.0 for intent in INTENT_EVIDENCE}
    for intent, phrases in INTENT_EVIDENCE.items():
        matches = [phrase for phrase in phrases if phrase in query]
        scores[intent] += sum(2.0 + min(len(phrase), 20) / 20 for phrase in matches)

    # Compositional evidence covers natural variants without matching a whole test sentence.
    generation = bool(re.search(r"生成|出\s*\d*\s*道|出一?份|重新出|create|generate|make", query))
    exam_object = bool(re.search(r"试卷|考试题|试题|题目|练习题|模拟卷|exam|paper|questions?|practice test", query))
    if generation and exam_object:
        scores["generate_mock_exam"] += 5.0
    if re.search(r"总结|归纳|summari[sz]e", query) and re.search(r"考点|重点|高频|key points?|topics?", query):
        scores["extract_key_points"] += 5.0
    if re.search(r"解释|说明|为什么|explain|why", query) and not exam_object:
        scores["explain_questions"] += 2.0
    if re.search(r"总结|概括|summari[sz]e", query):
        scores["summarize"] += 2.0

    intent, score = max(scores.items(), key=lambda item: item[1])
    if score < 2.0:
        # Ordinary course questions still belong to general chat; vague document actions need clarification.
        if re.search(r"帮我处理|处理这份|看一下这份|怎么办|handle this|process this", query):
            return "unknown", 0.25
        return "general_chat", 0.65
    confidence = min(0.99, 0.62 + score / 20)
    return intent, round(confidence, 2)


def classify_request(message: str, materials: Iterable[dict[str, Any]]) -> RoutingDecision:
    """Classify current input only; no session state can leak into the next turn."""
    classified = [classify_source(material) for material in materials]
    # Pasted document content is itself a source signal, independent from the requested action.
    pasted = classify_source({"name": "pasted-input.txt", "kind": "", "text": message})
    if pasted.sourceType != "unknown":
        classified.append(pasted)
    source = max(classified, key=lambda item: item.sourceConfidence, default=SourceClassification("unknown", 0.0))
    intent, intent_confidence = _classify_intent(message)
    needs_clarification = intent == "unknown"
    route = "clarification" if needs_clarification else ROUTES.get(intent, "general_chat")
    return RoutingDecision(source.sourceType, source.sourceConfidence, intent, intent_confidence, route, needs_clarification)
