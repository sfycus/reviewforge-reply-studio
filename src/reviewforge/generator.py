from __future__ import annotations

from dataclasses import dataclass

from .analyzer import Review, ReviewAnalysis, analyze_review


@dataclass(frozen=True)
class ReplyDraft:
    text: str
    tone: str
    escalation_required: bool


def generate_reply(review: Review, brand: str = "наш магазин", tone: str = "friendly") -> ReplyDraft:
    analysis = analyze_review(review)
    greeting = _greeting(review)
    sign = f"С уважением, команда {brand}"

    if analysis.sentiment == "positive":
        body = (
            "Спасибо за отзыв и высокую оценку. Рады, что товар подошел и оставил хорошее впечатление. "
            "Будем рады видеть вас снова."
        )
        return ReplyDraft(f"{greeting} {body} {sign}.", tone, escalation_required=False)

    if analysis.sentiment == "neutral":
        body = (
            "Спасибо, что поделились впечатлением. Мы внимательно относимся к обратной связи и используем ее, "
            "чтобы улучшать карточку товара, комплектацию и описание."
        )
        return ReplyDraft(f"{greeting} {body} {sign}.", tone, escalation_required=False)

    apology = "Нам жаль, что покупка оставила такое впечатление."
    issue_line = _issue_line(analysis)
    next_step = (
        "Пожалуйста, напишите нам через раздел обращений, чтобы мы смогли проверить ситуацию по заказу "
        "и предложить подходящее решение."
    )

    if tone == "short":
        text = f"{greeting} {apology} {next_step} {sign}."
    else:
        text = f"{greeting} {apology} {issue_line} {next_step} {sign}."

    return ReplyDraft(text, tone, escalation_required=analysis.urgency == "high")


def render_markdown_report(reviews: list[Review], brand: str = "наш магазин") -> str:
    lines = [
        "# ReviewForge Reply Report",
        "",
        f"Brand: **{brand}**",
        f"Reviews processed: **{len(reviews)}**",
        "",
    ]

    for index, review in enumerate(reviews, start=1):
        analysis = analyze_review(review)
        reply = generate_reply(review, brand=brand)
        tags = ", ".join(analysis.tags) if analysis.tags else "none"
        lines.extend(
            [
                f"## Review #{index}",
                "",
                f"- Stars: **{review.stars}**",
                f"- Sentiment: **{analysis.sentiment}**",
                f"- Urgency: **{analysis.urgency}**",
                f"- Tags: **{tags}**",
                f"- Summary: {analysis.summary}",
                "",
                "**Reply draft:**",
                "",
                reply.text,
                "",
            ]
        )

    return "\n".join(lines)


def _greeting(review: Review) -> str:
    if review.customer_name:
        return f"{review.customer_name}, здравствуйте!"
    return "Здравствуйте!"


def _issue_line(analysis: ReviewAnalysis) -> str:
    if "delivery" in analysis.tags:
        return "Мы понимаем, что проблемы с доставкой или упаковкой могут испортить впечатление от покупки."
    if "quality" in analysis.tags:
        return "Мы обязательно передадим информацию по качеству товара в проверку."
    if "size" in analysis.tags:
        return "Понимаем, что несовпадение размера особенно неприятно при онлайн-покупке."
    return "Спасибо, что подробно описали ситуацию."
