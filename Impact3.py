import threading
import time
import re

from base import DMWrapper
from supporters.dogfeed import SupportDogFeedTeamwork
from utils import check_methods, specific_check, wrap_callbacks, false_to_retry, wrap_run, index_super
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
        self.check_methods = {}
        self.child_tasks = []
        self.module_name = ''
        self.temp_result = ''

    def bind_callback(self, factory):
        if not self.pages:
            raise NoPageListFound('you should modify you class attr \'page_list\' to enable the factory')
        for page in self.pages:
            f_bound = self.callbacks.setdefault(self.module_name, {})
            f_bound[page] = getattr(factory, page, None)

    def check_page(self, page, **kwargs):
        """当将callback传递为None时不会调用callback, 否则一定会在result为真的时候调用它对应的callback"""
        func, *others = \
            check_methods.get(self.module_name).get('check_' + page) or check_methods['base'].get('check_' + page)
        others = zip(others, ('retry_times', 'use_callback', 'fail_to_check', 'timeout', 'binding'))
        retry_times, use_callback, fail_to_check, timeout, binding = [kwargs.get(n, v) for v, n in others]

        result = func()
        while not result and retry_times:
            result = func()

        if result and use_callback:
            callback = self.callbacks.get(self.module_name, {}).get('page')
            self.temp_result = callback() if callback else ''

        if r_page.endswith('?'):
            func = specific_check(self, r_page, func)
        if func:
            result, callback = func(), wrap_callbacks(r_page, self.callbacks.get(self.factory, {}).get(page.replace('?', ''), callback) if callback is not None else None)
            if result and r_page.endswith('?') and r_page in self.pages:
                callback()
                if index_super(self.pages, r_page) < index_super(self.pages, self.page):
                    return None
                return result
            time.sleep(0.1)
            callback() if callback and result else None
            self.page = r_page if result else self.page or page
            logger.info('the result of check_{} is {}'.format(page, str(result)))
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
                if factory.use_check_method:
                    self.module_name = factory.__module__.split('.')[-1]
                    for checker in check_methods[self.module_name].values():
                        checker[0] = partial(checker[0], self)
                if factory.use_callback:
                    self.bind_callback(factory)
                self.factory_i = factory(self)
                with self.factory_i as f:
                    f.run()
            self.alive = False


if __name__ == '__main__':
    a = Impact3([SupportDogFeedTeamwork])
    a.start()
    # a.compare_color(1210, 676, 'fd8a82')
    print()