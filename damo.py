#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
大漠插件调用库
MoveClick       移动并左键单击
SayString       发送文本，有x,y在x,y位置写入，没有就原地输入
SayZhong        发送中文
CombKey         组合键
Drag            拖拽

FindWindow      查找符合类名或者标题名的可见窗口
FindWindowEx    查找子窗口
Hwindow         获取顶层活动窗口
MoveWindow      移动窗口
ActiveWindow    激活窗口
MaxWindow       最大化窗口
SetWindowSize   设置窗口大小

FindPic         查找图片，可为多个，但只能得到第一个的位置
FindPicEx       查找图片，可为多个，能得到所有的位置
Capture

SetDict         设置字典
UseDict         使用字典
FindStr         查找字符串坐标
FindStrEx       查找字符串坐标
Ocr             识别文字
OcrEx           识别文字

BindWindow      绑定窗口
UnBindWindow    解除绑定

Created on 2016年10月30日
@author: ZRF
'''

import os, sys, logging
import win32com.client, win32gui
from time import sleep
from fish.lib import inc

class DM(object):
    '大漠插件调用类'


    _lt = [50, 800, 3000]
    _dt = 0.001


    #----初始化操作
    def __init__(self, dt = 0.001, rx=0, ry=0, lt = [50, 800, 3000]):
        '构造函数'
        DM._dt = dt
        DM._lt = lt
        self._bBindWnd = False
        self._rx = rx
        self._ry = ry
        #调用大漠插件
        try:
            self._dm = win32com.client.Dispatch('dm.dmsoft')
        except Exception as err:
            #print(type(err))
            if str(type(err)) == "<class 'pywintypes.com_error'>":
                try:
                    DM.RegDM()
                    #再次调用大漠插件
                    self._dm = win32com.client.Dispatch('dm.dmsoft')
                except Exception as err:
                    if str(type(err)) == "<class 'pywintypes.com_error'>":
                        inc.logError('插件调用失败，无法注册！')
                        raise DMerror(self, '插件调用失败，无法注册！')
                    else:
                        raise
            else:
                raise


    #类方法
    @classmethod
    def RegDM(cls):
        '注册，regsvr32'
        p = inc.GetRootDir() + '\\attach\\dm.dll'
        logging.info('注册大漠插件:'  + r'regsvr32 %s /s' % p)
        os.system(r'regsvr32 %s /s' % p)
        sleep(2)


    @property
    def version(self):
        return self._dm.Ver()


    def EnableRXY(self, rx=0, ry=0):
        self._rx = rx
        self._ry = ry


    def DisableRXY(self):
        self._rx = 0
        self._ry = 0


    #----键盘、鼠标操作
    def MoveClick(self, x, y, t=0):
        '移动并左键单击'
        self._dm.MoveTo(self._rx+x, self._ry+y)
        self.sleep()
        self._dm.LeftClick()
        self.sleep(t)
    
    
    def LMoveClick(self, x, y, t=1):
        '拖拽，从x1,y1到x2,y2'
        self._dm.MoveTo(self._rx+x, self._ry+y)
        self.sleep()
        for i in range(t):
            self._dm.LeftDown()
            sleep(1)
            self._dm.LeftUp()
            self.sleep()
            i


    def KeyPress(self, char, t=0):
        '''按键
        key_str     虚拟键码
        "1",          49
        "2",          50
        "3",          51
        "4",          52
        "5",          53
        "6",          54
        "7",          55
        "8",          56
        "9",          57
        "0",          48
        "-",          189
        "=",          187
        "back",       8

        "a",          65
        "b",          66
        "c",          67
        "d",          68
        "e",          69
        "f",          70
        "g",          71
        "h",          72
        "i",          73
        "j",          74
        "k",          75
        "l",          76
        "m",          77
        "n",          78
        "o",          79
        "p",          80
        "q",          81
        "r",          82
        "s",          83
        "t",          84
        "u",          85
        "v",          86
        "w",          87
        "x",          88
        "y",          89
        "z",          90

        "ctrl",       17
        "alt",        18
        "shift",      16
        "win",        91
        "space",      32
        "cap",        20
        "tab",        9
        "~",          192
        "esc",        27
        "enter",      13

        "up",         38
        "down",       40
        "left",       37
        "right",      39

        "option",     93

        "print",      44
        "delete",     46
        "home",       36
        "end",        35
        "pgup",       33
        "pgdn",       34

        "f1",         112
        "f2",         113
        "f3",         114
        "f4",         115
        "f5",         116
        "f6",         117
        "f7",         118
        "f8",         119
        "f9",         120
        "f10",        121
        "f11",        122
        "f12",        123

        "[",          219
        "]",          221
        "\\",         220
        ";",          186
        "'",          222
        ",",          188
        ".",          190
        "/",          191
        '''
        self._dm.KeyPressChar(char)
        self.sleep(t)


    def SayString(self, s, x=0, y=0, t=1):
        '''
        发送文本，有x,y在x,y位置写入，没有就原地输入
        long KeyPressChar(key_str)
        注：调用的KeyPressChar，即模拟键盘
              不完善，仅支持字母、数字、空格的输入
              无法区分大小写，目前也没加入特殊键的响应
        '''
        if x!=0 or y!=0:
            self.MoveClick(x, y)
        for char in s:
            if char==' ': char='space'
            self.KeyPress(char)
        self.sleep(t)


    def CombKey(self, key, fkey='Ctrl', t=1):
        '组合键：fkey + key，fkey默认为Ctrl'
        self._dm.KeyDownChar(fkey)
        self.sleep()
        self._dm.KeyPressChar(key)
        self.sleep()
        self._dm.KeyUpChar(fkey)
        self.sleep(t)


    def KeyPressLong(self, key, t=1):
        '长按按键'
        self._dm.KeyDownChar(key)
        self.sleep(t)
        self._dm.KeyUpChar(key)


    def Drag(self, x1, y1, t1, x2, y2, t2, t=1):
        '拖拽，从x1,y1到x2,y2'
        self._dm.MoveTo(self._rx+x1, self._ry+y1)
        self.sleep()
        self._dm.LeftDown()
        self.sleep(t1)
        self._dm.MoveTo(self._rx+x2, self._ry+y2)
        self.sleep(t2)
        self._dm.LeftUp()
        self.sleep(t)


    def WaitKey(self, vk_code, time_out=1000):
        '''
        等待指定的按键按下 (前台,不是后台)
        long WaitKey(vk_code,time_out)
        vk_code 整形数:虚拟按键码
        time_out 整形数:等待多久,单位毫秒. 如果是0，表示一直等待
        返回值:0:超时；1:指定的按键按下
        '''
        return self._dm.WaitKey(vk_code, time_out)


    #----图色相关
    def SetPath(self, p):
        '''
        设置全局路径,设置了此路径后,所有接口调用中,相关的文件都相对于此路径. 比如图片,字库等.
        long SetPath(path)
        '''
        self._dm.SetPath(inc.GetRootDir() + p)


    def SetPicParam(self, delta_color=101010, sim=0.6, direction=0):
        self._delta_color = delta_color
        self._sim = sim
        self._direction = direction


    def FindPic(self, x1, y1, x2, y2, pic_fullname_list):
        '''
        查找指定区域内的图片,位图必须是24位色格式,支持透明色,当图像上下左右4个顶点的颜色一样时,则这个颜色将作为透明色处理.
        这个函数可以查找多个图片,只返回第一个找到的X Y坐标.
        查找区域应至少比特征图大一个像素
        返回：(True/False, 图片序号, 偏移坐标x, 偏移坐标y)
        string FindPicE(x1, y1, x2, y2, pic_name, delta_color,sim, dir)
        返回找到的图片序号(从0开始索引)以及X和Y坐标 形式如"index|x|y", 比如"3|100|200"
        '''
        assert(isinstance(pic_fullname_list, list) or isinstance(pic_fullname_list, tuple))
        ss = self._dm.FindPicE(self._rx + x1, self._ry + y1, self._rx + x2, self._ry + y2,
                        '|'.join(pic_fullname_list), self._delta_color, self._sim, self._direction)
        s = ss.split('|')
        return (s[0] != '-1', int(s[0]), int(s[1]) - self._rx, int(s[2]) - self._ry)


    def FindPicEx(self, x1, y1, x2, y2, pic_fullname_list):
        '''
        查找指定区域内的图片,位图必须是24位色格式,支持透明色,当图像上下左右4个顶点的颜色一样时,则这个颜色将作为透明色处理.
        这个函数可以查找多个图片,并且返回所有找到的图像的坐标.
        返回：((图片序号，偏移坐标x, 偏移坐标y), (图片序号，偏移坐标x, 偏移坐标y))

        string FindPicEx(x1, y1, x2, y2, pic_name, delta_color,sim, dir)
        返回的是所有找到的坐标格式如下:"id,x,y|id,x,y..|id,x,y" (图片左上角的坐标)
        比如"0,100,20|2,30,40" 表示找到了两个,第一个,对应的图片是图像序号为0的图片,坐标是(100,20),第二个是序号为2的图片,坐标(30,40)
        '''
        assert(isinstance(pic_fullname_list, list) or isinstance(pic_fullname_list, tuple))
        sss = self._dm.FindPicEx(self._rx + x1, self._ry + y1, self._rx + x2, self._ry + y2,
                        '|'.join(pic_fullname_list), self._delta_color, self._sim, self._direction)
        '参数调整，整理FindPicEx返回的参数'
        rr = []
        if sss!='':
            for ss in sss.split('|'):
                r = []
                s = ss.split(',')
                r.append(int(s[0]))
                r.append(int(s[1]) - self._rx)
                r.append(int(s[2]) - self._ry)
                rr.append(tuple(r))
        return tuple(rr)


    def Capture(self, x1, y1, x2, y2, fileName):
        '''
        抓取指定区域(x1, y1, x2, y2)的图像,保存为file(24位位图)
        long Capture(x1, y1, x2, y2, file)
        '''
        if self._dm.Capture(x1 + self._rx, y1 + self._ry, x2 + self._rx, y2 + self._ry, fileName)==0:
            raise DMerror(self, 'Capture失败！')


    #----识字
    def SetDict(self, i, dic_file, color_format, sim):
        '''
        设置字库文件
        
        //RGB单色识别
        s = dm.Ocr(0,0,2000,2000,"9f2e3f-000000",1.0)
        MessageBox s
        
        //RGB单色差色识别
        s = dm.Ocr(0,0,2000,2000,"9f2e3f-030303",1.0)
        MessageBox s
        
        //RGB多色识别(最多支持10种,每种颜色用"|"分割)
        s = dm.Ocr(0,0,2000,2000,"9f2e3f-030303|2d3f2f-000000|3f9e4d-100000",1.0)
        MessageBox s
        
        //HSV多色识别(最多支持10种,每种颜色用"|"分割)
        s = dm.Ocr(0,0,2000,2000,"20.30.40-0.0.0|30.40.50-0.0.0",1.0)
        MessageBox s
        
        //识别后,每行字符串用指定字符分割
        比如用"|"字符分割
        s = dm.Ocr(0,0,2000,2000,"9f2e3f-000000,|",1.0)
        MessageBox s
        
        //比如用回车换行分割
        s = dm.Ocr(0,0,2000,2000,"9f2e3f-000000,"+vbcrlf,1.0)
        MessageBox s
        
        //背景色识别
        //比如要识别背景色为白色,文字颜色未知的字形
        s = dm.Ocr(0,0,2000,2000,"b@ffffff-000000",1.0)
        MessageBox s
        //注: 在color_fomat最前面加上"b@"表示后面的颜色描述是针对背景色,而非字的颜色.
        '''
        if self._dm.SetDict(i, dic_file) != 1:
            raise DMerror(self, '设置字库失败')
        self._dicIndex = i
        if '_color_formats' not in dir(self):
            self._color_formats = ['']*10
        self._color_formats[i] = color_format
        if '_sims' not in dir(self):
            self._sims = [1.0]*10
        self._sims[i] = sim


    def UseDict(self, i):
        '''表示使用哪个字库文件进行识别(index范围:0-9)

        设置之后，永久生效，除非再次设定
        '''
        if self._dicIndex != i:
            if self._dm.UseDict(i) != 1:
                raise DMerror(self, '设置字库失败')
            self._dicIndex = i


    def FindStr(self, x1, y1, x2, y2, strs):
        '''
        在屏幕范围(x1,y1,x2,y2)内,查找string(可以是任意个字符串的组合),并返回符合color_format的坐标位置,相似度sim同Ocr接口描述.

        x1, y1, x2, y2 = 左上, 右下
        strs: 待查找字符串元组，如('长安', '洛阳', '大雁塔')
        color_format 字符串:颜色格式串, '颜色1-偏差1|颜色2-偏差2'
        sim 双精度浮点数:相似度,取值范围0.1-1.0
        返回: (True/False, 找到的字符串, x, y)

        调用大漠接口：
        string FindStrE(x1,y1,x2,y2,string,color_format,sim)
        '''
        assert(isinstance(strs, list) or isinstance(strs, tuple))
        #print(self._rx + x1, self._ry + y1, self._rx + x2, self._ry + y2, '|'.join(strs), self._color_formats[self._dicIndex], self._sims[self._dicIndex])
        ss = self._dm.FindStrE(self._rx + x1, self._ry + y1, self._rx + x2, self._ry + y2, '|'.join(strs), self._color_formats[self._dicIndex], self._sims[self._dicIndex])
        s = ss.split('|')
        return (s[0] != '-1', strs[int(s[0])], int(s[1]) - self._rx, int(s[2]) - self._ry)
    
    
    def FindStrEx(self, x1, y1, x2, y2, strs):
        '''
        在屏幕范围(x1,y1,x2,y2)内,查找string(可以是任意个字符串的组合),并返回符合color_format的坐标位置,相似度sim同Ocr接口描述.
        
        x1, y1, x2, y2 = 左上, 右下
        strs: 待查找字符串元组，如('长安', '洛阳', '大雁塔')
        color_format 字符串:颜色格式串, '颜色1-偏差1|颜色2-偏差2'
        sim 双精度浮点数:相似度,取值范围0.1-1.0
        返回: (True/False, 找到的字符串, x, y)

        调用大漠接口：
        string FindStrFastEx(x1,y1,x2,y2,string,color_format,sim)
        '''
        assert(isinstance(strs, list) or isinstance(strs, tuple))
        sss = self._dm.FindStrFastE(self._rx + x1, self._ry + y1, self._rx + x2, self._ry + y2, '|'.join(strs), self._color_formats[self._dicIndex], self._sims[self._dicIndex])
        rr = []
        if sss != '':
            for ss in sss.split('|'):
                r = []
                s = ss.split(',')
                r.append(strs[int(s[0])])
                r.append(int(s[1]) - self._rx)
                r.append(int(s[2]) - self._ry)
                rr.append(tuple(r))
        return tuple(rr)
    
    
    def Ocr(self, x1, y1, x2, y2):
        '''
        识别屏幕范围(x1,y1,x2,y2)内符合color_format的字符串,并且相似度为sim,sim取值范围(0.1-1.0)
        返回字符串，未找到则为空

        调用大漠接口：
        string Ocr(x1,y1,x2,y2,color_format,sim)
        '''
        #print(self._rx + x1, self._ry + y1, self._rx + x2, self._ry + y2, self._color_formats[self._dicIndex], self._sims[self._dicIndex])
        return self._dm.Ocr(self._rx + x1, self._ry + y1, self._rx + x2, self._ry + y2, self._color_formats[self._dicIndex], self._sims[self._dicIndex])
    
    
    def OcrEx(self, x1, y1, x2, y2):
        '''
        识别屏幕范围(x1,y1,x2,y2)内符合color_format的字符串,并且相似度为sim,sim取值范围(0.1-1.0)
        这个函数可以返回识别到的字符串，以及每个字符的坐标.        
        返回：(字符串, ((x1, y1), (x2, y2), (x3, y3)))
        '''
        sss = self._dm.OcrEx(self._rx + x1, self._ry + y1, self._rx + x2, self._ry + y2, self._color_formats[self._dicIndex], self._sims[self._dicIndex])
        rr = []
        if sss != '':
            rr.append(sss.split('|')[0])
            for ss in sss.split('|')[1:]:
                r = []
                s = ss.split(',')
                r.append(int(s[0]) - self._rx)
                r.append(int(s[1]) - self._ry)
                rr.append(tuple(r))
        return tuple(rr)
        

    #----后台设置
    def BindWindow(self, display, mouse, keypad, mode, hwnd = -1):
        '''
        绑定窗口

        绑定指定的窗口,并指定这个窗口的屏幕颜色获取方式,鼠标仿真模式,键盘仿真模式,以及模式设定,高级用户可以参考BindWindowEx更加灵活强大.
        long BindWindow(hwnd,display,mouse,keypad,mode)
        返回值: 整形数 0: 失败 1: 成功
        '''
        self.UnBindWindow()
        if self._dm.BindWindow(self.Hwindow(hwnd), display, mouse, keypad, mode) == 0:
            raise DMerror(self, '绑定窗口错误！请检查')
        else:
            self.DisableRXY()
            self._bBindWnd = True


    def BindWindowEx(self, display, mouse, keypad, public, mode, hwnd = -1):
        '''
        绑定窗口

        绑定指定的窗口,并指定这个窗口的屏幕颜色获取方式,鼠标仿真模式,键盘仿真模式,以及模式设定,高级用户可以参考BindWindowEx更加灵活强大.
        long BindWindow(hwnd,display,mouse,keypad,mode)
        返回值: 整形数 0: 失败 1: 成功

        hwnd 整形数: 指定的窗口句柄

        display 字符串: 屏幕颜色获取方式 取值有以下几种
        "normal" : 正常模式,平常我们用的前台截屏模式
        "gdi" : gdi模式,用于窗口采用GDI方式刷新时. 此模式占用CPU较大.
        "gdi2" : gdi2模式,此模式兼容性较强,但是速度比gdi模式要慢许多,如果gdi模式发现后台不刷新时,可以考虑用gdi2模式.
        "dx" : 代表"dx.graphic.2d| dx.graphic.3d"
        "dx2" : dx2模式,用于窗口采用dx模式刷新,如果dx方式会出现窗口进程崩溃的状况,可以考虑采用这种.采用这种方式要保证窗口有一部分在屏幕外.win7或者vista不需要移动也可后台. 此模式占用CPU较大.
        "dx3" : dx3模式,同dx2模式,但是如果发现有些窗口后台不刷新时,可以考虑用dx3模式,此模式比dx2模式慢许多. 此模式占用CPU较大.
        dx模式,用于窗口采用dx模式刷新,取值可以是以下任意组合，组合采用"|"符号进行连接  注意此模式需要管理员权限. 支持BindWindow中的缩写模式.
        1. "dx.graphic.2d"  2d窗口的dx图色模式
        ※2. "dx.graphic.2d.2"  2d窗口的dx图色模式  是dx.graphic.2d的增强模式.兼容性更好. <收费功能，具体详情点击查看>
        3. "dx.graphic.3d"  3d窗口的dx图色模式,注意采用这个模式，必须关闭窗口3D视频设置的全屏抗锯齿选项.
        ※4. "dx.graphic.3d.8"  3d窗口的dx8图色模式,注意采用这个模式，必须关闭窗口3D视频设置的全屏抗锯齿选项. 这个模式支持某些老的引擎. <收费功能，具体详情点击查看>

        mouse 字符串: 鼠标仿真模式 取值有以下几种
        "normal" : 正常模式,平常我们用的前台鼠标模式
        "windows" : Windows模式,采取模拟windows消息方式 同按键的后台插件.
        "windows2" : 代表"dx.mouse.position.lock.api|dx.mouse.position.lock.message|dx.mouse.state.message"
        "windows3": Windows3模式，采取模拟windows消息方式,可以支持有多个子窗口的窗口后台
        dx模式,取值可以是以下任意组合. 组合采用"|"符号进行连接 注意此模式需要管理员权限.支持BindWindow中的缩写模式
        1. "dx.mouse.position.lock.api"  此模式表示通过封锁系统API，来锁定鼠标位置.
        2. "dx.mouse.position.lock.message" 此模式表示通过封锁系统消息，来锁定鼠标位置.
        3. "dx.mouse.focus.input.api" 此模式表示通过封锁系统API来锁定鼠标输入焦点.
        4. "dx.mouse.focus.input.message"此模式表示通过封锁系统消息来锁定鼠标输入焦点.
        5. "dx.mouse.clip.lock.api" 此模式表示通过封锁系统API来锁定刷新区域。注意，使用这个模式，在绑定前，必须要让窗口完全显示出来.
        6. "dx.mouse.input.lock.api" 此模式表示通过封锁系统API来锁定鼠标输入接口.
        7. "dx.mouse.state.api" 此模式表示通过封锁系统API来锁定鼠标输入状态.
        8. "dx.mouse.state.message" 此模式表示通过封锁系统消息来锁定鼠标输入状态.
        9. "dx.mouse.api"  此模式表示通过封锁系统API来模拟dx鼠标输入.
        ※10. "dx.mouse.cursor"  开启此模式，可以后台获取鼠标特征码. <收费功能，具体详情点击查看>
        ※11. "dx.mouse.raw.input"  有些窗口需要这个才可以正常操作鼠标. <收费功能，具体详情点击查看>
        ※12. "dx.mouse.input.lock.api2"  部分窗口在后台操作时，前台鼠标会移动,需要这个属性. <收费功能，具体详情点击查看>
        ※13. "dx.mouse.input.lock.api3"  部分窗口在后台操作时，前台鼠标会移动,需要这个属性. <收费功能，具体详情点击查看>

        keypad 字符串: 键盘仿真模式 取值有以下几种
        "normal" : 正常模式,平常我们用的前台键盘模式
        "windows": Windows模式,采取模拟windows消息方式 同按键的后台插件.
        "dx" : 代表" dx.public.active.api|dx.public.active.message| dx.keypad.state.api|dx.keypad.api|dx.keypad.input.lock.api"
        dx模式 : 取值可以是以下任意组合. 组合采用"|"符号进行连接 注意此模式需要管理员权限.支持BindWindow中的缩写模式.
        1. "dx.keypad.input.lock.api" 此模式表示通过封锁系统API来锁定键盘输入接口.
        2. "dx.keypad.state.api" 此模式表示通过封锁系统API来锁定键盘输入状态.
        3. "dx.keypad.api" 此模式表示通过封锁系统API来模拟dx键盘输入.
        ※4. "dx.keypad.raw.input"  有些窗口需要这个才可以正常操作键盘. <收费功能，具体详情点击查看>

        public 字符串: 公共属性 dx模式共有  注意以下列表中,前面打五角星的表示需要管理员权限
        取值可以是以下任意组合. 组合采用"|"符号进行连接 这个值可以为空
        1. ★ "dx.public.active.api" 此模式表示通过封锁系统API来锁定窗口激活状态.  注意，部分窗口在此模式下会耗费大量资源慎用.
        2. ★ "dx.public.active.message" 此模式表示通过封锁系统消息来锁定窗口激活状态.  注意，部分窗口在此模式下会耗费大量资源 慎用. 另外如果要让此模式生效，必须在绑定前，让绑定窗口处于激活状态,否则此模式将失效. 比如dm.SetWindowState hwnd,1 然后再绑定.
        3.    "dx.public.disable.window.position" 此模式将锁定绑定窗口位置.不可与"dx.public.fake.window.min"共用.
        4.    "dx.public.disable.window.size" 此模式将锁定绑定窗口,禁止改变大小. 不可与"dx.public.fake.window.min"共用.
        5.    "dx.public.disable.window.minmax" 此模式将禁止窗口最大化和最小化,但是付出的代价是窗口同时也会被置顶. 不可与"dx.public.fake.window.min"共用.
        ※6.    "dx.public.fake.window.min" 此模式将允许目标窗口在最小化状态时，仍然能够像非最小化一样操作.. 另注意，此模式会导致任务栏顺序重排，所以如果是多开模式下，会看起来比较混乱，建议单开使用，多开不建议使用. <收费功能，具体详情点击查看>
        ※7.    "dx.public.hide.dll" 此模式将会隐藏目标进程的大漠插件，避免被检测..另外使用此模式前，请仔细做过测试，此模式可能会造成目标进程不稳定，出现崩溃。<收费功能，具体详情点击查看>
        ※8. ★ "dx.public.active.api2" 此模式表示通过封锁系统API来锁定窗口激活状态. 部分窗口遮挡无法后台,需要这个属性. <收费功能，具体详情点击查看>
        ※9. ★ "dx.public.input.ime" 此模式是配合SendStringIme使用. 具体可以查看SendStringIme接口. <收费功能，具体详情点击查看>
        ※10 ★ "dx.public.graphic.protect" 此模式可以保护dx图色不被恶意检测.同时对dx.keypad.api和dx.mouse.api也有保护效果. <收费功能，具体详情点击查看>
        ※11 ★ "dx.public.disable.window.show" 禁止目标窗口显示,这个一般用来配合dx.public.fake.window.min来使用. <收费功能，具体详情点击查看>
        ※12 ★ "dx.public.anti.api" 此模式可以突破部分窗口对后台的保护. <收费功能，具体详情点击查看>
        ※13 ★ "dx.public.memory" 此模式可以让内存读写函数突破保护.只要绑定成功即可操作内存函数. <收费功能，具体详情点击查看>
        ※14 ★ "dx.public.km.protect" 此模式可以保护dx键鼠不被恶意检测.最好配合dx.public.anti.api一起使用. 此属性可能会导致部分后台功能失效. <收费功能，具体详情点击查看>
        ※15    "dx.public.prevent.block"  绑定模式1 3 5 7 101 103下，可能会导致部分窗口卡死. 这个属性可以避免卡死. <收费功能，具体详情点击查看>
        ※16    "dx.public.ori.proc"  此属性只能用在模式0 1 2 3和101下. 有些窗口在不同的界面下(比如登录界面和登录进以后的界面)，键鼠的控制效果不相同. 那可以用这个属性来尝试让保持一致. 注意的是，这个属性不可以滥用，确保测试无问题才可以使用. 否则可能会导致后台失效. <收费功能，具体详情点击查看>

        mode 整形数: 模式。 取值有以下两种
        0 : 推荐模式,此模式比较通用，而且后台效果是最好的.
        ※1 : 和模式0效果一样，如果模式0会失败时，可以尝试此模式, <收费功能，具体详情点击查看>.
        2 : 同模式0,此模式为老的模式0,尽量不要用此模式，除非有兼容性问题.
        ※3 : 同模式1,此模式为老的模式1,尽量不要用此模式，除非有兼容性问题. <收费功能，具体详情点击查看>
        4 : 同模式0,如果模式0有崩溃问题，可以尝试此模式.
        ※5 : 同模式1, 如果模式0有崩溃问题，可以尝试此模式. <收费功能，具体详情点击查看>
        ※6 : 同模式0，如果模式0有崩溃问题，可以尝试此模式. <收费功能，具体详情点击查看>.
        ※7 : 同模式1，如果模式1有崩溃问题，可以尝试此模式. <收费功能，具体详情点击查看>.
        ※101 : 超级绑定模式. 可隐藏目标进程中的dm.dll.避免被恶意检测.效果要比dx.public.hide.dll好. 推荐使用. <收费功能，具体详情点击查看>
        ※103 : 同模式101，如果模式101有崩溃问题，可以尝试此模式. <收费功能，具体详情点击查看>

        需要注意的是: 模式1 3 5 7 101 103在大部分窗口下绑定都没问题。但也有少数特殊的窗口，比如有很多子窗口的窗口，对于这种窗口，在绑定时，一定要把鼠标指向一个可以输入文字的窗口，比如一个文本框，最好能激活这个文本框，这样可以保证绑定的成功.
        '''
        self.UnBindWindow()
        if self._dm.BindWindowEx(self.Hwindow(hwnd), display, mouse, keypad, public, mode) == 0:
            raise DMerror(self, '绑定窗口错误！请检查')
        else:
            self._bBindWnd = True


    def UnBindWindow(self):
        '''
        解除绑定

        long UnBindWindow()
        返回值: 整形数 0: 失败 1: 成功
        '''
        if self._bBindWnd:
            if self._dm.UnBindWindow() == 0:
                raise DMerror(self, '解除窗口绑定错误！请检查')


    #----窗体类函数
    def FindWindow(self, className, title):
        '''
        查找窗口（类名，标题名），返回窗口hwnd
        long FindWindow(class,title)
        '''
        self._hwnd = self._dm.FindWindow(className, title)
        #if self._hwnd <= 0:
        #    raise DMerror(self, "找不到窗口，请检查窗口名是否正确")
        return self._hwnd


    def FindWindowEx(self, className, title, hwnd = -1):
        '''
        在当前窗口中查找子窗口。

        long FindWindowEx(parent,class,title)
        '''
        self._hwnd = self._dm.FindWindowEx(self.Hwindow(hwnd), className, title)
        #if self._hwnd <= 0:
        #    raise DMerror(self, "找不到窗口，请检查窗口名是否正确")
        return self._hwnd


    def Hwindow(self, hwnd = -1):
        '''
        获取hwnd，无则获取当前窗口
        long GetForegroundWindow()
        '''
        if hwnd > 0:
            self._hwnd = hwnd
        elif self._hwnd == None or self._hwnd <= 0:
            self._hwnd = self._dm.GetForegroundWindow()
            if self._hwnd <= 0:
                raise DMerror(self, "找不到窗口，请检出hwnd是否存在！")
        return self._hwnd


    def MoveWindow(self, global_x, global_y, t=1, hwnd = -1):
        '''
        移动窗口，x, y指全局坐标。
        long MoveWindow(hwnd,x,y)
        '''
        self._dm.MoveWindow(self.Hwindow(hwnd), global_x, global_y)
        self.sleep(t)


    def SetWindowState(self, flag, t=1, hwnd = -1):
        '''
        long SetWindowState(hwnd,flag)
        flag 整形数: 取值定义如下
        0 : 关闭指定窗口
        1 : 激活指定窗口
        2 : 最小化指定窗口,但不激活
        3 : 最小化指定窗口,并释放内存,但同时也会激活窗口.
        4 : 最大化指定窗口,同时激活窗口.
        5 : 恢复指定窗口 ,但不激活
        6 : 隐藏指定窗口
        7 : 显示指定窗口
        8 : 置顶指定窗口
        9 : 取消置顶指定窗口
        10 : 禁止指定窗口
        11 : 取消禁止指定窗口
        12 : 恢复并激活指定窗口
        13 : 强制结束窗口所在进程.
        '''
        self._dm.SetWindowState(self.Hwindow(hwnd), flag)
        self.sleep(t)


    def ActiveWindow(self, t=1, hwnd = -1):
        '''
        激活窗口
        '''
        self.SetWindowState(1, t, hwnd)


    def MaxWindow(self, t=1, hwnd = -1):
        '''
        最大化窗口
        '''
        self.SetWindowState(4, t, hwnd)


    def SetWindowSize(self, width, height, hwnd = -1):
        '''
        设置窗口大小
        long SetWindowSize(hwnd,width,height)
        '''
        self._dm.SetWindowSize(self.Hwindow(hwnd), width, height)


    def SayZhong(self, s, t=0, x=0, y=0, hwnd = -1):
        '''
        向指定窗口发送文本数据
        long SendString(hwnd,str)
        '''
        if x!=0 or y!=0:
            self.MoveClick(x, y)
        self._dm.SendString(self.Hwindow(hwnd), s)
        self.sleep(t)


    #----win32gui
    def GetCursorPos(self):
        '获取鼠标位置'
        x, y = win32gui.GetCursorPos()
        return x - self._rx, y - self._ry


    def _GetCursorPos(self):
        '''
        获取鼠标位置. 当前无法使用，因变体指针问题
        long GetCursorPos(x, y)
        '''
        x, y = 1, 1
        if self._dm.GetCursorPos(x, y) == 0:
            raise DMerror(self, 'GetCursorPos失败！')
        return (x - self._rx, y - self._ry)


    #支持性函数
    @staticmethod
    def sleep(t=0):
        '延时。t<3时是参数，与dt值有关，t>3是t秒'
        if inc.G_EXIT:
            sys.exit(2)
        if t < len(DM._lt):
            sleep(DM._lt[t]   * DM._dt)
        else:
            for i in range(t):
                if inc.G_EXIT:
                    sys.exit(2)
                else:
                    sleep(1)
            i


    def Delay(self, mis):
        '延时指定的毫秒,过程中不阻塞UI操作'
        self._dm.Delay(mis)


class DMerror(Exception):
    '大漠异常'
    def __init__(self, dm, msg):
        self._dm = dm
        super().__init__('大漠错误（' + self.GetLastError() + '） \n---- ' + msg)


    def GetLastError(self):
        '获取插件命令的最后错误'
        e = self._dm.GetLastError()
        s = '无错误'
        if e == -1 :
            s = '表示你使用了绑定里的收费功能，但是没注册，无法使用.'
        elif e == -2 :
            s =  '使用模式0 2 4 6时出现，因为目标窗口有保护，或者目标窗口没有以管理员权限打开. 常见于win7以上系统.或者有安全软件拦截插件.解决办法: 关闭所有安全软件，并且关闭系统UAC,然后再重新尝试. 如果还不行就可以肯定是目标窗口有特殊保护.'
        elif e == -3 :
            s = '使用模式0 2 4 6时出现，可能目标窗口有保护，也可能是异常错误.'
        elif e == -4 :
            s =  '使用模式1 3 5 7 101 103时出现，这是异常错误.'
        elif e == -5 :
            s = '使用模式1 3 5 7 101 103时出现, 这个错误的解决办法就是关闭目标窗口，重新打开再绑定即可. 也可能是运行脚本的进程没有管理员权限.'
        elif e in (-6, -7, -9) :
            s = '使用模式1 3 5 7 101 103时出现,异常错误. 还有可能是安全软件的问题，比如360等。尝试卸载360.'
        elif e in (-8, -10) :
            s = '使用模式1 3 5 7 101 103时出现, 目标进程可能有保护,也可能是插件版本过老，试试新的或许可以解决.'
        elif e == -11 :
            s = '使用模式1 3 5 7 101 103时出现, 目标进程有保护. 告诉我解决。'
        elif e == -12 :
            s = '使用模式1 3 5 7 101 103时出现, 目标进程有保护. 告诉我解决。'
        elif e == -13 :
            s = '使用模式1 3 5 7 101 103时出现, 目标进程有保护. 或者是因为上次的绑定没有解绑导致。 尝试在绑定前调用ForceUnBindWindow.'
        elif e == -14 :
            s = '使用模式0 1 4 5时出现, 有可能目标机器兼容性不太好. 可以尝试其他模式. 比如2 3 6 7'
        elif e == -16 :
            s = '可能使用了绑定模式 0 1 2 3 和 101，然后可能指定了一个子窗口.导致不支持.可以换模式4 5 6 7或者103来尝试. 另外也可以考虑使用父窗口或者顶级窗口.来避免这个错误。还有可能是目标窗口没有正常解绑 然后再次绑定的时候.'
        elif e == -17 :
            s = '模式1 3 5 7 101 103时出现. 这个是异常错误. 告诉我解决.'
        elif e == -18 :
            s = '句柄无效.'
        elif e == -19 :
            s = '使用模式0 1 2 3 101时出现,说明你的系统不支持这几个模式. 可以尝试其他模式.'
        return s


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    dm = DM()
    print(dm.version)
    print(dm.WaitKey(27))