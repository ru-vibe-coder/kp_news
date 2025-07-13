import scrapy
# import base64
import requests
from kp_news.items import KpNewsItem


class KpSpider(scrapy.Spider):
    name = "kp_spider"
    allowed_domains = ["kp.ru"]
    start_urls = ["https://www.kp.ru/online/"]

    def __init__(self, count=10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.count = int(count)

    def parse(self, response):
        latest_url = response.xpath(
            '//a[contains(@href,"/online/news/")]/@href'
        ).get()
        if not latest_url:
            self.logger.error("❌ Не удалось найти свежую новость на странице")
            return

        latest_id = int(latest_url.rstrip("/").split("/")[-1])
        self.logger.info(f"✅ Найден последний id: {latest_id}")

        for i in range(latest_id, latest_id - self.count, -1):
            url = f"https://www.kp.ru/online/news/{i}/"
            yield scrapy.Request(url, callback=self.parse_article)

    def parse_article(self, response):
        if response.status != 200:
            self.logger.info(f"⚠️ Пропущено {response.url} — статус {response.status}")
            return

        item = KpNewsItem()
        item["source_url"] = response.url
        item["title"] = response.xpath("//h1/text()").get(default="").strip()
        item["description"] = response.xpath("//meta[@name='description']/@content").get(default="").strip()

        # article_text
        item["article_text"] = "https://www.kp.ru/online/"

        # publication_datetime
        item["publication_datetime"] = response.xpath(
            '//span[contains(@class, "sc-j7em19")]/text()'
        ).get(default="").strip()

        # header_photo_url и base64
        header_photo_url = response.xpath("//meta[@property='og:image']/@content").get(default="").strip()
        item["header_photo_url"] = header_photo_url
        if header_photo_url:
            try:
                img_resp = requests.get(header_photo_url)
                img_resp.raise_for_status()
                item["header_photo_base64"] = ""
                # item["header_photo_base64"] = base64.b64encode(img_resp.content).decode("utf-8")
            except Exception as e:
                self.logger.warning(f"Не удалось скачать фото {header_photo_url}: {e}")
                item["header_photo_base64"] = ""

        # keywords
        item["keywords"] = response.xpath("//meta[@name='keywords']/@content").get(default="").split(",")

        # authors
        authors = response.xpath(
            '//a[contains(@href, "/daily/author/")]/span/text()'
        ).getall()
        item["authors"] = [a.strip() for a in authors if a.strip()]

        yield item
