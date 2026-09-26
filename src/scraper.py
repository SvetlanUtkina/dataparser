import json
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.ss.lv"
BRAND = "bmw"
OUTPUT_FILE = Path("data/listings.json")


def fetch_results(brand: str) -> list[dict]:
    url = f"{BASE_URL}/lv/transport/cars/{brand}/filter/"

    with requests.Session() as session:
        response = session.get(url, timeout=20)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    # Same row selector and ten-row limit as your original script.
    for row in soup.select("tr[id^=tr_]")[:10]:
        cols = row.find_all("td")
        title_tag = row.select_one("a.am")

        # Skip rows that don't contain a usable listing.
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
    listings = fetch_results(BRAND)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(listings, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Saved {len(listings)} listings to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()