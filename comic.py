from bs4 import BeautifulSoup
from slugify import slugify


class Comic:
    def get_title(self, item_detail: BeautifulSoup) -> str:
        title = item_detail.find("h1", class_="title-detail")
        if not title:
            return ""

        return title.text.strip()

    def get_cover_url(self, item_detail: BeautifulSoup) -> str:
        img = item_detail.find("img")
        if not img:
            return ""
        cover_url = img.get("src", "")
        if cover_url and not cover_url.startswith("https"):
            cover_url = "https:" + cover_url

        return cover_url

    def get_list_info(self, item_detail: BeautifulSoup) -> dict:
        result = {}
        list_info = item_detail.find("ul", class_="list-info")
        if list_info:
            li_elements = list_info.find_all("li")
            for li in li_elements:
                p = li.find("p", class_="name")
                if not p:
                    continue

                key = slugify(p.text)
                value = li.text.replace(p.text, "").strip()
                if value:
                    result[key] = value

        return result

    def get_description(self, item_detail: BeautifulSoup) -> str:
        detail_content = item_detail.find("div", class_="detail-content")
        if not detail_content:
            return ""

        p = detail_content.find("p")
        if not p:
            return ""

        return p.text

    def get_chapters_href(self, item_detail: BeautifulSoup) -> dict:
        nt_listchapter = item_detail.find("div", {"id": "nt_listchapter"})
        if not nt_listchapter:
            return {}

        chapters_dict = {}
        li_elements = nt_listchapter.find_all("li")
        for li in li_elements:
            chapter = li.find("div", class_="chapter")
            if not chapter:
                continue

            a = chapter.find("a")
            if not a:
                continue

            chapter_name = chapter.text.strip()
            href = a.get("href")
            if href:
                chapters_dict[chapter_name] = href

        return chapters_dict

    def get_comic_details(self, href: str, soup: BeautifulSoup) -> dict:
        item_detail = soup.find("article", {"id": "item-detail"})
        if not item_detail:
            return {}

        title = self.get_title(item_detail=item_detail)
        slug = href.strip().strip("/").split("/")[-1]
        cover_url = self.get_cover_url(item_detail=item_detail)
        description = self.get_description(item_detail=item_detail)
        detail_list_info = self.get_list_info(item_detail=item_detail)

        chapters_dict = self.get_chapters_href(item_detail=item_detail)

        return {
            "title": title,
            "slug": slug,
            "cover_url": cover_url,
            "description": description,
            **detail_list_info,
            "chapters": chapters_dict,
        }


_comic = Comic()
