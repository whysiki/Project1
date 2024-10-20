# coding=utf-8
import sys
import threading
import os
from os.path import abspath, dirname

sys.path.insert(0, abspath(dirname(__file__)))
import tkinter
from tkinter import *
import Fun
from douban import Search, Comment, Movie
import asyncio
from my_test.test_tools import *
from dataclasses import dataclass


uiName = "Project1"
ElementBGArray = {}
ElementBGArray_Resize = {}
ElementBGArray_IM = {}


@dataclass
class State:
    search_input_text: str
    page: int
    search_result_total: int
    page_count: int
    current_movies: list[Movie]
    page_movies_dict: dict[int, list[Movie]]
    selected_movie: Movie

    def __init__(self):
        self.search_input_text = ""
        self.page = 1
        self.search_result_total = 0
        self.page_count = 0
        self.current_movies = []
        self.page_movies_dict = {}
        self.selected_movie = None


global_statue = State()


def Form_1_onLoad(uiName, threadings=0):
    Fun.SetText(uiName, "Label_2", f"{global_statue.search_result_total}")
    Fun.SetVisible(uiName, "Progress_1", True)
    Fun.SetProgress(uiName, "Progress_1", 100, 0)
    Fun.SetText(uiName, "Label_6", f"{global_statue.page}")


async def search_and_display(search_input_text, page: int):
    Fun.DeleteAllRows(uiName, "ListView_1")
    if page in global_statue.page_movies_dict:
        movies = global_statue.page_movies_dict[page]
        for index, movie in enumerate(movies):
            row = [
                movie.title,
                movie.category,
                movie.director,
                movie.score,
                movie.comment_num,
                movie.url,
            ]
            Fun.AddRowText(uiName, "ListView_1", "end", ",".join(row))
            global_statue.current_movies.append(movie)
            Fun.SetProgress(uiName, "Progress_1", 100, (index + 1) * 100 / len(movies))
            Fun.SetText(uiName, "Label_4", f"{index + 1}/{len(movies)}")
            Fun.SetText(uiName, "Label_6", f"{global_statue.page}")
        return
    search = await Search.create(search_input_text)
    global_statue.search_result_total = search.search_result_total
    global_statue.page_count = search.page_count
    Fun.SetText(uiName, "Label_2", f"{global_statue.search_result_total}")
    num = 15 if page != search.page_count else search.search_result_total % 15
    index = 0
    movies = []
    async for url in search.get_urls(page=page):
        movie = await Movie.create(url)
        movies.append(movie)
        row = [
            movie.title,
            movie.category,
            movie.director,
            movie.score,
            movie.comment_num,
            movie.url,
        ]
        Fun.AddRowText(uiName, "ListView_1", "end", ",".join(row))
        global_statue.current_movies.append(movie)
        Fun.SetProgress(uiName, "Progress_1", 100, (index + 1) * 100 / num)
        Fun.SetText(uiName, "Label_4", f"{index + 1}/{num}")
        Fun.SetText(uiName, "Label_6", f"{global_statue.page}")
        index += 1

    global_statue.page_movies_dict[global_statue.page] = movies


def run_async_task(search_input_text, page: int):
    asyncio.run(search_and_display(search_input_text, page))


def Button_1_onCommand(uiName, widgetName, threadings=0):
    global_statue.search_input_text = Fun.GetText(uiName, "Entry_1")
    if not global_statue.search_input_text:
        Fun.MessageBox("请输入一个关键字进行查找", "", "info", None)
    else:
        global_statue.page = 1
        thread = threading.Thread(
            target=run_async_task,
            args=(global_statue.search_input_text, global_statue.page),
        )
        thread.start()


# 下一页逻辑
def Button_2_onCommand(uiName, widgetName, threadings=0):
    if global_statue.page < global_statue.page_count:
        global_statue.page += 1
        thread = threading.Thread(
            target=run_async_task,
            args=(global_statue.search_input_text, global_statue.page),
        )
        thread.start()
    else:
        Fun.MessageBox("已经是最后一页了", "", "info", None)


# 上一页
def Button_3_onCommand(uiName, widgetName, threadings=0):
    if global_statue.page > 1:
        global_statue.page -= 1
        thread = threading.Thread(
            target=run_async_task,
            args=(global_statue.search_input_text, global_statue.page),
        )
        thread.start()
    else:
        Fun.MessageBox("已经是第一页了", "", "info", None)


def ListView_1_onHeadingClicked(uiName, widgetName, columnname, threadings=0):
    pass


# Entry 'Entry_1's Key Event :
def Entry_1_onKey(event, uiName, widgetName, threadings=0):
    pass


# ListView 'ListView_1's CellClicked Event :
def ListView_1_onCellClicked(uiName, widgetName, rowIndex, columnIndex, threadings=0):
    # print(rowIndex)
    # # print(columnIndex)
    # # print(columnIndex)
    selected_movide = global_statue.current_movies[rowIndex]
    global_statue.selected_movie = selected_movide
    if columnIndex == 0:
        thumnail_pic = selected_movide.thumbnail
        topmost = 1
        toolwindow = 1
        grab_set = 1
        wait_window = 1
        animation = ""
        params = None
        InputDataArray = Fun.CallUIDialog(
            "Image", topmost, toolwindow, grab_set, wait_window, animation, params
        )

        # print(thumnail_pic)
    elif columnIndex == 4:
        # print("Clicked Comment_count")
        topmost = 1
        toolwindow = 1
        grab_set = 1
        wait_window = 1
        animation = ""
        params = None
        InputDataArray = Fun.CallUIDialog(
            "Comment", topmost, toolwindow, grab_set, wait_window, animation, params
        )
        # print(InputDataArray)
