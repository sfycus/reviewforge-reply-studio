from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Iterable


POSITIVE_WORDS = {
    "отлично",
    "хороший",
    "хорошая",
    "качественный",
    "быстро",
    "удобно",
    "понравилось",
    "рекомендую",
    "супер",
    "идеально",
}

NEGATIVE_WORDS = {
    "плохо",
    "сломался",
    "сломалась",
    "брак",
    "ужас",
    "долго",
    "грязный",
    "грязная",
    "не подошел",
    "не подошла",
    "разочарован",
    "разочарована",
}

ISSUE_TAGS = {
    "delivery": {"доставка", "курьер", "долго", "коробка", "упаковка", "помята"},
    "quality": {"брак", "сломался", "сломалась", "царапина", "дефект", "качество"},
    "size": {"размер", "маленький", "большой", "не подошел", "не подошла"},
    "price": {"дорого", "цена", "скидка", "дешевле"},
    "support": {"ответ", "поддержка", "продавец", "обратная связь"},
}


@dataclass(frozen=True)
class Review:
    text: str
    stars: int
    marketplace: str = "marketplace"
    customer_name: str | None = None


@dataclass(frozen=True)
class ReviewAnalysis:
    sentiment: str
    urgency: str
    score: float
    tags: tuple[str, ...]
    summary: str


def _contains_any(text: str, words: Iterable[str]) -> int:
    return sum(1 for word in words if word in text)


def _detect_tags(text: str) -> tuple[str, ...]:
    tags = [
        tag
        for tag, words in ISSUE_TAGS.items()
        if any(word in text for word in words)
    ]
    return tuple(tags)


def analyze_review(review: Review) -> ReviewAnalysis:
    text = review.text.lower()
    positive = _contains_any(text, POSITIVE_WORDS)
    negative = _contains_any(text, NEGATIVE_WORDS)
    tags = _detect_tags(text)

    star_score = (review.stars - 3) * 0.55
    text_score = positive * 0.28 - negative * 0.34
    issue_penalty = len(tags) * 0.18
    score = round(max(-1.0, min(1.0, star_score + text_score - issue_penalty)), 2)

    if score >= 0.35:
        sentiment = "positive"
    elif score <= -0.25:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    if sentiment == "negative" and (review.stars <= 2 or {"quality", "delivery"} & set(tags)):
        urgency = "high"
    elif sentiment == "negative" or len(tags) >= 2:
        urgency = "medium"
    else:
        urgency = "low"

    summary = _build_summary(sentiment, tags, review.stars)
    return ReviewAnalysis(sentiment, urgency, score, tags, summary)


def analyze_reviews(reviews: Iterable[Review]) -> dict[str, object]:
    reviews = list(reviews)
    analyses = [analyze_review(review) for review in reviews]
    if not reviews:
        return {"total": 0, "average_stars": 0, "negative_share": 0, "analyses": []}

    negative_count = sum(1 for item in analyses if item.sentiment == "negative")
    return {
        "total": len(reviews),
        "average_stars": round(mean(review.stars for review in reviews), 2),
        "negative_share": round(negative_count / len(reviews), 2),
        "analyses": analyses,
    }


def _build_summary(sentiment: str, tags: tuple[str, ...], stars: int) -> str:
    if sentiment == "positive":
        return "Customer is satisfied. Reply should reinforce trust and mention a relevant benefit."
    if not tags:
        return f"Customer left a {stars}-star review without a clear issue. Ask for details politely."

    readable_tags = ", ".join(tags)
    return f"Customer is unhappy about: {readable_tags}. Reply should acknowledge the problem and propose a next step."
