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

"""这个模块实现了框架里的实用工具, 包括装饰器, 工具函数, 工具类等等"""


def func_error_wrapper(func):
    """让被装饰的函数静默退出, 只记录日志"""
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
    装饰后的函数/方法将会被注册并绑定, 会被注册到check_methods中,以便被框架调用。
    :param retry_times: 失败后重试次数
    :param use_callback: 当成功的时候是否使用回调函数
    :param fail_to_check: 字符串或者函数的字符串表示或者包含两者的列表
            特殊字符串: all, [所有的page的名字], [所有的page的名字前面再加上 - ]
                        比如 'all', '-home', 'home'
                        all 相当于执行所有page的check_page函数
                        -home相当于执行check_page(home),但是不进行回调
                        home是执行check_page(home)并且成功后进行回调函数
                        
            函数字符串: '比如self.pass_page('home')', 相当于执行 self.pass_page('home') 
                        和正常语法一样只是需要用字符串的形式表示                                
            *** 会按照列表顺序执行, 直到返回 True 或者等效结果, 当为 False 或等效结果时会继续向下执行            
            *** 注意, func必须是字符串, 因为python的装饰器不能在运行的时候动态加载self....
    :param timeout: 检查最长时间，如果超时会抛出一个超时错误
    :param binding: 成功后的绑定函数。和fail_to_check一样, 需要一个字符串或字符串列表, 只不过没有特殊字符串
            当result为True或者其他等效值的时候会执行
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
                        if hasattr(self.impact3, 'page'):
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
    对threading的Tread的封装, 实现原类不具备的高级功能
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
        raise TypeError('只能传递异常类, 不能传递实例')
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(error_type))
    if res == 0:
        raise ValueError('无效的tid: {}'.format(tid))
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
        raise SystemError('对{}抛出异常失败'.format(tid))


def time_checker(timeout=None, retry=0, callback_s=None, callback_f=None):
    """
    通用的超时装饰器
    :param timeout: 最大时间限制
    :param retry: 重试次数
    :param callback_s: 成功时的回调函数
    :param callback_f: 失败时的回调函数
    :return: 函数或者方法的结果
    """
    if callable(timeout):
        func, timeout = timeout, None

    def outer(fun):
        def wrapper(*args, **kwargs):
            nonlocal retry
            result = threading_timeout(fun, timeout, *args, **kwargs)
            while not result and retry > 0:
                logger.error('没有拿到结果, 开始重试, 剩余重试次数{}'.format(retry))
                result = threading_timeout(fun, timeout, *args, **kwargs)
                retry -= 1
            logger.info('执行函数{}{}'.format(get_fun_name(fun), '成功' if result else '失败'))
            r = None
            if result and callback_s:
                r = callable_dispatch(callback_s)
                logger.info('执行{}的回调函数成功, 结果是{}'.format(get_fun_name(fun), r))
            if not result and callback_f:
                r = callable_dispatch(callback_f)
                logger.info('执行{}的回调函数成功, 结果是{}'.format(get_fun_name(fun), r))
            return r
        return wrapper
    return outer


def threading_timeout(fun, timeout=None, *args, **kwargs):
    name = get_fun_name(fun)
    if timeout:
        logger.info('开始执行{}, 限时{}s'.format(name, timeout))
        thread = TimeoutThreading(target=fun, args=args, kwargs=kwargs)
        thread.setDaemon(True)
        thread.start()
        thread.join(timeout)
        result = thread.get_result()
        if thread.is_alive():
            logger.error('{}的执行超时, 强制终止'.format(name))
            thread.raise_error(TimeoutError)
    else:
        logger.info('开始执行{}'.format(name))
        result = fun()
    logger.info('{}执行完毕, 结果是{}'.format(name, result))
    return result


@func_error_wrapper
def callable_dispatch(fun):
    r = None
    if callable(fun):
        r = fun()
    else:
        for f in fun:
            r = f()
            if r:
                break
    return r


@func_error_wrapper
def get_fun_name(fun):
    if isinstance(fun, functools.partial):
        return fun.func.__name__
    return fun.__name__


def super_index(li, page):
    try:
        return li.index(page)
    except:
        return -1
