#coding=utf-8
#import libs 
import sys
import os
from   os.path import abspath, dirname
sys.path.insert(0,abspath(dirname(__file__)))
ElementBGArray = {}
ElementBGArray_Resize = {}
ElementBGArray_IM = {}
import Project1_sty
import Fun
import tkinter
from   tkinter import *
import tkinter.ttk
import tkinter.font
from   PIL import Image,ImageTk

#Add your Varial Here: (Keep This Line of comments)
#Define UI Class
class  Project1:
    def __init__(self,root,isTKroot = True,params=None):
        uiName = Fun.GetUIName(root,self.__class__.__name__)
        self.uiName = uiName
        Fun.Register(uiName,'UIClass',self)
        self.root = root
        self.configure_event = None
        self.isTKroot = isTKroot
        self.firstRun = True
        Fun.G_UIParamsDictionary[uiName]=params
        Fun.Register(uiName,'root',root)
        style = Project1_sty.SetupStyle(isTKroot)
        self.UIJsonString ='{"Version": "1.0.0", "UIName": "Project1", "Description": "", "WindowSize": [720, 660], "WindowPosition": "Center", "WindowHide": false, "WindowResizable": true, "WindowTitle": "豆瓣电影信息爬取", "DarkMode": false, "BorderWidth": 0, "BorderColor": "#ffffff", "DropTitle": false, "DragWindow": true, "MinSize": [0, 0], "TransparentColor": null, "RootTransparency": 255, "ICOFile": null, "WinState": 1, "WinTopMost": false, "BGColor": "#FFFFFF", "GroupList": {}, "WidgetList": [{"Type": "Form", "Index": 1, "AliasName": "Form_1", "BGColor": "#FFFFFF", "Size": [720, 660], "EventList": {"Load": "Form_1_onLoad"}}, {"Type": "Button", "Index": 4, "AliasName": "Button_1", "ParentName": "Form_1", "PlaceInfo": [292, 22, 66, 26, "nw", true, false], "Visible": true, "Size": [120, 48], "BGColor": "#5D9CEC", "ActiveBGColor": "#A0D468", "Text": "搜索", "FGColor": "#000000", "Font": ["Segoe UI", 6, "bold", "roman", 0, 0], "Relief": "raised", "EventList": {"Command": "Button_1_onCommand"}}, {"Type": "Button", "Index": 10, "AliasName": "Button_2", "ParentName": "Form_1", "PlaceInfo": [322, 333, 55, 22, "nw", true, false], "Visible": true, "Size": [100, 40], "BGColor": "#5D9CEC", "Text": "下一页", "FGColor": "#000000", "Font": ["Segoe UI", 6, "bold", "roman", 0, 0], "Relief": "raised", "EventList": {"Command": "Button_2_onCommand"}}, {"Type": "Button", "Index": 14, "AliasName": "Button_3", "ParentName": "Form_1", "PlaceInfo": [322, 55, 55, 22, "nw", true, false], "Visible": true, "Size": [100, 40], "BGColor": "#5D9CEC", "Text": "上一页", "FGColor": "#000000", "Font": ["Segoe UI", 6, "bold", "roman", 0, 0], "Relief": "raised", "EventList": {"Command": "Button_3_onCommand"}}, {"Type": "ListView", "Index": 5, "AliasName": "ListView_1", "ParentName": "Form_1", "PlaceInfo": [11, 88, 377, 236, "nw", true, false], "Visible": true, "Size": [680, 425], "SelectMode": "EXTENDED", "RowHeight": 28, "ColumnList": [["电影名称", "center", 180, true], ["电影类型", "center", 100, false], ["导演", "center", 100, false], ["评分", "center", 100, false], ["评论数量", "center", 100, false], ["下载地址", "center", 100, true]], "EventList": {"HeadingClicked": "ListView_1_onHeadingClicked", "CellClicked": "ListView_1_onCellClicked", "CellDoubleClicked": "ListView_1_onCellDoubleClicked"}}, {"Type": "Entry", "Index": 6, "AliasName": "Entry_1", "ParentName": "Form_1", "PlaceInfo": [35, 22, 243, 26, "nw", true, false], "Visible": true, "Size": [438, 48], "BGColor": "#CCD1D9", "BGColor_ReadOnly": "#EFEFEF", "FGColor": "#000000", "Font": ["Segoe UI", 6, "normal", "roman", 0, 0], "InnerBorderColor": "#000000", "TipText": "搜索电影、电视剧、综艺、影人", "TipFGColor": "#4A89DC", "Relief": "solid", "RoundCorner": 30, "EventList": {"Key": "Entry_1_onKey"}}, {"Type": "Label", "Index": 7, "AliasName": "Label_1", "ParentName": "Form_1", "PlaceInfo": [22, 55, 52, 26, "nw", true, false], "Visible": true, "Size": [95, 48], "BGColor": "#FFFFFF", "Text": "共找到", "FGColor": "#5D9CEC", "Font": ["Segoe UI", 6, "bold", "roman", 0, 0]}, {"Type": "Label", "Index": 8, "AliasName": "Label_2", "ParentName": "Form_1", "PlaceInfo": [67, 54, 41, 26, "nw", true, false], "Visible": true, "Size": [75, 48], "BGColor": "#FFFFFF", "Text": "n", "FGColor": "#000000", "Font": ["Segoe UI", 6, "bold", "roman", 0, 0]}, {"Type": "Label", "Index": 9, "AliasName": "Label_3", "ParentName": "Form_1", "PlaceInfo": [111, 55, 144, 26, "nw", true, false], "Visible": true, "Size": [260, 48], "BGColor": "#FFFFFF", "Text": "条数据，每页将显示15条数据。", "FGColor": "#5D9CEC", "Font": ["Segoe UI", 6, "bold", "roman", 0, 0]}, {"Type": "Label", "Index": 11, "AliasName": "Label_4", "ParentName": "Form_1", "PlaceInfo": [266, 333, 44, 22, "nw", true, false], "Visible": true, "Size": [80, 40], "BGColor": "#FFFFFF", "Text": "0/0", "FGColor": "#000000", "Font": ["Segoe UI", 6, "normal", "roman", 0, 0]}, {"Type": "Label", "Index": 15, "AliasName": "Label_5", "ParentName": "Form_1", "PlaceInfo": [241, 55, 55, 26, "nw", true, false], "Visible": true, "Size": [100, 48], "BGColor": "#FFFFFF", "Text": "页码：", "FGColor": "#5D9CEC", "Font": ["Segoe UI", 6, "bold", "roman", 0, 0]}, {"Type": "Label", "Index": 17, "AliasName": "Label_6", "ParentName": "Form_1", "PlaceInfo": [278, 55, 41, 26, "nw", true, false], "Visible": true, "Size": [75, 48], "BGColor": "#FFFFFF", "Text": "n", "FGColor": "#000000", "Font": ["Segoe UI", 6, "bold", "roman", 0, 0]}, {"Type": "Progress", "Index": 13, "AliasName": "Progress_1", "ParentName": "Form_1", "PlaceInfo": [11, 333, 233, 22, "nw", true, false], "Visible": true, "Size": [420, 40], "Orient": "horizontal", "Mode": "determinate", "MaxValue": 100, "Value": 50, "RoundCorner": 30}]}'
        Form_1 = Fun.CreateUIFormJson(uiName,root,isTKroot,style,self.UIJsonString,False)
        #Inital all element's Data 
        Fun.InitElementData(uiName)
        #Call Form_1's OnLoad Function
        #Add Some Logic Code Here: (Keep This Line of comments)



        #Exit Application: (Keep This Line of comments)
        if self.isTKroot == True and Fun.GetElement(self.uiName,"root"):
            self.root.protocol('WM_DELETE_WINDOW', self.Exit)
            self.root.bind('<Configure>', self.Configure)
            
    def GetRootSize(self):
        return Fun.GetUIRootSize(self.uiName)
    def GetAllElement(self):
        return Fun.G_UIElementDictionary[self.uiName]
    def Escape(self,event):
        if Fun.AskBox('提示','确定退出程序？') == True:
            self.Exit()
    def Exit(self):
        if self.isTKroot == True:
            Fun.DestroyUI(self.uiName,0,'')

    def Configure(self,event):
        Form_1 = Fun.GetElement(self.uiName,'Form_1')
        if Form_1 == event.widget:
            Fun.ReDrawCanvasRecord(self.uiName)
        if self.root == event.widget and (self.configure_event is None or self.configure_event[2]!= event.width or self.configure_event[3]!= event.height):
            uiName = self.uiName
            self.configure_event = [event.x,event.y,event.width,event.height]
            Fun.ResizeRoot(self.uiName,self.root,event)
            Fun.ResizeAllChart(self.uiName)
            pass
#Create the root of tkinter 
