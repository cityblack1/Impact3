import threading
import time
import re

from queue import Queue
from base import DMWrapper
from supporters.dogfeed import SupportDogFeedTeamwork
from utils import check_methods, specific_check, wrap_callbacks, false_to_retry, wrap_run, index_super
from functools import partial
from exceptions import InvalidCheckMethod, NoPageListFound
from logger import logger


class Impact3Supporter(DMWrapper):
    """MuMu 模拟器   720 宽 * 1280高"""
    def __init__(self):
        super().__init__()
        self.child_task = []
        self.page = ''
        self.pages = []
        self.main_task = None
        self.alive = True
        self.task_queue = Queue(maxsize=10)
        self.factory = None
        self.factories = [SupportDogFeedTeamwork]
        self.callbacks = {}

    def bind_callback(self, factory):
        order_page = self.pages or getattr(factory, 'page_list')
        if not order_page:
            raise NoPageListFound('you should modify you class attr \'page_list\' to enable the factory')
        for page in order_page:
            page = page.replace('?', '')
            f_bound = self.callbacks.setdefault(self.factory, {})
            f_bound[page] = getattr(factory, page, None)

    @false_to_retry(5)
    def check_page(self, page, callback=''):
        """当将callback传递为None时不会调用callback, 否则一定会在result为真的时候调用它对应的callback"""
        if index_super(self.pages, page) <= (index_super(self.pages, self.page) if self.page else -1):
            if page in self.pages[0]:
                self.page = page
            else:return None
        r_page, page = page, re.sub('\d+$|\W+$|\d+\W+$', '', page)
        func = check_methods.get(self.factory, {}).get('check_' + page) or check_methods['utils'].get('check_' + page)
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
            self.child_task.append(thread)

    def start(self):
        while self.alive:
            for f in self.factories:
                self.pages = getattr(f, 'page_list', [])[::]
                use_callback, use_check_method = getattr(f, 'use_callback', True), getattr(f, 'use_check_method', True)
                self.factory = f.__module__.split('.')[-1]
                if use_check_method:
                    for fn, func in check_methods.get(self.factory, {}).items():
                        check_methods.get(self.factory)[fn] = partial(func, self)
                    for fn, func in check_methods.get('utils', {}).items():
                        check_methods.get('utils')[fn] = partial(func, self)
                factory = f()
                setattr(factory, 'impact3', self)
                if use_callback:
                    self.bind_callback(factory)
                # 将会无限循环执行run方法, 知道崩溃3次。会重新执行start方法。
                wrap_run(factory)(factory.run)(self)


if __name__ == '__main__':
    a = Impact3Supporter()
    a.start()
    # a.compare_color(1210, 676, 'fd8a82')
    print()