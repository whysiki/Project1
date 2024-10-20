# 版权声明：日历控件参考CSDN博主「我的眼_001」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原作者出处链接及声明
# 原文链接：https://blog.csdn.net/wodeyan001/article/details/86703034
# -*- coding: utf-8 -*- 
import os
import tkinter
import tkinter.ttk
import tkinter.font
from   PIL import Image,ImageTk
from   functools import partial
import win32gui
import inspect
import threading
G_ExeDir = None
G_ResDir = None
FunLib = None
SCALE_FACTOR = 1.5
def EventFunction_Adaptor(fun,  **params):
    """重新定义消息映射函数,自定义参数。"""
    return lambda event, fun=fun, params=params: fun(event, **params)
#判读是否多线程调用
def onThreadingCallFunction(fun,FunctionThreadDict,uiName,widgetName,value=None):
    threadingvalue = 0
    argspec = inspect.getfullargspec(fun)
    if "threadings" in argspec.args:
        threadingindex = argspec.args.index('threadings')
        threadingvalue = argspec[threadingindex+1]
        if type(threadingvalue) == type(()) or type(threadingvalue) == type([]):
            if len(threadingvalue) == 0:
                threadingvalue = 0
            else:
                threadingvalue = threadingvalue[0]
        if threadingvalue > 0:
            EventFunctionNameKey = fun.__module__+'.'+fun.__name__
            if EventFunctionNameKey in FunctionThreadDict:
                for thread in FunctionThreadDict[EventFunctionNameKey]:
                    if not thread.is_alive():
                        FunctionThreadDict[EventFunctionNameKey].remove(thread)
                if len(FunctionThreadDict[EventFunctionNameKey]) >= threadingvalue:
                    return
            function_args = [uiName,widgetName]
            if value != None:
                function_args.append(value)
            run_thread = threading.Thread(target=fun, args=function_args)
            run_thread.Daemon = True
            run_thread.start()
            if threadingvalue > 0:
                if EventFunctionNameKey not in FunctionThreadDict:
                    FunctionThreadDict[EventFunctionNameKey] = [run_thread]
                else:
                    FunctionThreadDict[EventFunctionNameKey].append(run_thread)
            return
    if value:
        fun(uiName,widgetName,value)
    else:
        fun(uiName,widgetName)
#圆角编辑框 
class CustomEntry:
    def __init__(self, widget):
        self.ParentWidget = widget
        self.EntryValue = tkinter.StringVar()
        self.EntryValue.set('')
        self.Canvas_width = 100
        self.Canvas_height = 24
        self.Canvas = tkinter.Canvas(self.ParentWidget,width=self.Canvas_width,height=self.Canvas_height,bg = '#FFFFFF',highlightthickness=0,bd=0)
        self.Entry = tkinter.Entry(self.Canvas,textvariable=self.EntryValue,background='#FFFFFF')
        self.Font = tkinter.font.Font(font='TkDefaultFont')
        self.TipText = ''
        self.TipTextColor = '#777777'
        self.TipLabel = tkinter.Label(self.Entry, text = '', justify = 'left',anchor=tkinter.W,bg='#FFFFFF')
        self.TipLabel.configure(fg = self.TipTextColor)
        self.TipLabel.bind('<Button-1>',self.onLeftClickTip)
        self.TipLabel.bind('<B1-Motion>',self.onLeftMotionTip)
        self.TipLabel.bind('<ButtonRelease-1>',self.onLeftReleaseTip)
        self.TipLabel.bind('<Double-1>',self.onDoubleClickTip)
        self.TipLabel.bind('<Button-3>',self.onRightClickTip)
        self.Entry.bind('<FocusOut>',self.onResetTip)
        self.Canvas.bind('<Configure>',self.Configure)
        self.LeftIconImage = None
        self.LeftPhotoIconImage = None
        self.LeftIconImageFile = None
        self.LeftIconClickedFunction = None
        self.RightIconImage = None
        self.RightPhotoIconImage = None
        self.RightIconImageFile = None
        self.RightIconClickedFunction = None
        self.TextChangedFunction = None
        self.uiName = None
        self.widgetName = None
        self.RoundRadius = 0
        self.Restriction = ''
        self.InnerSpacingX = 0
        self.InnerSpacingY = 0
        self.InnerBorderType = None
        self.InnerBorderWidth = 0
        self.InnerBorderDash = None
        self.InnerBorderColor = '#000000'
    #取得当前编辑框宽度
    def GetWidth(self):
        return self.Canvas.winfo_width()
    #传递绑定事件
    def bind(self,EventName,callBack):
        if self.Entry:
            self.Entry.bind(EventName,callBack)
    #取得当前编辑框高度
    def GetHeight(self):
        return self.Canvas.winfo_height()
    #取得Canvas
    def GetWidget(self):
        return self.Canvas
    #取得Entry
    def GetEntry(self):
        return self.Entry
    #窗口大小变化
    def Configure(self,event):
        self.Rebuild()
    #取得边框样式
    def Hide(self,layout="place"):
        if layout == "pack":
            self.Canvas.pack_forget()
        elif layout == "grid":
            self.Canvas.grid_forget()
        else:
            self.Canvas.place_forget()
    #重载一下cget
    def cget(self,attrib):
        return self.Entry.cget(attrib)
    #设置属性
    def configure(self,**kw):
        if 'text' in kw:
            self.SetText(kw['text'])
        else:
            try:
               self.Entry.configure(kw)
            except:
               pass
    #设置焦点
    def focus_set(self):
        return self.Entry.focus_set()
    #隐藏(兼容原Text控件)
    def pack_forget(self):
        return self.Canvas.pack_forget()
    #隐藏(兼容原Text控件)
    def grid_forget(self):
        return self.Canvas.grid_forget()
    #隐藏(兼容原Text控件)
    def place_forget(self):
        return self.Canvas.place_forget()
    #鼠标进入和离开图标时的处理
    def onIconEnter(self,event):
        event.widget.configure(cursor='hand2')
    def onIconLeave(self,event):    
        event.widget.configure(cursor='arrow')
    def onIconClick(self,event,tagName):  
        print("Click " + tagName)
        if tagName == "left_icon":
            if self.LeftIconClickedFunction:
                self.LeftIconClickedFunction(self.uiName,self.widgetName)
        else:
            if self.RightIconClickedFunction:
                self.RightIconClickedFunction(self.uiName,self.widgetName)
    #鼠标左键单击
    def onLeftClickTip(self,event):
        self.TipLabel.place_forget()
        self.Entry.focus_set()
    #鼠标左键拖动Tip
    def onLeftMotionTip(self,event):
        self.TipLabel.place_forget()
        self.Entry.focus_set()
    #鼠标左键松开Tip
    def onLeftReleaseTip(self,event):
        self.TipLabel.place_forget()
        self.Entry.focus_set()
    #鼠标左键双击Tip
    def onDoubleClickTip(self,event):
        pass
    #鼠标右键单击
    def onRightClickTip(self,event):
        self.TipLabel.place_forget()
        self.Entry.focus_set()
        self.Entry.event_generate("<Button-3>",x = event.x,y = event.y)
    #点击Tiip
    def onResetTip(self,event):
        text =  self.EntryValue.get()
        if text == '':
            self.SetTipText(self.TipText)
    #设置左边的图标按钮
    def SetLeftIcon(self,IconFile):
        global G_ExeDir
        global G_ResDir
        filePath = IconFile
        if IconFile:
            if filePath and os.path.exists(filePath) == False:
                 filePath = "Resources\\" + IconFile
                 if os.path.exists(filePath) == False:
                    filePath = os.path.join(G_ExeDir,IconFile)
                    if os.path.exists(filePath) == False:
                        filePath = os.path.join(G_ResDir,IconFile)
            if filePath and os.path.exists(filePath) == True:
                imagePath,imageFile = os.path.split(filePath)
                try:
                    self.LeftIconImage = Image.open(filePath).convert('RGBA')
                    IconSize = self.GetHeight() - 2 * self.InnerSpacingY
                    Image_Resize = self.LeftIconImage.resize((IconSize, IconSize),Image.LANCZOS)
                    self.LeftPhotoIconImage = ImageTk.PhotoImage(Image_Resize)
                    self.LeftIconImageFile = imageFile
                except:
                    self.LeftIconImage = None
                    self.LeftPhotoIconImage = None
                    self.LeftIconImageFile = None
        self.Redraw()
    #设置左边的图标按钮回调函数
    def SetLeftIconClickFunction(self,callBackFunc,uiName,widgetName):
        self.LeftIconClickedFunction = callBackFunc
        self.uiName = uiName
        self.widgetName = widgetName
        self.Canvas.tag_bind('left_icon','<Enter>',self.onIconEnter)
        self.Canvas.tag_bind('left_icon','<Leave>',self.onIconLeave)
        self.Canvas.tag_bind('left_icon','<ButtonRelease-1>',EventFunction_Adaptor(self.onIconClick,tagName='left_icon'))
    #设置右边的图标按钮
    def SetRightIcon(self,IconFile):
        global G_ExeDir
        global G_ResDir
        filePath = IconFile
        if IconFile:
            if filePath and os.path.exists(filePath) == False:
                filePath = "Resources\\" + IconFile
                if os.path.exists(filePath) == False:
                    filePath = os.path.join(G_ExeDir,IconFile)
                    if os.path.exists(filePath) == False:
                        filePath = os.path.join(G_ResDir,IconFile)
            if filePath and os.path.exists(filePath) == True:
                imagePath,imageFile = os.path.split(filePath)
                try:
                    self.RightIconImage = Image.open(filePath).convert('RGBA')
                    IconSize = self.GetHeight() - 2 * self.InnerSpacingY
                    Image_Resize = self.RightIconImage.resize((IconSize, IconSize),Image.LANCZOS)
                    self.RightPhotoIconImage = ImageTk.PhotoImage(Image_Resize)
                    self.RightIconImageFile = imageFile
                except:
                    self.RightIconImage = None
                    self.RightPhotoIconImage = None
                    self.RightIconImageFile = None
        self.Redraw()
    #设置左边的图标按钮回调函数
    def SetRightIconClickFunction(self,callBackFunc,uiName,widgetName):
        self.RightIconClickedFunction = callBackFunc
        self.uiName = uiName
        self.widgetName = widgetName
        self.Canvas.tag_bind('right_icon','<Enter>',self.onIconEnter)
        self.Canvas.tag_bind('right_icon','<Leave>',self.onIconLeave)
        self.Canvas.tag_bind('right_icon','<ButtonRelease-1>',EventFunction_Adaptor(self.onIconClick,tagName='right_icon'))
    #内置的输入文本被修改时的回调函数
    def onTextChangedCallBack(self,*args):
        if self.TextChangedFunction:
            Text = self.EntryValue.get()
            print("TextChanged:"+Text)
            self.TextChangedFunction(self.uiName,self.widgetName,Text)
    #设置输入文本被修改时的回调函数
    def SetTextChangedFunction(self,callBackFunc,uiName,widgetName):
        self.TextChangedFunction = callBackFunc
        self.uiName = uiName
        self.widgetName = widgetName
        self.EntryValue.trace('w',self.onTextChangedCallBack)
    #设置边角半径
    def SetRoundRadius(self,radius):
        self.RoundRadius = radius
        w = self.GetWidth()
        h = self.GetHeight()
        if radius > 0 and w > 1 and h > 1:
            HRGN = win32gui.CreateRoundRectRgn(0,0,w,h,radius,radius)
            win32gui.SetWindowRgn(self.Canvas.winfo_id(), HRGN,1)
    #取得边角半径
    def GetRoundRadius(self):
        return self.RoundRadius
    #设置类型限制
    def SetRestriction(self,restriction):
        self.Restriction = restriction
    #取得类型限制
    def GetRestriction(self):
        return self.Restriction
    #设置横向间距
    def SetInnerSpacingX(self,InnerSpacingX):
        self.InnerSpacingX = InnerSpacingX
    #取得横向间距
    def GetInnerSpacingX(self):
        return self.InnerSpacingX
    #设置纵向间距
    def SetInnerSpacingY(self,InnerSpacingY):
        self.InnerSpacingY = InnerSpacingY
    #取得纵向间距
    def GetInnerSpacingY(self):
        return self.InnerSpacingY
    #设置内边框类型
    def SetInnerBorderType(self,InnerBorderType):
        self.InnerBorderType = InnerBorderType
    #取得内边框类型
    def GetInnerBorderType(self):
        return self.InnerBorderType
    #设置内边框宽度
    def SetInnerBorderWidth(self,InnerBorderWidth):
        self.InnerBorderWidth = InnerBorderWidth
    #取得内边框宽度
    def GetInnerBorderWidth(self):
        return self.InnerBorderWidth
    #设置内边框Dash
    def SetInnerBorderDash(self,InnerBorderDash):
        self.InnerBorderDash = InnerBorderDash
    #取得内边框Dash
    def GetInnerBorderDash(self):
        return self.InnerBorderDash
    #设置内边框颜色
    def SetInnerBorderColor(self,InnerBorderColor):
        self.InnerBorderColor = InnerBorderColor
    #取得内边框颜色
    def GetInnerBorderColor(self):
        return self.InnerBorderColor
    #设置文字
    def SetText(self,text):
        if text != "":
            self.TipLabel.place_forget()
        else:
            self.SetTipText(self.TipText)
        self.EntryValue.set(text)
    #取得文字
    def GetText(self):
        text =  self.EntryValue.get()
        if text != "":
            if hasattr(FunLib,"GetElementName") == True:
                uiName,elementName = FunLib.GetElementName(self)
                if self.Restriction == "letter":
                    if text.isalpha() == False:
                        FunLib.MessageBox(elementName+"请输入字母","类型限制")
                        return None
                if self.Restriction == "number":
                    if FunLib.IsNumeric(text) == False:
                        FunLib.MessageBox(elementName+"请输入数字","类型限制")
                        return None
                if self.Restriction == "letter":
                    if text.isalpha() == False:
                        FunLib.MessageBox(elementName+"请输入字母","类型限制")
                        return None
                if self.Restriction == "alphanumeric":
                    if FunLib.IsAlphanumeric(text) == False:
                        FunLib.MessageBox(elementName+"请输入字母或数字","类型限制")
                        return None
                if self.Restriction == "integer":
                    if FunLib.IsInt(text) == False:
                        FunLib.MessageBox(elementName+"请输入整数","类型限制")
                        return None
                if self.Restriction == "phone":
                    if FunLib.IsMobilePhone(text) == False:
                        FunLib.MessageBox(elementName+"请输入手机号码","类型限制")
                        return None
                if self.Restriction == "email":
                    if FunLib.IsEmail(text) == False:
                        FunLib.MessageBox(elementName+"请输入电子邮件","类型限制")
                        return None
        return text
    #设置字体
    def SetFont(self,font):
        self.Font = font
        self.Entry.configure(font = self.Font)
        self.TipLabel.configure(font = self.Font)
    #取得字体
    def GetFont(self):
        return self.Font
    #设置提示文字
    def SetTipText(self,text):
        self.TipText = text
        if text != '':
            TipLabelWidth = self.Entry.winfo_width()
            if self.LeftIconImage:
                TipLabelWidth = TipLabelWidth - self.Entry.winfo_height() - 2 * self.InnerSpacingX
            if self.RightIconImage:
                TipLabelWidth = TipLabelWidth - self.Entry.winfo_height() - 2 * self.InnerSpacingX
            self.TipLabel.place(x=2,y=2,width=TipLabelWidth-4,height=self.Entry.winfo_height()-4)
            self.TipLabel.configure(bg = self.GetBGColor())
            self.TipLabel.configure(fg = self.TipTextColor)
            self.TipLabel.configure(text = self.TipText)
        else:
            self.TipLabel.place_forget()
    #取得提示文字
    def GetTipText(self):
        return self.TipText
    #设置提示文字颜色
    def SetTipFGColor(self,color):
        self.TipTextColor = color
        self.TipLabel.configure(fg=color)
    #取得提示文字颜色
    def GetTipFGColor(self):
        return self.TipTextColor
    #设置背景色
    def SetBGColor(self,bgColor):
        self.Entry.configure(bg = bgColor)
        self.TipLabel.configure(bg = bgColor)
    #取得背景色
    def GetBGColor(self):
        return self.Entry.cget('bg')
    #设置文字色
    def SetFGColor(self,fgColor):
        self.Entry.configure(fg = fgColor)
    #取得文字色
    def GetFGColor(self):
        return self.Entry.cget('fg')
    #设置只读状态的背景色
    def SetBGColor_ReadOnly(self,bgColor):
        self.Entry.configure(readonlybackground = bgColor)
    #取得只读状态的背景色
    def GetBGColor_ReadOnly(self):
        return self.Entry.cget('readonlybackground')
    #设置替代符
    def SetShowChar(self,showChar):
        self.Entry.configure(show = showChar)
    #取得替代符
    def GetShowChar(self):
        return self.Entry.cget('show')
    #设置对齐方式
    def SetJustify(self,justify):
        self.Entry.configure(justify = justify)
    #取得对齐方式
    def GetJustify(self):
        return self.Entry.cget('justify')
    #设置样式
    def SetRelief(self,relief):
        self.Entry.configure(relief = relief)
    #取得样式
    def GetRelief(self):
        return self.Entry.cget('relief')
    #设置状态
    def SetState(self,state):
        self.Entry.configure(state = state)
    #取得状态
    def GetState(self):
        return self.Entry.cget('state')
    #重置
    def Rebuild(self):
        if self.RoundRadius > 0:
            self.SetRoundRadius(self.RoundRadius)
        IconSize = self.GetHeight()
        if self.LeftIconImage:
            Image_Resize = self.LeftIconImage.resize((IconSize, IconSize),Image.LANCZOS)
            self.LeftPhotoIconImage = ImageTk.PhotoImage(Image_Resize)
        if self.RightIconImage:
            Image_Resize = self.RightIconImage.resize((IconSize, IconSize),Image.LANCZOS)
            self.RightPhotoIconImage = ImageTk.PhotoImage(Image_Resize)
        self.Redraw()
    #重绘
    def Redraw(self):
        AllWidth = self.GetWidth()
        IconWidth = self.GetHeight()
        if AllWidth == 1 or IconWidth == 1:
            AllWidth = 160
            IconWidth = 24
        EntryWidth = AllWidth
        EntryLeft = 0
        #左图标
        if self.LeftPhotoIconImage:
            self.Canvas.create_image(self.InnerSpacingX,self.InnerSpacingY,anchor=tkinter.NW,image=self.LeftPhotoIconImage,tag="left_icon")
            EntryWidth = EntryWidth - 2 * self.InnerSpacingX - IconWidth
            EntryLeft = 2 * self.InnerSpacingX + IconWidth
        #左图标
        if self.RightPhotoIconImage:
            self.Canvas.create_image(AllWidth - self.InnerSpacingX,self.InnerSpacingY,anchor=tkinter.NE,image=self.RightPhotoIconImage,tag="right_icon")
            EntryWidth = EntryWidth - 2 * self.InnerSpacingX - IconWidth
        self.Canvas.delete('border')
        if self.InnerBorderType =='borderline':
            self.Entry.place(x = EntryLeft+self.InnerBorderWidth , y = self.InnerBorderWidth , width = EntryWidth-2*self.InnerBorderWidth + 1 ,height=IconWidth-2*self.InnerBorderWidth + 1)
            if self.InnerBorderDash and self.InnerBorderDash != [0,0] and self.InnerBorderDash != (0,0):
                self.Canvas.create_line(EntryLeft,0,EntryWidth,0,width=self.InnerBorderWidth,fill = self.InnerBorderColor,dash=self.InnerBorderDash,tag='border')
                self.Canvas.create_line(EntryLeft,0,EntryLeft,IconWidth,width=self.InnerBorderWidth,fill = self.InnerBorderColor,dash=self.InnerBorderDash,tag='border')
                self.Canvas.create_line(EntryLeft+EntryWidth,0,EntryLeft+EntryWidth,IconWidth,width=self.InnerBorderWidth,fill = self.InnerBorderColor,dash=self.InnerBorderDash,tag='border')
                self.Canvas.create_line(EntryLeft,IconWidth,EntryWidth,IconWidth,width=self.InnerBorderWidth,fill = self.InnerBorderColor,dash=self.InnerBorderDash,tag='border')
            else:
               self.Canvas.create_line(EntryLeft,0,EntryWidth,0,width=self.InnerBorderWidth,fill = self.InnerBorderColor,tag='border')
               self.Canvas.create_line(EntryLeft,0,EntryLeft,IconWidth,width=self.InnerBorderWidth,fill = self.InnerBorderColor,tag='border')
               self.Canvas.create_line(EntryLeft+EntryWidth,0,EntryLeft+EntryWidth,IconWidth,width=self.InnerBorderWidth,fill = self.InnerBorderColor,tag='border')
               self.Canvas.create_line(EntryLeft,IconWidth,EntryWidth,IconWidth,width=self.InnerBorderWidth,fill = self.InnerBorderColor,tag='border')
        elif self.InnerBorderType =='underline':
            if self.InnerBorderDash and self.InnerBorderDash != [0,0] and self.InnerBorderDash != (0,0):
               self.Canvas.create_line(EntryLeft,IconWidth-self.InnerBorderWidth,EntryLeft+EntryWidth,IconWidth-self.InnerBorderWidth,width=self.InnerBorderWidth,fill = self.InnerBorderColor,dash=self.InnerBorderDash,tag='border')
            else:
               self.Canvas.create_line(EntryLeft,IconWidth-self.InnerBorderWidth,EntryLeft+EntryWidth,IconWidth-self.InnerBorderWidth,width=self.InnerBorderWidth,fill = self.InnerBorderColor,tag='border')
            self.Entry.place(x = EntryLeft , y = 0 , width = EntryWidth ,height=IconWidth-self.InnerBorderWidth)
        else:
            self.Entry.place(x = EntryLeft , y = 0 , width = EntryWidth ,height=IconWidth)
        if self.GetText() == '' and self.TipText != '':
            self.SetTipText(self.TipText)
