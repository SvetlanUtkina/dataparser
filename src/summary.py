"""Render saved listings as a GitHub Actions Markdown summary."""
import html
import json
from pathlib import Path
from urllib.parse import quote, urlsplit


def cell(value: object) -> str:
    text = html.escape(" ".join(str(value or "").split()), quote=True)
    for character in "\\`*_{}[]|~!":
        text = text.replace(character, f"&#{ord(character)};")
    return text


def render_summary(listings: list[dict]) -> str:
    lines = [
        "## Car listings", "", f"{len(listings)} listings from this run.", "",
        "| Brand | Model | Year | Mileage | Price | Listing |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for listing in listings:
        values = [cell(listing.get(key)) for key in ("brand", "model", "year", "mileage", "price")]
        url = str(listing.get("url") or "")
        try:
            parsed = urlsplit(url)
            valid = parsed.scheme == "https" and parsed.hostname in {"ss.lv", "www.ss.lv"} and not parsed.username and not parsed.password
        except ValueError:
            valid = False
        link = f"[Open listing](<{quote(url, safe=':/?=&%#')}>)" if valid else "Unavailable"
        lines.append("| " + " | ".join(values + [link]) + " |")
    lines.extend(["", "Download the JSON and CSV files from this run's Artifacts section.", ""])
    return "\n".join(lines)


if __name__ == "__main__":
    listings = json.loads(Path("data/listings.json").read_text(encoding="utf-8-sig"))
    print(render_summary(listings))
