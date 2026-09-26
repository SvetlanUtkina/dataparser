import unittest
from unittest.mock import patch

from src.scraper import brand_slug, fetch_results, parse_results
import argparse


HTML = """
<table><tr id="tr_123">
<td></td><td></td>
<td><a class="am" href="/msg/lv/transport/cars/bmw/example.html">BMW</a></td>
<td>320</td><td>2018</td><td>2.0</td><td>120 000</td><td>15&nbsp;000 EUR</td>
</tr></table>
"""


class ParserTests(unittest.TestCase):
    def test_extracts_listing_fields(self):
        self.assertEqual(parse_results(HTML, "bmw"), [{
            "brand": "bmw", "model": "320", "year": "2018",
            "mileage": "120 000", "price": "15 000 EUR",
            "url": "https://www.ss.lv/msg/lv/transport/cars/bmw/example.html",
        }])

    def test_empty_page_raises_error(self):
        with self.assertRaises(RuntimeError):
            parse_results("<html></html>", "bmw")

    @patch("src.scraper.requests.Session")
    def test_sorting_and_brand_are_sent_to_website(self, session_class):
        session = session_class.return_value.__enter__.return_value
        session.get.return_value.text = HTML
        results = fetch_results("audi", "price_asc")
        session.get.assert_called_once_with(
            "https://www.ss.lv/lv/transport/cars/audi/filter/fDgSeF4belM=.html",
            timeout=20,
        )
        session.get.return_value.raise_for_status.assert_called_once()
        self.assertEqual(results[0]["brand"], "audi")

    def test_brand_rejects_path_components(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            brand_slug("../other")


if __name__ == "__main__":
    unittest.main()
