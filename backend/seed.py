"""Explicitly synthetic course, with complete authored excerpts to cite in the demo."""

from datetime import date, timedelta
from uuid import uuid4


def uid(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:16]}"


def priority(topic: dict) -> float:
    mastery = topic.get("mastery")
    weakness = 50 if mastery is None else 100 - mastery
    return round(.25 * topic.get("frequency", 0) + .20 * topic.get("marks", 0) + .15 * topic.get("recency", 0) + .15 * topic.get("teachingPlan", 0) + .10 * topic.get("diversity", 0) + .15 * weakness, 1)


def readiness(topics: list[dict]):
    measured = [topic for topic in topics if topic.get("mastery") is not None]
    if not measured:
        return None
    return round(sum(topic["mastery"] for topic in measured) / len(measured))


def demo_course() -> dict:
    lecture_id, exam_id, syllabus_id = uid("material"), uid("material"), uid("material")
    lecture = """Exam Radar authored demo — Machine Learning lecture notes. This is a teaching sample, not an uploaded university document.
[Page 1] Chapter 1. Learning foundations
Supervised learning estimates a mapping from labeled examples. Regression predicts a continuous quantity; classification predicts a category. Divide data into training, validation and test sets. Fit preprocessing only on the training set to avoid data leakage.
[Page 2] Chapter 2. Logistic regression
Logistic regression models P(y=1|x)=1/(1+exp(-(w·x+b))). A threshold converts the probability into a predicted class. Lowering the threshold usually increases recall while potentially lowering precision. Cross-entropy penalizes confident incorrect predictions. L2 regularization penalizes squared weights and controls overfitting. Despite its name logistic regression is commonly used for classification.
[Page 3] Chapter 3. K-nearest neighbours
KNN predicts from the labels of the k nearest training examples. Euclidean distance is sqrt(sum((x_i-z_i)^2)). Standardize features when scales differ; fit the scaler on training data only. Small k has lower bias and higher variance; large k smooths the boundary and can underfit. Use validation or cross-validation to choose k. Distance-weighted voting gives closer points greater influence.
[Page 4] Chapter 4. Model evaluation
True positives (TP) are actual positives predicted positive. False positives (FP) are actual negatives predicted positive. False negatives (FN) are actual positives predicted negative. Precision=TP/(TP+FP). Recall=TP/(TP+FN). F1=2*precision*recall/(precision+recall)=2TP/(2TP+FP+FN). Accuracy=(TP+TN)/(TP+TN+FP+FN). For rare disease screening false negatives can be costly, making recall especially relevant. In a spam filter false positives can hide important mail, so precision also matters.
[Page 5] Chapter 5. Generalization
Training error can be low while test error is high: this indicates overfitting. Cross-validation estimates performance on held-out folds. A learning curve compares training and validation errors as sample size varies. Regularization constrains complexity; excessive regularization can cause underfitting. Bias is systematic error from simplifying assumptions; variance reflects sensitivity to the training sample.
"""
    exam = """Exam Radar authored demo — practice exam examples (not authentic historical papers).
[Page 1] Sample exam A (2024), Q1 (12 marks): Given TP=36, FP=9 and FN=24, compute precision, recall and F1. Explain which metric matters most when missing a disease case has a high cost. Expected: precision=.80; recall=.60; F1≈.686; prioritize recall with an explicit discussion of false positives.
[Page 2] Sample exam B (2025), Q2 (10 marks): A binary classifier uses logistic regression. Explain the sigmoid, what happens when the decision threshold drops, and the effect of L2 regularization. Expected: probability in [0,1]; more predicted positives and usually greater recall; large weights penalized.
[Page 3] Sample exam C (2026), Q3 (10 marks): A KNN classifier uses income in dollars and age in years. Explain why scaling matters, compare k=1 and k=25, and describe leakage-free cross-validation. Expected: large-scale features dominate distance; k=1 high variance; k=25 smoother, potentially biased; fit scaling inside each training fold.
[Page 4] Sample exam C (2026), Q4 (8 marks): Training accuracy is 99% and validation accuracy is 68%. Diagnose the issue and suggest two justified changes. Expected: likely overfitting; regularize, simplify the model, collect representative data, or tune with cross-validation. Do not tune against the final test set.
"""
    syllabus = """Exam Radar authored demo syllabus. Every unit is synthetic demonstration content.
[Page 1] Learning outcomes: CLO1 distinguish supervised problem types and prevent leakage. CLO2 explain and apply logistic regression. CLO3 choose KNN parameters and preprocessing. CLO4 compute and interpret precision, recall and F1. CLO5 diagnose bias, variance and overfitting using held-out data.
Teaching emphasis: model evaluation 30%; logistic regression 25%; KNN 20%; generalization 15%; foundations 10%. Assessment includes calculations, comparisons, explanations and applied scenarios.
"""
    materials = [
        {"id": lecture_id, "name": "ML · Course notes.pdf", "kind": "lecture", "status": "ready", "pages": 5, "text": lecture, "excerpt": lecture[:280], "isDemo": True},
        {"id": exam_id, "name": "Practice exams · 2024–2026.pdf", "kind": "past_paper", "status": "ready", "pages": 4, "text": exam, "excerpt": exam[:280], "isDemo": True},
        {"id": syllabus_id, "name": "ML · Learning outcomes.docx", "kind": "syllabus", "status": "ready", "pages": 1, "text": syllabus, "excerpt": syllabus[:280], "isDemo": True},
    ]
    raw_topics = [
        ("Logistic Regression", "02 · Classification", 72, 95, 90, 95, 95, 90, "Predict probabilities with the sigmoid; explain thresholds, cross-entropy and regularization."),
        ("K-Nearest Neighbours", "03 · Distance-based learning", 66, 90, 85, 100, 85, 90, "Choose k, scale features, and explain the bias–variance tradeoff."),
        ("Precision & Recall", "04 · Model evaluation", 58, 100, 100, 100, 100, 100, "Calculate TP-based metrics and choose the appropriate metric for the cost of an error."),
        ("F1 Score", "04 · Model evaluation", 31, 90, 85, 100, 95, 80, "Combine precision and recall with their harmonic mean; explain why accuracy may mislead."),
        ("Bias & Variance", "05 · Generalization", 81, 75, 65, 90, 80, 90, "Diagnose overfitting and underfitting, then choose a justified intervention."),
        ("Cross-validation", "05 · Generalization", 84, 80, 70, 100, 80, 85, "Evaluate on held-out folds and fit preprocessing inside each training fold."),
    ]
    topics = []
    for title, chapter, mastery, frequency, marks, recency, teaching, diversity, summary in raw_topics:
        topic = {"id": uid("topic"), "title": title, "chapter": chapter, "mastery": mastery, "frequency": frequency, "marks": marks, "recency": recency, "teachingPlan": teaching, "diversity": diversity, "summary": summary, "sourceIds": [lecture_id, exam_id, syllabus_id], "reasoning": ["Illustrative weights from 3 authored practice exam examples; not a prediction of a real exam.", "Teaching emphasis follows the included demo learning outcomes.", "Personal weakness updates after each submitted practice answer."]}
        topic["priority"] = priority(topic)
        topics.append(topic)
    session = {"id": uid("session"), "title": "Your exam, a little clearer", "messages": [{"id": uid("message"), "role": "assistant", "content": "Welcome to your Machine Learning workspace. I’ve organized the sample course notes, practice exams and learning outcomes into a study map.\n\n**Precision & Recall** and **F1 Score** are useful places to start. Ask me to explain a concept, try a practice question, or turn selected topics into a revision pack.\n\nThis is a clearly labeled demo with authored sample materials and illustrative starting mastery. Create your own course to analyze your documents with GPT-5.", "sourceIds": [lecture_id, exam_id], "isDemo": True}]}
    return {"id": uid("course"), "name": "Machine Learning", "code": "CS 229", "examDate": (date.today() + timedelta(days=14)).isoformat(), "isDemo": True, "topics": topics, "materials": materials, "sessions": [session], "readiness": readiness(topics), "packs": [], "_questions": [], "_attempts": []}
