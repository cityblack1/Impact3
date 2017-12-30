import threading
import time
import re
import typing
from base import DMWrapper
from supporters.dogfeed import SupportDogFeedTeamwork
from utils import check_methods, specific_check, wrap_callbacks, false_to_retry, wrap_run, index_super
from functools import partial
from exceptions import InvalidCheckMethod, NoPageListFound
from logger import logger
from collections.abc import Sequence, Iterable


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
        self.child_tasks = []
        self.module_name = ''
        self.temp_result = ''
        for fl in check_methods['base'].values():
            fl[0] = partial(fl[0], self)

    def bind_callback(self, factory):
        if not self.pages:
            raise NoPageListFound('you should modify you class attr \'page_list\' to enable the factory')
        for page in self.pages:
            f_bound = self.callbacks.setdefault(self.module_name, {})
            f_bound[page] = partial(getattr(factory, page, None), self.factory_i)

    def check_page(self, page, retry_times=None, use_callback=None, fail_to_check=None, timeout=None, binding=None):
        """当将callback传递为None时不会调用callback, 否则一定会在result为真的时候调用它对应的callback"""
        func, *others = check_methods.get(self.module_name).get('check_' + page) or check_methods['base'].get('check_' + page)
        packed = zip([retry_times, use_callback, fail_to_check, timeout, binding], others)
        retry_times, use_callback, fail_to_check, timeout, binding = map(lambda x: x[0] if x[0] is not None else x[1], packed)
        result = func()
        while not result and retry_times:
            logger.info('check_' + page + '的检测失败, 重新检测, 剩余重试次数为' + str(retry_times))
            time.sleep(0.3)
            result = func()
            retry_times -= 1
        if result and use_callback:
            callback = self.callbacks.get(self.module_name, {}).get(page)
            _ = callback() if callback else ''
            logger.info('回调执行成功, 返回值为' + str(_))
        if not result and isinstance(fail_to_check, str):
            self.check_page(fail_to_check, 0, False, list(), -1, list()) if fail_to_check[0] == '-' else \
                self.check_page(fail_to_check, 0, True, list(), -1, list())
        elif not result:
            for f_checker in fail_to_check:
                self.check_page(f_checker, 0, False, list(), -1, list()) if fail_to_check[0] == '-' else\
                    self.check_page(fail_to_check, 0, True, list(), -1, list())
        return result
        raise InvalidCheckMethod('the check method of Page %s  can\'t be found' % page)

    def gen_threading(self, func, *args, name=None, **kwargs):
        if self.alive:
            thread = threading.Thread(target=func, args=args, kwargs=kwargs, name=name)
            thread.setDaemon(True)
            thread.start()
            self.child_tasks.append(thread)

    def start(self):
        while self.alive:
            for factory in self.factories:
                self.pages = factory.page_list[::]
                self.module_name = factory.__module__.split('.')[-1]
                self.factory_i = factory(self)
                if factory.use_check_method:
                    for checker in check_methods[self.module_name].values():
                        checker[0] = partial(checker[0], self.factory_i)
                if factory.use_callback:
                    self.bind_callback(factory)
                with self.factory_i as f:
                    f.run()
            self.alive = False


if __name__ == '__main__':
    impact3 = Impact3([SupportDogFeedTeamwork])
    impact3.start()
    # a.compare_color(1210, 676, 'fd8a82')
    print()