# coding=utf-8
import aiohttp
import re
from bs4 import BeautifulSoup
from dataclasses import dataclass


@dataclass
class Comment:
    user: str
    rating: str
    time: str
    location: str
    content: str

    def __init__(self, comment_item_tag: BeautifulSoup):
        self.user = comment_item_tag.select_one("span.comment-info a").text
        self.rating = (
            comment_item_tag.select_one("span.comment-info span.rating")["class"][0]
            .replace("allstar", "")
            .rstrip("0")
            or "0"
        ) + "星"
        self.time = comment_item_tag.select_one("span.comment-time")["title"]
        self.location = comment_item_tag.select_one("span.comment-location").text
        self.content = comment_item_tag.select_one(
            "p.comment-content > span.short"
        ).text


@dataclass
class Movie:
    url: str
    title: str
    year: str
    director: str
    score: str
    comment_num: str
    category: str
    thumbnail: str

    @classmethod
    async def create(cls, url):
        self = cls(
            url=url,
            title="",
            year="",
            director="",
            score="",
            comment_num="",
            category="",
            thumbnail="",
        )
        self.__headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Referer": "https://movie.douban.com/explore",
        }
        self.__html = await self.get_html()
        self.__soup = BeautifulSoup(self.__html, "html.parser")
        self.__info = self.get_info()
        self.title = self.get_title()
        self.year = self.get_year()
        self.director = self.__info["director"] or "未知"
        self.score = self.__info["score"] or "暂无评分"
        self.comment_num = self.__info["comment_num"] or "0"
        self.category = self.get_category() or "未知"
        self.thumbnail = self.get_thumbnail()
        return self

    async def get_html(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url, headers=self.__headers) as response:
                html = await response.text()
        return html

    def get_category(self):
        categorys = self.__soup.select("span[property='v:genre']")
        category = "/".join([category.text for category in categorys])
        return category

    def get_title(self):
        title = self.__soup.select_one("meta[property='og:title']")["content"]
        return title

    def get_year(self):
        year = self.__soup.select_one("#content > h1 > span.year").text
        year = re.search(r"\d{4}", year).group()
        return year

    def get_info(self):
        info = self.__soup.select_one("#info")
        director = info.select_one("div#info > span > span.attrs > a")
        director = director.text if director else ""
        score = self.__soup.select_one("strong[property='v:average']")
        score = score.text if score else ""
        commment_num_tag = self.__soup.select_one(
            "a[href='comments'] > span[property='v:votes']"
        )
        return {
            "director": director,
            "score": score,
            "comment_num": commment_num_tag.text if commment_num_tag else "0",
        }

    def get_thumbnail(self):
        thumbnail = self.__soup.select_one("div#mainpic a.nbgnbg img")
        return thumbnail["src"]

    async def get_comments(self, start: int, limit: int = 20):
        url = (
            f"{self.url}comments?start={start}&limit={limit}&status=P&sort=new_score"
            if self.url.endswith("/")
            else f"{self.url}/comments?start={start}&limit={limit}&status=P&sort=new_score"
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.__headers) as response:
                html = await response.text()

        soup = BeautifulSoup(html, "html.parser")
        comment_items = soup.select("div.comment-item")
        for comment_item in comment_items:
            yield Comment(comment_item)


@dataclass
class Search:
    search_text: str
    search_base_url: str
    search_result_total: int
    single_page_count: int
    page_count: int

    @classmethod
    async def create(cls, search_text):
        self = cls(
            search_text=search_text,
            search_base_url="https://search.douban.com/movie/subject_search",
            search_result_total=0,
            single_page_count=15,
            page_count=0,
        )
        self.__headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Referer": "https://movie.douban.com/explore",
        }
        self.search_result_total = await self.get_count()
        self.page_count = self.search_result_total // self.single_page_count + 1
        return self

    async def get_count(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.search_base_url,
                params={"search_text": self.search_text},
            ) as response:
                html_content = await response.text()

        soup = BeautifulSoup(html_content, "html.parser")
        script_tag = soup.find("script", string=re.compile(r"window\.__DATA__"))
        script_content = script_tag.string
        data_match = re.search(
            r"window\.__DATA__\s*=\s*({.*?});", script_content, re.DOTALL
        )
        if data_match:
            data_str = data_match.group(1)
            data_str = data_str.replace("\n", "").replace("\r", "")
            urls = re.findall(
                r'"url"\s*:\s*"(https://movie.douban.com/subject/[^"]+)"', data_str
            )
            urls = list(set(urls))
            total_match = re.search(r'"total"\s*:\s*(\d+)', data_str)
            total = int(total_match.group(1)) if total_match else 0
            return total

    async def get_urls(self, page: int):
        params = {
            "search_text": self.search_text,
        }
        if page > 1:
            params["start"] = (page - 1) * self.single_page_count

        async with aiohttp.ClientSession(headers=self.__headers) as session:
            async with session.get(
                self.search_base_url,
                params=params,
            ) as response:
                html_content = await response.text()

        soup = BeautifulSoup(html_content, "html.parser")
        script_tag = soup.find("script", string=re.compile(r"window\.__DATA__"))
        script_content = script_tag.string
        data_match = re.search(
            r"window\.__DATA__\s*=\s*({.*?});", script_content, re.DOTALL
        )
        if data_match:
            data_str = data_match.group(1)
            data_str = data_str.replace("\n", "").replace("\r", "")
            for match in re.finditer(
                r'"url"\s*:\s*"(https://movie.douban.com/subject/[^"]+)"', data_str
            ):
                yield match.group(1)
