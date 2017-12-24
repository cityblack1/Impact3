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
    page_list = ['home', 'download_music?', 'home?', 'world_map', 'teamwork', 'dog_feed', 'advanced_equipment']
    use_callback = True
    use_check_method = True

    def __init__(self):
        super().__init__()

    def run(self, instance=None, *args, **kwargs):
        while self.page_list:
            page = self.page_list.pop(0)
            instance.check_page(page)

    def home(self):
        logger.info('当前是home页面, 点击出击按钮')
        self.impact3.click(1093,164)

    def download_music(self):
        logger.info('当前是download_music页面, 点击取消按钮')
        self.impact3.click(491, 515)

    def world_map(self):
        logger.info('尝试点击回到世界地图')
        self.impact3.click(1196,685)

    def teamwork(self):
        logger.info('尝试切换到团队模式')
        self.impact3.click(766, 110)


@page_checker_register
def check_download_music(impact3):
    return impact3.compare_color(734, 202, 0.95, '00c0fc') and impact3.compare_color(747, 496, 0.95, 'ffe14b')


@page_checker_register
def check_world_map(impact3):
    return impact3.compare_color(78, 21, 0.95, 'ffdf4d') and impact3.compare_color(1196, 685, 0.95, 'ffdd51')


@page_checker_register
def check_teamwork(impact3):
    return impact3.compare_color(598, 115, 'ffffff') or impact3.compare_color(697, 108, 'ffffff')
