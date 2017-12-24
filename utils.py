# _*_ coding: utf-8 _*_
import win32gui
import functools
import os
import time

from logger import logger
__author__ = '别用铅笔写爱'
__date__ = '2017/12/21 0021 上午 2:54'
check_methods = {}
broken_down = 0


def wrap_run(self):
    def outer(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            global broken_down
            if broken_down > 3:
                self.over = True
                broken_down = 0
            while not self.over:
                func(*args, **kwargs)
            return
        return inner
    return outer


def false_to_retry(retry=5, broken=3):
    def outer(func):
        def inner(*args, **kwargs):
            global broken_down
            nonlocal retry
            result = func(*args, **kwargs)
            while not result and retry > 0 and result is not None:
                logger.info('尝试重新检查页面{}, 剩余次数{}'.format(args[-1], str(retry)))
                result = func(*args, **kwargs)
                retry -= 1
                time.sleep(0.5)
            retry = 5 if result else retry
            if retry == 0:
                broken_down += 1
            return result
        return inner
    return outer


def page_checker_register(func):
    def bool_dispatcher(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            self = args[0]
            if f(*args, **kwargs):
                self.page = f.__name__.split('check_')[-1]
                return True
            return False
        return wrapper
    module_name = os.path.basename(func.__globals__['__file__'])[:-3]
    func = bool_dispatcher(func)
    check_methods.setdefault(module_name, {})
    check_methods[module_name][func.__name__] = func


def specific_check(self, page, func):
    """特殊的检查, 这个检查可以同时检查这个页面和下个页面, 直到无法遇到特殊检查"""
    if func is None:
        return
    index = self.pages.index(page) or 0

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        time.sleep(0.3)
        result = func(*args, **kwargs)
        if not result:
            next_check = self.check_page(self.pages[index + 1])
            if next_check:
                logger.info('特殊页面不存在, 当前页面是', self.page)
                return True
        if result:
            logger.info('特殊页面检查成功', str(func))
        return result
    return wrapper


def wrap_callbacks(page, func):
    if not func:
        return None

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        logger.info('{}页面的回调函数执行成功'.format(page))
        return func
    return wrapper


def retry_times(retry=3):
    def outer(func):
        @functools.wraps(func)
        def inner(self, *args, **kwargs):
            nonlocal retry
            while retry > 0:
                try:
                    func(self, *args, **kwargs)
                except Exception as e:
                    print(str(e))
                    if not self.hwnd:
                        self.hwnd = win32gui.FindWindow('Qt5QWindowIcon', '崩坏3 - MuMu模拟器')
                    win32gui.SetForegroundWindow(self.hwnd)
                    print('剩余尝试次数', str(retry))
                    retry -= 1
                else:
                    break
                finally:
                    if retry == 0:
                        raise Exception('没办法得到正确的窗口')
        return inner
    if callable(retry):
        retry, func = 3, retry
        return outer(func)
    return outer


@page_checker_register
def check_home(impact3):
    return impact3.compare_color(1210, 676, 1, 'fd8a82') and impact3.compare_color(1226, 692, 0.8, '8ab33e') and \
           not impact3.compare_color(734, 202, 1, '00c0fc') and not impact3.compare_color(747, 496, 1, 'ffe14b')