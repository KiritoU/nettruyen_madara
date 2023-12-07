import sys
from time import sleep

from icecream import ic

from _db import Database
from crawler import Crawler
from settings import CONFIG
from telegram_noti import send_direct_message

LINKS = [
    # Manga links
    "https://www.nettruyenus.com/truyen-tranh/beat-and-motion-90092",
    "https://www.nettruyenus.com/truyen-tranh/nega-kun-va-posi-chan-274380",
]


def main():
    database_for_crawl_links = Database()
    print(f"Using database: {database_for_crawl_links} for crawl_links.py file...")
    _crawler = Crawler(database=database_for_crawl_links)

    try:
        is_netttruyen_domain_work = _crawler.is_nettruyen_domain_work()
        if not is_netttruyen_domain_work:
            send_direct_message(msg="Nettruyen domain might be changed!!!")
            sys.exit(1)

        for link in LINKS:
            _crawler.crawl_comic(href=link)
    except Exception as e:
        ic(e)


if __name__ == "__main__":
    main()
