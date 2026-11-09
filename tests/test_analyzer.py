import unittest

from reviewforge import Review, analyze_review, generate_reply


class ReviewForgeTests(unittest.TestCase):
    def test_positive_review_is_low_urgency(self):
        analysis = analyze_review(Review(text="Отлично, хороший товар, рекомендую", stars=5))

        self.assertEqual(analysis.sentiment, "positive")
        self.assertEqual(analysis.urgency, "low")

    def test_quality_complaint_is_high_urgency(self):
        analysis = analyze_review(Review(text="Брак, коробка помята, качество ужас", stars=1))

        self.assertEqual(analysis.sentiment, "negative")
        self.assertEqual(analysis.urgency, "high")
        self.assertIn("quality", analysis.tags)

    def test_reply_generation_mentions_next_step(self):
        draft = generate_reply(
            Review(text="сломалась через день, продавец не ответил", stars=1),
            brand="SmartSeller",
        )

        self.assertTrue(draft.escalation_required)
        self.assertIn("SmartSeller", draft.text)
        self.assertIn("раздел обращений", draft.text)


if __name__ == "__main__":
    unittest.main()
