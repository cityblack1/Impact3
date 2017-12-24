import win32gui
import win32com.client
import time
import os
import hashlib
import inspect

from logger import logger
from exceptions import HandlerError, SizeError, PluginError
from abc import ABCMeta, abstractmethod


class BaseFactory:
    __metaclass__ = ABCMeta

    def __init__(self):
        self.impact3 = None
        self.over = False

    @abstractmethod
    def run(self, instance, *args, **kwargs): pass


class DMWrapper(object):
    """MuMu 模拟器   720 宽 * 1280高"""
    def __init__(self):
        self.dm = None
        self.hwnd = None
        self.bind = False
        self.load_damo()
        self.set_path()
        self.width, self.height = self.dm.GetClientSize(self.hwnd)[1:]
        self.rate = self.get_size_rate()
        self.key_map = DMWrapper.get_key_map()

    @staticmethod
    def get_key_map():
        """得到键盘按键的码位映射"""
        with open('keyMap') as f:
            key_map = f.read()
            return dict(((x.strip().replace('"', ''), y.strip()) for x, y in (i.split(',  ') for i in key_map.split('\n'))))

    def click(self, x=0, y=0, temp=0.05):
        self.dm.MoveTo(x*self.rate, y*self.rate)
        time.sleep(temp)
        self.dm.LeftClick()

    def drag(self, x1, y1, x2, y2):
        '拖拽，从x1,y1到x2,y2'
        self.dm.MoveTo(x1, y1)
        time.sleep(1)
        self.dm.LeftDown()
        time.sleep(10)
        self.dm.MoveTo(x2, y2)
        time.sleep(1)
        self.dm.LeftUp()
        time.sleep(1)
        
    def press_key(self, key_str=''):
        self.dm.KeyPress(int(self.key_map[key_str]))

    def set_path(self, p=os.getcwd()):
        self.dm.SetPath(p)

    def capture(self, fn=hashlib.md5(bytes(str(time.time()), encoding='ascii')).hexdigest() + '.png'):
        self.dm.CapturePng(0, 0, 1280*self.rate, 720*self.rate, fn)

    def get_color(self, *args):
        x, y = args if args else self.dm.GetCursorPos()[1:]
        return self.dm.GetColor(x, y)

    def compare_color(self, x, y, tolerate, *args):
        compared_color = '|'.join(args) if args else ''
        if isinstance(tolerate, str):
            compared_color, tolerate = tolerate + '|' + compared_color if compared_color else tolerate, 0.95
        return False if self.dm.CmpColor(x, y, compared_color, str(tolerate)) else True

    def fetch_hwnd(self):
        """取到模拟器内部屏幕控件的句柄, 并绑定窗口"""
        if self.hwnd is None:
            try:
                logger.debug('trying to fetch the handler...')
                _ = win32gui.FindWindow('Qt5QWindowIcon', '崩坏3 - MuMu模拟器')
                self.hwnd = self.dm.EnumWindow(_, '', '', 4)
            except Exception as e:
                try:
                    logger.error(str(e), 'fail to fetch, attempting another way...')
                    hwnd_list = []
                    win32gui.EnumWindows(lambda h, param: param.append(h), hwnd_list)
                    for h in hwnd_list:
                        if '崩坏3' in win32gui.GetWindowText(h) or 'MuMu模拟器' in win32gui.GetWindowText(h):
                            self.hwnd = self.dm.EnumWindow(h, '', '', 4)
                            break
                except Exception as e:
                    raise HandlerError(str(e), 'catch a exception while reloading handler.')
            logger.debug('succeed finding handler')
        if not self.bind:
            self.bind = True
            self.dm.BindWindow(self.hwnd, 'dx2', 'dx', 'dx', 0)
            logger.debug('succeed fetching and binding')

    def load_damo(self):
        if self.dm is None:
            try:
                logger.debug('trying to touch the instance of dm')
                self.dm = win32com.client.Dispatch('dm.dmsoft')
            except Exception as e:
                logger.error('failed, attempt to registry again')
                if str(type(e)) == "<class 'pywintypes.com_error'>":
                    try:
                        os.system(r'regsvr32 %s /s' % os.getcwd() + '\\dm.dll')
                    except Exception as e:
                        raise PluginError(str(e), 'invalid dm plugin!')
        if self.hwnd is None:
            self.fetch_hwnd()

    def get_size_rate(self):
        """获得长宽倍率"""
        if abs(self.width / 1280 - self.height / 720) > 0.025 * sum([self.width, self.height]) / 2000:
            raise SizeError('size error, 1280 * 720 required')
        return self.width / 1280

