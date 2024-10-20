# coding=utf-8
import sys
import urllib.request
import os
from os.path import abspath, dirname
import threading

# import urllib3
sys.path.insert(0, abspath(dirname(__file__)))
import tkinter
from tkinter import *
import Fun
from Project1_cmd import global_statue

uiName = "Image"
ElementBGArray = {}
ElementBGArray_Resize = {}
ElementBGArray_IM = {}


def download_pic(url, save_path):
    try:
        urllib.request.urlretrieve(url, save_path)
        return True
    except Exception as e:
        Fun.MessageBox("Error", f"Download Error: {e}")
        return False


# Form 'Form_1's Event :Load
def Form_1_onLoad(uiName):
    #win32gui.SetWindowText(hWinHandle,"")
    temp_pic = os.path.join(Fun.G_ExeDir, "cache", "temp.jpg")
    os.makedirs(os.path.join(Fun.G_ExeDir, "cache"), exist_ok=True)
    threading.Thread(
        target=download_pic, args=(global_statue.selected_movie.thumbnail, temp_pic)
    ).start()
    Fun.SetImage(uiName, "Canvas_1", temp_pic, True)
