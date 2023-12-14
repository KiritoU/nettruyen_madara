import logging
import mimetypes
import os
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep

import boto3
import requests
from bs4 import BeautifulSoup
from slugify import slugify

from settings import CONFIG

logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s", level=logging.INFO)


s3 = boto3.client(
    "s3",
    aws_access_key_id=CONFIG.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=CONFIG.AWS_SECRET_ACCESS_KEY,
)


class Helper:
    def get_header(self):
        header = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E150",  # noqa: E501
            "Accept-Encoding": "gzip, deflate",
            "Cache-Control": "max-age=0",
            "Accept-Language": "vi-VN",
            "Referer": f"{CONFIG.NETTRUYEN_HOMEPAGE}/",
        }
        return header

    def download_url(self, url):
        return requests.get(url, headers=self.get_header())

    def crawl_soup(self, url):
        logging.info(f"[+] Crawling {url}")

        html = self.download_url(url)
        soup = BeautifulSoup(html.content, "html.parser")

        return soup

    def error_log(self, msg, filename: str = "failed.txt"):
        Path("log").mkdir(parents=True, exist_ok=True)
        with open(f"log/{filename}", "a") as f:
            print(f"{msg}\n{'-' * 80}", file=f)

    def save_image(
        self,
        image_url: str,
        comic_seo: str = "",
        chap_seo: str = "",
        image_name: str = "0.jpg",
        is_thumb: bool = False,
        overwrite: bool = False,
    ) -> str:
        if not is_thumb and CONFIG.SAVE_CHAPTER_IMAGES_TO_S3:
            try:
                file_name = slugify(
                    f"{comic_seo}-{chap_seo}-{image_name.replace('.jpg', '')}"
                )
                imageResponse = requests.get(
                    image_url, headers=helper.get_header(), stream=True
                ).raw
                content_type = imageResponse.headers["content-type"]
                extension = mimetypes.guess_extension(content_type)
                if not extension:
                    extension = ".jpg"
                s3.upload_fileobj(
                    imageResponse, CONFIG.S3_BUCKET, file_name + extension
                )
                return file_name + extension, False
            except:
                return "", True

        save_full_path = os.path.join(CONFIG.IMAGE_SAVE_PATH, comic_seo, chap_seo)

        Path(save_full_path).mkdir(parents=True, exist_ok=True)
        Path(CONFIG.THUMB_SAVE_PATH).mkdir(parents=True, exist_ok=True)

        save_image = os.path.join(save_full_path, image_name)
        if is_thumb:
            save_image = os.path.join(CONFIG.THUMB_SAVE_PATH, image_name)

        is_not_saved = not Path(save_image).is_file()

        if overwrite or is_not_saved:
            image = self.download_url(image_url)
            with open(save_image, "wb") as f:
                f.write(image.content)
            is_not_saved = True

        return [save_image, is_not_saved]


helper = Helper()
