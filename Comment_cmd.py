# coding=utf-8
import sys
import os
from os.path import abspath, dirname
import threading
import asyncio

sys.path.insert(0, abspath(dirname(__file__)))
import tkinter
from tkinter import *
import Fun
from Project1_cmd import global_statue

uiName = "Comment"
ElementBGArray = {}
ElementBGArray_Resize = {}
ElementBGArray_IM = {}


# Form 'Form_1's Event :Load
def Form_1_onLoad(uiName):
    selected_movie = global_statue.selected_movie
    comment_num = selected_movie.comment_num
    if int(comment_num) > 0:
        threading.Thread(target=run_async_task, args=(10,)).start()
    else:
        Fun.MessageBox("没有评论数据", "", "info", None)


async def generate_comment(num: int = 20):
    selected_movie = global_statue.selected_movie
    index = num
    while index > 0:
        async for comment in selected_movie.get_comments():
            # 用户信息
            Fun.AddItemText(
                uiName,
                "ListBox_1",
                f"{comment.user} {comment.rating} {comment.time} {comment.location}",
                "end",
            )
            Fun.SetItemFGColor(uiName, "ListBox_1", "end", "#008000")
            Fun.AddItemText(
                uiName,
                "ListBox_1",
                f"{comment.content}",
                "end",
            )
            Fun.SetItemFGColor(uiName, "ListBox_1", "end", "#000000")
            Fun.AddItemText(
                uiName,
                "ListBox_1",
                "",
                "end",
            )
            index -= 1


def run_async_task(num: int = 20):
    asyncio.run(generate_comment(num))
