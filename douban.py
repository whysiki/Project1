# coding=utf-8
import aiohttp
import re
from bs4 import BeautifulSoup
from dataclasses import dataclass
from functools import wraps, total_ordering
import random
from loguru import logger
import asyncio
from rich import print
import requests

logger.add(
    "log/douban.log",
    rotation="1 day",
    retention="7 days",
    level="INFO",
    format="{level} {message}",
    mode="a",
)

IP_BANED_RETRY_TIMES = 10


def check_if_banned(html: str):
    if (
        "有异常请求从你的 IP 发出" in html  # c1
        or "IP被封禁" in html  # c2
        or "异常请求" in html  # c3
        or (
            tz_tag := BeautifulSoup(html, "html.parser").select_one(
                "body > div:nth-child(1) > div:nth-child(1) > h1:nth-child(2)"
            )
            and tz_tag.text == "登录跳转"
        )  # c4
    ):
        raise Exception("IP被封禁")


def ip_baned_retry_decorator(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        for attempt in range(IP_BANED_RETRY_TIMES):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if "IP被封禁" in str(e):
                    wait_time = random.randint(1, 2)
                    logger.warning(
                        f"Attempt {attempt + 1} failed due to IP ban. Retrying in {wait_time} seconds..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    raise e
        raise Exception("IP被封禁")

    return wrapper


def error_return_a_default_value(errortype, default_value):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except errortype:
                logger.warning(
                    f"Error: {errortype} on {func.__name__}, return default value: {default_value}"
                )
                return default_value

        return wrapper

    return decorator


# def hashable(cls):
#     cls.__hash__ = lambda self: hash(
#         (self.user, self.rating, self.time, self.location, self.content)
#     )
#     return cls


@dataclass
class Comment:
    user: str = ""
    rating: str = ""
    time: str = ""
    location: str = ""
    content: str = ""

    def __init__(self, comment_item_tag: BeautifulSoup):
        self.__comment_item_tag = comment_item_tag
        self.user = self.extract_user()
        self.rating = self.extract_rating()
        self.time = self.extract_time()
        self.location = self.extract_location()
        self.content = self.extract_content()

    def extract_user(self) -> str:
        return self.__comment_item_tag.select_one("span.comment-info a").text

    @error_return_a_default_value(TypeError, "暂无评分")
    @error_return_a_default_value(AttributeError, "暂无评分")
    def extract_rating(self) -> str:
        ratingtag = self.__comment_item_tag.select_one("span.comment-info span.rating")
        return (ratingtag["class"][0].replace("allstar", "").rstrip("0") or "0") + "星"

    def extract_time(self) -> str:
        return self.__comment_item_tag.select_one("span.comment-time")["title"]

    @error_return_a_default_value(AttributeError, "未知地点")
    def extract_location(self) -> str:
        return self.__comment_item_tag.select_one("span.comment-location").text

    def extract_content(self) -> str:
        return self.__comment_item_tag.select_one("p.comment-content > span.short").text


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

    def __post_init__(self):
        self.__current_start = 0

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
        self.title = self.get_title()  # 电影名称
        self.year = self.get_year()  # 上映年份
        self.director = self.get_director()  # 导演
        self.score = self.get_score() or "未知评分"  # 评分
        self.comment_num = self.get_comment_num()  # 评论数 评价人数
        self.category = self.get_category()  # 类别
        self.thumbnail = self.get_thumbnail()  # 缩略图
        return self

    @ip_baned_retry_decorator
    async def get_html(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url, headers=self.__headers) as response:
                html = await response.text()
        check_if_banned(html)
        return html

    @error_return_a_default_value(AttributeError, "未知类别")
    def get_category(self):
        categorys = self.__soup.select("span[property='v:genre']")
        category = "/".join([category.text for category in categorys])
        return category

    @error_return_a_default_value(AttributeError, "未知标题")
    def get_title(self):
        title_tag1 = self.__soup.select_one("meta[property='og:title']")
        title_tag2 = self.__soup.select_one(
            "#content > h1 > span[property='v:itemreviewed']"
        )
        title_tag = title_tag1 or title_tag2
        return title_tag["content"]

    @error_return_a_default_value(AttributeError, "未知年份")
    def get_year(self):
        year_text = self.__soup.select_one("#content > h1 > span.year").text
        year_year_text = re.search(r"\d{4}", year_text).group()
        return year_year_text

    @error_return_a_default_value(AttributeError, "未知导演")
    def get_director(self):
        try:
            info = self.__soup.select_one("#info")
            director = info.select_one("div#info > span > span.attrs > a")
            return director.text
        except Exception as e:
            logger.debug(
                f"A {type(e)} occurred when getting director: {str(e)}, movie url: {self.url}"
            )
            raise e

    @error_return_a_default_value(AttributeError, "未知评分")
    def get_score(self):
        score = self.__soup.select_one("strong[property='v:average']")
        return score.text

    @error_return_a_default_value(AttributeError, "0")
    def get_comment_num(self):
        commment_num_tag = self.__soup.select_one(
            "a[href='comments'] > span[property='v:votes']"
        )
        return commment_num_tag.text

    def get_thumbnail(self):
        thumbnail = self.__soup.select_one("div#mainpic a.nbgnbg img")
        return thumbnail["src"]

    async def get_comments_sync(self, limit: int = 20):  # 短评
        while self.__current_start < int(self.comment_num):
            print(f"Current Comment Start: {self.__current_start}")
            url = (
                f"{self.url}comments?start={self.__current_start}&limit={limit}&status=P&sort=new_score"
                if self.url.endswith("/")
                else f"{self.url}/comments?start={self.__current_start}&limit={limit}&status=P&sort=new_score"
            )
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.__headers) as response:
                    html = await response.text()

            soup = BeautifulSoup(html, "html.parser")
            comment_items = soup.select("div.comment-item")
            for comment_item in comment_items:
                self.__current_start += 1
                yield Comment(comment_item)

    def get_comments_sync(self, limit: int = 20):  # 短评
        while self.__current_start < int(self.comment_num):
            print(f"Current Comment Start: {self.__current_start}")
            url = (
                f"{self.url}comments?start={self.__current_start}&limit={limit}&status=P&sort=new_score"
                if self.url.endswith("/")
                else f"{self.url}/comments?start={self.__current_start}&limit={limit}&status=P&sort=new_score"
            )
            response = requests.get(url, headers=self.__headers)
            html = response.text

            soup = BeautifulSoup(html, "html.parser")
            comment_items = soup.select("div.comment-item")
            for comment_item in comment_items:
                self.__current_start += 1
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
        self.__html = await self.get_html()
        self.__soup = BeautifulSoup(self.__html, "html.parser")
        self.search_result_total = await self.get_count()
        self.page_count = self.search_result_total // self.single_page_count + 1
        return self

    @ip_baned_retry_decorator
    async def get_html(self):
        async with aiohttp.ClientSession(headers=self.__headers) as session:
            async with session.get(
                self.search_base_url,
                params={"search_text": self.search_text},
            ) as response:
                html = await response.text()
            check_if_banned(html)
        return html

    async def get_count(self):
        script_tag = self.__soup.find("script", string=re.compile(r"window\.__DATA__"))
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
        script_tag = self.__soup.find("script", string=re.compile(r"window\.__DATA__"))
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


if __name__ == "__main__":

    async def main():
        try:
            # search = await Search.create("复仇者联盟")
            # print(search.search_result_total)
            # urls = [url async for url in search.get_urls(1)]
            # movies = await asyncio.gather(*[Movie.create(url) for url in urls])

            # for movie in movies:
            #     print(movie)
            #     async for comment in movie.get_comments():
            #         print(comment)
            #         break
            movie = await Movie.create("https://movie.douban.com/subject/34909341")
            num1 = 20
            set1 = set()
            async for comment in movie.get_comments_sync():
                # print(comment)
                set1.add((comment.user, comment.time))
                num1 -= 1
                if num1 == 0:
                    break
            num2 = 20
            set2 = set()
            async for comment in movie.get_comments_sync():
                # print(comment)
                set2.add((comment.user, comment.time))
                num2 -= 1
                if num2 == 0:
                    break
            intersection = set1.intersection(set2)
            print(intersection)
        except AttributeError as ea:
            # print(f"AttributeError: {str(ea)}")
            raise ea
        except Exception as e:
            print(f"Type: {type(e)}, Message: {str(e)}")

    asyncio.run(main())
