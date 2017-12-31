import win32gui
import win32com.client
import time
import os
import hashlib
import inspect

from logger import logger
from exceptions import HandlerError, SizeError, PluginError
from utils import page_checker_register

"""这个模块定义了框架的基类和基础的check方法"""


class BaseFactory:
    page_list = []
    use_callback = True
    use_check_method = True

    def __enter__(self):
        self.over = False
        return self

    def __init__(self, impact3=None):
        self.impact3 = impact3
        self.over = True

    def run(self, *args, **kwargs):
        while not self.over and self.page_list:
            for ind, page in enumerate(self.page_list):
                if self.over:
                    break
                if ind < self.impact3.pages.index(page):
                    continue
                self.impact3.check_page(page)
        self.over = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.impact3.capture('errors/' + str(time.time()).replace('.', '')[:12] + '.png')
        self.over = True
        print('释放绑定窗口')
        self.impact3.dm.UnBindWindow()


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

    def click(self, x=0, y=0, temp=0.05):
        self.dm.MoveTo(x*self.rate, y*self.rate)
        time.sleep(temp)
        self.dm.LeftClick()
        time.sleep(0.01)

    def find_str(self, x1, y1, x2, y2, color='', sim=0.5):
        x1, y1, x2, y2 = x1 * self.rate, y1 * self.rate, x2 * self.rate, y2 * self.rate
        text = self.dm.Ocr(x1, y1, x2, y2, color, sim)
        return text

    def load_pic(self, filename):
        """将指定的图片加入缓存, 0失败, 1成功"""
        pass

    def find_pic(self, x1, y1, x2, y2, filename, delta_color, sim, dir):
        """查找区域内的所有符合图片的坐标, 返回格式id,x,y|id,x,y..|id,x,y, id是filename的排序"""
        pass

    def get_ave_RGB(self, x1, y1, x2, y2):
        """返回区域内的颜色均值"""
        pass

    def press_key(self, key_str=''):
        self.dm.KeyPressChar(key_str)
        time.sleep(0.01)

    def wheel_down(self):
        self.dm.WheelDown()
        time.sleep(0.01)

    def wheel_up(self):
        self.dm.WheelUp()
        time.sleep(0.01)

    def set_path(self, p=os.getcwd()):
        self.dm.SetPath(p)

    def capture(self, fn=hashlib.md5(bytes(str(time.time()), encoding='ascii')).hexdigest() + '.png'):
        self.dm.CapturePng(0, 0, 1280*self.rate, 720*self.rate, fn)
        time.sleep(0.01)

    def drag(self, x1, y1, x2, y2, t=2):
        x1, y1, x2, y2 = x1*self.rate, y1*self.rate, x2*self.rate, y2*self.rate
        self.dm.MoveTo(x1, y1)
        self.dm.LeftDown()
        time.sleep(t)
        t /= abs((x1 - x2) / 20)
        path = -20 if x1 > x2 else 20
        for i in range(int(x1), int(x2), path):
            x1, _ = path + x1, x1
            y1 = y1 * (x1 / _)
            self.dm.MoveTo(x1, y1)
            time.sleep(t)
        self.dm.MoveTo(x2, y2)
        self.dm.LeftUp()
        time.sleep(0.01)

    def get_color(self, *args):
        x, y = args if args else self.dm.GetCursorPos()[1:]
        time.sleep(0.01)
        return self.dm.GetColor(x, y)

    def compare_color(self, x, y, tolerate, *args):
        compared_color = '|'.join(args) if args else ''
        if isinstance(tolerate, str):
            compared_color, tolerate = tolerate + '|' + compared_color if compared_color else tolerate, 0.95
        time.sleep(0.01)
        return False if self.dm.CmpColor(x*self.rate, y*self.rate, compared_color, str(tolerate)) else True

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
        try:
            if not self.bind:
                self.bind = True
                self.dm.BindWindow(self.hwnd, 'dx2', 'dx', 'dx', 0)
                logger.debug('succeed fetching and binding')
        except Exception as e:
            raise HandlerError(str(e), 'can\'t bind the handler, because no handler found')

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


@page_checker_register(retry_times=1)
def check_home(impact3):
    return impact3.compare_color(1210, 676, 1, 'fd8a82') and impact3.compare_color(1226, 692, 0.8, '8ab33e') and \
           not impact3.compare_color(734, 202, 1, '00c0fc') and not impact3.compare_color(747, 496, 1, 'ffe14b')