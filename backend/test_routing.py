"""Intent and source routing regression tests for the course agent."""

from backend.routing import classify_request, classify_source


PAST_EXAM = {
    "name": "2025年期末考试试卷.txt",
    "kind": "lecture",
    "text": """2025年期末考试
考试时间：120分钟
满分：100分
一、选择题（共20题，每题2分）
二、填空题（共10题，每题2分）
三、简答题（共4题，每题5分）
四、计算题（共2题，每题10分）""",
}
REVIEW = {"name": "期末复习提纲.md", "kind": "notes", "text": "重点概念、公式总结、常见误区与复习建议。"}
TEXTBOOK = {"name": "高等数学教材第三章.pdf", "kind": "lecture", "text": "第三章 微分中值定理。本章介绍定理、证明、例题与课后习题。"}


def test_past_exam_and_generation_routes_to_exam_generation():
    source = classify_source(PAST_EXAM)
    result = classify_request("参考这份试卷，举一反三生成一份新的考试卷", [PAST_EXAM])
    assert source.sourceType == "past_exam"
    assert result.taskIntent == "generate_mock_exam"
    assert result.route == "exam_generation"


def test_past_exam_and_key_points_routes_to_analysis():
    result = classify_request("总结这份历年试卷的高频考点", [PAST_EXAM])
    assert result.sourceType == "past_exam"
    assert result.taskIntent == "extract_key_points"
    assert result.route == "review_or_analysis"


def test_review_material_does_not_override_explicit_exam_generation():
    result = classify_request("根据这份资料生成一份模拟考试卷", [REVIEW])
    assert result.sourceType == "review_material"
    assert result.taskIntent == "generate_mock_exam"
    assert result.route == "exam_generation"


def test_textbook_summary_routes_to_summary():
    result = classify_request("帮我总结本章", [TEXTBOOK])
    assert result.sourceType == "textbook"
    assert result.taskIntent == "summarize"
    assert result.route == "summary"


def test_ambiguous_request_requires_clarification():
    result = classify_request("帮我处理这份资料", [REVIEW])
    assert result.taskIntent == "unknown"
    assert result.needsClarification is True
    assert result.route == "clarification"


def test_english_mock_exam_request_routes_to_generation():
    result = classify_request("Generate a new mock exam based on this past paper.", [PAST_EXAM])
    assert result.taskIntent == "generate_mock_exam"
    assert result.route == "exam_generation"


def test_source_classifier_recognizes_required_document_types():
    assert classify_source({"name": "课件.pptx", "kind": "lecture", "text": "第一讲 极限"}).sourceType == "slides"
    assert classify_source({"name": "线性代数题库.pdf", "kind": "lecture", "text": "练习题集合"}).sourceType == "question_bank"
    assert classify_source({"name": "材料.pdf", "kind": "lecture", "text": "零散文字"}).sourceType == "unknown"


def test_required_intents_have_distinct_routes():
    cases = {
        "给我制订一份复习计划": ("create_review_plan", "review_plan"),
        "讲解这道题": ("explain_questions", "question_explanation"),
        "回答题目并给出答案": ("answer_questions", "question_answering"),
        "根据资料生成闪卡": ("create_flashcards", "flashcards"),
    }
    for message, expected in cases.items():
        result = classify_request(message, [REVIEW])
        assert (result.taskIntent, result.route) == expected


def test_pasted_exam_content_is_classified_as_a_past_exam():
    message = """2025年期末考试
考试时间：120分钟
满分：100分
一、选择题（每题2分）
请据此生成一份新的考试卷"""
    result = classify_request(message, [])
    assert result.sourceType == "past_exam"
    assert result.route == "exam_generation"
