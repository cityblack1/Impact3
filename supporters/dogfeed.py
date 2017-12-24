import time

from utils import page_checker_register
from base import BaseFactory
from logger import logger
"""
工厂类模块使用说明:

1. 每个工厂类模块都抽象为一个工厂, 代表了一种辅助内一种功能的内部抽象, 比如"联机刷狗粮"

2. 每个Support开头的类都是一个工厂类, 内部必须有一个静态run方法, 会在加载工厂后进行调用, 是辅助运行的主要逻辑所在
   run 方法需要包含一个 instance 参数, 代表的是 Impact3Supporter 的实例
   page_order 记录了每个页面的点击顺序

2. 其余的检查页面的函数要以 check 开头, 另外的部分则是页面的名称, 要和 page_order 里面一致

3. check函数必须被装饰器page_checker_register装饰。装饰器内部维护了一个字典，会注册每个模块下的每个check函数
   同时page_checker_register装饰器会检查check函数返回值是否为True, 当为True时候会将 Impact3Supporter 中的self.page的值变成
   check成功的页面
   
4. 所有注册后的 check 函数都会被注册到Impact3中, 只能通过 Impact3Supporter 的实例中的 check_page方法调用
   比如, 你可以在 工厂类中的run方法中使用 instance.check_page('home'),相当于自动调用check_home的方法.
"""


class SupportDogFeedTeamwork(BaseFactory):
    """刷联机模式的狗粮"""
    page_list = ['home', 'download_music?', 'home?', 'world_map', 'teamwork', 'dog_feed', 'advanced_equipment',
                 'choose']
    use_callback = True
    use_check_method = True

    def __init__(self):
        super().__init__()
        self.on_battle = False

    def run(self, instance=None, *args, **kwargs):
        while self.page_list:
            page = self.page_list.pop(0)
            instance.check_page(page)

    def home(self):
        time.sleep(0.2)
        logger.info('当前是home页面, 点击出击按钮')
        self.impact3.click(1093,164)

    def download_music(self):
        time.sleep(0.2)
        logger.info('当前是download_music页面, 点击取消按钮')
        self.impact3.click(491, 515)

    def world_map(self):
        time.sleep(0.2)
        logger.info('尝试点击回到世界地图')
        self.impact3.click(1196,685)

    def teamwork(self):
        time.sleep(0.2)
        logger.info('尝试切换到团队模式')
        self.impact3.click(766, 110)

    def dog_feed(self):
        logger.info('尝试拖动到最左边')
        time.sleep(1)
        self.impact3.press_key('e')
        time.sleep(0.5)
        self.impact3.press_key('e')
        time.sleep(0.5)
        self.impact3.press_key('e')
        time.sleep(0.5)
        self.impact3.click(856,428)

    def advanced_equipment(self):
        logger.info('')
        time.sleep(0.2)
        self.impact3.click(966,366)
        time.sleep(1)
        if self.impact3.compare_color(960,376, 0.99, '798ba1'):
            self.impact3.click(960,376)
            time.sleep(1)
        while self.impact3.compare_color(1226,681, 0.99, 'ffe14b'):
            self.impact3.click(1226,681)
            break

    def choose(self):
        logger.info('进入选人界面')
        pre = time.time()
        while time.time() - pre < 60:
            time.sleep(2)
            if self.impact3.compare_color(646,645, 0.99, 'a7d73a') \
                    or self.impact3.compare_color(769,675, 0.99, 'ffe14b'):
                self.impact3.click(646,645)
                while not self.impact3.compare_color(966, 344, 0.99, '114469') and time.time() - pre < 100:
                    time.sleep(1)
                if time.time() - pre <= 100:
                    self.impact3.on_battle = True
                    logger.info('即将开始战斗')
            time.sleep(1)

    def battle(self):
        while not self.impact3.compare_color(728,670, 1, '00d3ff'):
            time.sleep(1)
        self.impact3.press_key('w')
        time.sleep(0.1)
        self.impact3.press_key('w')
        time.sleep(0.1)
        self.impact3.press_key('w')
        while not self.impact3.compare_color(699,662, 0.99, 'ffde4a'):
            self.impact3.press_key('2')
            time.sleep(0.1)
            self.impact3.press_key('j')
            time.sleep(0.1)
        self.impact3.click(699,662)


@page_checker_register
def check_download_music(impact3):
    return impact3.compare_color(734, 202, 0.95, '00c0fc') and impact3.compare_color(747, 496, 0.95, 'ffe14b')


@page_checker_register
def check_world_map(impact3):
    return impact3.compare_color(78, 21, 0.95, 'ffdf4d') and impact3.compare_color(1196, 685, 0.95, 'ffdd51')


@page_checker_register
def check_teamwork(impact3):
    return impact3.compare_color(598, 115, 'ffffff') or impact3.compare_color(697, 108, 'ffffff')


@page_checker_register
def check_dog_feed(impact3):
    return impact3.compare_color(1232,105, 'ffffff') and impact3.compare_color(49,473, 'ffffff')


@page_checker_register
def check_advanced_equipment(impact3):
    return impact3.compare_color(800,100, '0f6d93') and impact3.compare_color(317,383, 'ffffff')


@page_checker_register
def check_choose(impact3):
    pre = time.time()
    while time.time() - pre < 60:
        if impact3.compare_color(769,675, 'ffe14b') or  impact3.compare_color(628,490, 'a7e52e') or impact3.compare_color(767,660, '545047'):
            return True
        time.sleep(1)
    return False


@page_checker_register
def check_battle(impact3):
    return impact3.compare_color(324,368, '10d8ff') and impact3.compare_color(93,205, '06314b')


@page_checker_register
def check_battle(impact3):
    return True if impact3.on_battle else False