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


def index_super(li, em):
    try:
        return li.index(em)
    except:
        try:
            return li.index(em[:-2])
        except:
            try:
                return li.index(em+'?')
            except:
                return -1


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


def page_checker_register(retry_times=0, use_callback=True, fail_to_check=list(), timeout=-1, binding=list()):
    """
    装饰后的函数将会被注册并绑定。
    :param retry_times: 失败后重试次数
    :param use_callback: 当成功的时候是否使用回调函数
    :param fail_to_check: 字符串列表或字符串, 当失败的时候检查那些页面，直到成功为止, 字符串all代表全部检查, None代表不检查, 列表代表顺序检查.
            默认执行回调, 如果不想执行回调需要在每个字符串前加上 '-'
    :param timeout: 检查最长时间，如果超时会抛出一个超时错误
    :param binding: 绑定函数。会按照列表的顺序执行所有里面的函数
    :return:
    """
    def outer(fun):
        def bool_dispatcher(f):
            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                self = args[0]
                logger.info('开始执行检查函数' + f.__name__)
                if f(*args, **kwargs):
                    try:
                        self.impact3.page = f.__name__.split('check_')[-1]
                    except AttributeError as e:
                        self.page = f.__name__.split('check_')[-1]
                    logger.info(f.__name__ + '的结果是True')
                    return True
                logger.info(f.__name__ +  '的结果是False')
                return False
            return wrapper
        module_name = os.path.basename(fun.__module__.split('.')[-1])
        fu = bool_dispatcher(fun)
        check_methods.setdefault(module_name, {})
        check_methods[module_name][fu.__name__] = [fu, retry_times, use_callback, fail_to_check, timeout, binding]

    if callable(retry_times):
        call, retry_times = retry_times, 0
        return outer(call)
    return outer


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




