# coding=utf-8
import sys
import os
from os.path import abspath, dirname
import threading

sys.path.insert(0, abspath(dirname(__file__)))
import tkinter
from tkinter import *
import Fun
from Project1_cmd import global_statue

uiName = "Comment"
ElementBGArray = {}
ElementBGArray_Resize = {}
ElementBGArray_IM = {}

lock = threading.Lock()


def Form_1_onLoad(uiName):
    Fun.DelAllLines(uiName, "ListBox_1")
    selected_movie = global_statue.selected_movie
    selected_movie.reset_start()
    comment_num = selected_movie.comment_num
    if int(comment_num) > 0:
        threading.Thread(target=generate_comment, args=(20,)).start()
    else:
        Fun.MessageBox("没有评论数据", "", "info", None)


def generate_comment(num):
    selected_movie = global_statue.selected_movie
    index = num
    with lock:
        for comment in selected_movie.get_comments_sync():
            Fun.AddItemText(
                uiName,
                "ListBox_1",
                f"{comment.user} {comment.rating} {comment.time} {comment.location}",
                "end",
            )
            Fun.SetItemFGColor(uiName, "ListBox_1", "end", "#008000")
            Fun.AddItemText(uiName, "ListBox_1", f"{comment.content}", "end")
            Fun.SetItemFGColor(uiName, "ListBox_1", "end", "#000000")
            Fun.AddItemText(uiName, "ListBox_1", "", "end")
            index -= 1
            if index <= 0:
                return


def ListBox_1_onMouseWheel(event, uiName, widgetName, threadings=0):
    threading.Thread(target=generate_comment, args=(20,)).start()
