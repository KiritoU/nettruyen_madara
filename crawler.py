import json
import logging
import re
import sys
from pathlib import Path
from time import sleep

import requests
from bs4 import BeautifulSoup
from slugify import slugify

from chapter import _chapter
from comic import _comic
from helper import helper
from madara import _madara
from settings import CONFIG

logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s", level=logging.INFO)


class Crawler:
    def crawl_chapter(
        self,
        comic_title: int,
        comic_id: int,
        comic_slug: str,
        chapter_name: str,
        chapter_href: str,
    ) -> None:
        soup = helper.crawl_soup(chapter_href)

        chapter_details = _chapter.get_chapter_detail(
            chapter_name=chapter_name, soup=soup
        )

        # with open("json/chapter.json", "w") as f:
        #     f.write(json.dumps(chapter_details, indent=4, ensure_ascii=False))

        content = _madara.get_download_chapter_content(
            comic_title=comic_title,
            comic_slug=comic_slug,
            chapter_details=chapter_details,
            chapter_name=chapter_name,
        )
        _madara.insert_chapter(
            comic_id=comic_id, chapter_name=chapter_name, content=content
        )
        logging.info(f"Inserted {chapter_name}")

    def crawl_comic(self, href: str):
        soup = helper.crawl_soup(href)
        comic_details = _comic.get_comic_details(href=href, soup=soup)

        comic_id = _madara.get_or_insert_comic(comic_details)
        logging.info(f"Got (or inserted) comic: {comic_id}")

        # with open("json/comic.json", "w") as f:
        #     f.write(json.dumps(comic_details, indent=4, ensure_ascii=False))

        if not comic_id:
            logging.error(f"Cannot crawl comic with: {href}")
            return

        chapters = comic_details.get("chapters", {})
        chapters_name = list(chapters.keys())
        inserted_chapters_slug = _madara.get_backend_chapters_slug(comic_id)

        for chapter_name in chapters_name[::-1]:
            chapter_slug = _chapter.get_chapter_slug(chapter_name=chapter_name)
            if chapter_slug in inserted_chapters_slug:
                continue

            chapter_href = chapters.get(chapter_name)
            self.crawl_chapter(
                comic_title=comic_details.get("title"),
                comic_id=comic_id,
                comic_slug=comic_details.get("slug"),
                chapter_name=chapter_name,
                chapter_href=chapter_href,
            )

    def crawl_item(self, item: BeautifulSoup):
        image = item.find("div", class_="image")
        figcaption = item.find("figcaption")

        href = ""
        if image:
            a = image.find("a")
            if a:
                href = a.get("href")

        if not href and figcaption:
            a = figcaption.find("a")
            if a:
                href = a.get("href")

        if not href:
            logging.error("[-] Could not find href for item")
            return

        self.crawl_comic(href=href)

    def crawl_page(self, page: int = 1):
        url = f"{CONFIG.NETTRUYEN_HOMEPAGE}/?page={page}"
        soup = helper.crawl_soup(url)

        div_items = soup.find("div", class_="items")
        if not div_items:
            return 0

        items = div_items.find_all("div", class_="item")

        for item in items:
            self.crawl_item(item=item)

        return 1

    def get_nettruyen_last_page(self):
        url = f"{CONFIG.NETTRUYEN_HOMEPAGE}/?page=1"
        soup = helper.crawl_soup(url)

        try:
            pagination = soup.find("ul", class_="pagination")
            lis = pagination.find_all("li")
            last_li = lis[-1]
            a = last_li.find("a")
            href = a.get("href")
            pattern = re.compile(r"page=(\d+)")
            matches = pattern.search(url)
            page = matches.group(1)
            return int(page)
        except:
            return CONFIG.NETTRUYEN_LAST_PAGE

    def is_nettruyen_domain_work(self):
        for _ in range(5):
            try:
                response = helper.download_url(CONFIG.NETTRUYEN_HOMEPAGE)
                if response.status_code == 200:
                    return True

            except Exception as e:
                pass

            sleep(5)

        return False
