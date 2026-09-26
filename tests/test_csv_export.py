import csv
import tempfile
import unittest
from pathlib import Path

from src.scraper import write_csv


class CsvExportTests(unittest.TestCase):
    def test_export_preserves_columns_unicode_and_quoted_text(self):
        listing = {
            "brand": "audi", "model": 'A4, "special"\nedition',
            "year": "2018", "mileage": "120 000", "price": "15 000 \u20ac",
            "url": "https://www.ss.lv/example.html",
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data" / "listings.csv"
            write_csv([listing], path)
            with path.open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.reader(handle))
        self.assertEqual(rows[0], ["Brand", "Model", "Year", "Mileage", "Price", "Listing URL"])
        self.assertEqual(rows[1], list(listing.values()))

    def test_formula_like_values_are_exported_as_text(self):
        values = ["=1+1", " +1", "-1", "@SUM(A1)", "\t=1", "\n=1"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "listings.csv"
            write_csv([{"model": value} for value in values], path)
            with path.open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
        self.assertEqual([row["Model"] for row in rows], ["'" + value for value in values])


if __name__ == "__main__":
    unittest.main()
