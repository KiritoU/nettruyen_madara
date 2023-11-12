from bs4 import BeautifulSoup
from slugify import slugify


class Chapter:
    def get_chapter_slug(self, chapter_name: str) -> str:
        return slugify(chapter_name)

    def get_chapter_detail(self, chapter_name: str, soup: BeautifulSoup) -> dict:
        result = {}

        ctl00_divCenter = soup.find("div", {"id": "ctl00_divCenter"})
        if not ctl00_divCenter:
            return result

        page_chapters = ctl00_divCenter.find_all("div", class_="page-chapter")
        for page_chapter in page_chapters:
            img = page_chapter.find("img")
            if not img:
                continue

            img_alt = img.get("alt")
            img_src = img.get("src")
            img_data_index = img.get("data-index")

            if not img_src or not img_data_index:
                continue

            if not img_src.startswith("https:"):
                img_src = "https:" + img_src

            result[img_data_index] = {
                "alt": img_alt,
                "src": img_src,
            }

        return result


_chapter = Chapter()
