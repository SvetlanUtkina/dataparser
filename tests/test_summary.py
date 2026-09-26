import unittest
from src.summary import render_summary


class SummaryTests(unittest.TestCase):
    def test_renders_listing_table_and_link(self):
        output = render_summary([{
            "brand": "audi", "model": "A4", "year": "2018",
            "mileage": "120 000", "price": "15 000 EUR",
            "url": "https://www.ss.lv/msg/example.html",
        }])
        self.assertIn("1 listings from this run.", output)
        self.assertIn("| audi | A4 | 2018 | 120 000 | 15 000 EUR |", output)
        self.assertIn("[Open listing](<https://www.ss.lv/msg/example.html>)", output)

    def test_untrusted_text_cannot_add_markup_or_unsafe_link(self):
        output = render_summary([{
            "model": "[click](evil)|<script>\nnew row", "url": "javascript:alert(1)",
        }])
        self.assertIn("&#91;click&#93;(evil)&#124;&lt;script&gt; new row", output)
        self.assertNotIn("javascript:", output)
        self.assertIn("Unavailable", output)


if __name__ == "__main__":
    unittest.main()
