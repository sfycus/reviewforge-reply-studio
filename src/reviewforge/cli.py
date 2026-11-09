from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analyzer import Review
from .generator import render_markdown_report


def load_reviews(path: Path) -> list[Review]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [
        Review(
            text=item["text"],
            stars=int(item["stars"]),
            marketplace=item.get("marketplace", "marketplace"),
            customer_name=item.get("customer_name"),
        )
        for item in raw
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze marketplace reviews and generate reply drafts.")
    parser.add_argument("input", type=Path, help="Path to JSON file with reviews.")
    parser.add_argument("--brand", default="наш магазин", help="Brand or seller name.")
    parser.add_argument("--out", type=Path, help="Optional output markdown path.")
    args = parser.parse_args()

    reviews = load_reviews(args.input)
    report = render_markdown_report(reviews, brand=args.brand)

    if args.out:
        args.out.write_text(report, encoding="utf-8")
        print(f"Report saved to {args.out}")
    else:
        print(report)


if __name__ == "__main__":
    main()
