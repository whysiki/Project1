#coding=utf-8
import sys
import os
from   os.path import abspath, dirname
sys.path.insert(0,abspath(dirname(__file__)))
import tkinter
from   tkinter import *
import Fun
uiName="Image"
ElementBGArray={}
ElementBGArray_Resize={}
ElementBGArray_IM={}
#Form 'Form_1's Event :Load
def Form_1_onLoad(uiName):
    pass
    #thumnail_pic = 
    uiDataDict = Fun.GetUIDataDictionary(uiName)
    print(uiDataDict)
    
    Fun.SetImage(uiName,'Canvas_1',"",True)
