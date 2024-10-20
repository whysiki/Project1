# coding=utf-8
import sys
import os
from os.path import abspath, dirname

sys.path.insert(0, abspath(dirname(__file__)))
import tkinter
from tkinter import *
import Fun

uiName = "Image"
ElementBGArray = {}
ElementBGArray_Resize = {}
ElementBGArray_IM = {}


# Form 'Form_1's Event :Load
def Form_1_onLoad(uiName):
    pass
    # print("image")
    # thumnail_pic = Fun.GetUserData("Image", "Canvas_1", "thumnail_pic")
    # movie_title = Fun.GetUserData("Image", "Canvas_1", "movie_title")
    # print(thumnail_pic)
    # print(movie_title)
    # Fun.SetImage(界面名
    # uiName,
    # "Canvas_1",
    # "https://img1.doubanio.com/view/photo/s_ratio_poster/public/p2153898948.jpg",
    # True,
    # )
    # Fun.SetImage(uiName,'Canvas_1',"D:\Backup\Pictures\QQ图片20241006165832.jpg",True)
