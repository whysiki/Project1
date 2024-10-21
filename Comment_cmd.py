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

# 全局事件循环
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

task_queue = asyncio.Queue()


def Form_1_onLoad(uiName):
    value = Fun.DelAllLines(uiName, "ListBox_1")
    selected_movie = global_statue.selected_movie
    comment_num = selected_movie.comment_num
    if int(comment_num) > 0:
        task_queue.put_nowait(10)
        threading.Thread(target=start_async_task_from_queue).start()
    else:
        Fun.MessageBox("没有评论数据", "", "info", None)


async def generate_comment(num):
    selected_movie = global_statue.selected_movie
    index = num
    async for comment in selected_movie.get_comments():
        loop.call_soon_threadsafe(
            Fun.AddItemText,
            uiName,
            "ListBox_1",
            f"{comment.user} {comment.rating} {comment.time} {comment.location}",
            "end",
        )
        loop.call_soon_threadsafe(
            Fun.SetItemFGColor, uiName, "ListBox_1", "end", "#008000"
        )
        loop.call_soon_threadsafe(
            Fun.AddItemText, uiName, "ListBox_1", f"{comment.content}", "end"
        )
        loop.call_soon_threadsafe(
            Fun.SetItemFGColor, uiName, "ListBox_1", "end", "#000000"
        )
        loop.call_soon_threadsafe(Fun.AddItemText, uiName, "ListBox_1", "", "end")
        index -= 1
        if index <= 0:
            return


async def run_async_task(num):
    await generate_comment(num)


def start_async_task(num):
    loop.call_soon_threadsafe(asyncio.create_task, run_async_task(num))


def start_async_task_from_queue():
    while not task_queue.empty():
        num = task_queue.get_nowait()
        start_async_task(num)


def ListBox_1_onMouseWheel(event, uiName, widgetName, threadings=0):
    task_queue.put_nowait(10)
    threading.Thread(target=start_async_task_from_queue).start()


threading.Thread(target=loop.run_forever).start()
