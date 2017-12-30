# _*_ coding: utf-8 _*_
import win32gui
import functools
import os
import time
import ctypes
import inspect
import threading

from logger import logger
__author__ = '别用铅笔写爱'
__date__ = '2017/12/21 0021 上午 2:54'
check_methods = {}


def func_error_wrapper(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            logger.error('执行函数{}时出现了异常, 错误信息是{}'.format(func.__name__, str(e)), exc_info=True)
        else:
            return result
    return wrapper


def page_checker_register(retry_times=0, use_callback=True, fail_to_check=list(), timeout=None, binding=list()):
    """
    装饰后的函数/方法将会被注册并绑定。
    :param retry_times: 失败后重试次数
    :param use_callback: 当成功的时候是否使用回调函数
    :param fail_to_check: 传递为页面名称的字符串或方法/函数或包含两者的列表, 当失败的时候检查那些页面，
            直到其中一次检查成功或者列表循环到尽头才会终止检查
            默认执行回调, 如果不想执行回调需要在每个字符串前加上 '-', 字符串的方式不能精确控制每个函数, 
            可以通过传递 函数/方法指针 的列表实现精确控制或者自定义的逻辑
    :param timeout: 检查最长时间，如果超时会抛出一个超时错误
    :param binding: 绑定函数。会按照列表的顺序执行所有里面的函数
    :return: 一个被注册后的函数/方法
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


class TimeoutThreading(threading.Thread):
    """
    调用 raise_error 方法, 可以强行结束线程
    可以获得函数执行的结果
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._result = None

    def _get_pid(self):
        if not self.is_alive():
            logger.error(self.name + '获得pid失败, 因为线程已经结束')
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for tid, obj in threading._active.items():
            if obj is self:
                self._thread_id = tid
                return tid
        logger.error(self.name + '无法找到对应的pid')

    def run(self):
        try:
            if self._target:
                self._result = self._target(*self._args, **self._kwargs)
        finally:
            del self._target, self._args, self._kwargs

    def raise_error(self, error_type=Exception):
        _async_raise(self._get_pid(), error_type)

    def get_result(self):
        return self._result


@func_error_wrapper
def _async_raise(tid, error_type):
    if not inspect.isclass(error_type):
        raise TypeError('只能传递错误的类')
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(error_type))
    if res == 0:
        raise ValueError('无效的tid: {}'.format(tid))
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
        raise SystemError('对{}抛出异常失败'.format(tid))




