
from html.parser import HTMLParser
from urllib.request import Request, urlopen
from urllib.parse import urljoin, urlparse
from pathlib import Path
import json

# Cougar Aquatics Photo Album on GoMotion
ALBUM_URL = (
    "https://www.gomotionapp.com/team/waca/"
    "page/system/res/236105"
)

OUTPUT_FILE = Path("photos.json")

# Only use photos from our GoMotion heroes folder.
# PHOTO_FOLDER = "/waca/UserFiles/Image/heros/"
PHOTO_FOLDER = "/waca/UserFiles/Image/slides/"


class PhotoParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.photos = []
        self.seen = set()

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "img":
            return

        attributes = dict(attrs)

        src = (
            attributes.get("src")
            or attributes.get("data-src")
        )

        if not src:
            return

        url = urljoin(ALBUM_URL, src)
        parsed = urlparse(url)

        if parsed.netloc.lower() != "www.gomotionapp.com":
            return

        if not parsed.path.startswith(PHOTO_FOLDER):
            return

        if url not in self.seen:
            self.seen.add(url)
            self.photos.append(url)


def main():
    print("Reading Cougar Aquatics Photo Album...")

    request = Request(
        ALBUM_URL,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/html"
        }
    )

    with urlopen(request, timeout=30) as response:
        html = response.read().decode(
            "utf-8", errors="replace"
        )

    parser = PhotoParser()
    parser.feed(html)

    if not parser.photos:
        raise RuntimeError(
            "No album photos found. "
            "Existing slideshow photos will not be changed."
        )

    print(f"Found {len(parser.photos)} photos:")

    for number, photo in enumerate(parser.photos, 1):
        print(f"{number}. {photo}")

    OUTPUT_FILE.write_text(
        json.dumps(parser.photos, indent=2) + "\n",
        encoding="utf-8"
    )

    print("Photo list saved to photos.json")


if __name__ == "__main__":
    main()
