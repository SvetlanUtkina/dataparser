import argparse
import re
import json
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.ss.lv"
sorting_options = {
    "date_desc": "",
    "date_asc": "fDgSeF4S.html",
    "brand_asc": "fDgSeF4QFDwT.html",
    "brand_desc": "fDgSeF4QFDwS.html",
    "year_asc": "fDgSeF4SHTwT.html",
    "year_desc": "fDgSeF4SHTwS.html",
    "volume_asc": "fDgSeF4SEDwT.html",
    "volume_desc": "fDgSeF4SEDwS.html",
    "mileage_asc": "fDgSeF4SEzwT.html",
    "mileage_desc": "fDgSeF4SEzwS.html",
    "price_asc": "fDgSeF4belM=.html",
    "price_desc": "fDgSeF4belI=.html",
}


def brand_slug(value: str) -> str:
    value = value.lower()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
        raise argparse.ArgumentTypeError("Use a brand URL name such as bmw or alfa-romeo")
    return value
OUTPUT_FILE = Path("data/listings.json")


def fetch_results(brand: str, sort: str = "date_desc") -> list[dict]:
    url = f"{BASE_URL}/lv/transport/cars/{brand}/filter/" + sorting_options[sort]

    with requests.Session() as session:
        response = session.get(url, timeout=20)
        response.raise_for_status()

    return parse_results(response.text, brand)


def parse_results(html: str, brand: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    results = []

    
    for row in soup.select("tr[id^=tr_]")[:10]:
        cols = row.find_all("td")
        title_tag = row.select_one("a.am")

       
        if title_tag is None or not title_tag.get("href"):
            continue
        if len(cols) < 8:
            continue

        link = urljoin(BASE_URL, title_tag["href"])
        model = cols[3].get_text(strip=True)
        year = cols[4].get_text(strip=True)
        mileage = cols[6].get_text(strip=True)
        price = cols[7].get_text(strip=True).replace("\xa0", " ")

        results.append({
            "brand": brand,
            "model": model,
            "year": year,
            "mileage": mileage,
            "price": price,
            "url": link,
        })

    if not results:
        raise RuntimeError(
            "No listings parsed. The page may be empty or its HTML may have changed."
        )

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect SS.lv car listings")
    parser.add_argument("--brand", type=brand_slug, default="bmw", help="Brand URL name, e.g. audi")
    parser.add_argument("--sort", choices=sorting_options, default="date_desc")
    args = parser.parse_args()
    listings = fetch_results(args.brand, args.sort)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(listings, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Saved {len(listings)} listings to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
