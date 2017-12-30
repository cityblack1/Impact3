import time
import os

from importlib import import_module
from collections.abc import Sequence
from utils import TimeoutThreading
from base import DMWrapper
from utils import check_methods
from functools import partial
from exceptions import InvalidCheckMethod, NoPageListFound
from logger import logger


class Impact3(DMWrapper):
    """MuMu 模拟器   720 宽 * 1280高"""
    def __init__(self, factories=None):
        super().__init__()
        self.alive = True
        self.factories = factories
        self.factory_i = None
        self.pages = []
        self.order_list = []
        self.callbacks = {}
        self.module_name = ''
        self.temp_result = ''
        self.child_tasks = []
        for fl in check_methods.get('base', {}).values():
            _ = fl[0].__name__
            fl[0] = partial(fl[0], self)
            fl[0].__name__ = _

    def bind_callback(self, factory):
        if not self.pages:
            raise NoPageListFound('you should modify you class attr \'page_list\' to enable the factory')
        for page in self.pages:
            f_bound = self.callbacks.setdefault(self.module_name, {})
            f_bound[page] = partial(getattr(factory, page, None), self.factory_i)

    def dispatch_run(self, func, timeout):
        if timeout:
            result = self.gen_threading(func, timeout=timeout)
            result = result if result is not None else False
        else:
            result = func()
        return result

    def check_page(self, page, retry_times=None, use_callback=None, fail_to_check=None, timeout=None, binding=None):
        """当将callback传递为None时不会调用callback, 否则一定会在result为真的时候调用它对应的callback"""
        try:
            func, *others = check_methods.get(self.module_name).get('check_' + page) or check_methods['base'].get('check_' + page)
        except TypeError as e:
            raise InvalidCheckMethod('{}页面的check函数无法找到, 错误原因:{}'.format(page, str(e)))
        if not func:
            raise InvalidCheckMethod('{}页面的check函数无法找到, 错误原因未知'.format(page))
        packed = zip([retry_times, use_callback, fail_to_check, timeout, binding], others[:5])
        retry_times, use_callback, fail_to_check, timeout, binding = map(lambda x: x[0] if x[0] is not None else x[1], packed)
        result = self.dispatch_run(func, timeout)
        while not result and retry_times:
            logger.info('check_' + page + '的检测失败, 重新检测, 剩余重试次数为' + str(retry_times))
            time.sleep(0.3)
            result = self.dispatch_run(func, timeout)
            retry_times -= 1
        if result and use_callback:
            callback = self.callbacks.get(self.module_name, {}).get(page)
            _ = callback() if callback else ''
            logger.info('回调执行成功, 返回值为' + str(_))
        if not result and fail_to_check == 'all':
            for p in self.pages:
                self.check_page(p, 0, True, list(), None, list())
        elif callable(fail_to_check):
            fail_to_check()
        elif not result and isinstance(fail_to_check, str):
            self.check_page(fail_to_check, 0, False, list(), None, list()) if fail_to_check[0] == '-' else \
                self.check_page(fail_to_check, 0, True, list(), None, list())
        elif not result and isinstance(fail_to_check, Sequence):
            for f_checker in fail_to_check:
                if callable(f_checker):
                    r = f_checker()
                else:
                    r = self.check_page(f_checker, 0, False, list(), -1, list()) if fail_to_check[0] == '-' else \
                        self.check_page(fail_to_check, 0, True, list(), -1, list())
                if r:
                    break
        return result

    def gen_threading(self, func, args=(), kwargs=None, name=None, timeout=None, ):
        name = func.__name__ if not name else name
        if self.alive and self.factory_i.over:
            thread = TimeoutThreading(target=func, args=args, kwargs=kwargs, name=name)
            thread.setDaemon(True)
            thread.start()
            thread.join(timeout)
            result = thread.get_result()
            thread.raise_error(TimeoutError)
            logger.error('执行{}的时候时间超时'.format(name))
            return result

    def start(self):
        self.load_all_factories() if not self.factories else None
        while self.alive:
            for factory in self.factories:
                self.pages = factory.page_list[::]
                self.module_name = factory.__module__.split('.')[-1]
                self.factory_i = factory(self)
                if factory.use_check_method:
                    for checker in check_methods[self.module_name].values():
                        _ = checker[0].__name__
                        checker[0] = partial(checker[0], self.factory_i)
                        checker[0].__name__ = _
                if factory.use_callback:
                    self.bind_callback(factory)
                with self.factory_i as f:
                    f.run()
            self.alive = False

    def load_all_factories(self):
        f_p = os.path.join(os.path.dirname(__file__), 'supporters')
        f_n = [n[:-3] for n in os.listdir(f_p) if n.endswith('.py') and n != '__init__.py']
        for f in f_n:
            maps = vars(import_module('supporters.' + f))
            base = maps['BaseFactory']
            for v in maps.values():
                if isinstance(v, type) and v.__bases__[0] == base:
                    self.factories.append(v)


if __name__ == '__main__':
    impact3 = Impact3()
    impact3.start()
    # a.compare_color(1210, 676, 'fd8a82')
    print()