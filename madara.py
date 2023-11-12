import logging
import time
from datetime import datetime

from slugify import slugify

from _db import database
from chapter import _chapter
from helper import helper
from settings import CONFIG

logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s", level=logging.INFO)


class Madara:
    def get_backend_chapters_slug(self, comic_id: int) -> list:
        chapters = database.select_all_from(
            table=f"manga_chapters",
            condition=f'post_id="{comic_id}"',
        )

        chapters_slug = [chapter[5] for chapter in chapters]
        return chapters_slug

    def insert_postmeta(self, postmeta_data: list, table: str = "postmeta"):
        database.insert_into(table=table, data=postmeta_data, is_bulk=True)

    def get_timeupdate(self) -> str:
        # TODO: later
        timeupdate = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

        return timeupdate

    def get_comic_timeupdate(self) -> str:
        # TODO
        return int(time.time())

    def download_and_save_thumb(self, cover_url: str):
        try:
            # Download the cover image
            image_name = cover_url.split("/")[-1]
            thumb_image_name, is_not_saved = helper.save_image(
                image_url=cover_url, image_name=image_name, is_thumb=True
            )

            return f"covers/{image_name}"
        except Exception:
            return CONFIG.DEFAULT_THUMB

    def insert_thumb(self, cover_url: str) -> int:
        if not cover_url:
            return 0

        saved_thumb_url = self.download_and_save_thumb(cover_url=cover_url)

        thumb_name = saved_thumb_url.split("/")[-1]

        timeupdate = self.get_timeupdate()
        thumb_post_data = (
            0,
            timeupdate,
            timeupdate,
            "",
            thumb_name,
            "",
            "inherit",
            "open",
            "closed",
            "",
            slugify(thumb_name),
            "",
            "",
            timeupdate,
            timeupdate,
            "",
            0,
            "",
            0,
            "attachment",
            "image/png",
            0,
            # "",
        )

        thumb_id = database.insert_into(table="posts", data=thumb_post_data)

        database.insert_into(
            table="postmeta",
            data=(thumb_id, "_wp_attached_file", saved_thumb_url),
        )

        return thumb_id

    def insert_terms(
        self,
        post_id: int,
        terms: str,
        taxonomy: str,
        is_title: str = False,
        term_slug: str = "",
    ):
        try:
            terms = (
                [term.strip() for term in terms.split("-")] if not is_title else [terms]
            )
        except Exception as e:
            logging.error(f"[-] Error in insert terms: {terms}")
            return

        term_ids = []
        for term in terms:
            term_insert_slug = slugify(term_slug) if term_slug else slugify(term)
            cols = "tt.term_taxonomy_id, tt.term_id"
            table = (
                f"{CONFIG.TABLE_PREFIX}term_taxonomy tt, {CONFIG.TABLE_PREFIX}terms t"
            )
            condition = f't.slug = "{term_insert_slug}" AND tt.term_id=t.term_id AND tt.taxonomy="{taxonomy}"'

            query = f"SELECT {cols} FROM {table} WHERE {condition}"

            be_term = database.select_with(query=query)
            if not be_term:
                term_id = database.insert_into(
                    table="terms",
                    data=(term, term_insert_slug, 0),
                )
                term_taxonomy_count = 1 if taxonomy == "seasons" else 0
                term_taxonomy_id = database.insert_into(
                    table="term_taxonomy",
                    data=(term_id, taxonomy, "", 0, term_taxonomy_count),
                )
                term_ids = [term_taxonomy_id, True]
            else:
                term_taxonomy_id = be_term[0][0]
                term_id = be_term[0][1]
                term_ids = [term_taxonomy_id, False]

            try:
                database.insert_into(
                    table="term_relationships",
                    data=(post_id, term_taxonomy_id, 0),
                )
            except:
                pass

        return term_ids

    def insert_comic(self, comic_data: dict):
        thumb_id = self.insert_thumb(comic_data.get("cover_url"))
        timeupdate = self.get_timeupdate()
        data = (
            0,
            timeupdate,
            timeupdate,
            comic_data.get("description", ""),
            comic_data["title"],
            "",
            "publish",
            "open",
            "closed",
            "",
            comic_data.get("slug", ""),
            "",
            "",
            timeupdate,
            timeupdate,
            "",
            0,
            "",
            0,
            "wp-manga",
            "",
            0,
            # "",
        )

        try:
            comic_id = database.insert_into(table=f"posts", data=data)
        except Exception as e:
            helper.error_log(
                msg=f"Failed to insert comic\n{e}", filename="helper.comic_id.log"
            )
            return 0

        postmeta_data = [
            (comic_id, "_latest_update", f"{self.get_comic_timeupdate()}"),
            (comic_id, "_thumbnail_id", thumb_id),
            (
                comic_id,
                "_wp_manga_status",
                comic_data.get("tinh-trang", "Đang cập nhật"),
            ),
            (comic_id, "_wp_manga_alternative", comic_data.get("ten-khac", "")),
            (comic_id, "manga_adult_content", ""),
            (comic_id, "manga_title_badges", "new"),
        ]

        self.insert_postmeta(postmeta_data)

        self.insert_terms(
            post_id=comic_id,
            terms=comic_data.get("tac-gia", ""),
            taxonomy="wp-manga-author",
        )
        self.insert_terms(
            post_id=comic_id,
            terms=comic_data.get("the-loai", ""),
            taxonomy="wp-manga-genre",
        )

        return comic_id

    def get_or_insert_comic(self, comic_details: dict) -> int:
        condition = f"""post_name = '{comic_details["slug"]}'"""
        be_post = database.select_all_from(table=f"posts", condition=condition)
        if not be_post:
            return self.insert_comic(comic_data=comic_details)
        else:
            return be_post[0][0]

    def get_download_chapter_content(
        self, comic_slug: str, chapter_details: dict, chapter_name: str
    ):
        result = []
        image_numbers = list(chapter_details.keys())
        # sorted(image_numbers, key=lambda x: int(x))

        for image_number in image_numbers:
            image_details = chapter_details[image_number]
            image_alt = image_details.get("alt")
            image_src = image_details.get("src")
            saved_image, _ = helper.save_image(
                image_url=image_src,
                comic_seo=comic_slug,
                chap_seo=_chapter.get_chapter_slug(chapter_name=chapter_name),
                image_name=f"{image_number}.jpg",
            )
            img_rrc = saved_image.replace(f"{CONFIG.IMAGE_SAVE_PATH}", "")
            result.append(
                f'"{int(image_number)+1}"'
                + ':{"src":'
                + f'"{img_rrc}","mime":"image/jpeg"'
                + "}"
            )

        return "{" + ",".join(result) + "}"

    def insert_chapter(
        self,
        comic_id: int,
        chapter_name: str,
        content: str,
    ):
        data = (
            comic_id,
            0,
            chapter_name,
            "",
            _chapter.get_chapter_slug(chapter_name=chapter_name),
            "local",
            self.get_timeupdate(),
            self.get_timeupdate(),
            0,
            "",
            "",
            0,
            "",
        )
        chapter_id = database.insert_into(table=f"manga_chapters", data=data)

        database.insert_into(
            table=f"manga_chapters_data",
            data=(chapter_id, "local", content),
        )


_madara = Madara()
