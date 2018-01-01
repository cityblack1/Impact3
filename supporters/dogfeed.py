import time
import random
import threading

from utils import page_checker_register, time_checker, TimeoutThreading
from base import BaseFactory
from logger import logger


def raise_timeout_error():
    raise TimeoutError


class SupportDogFeedTeamwork(BaseFactory):
    """刷联机模式的狗粮"""
    page_list = ['home', 'download_music', 'world_map', 'teamwork', 'dog_feed', 'advanced_equipment',
                 'choose', 'battle']
    is_active = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_battle = False
        self.click_po = (637, 371)
        # self.click_po = (966,366)

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
        self.impact3.drag(822,412, 1184,419, 0.6)
        self.impact3.drag(822,412, 1184,419, 0.6)
        self.impact3.drag(822,412, 1184,419, 0.6)
        time.sleep(1)
        self.impact3.click(856,428)
        # self.impact3.click(1101,416)
        # time.sleep(2)
        # self.impact3.click(947,416)

    @time_checker(timeout=60, callback_f=raise_timeout_error)
    def advanced_equipment(self):
        pre = time.time()
        logger.info('进入协助作战页面')
        time.sleep(0.2)
        #self.impact3.click(966,366)
        self.impact3.click(*self.click_po)
        # self.impact3.click(1101,416)
        # time.sleep(2)
        # self.impact3.click(947,416)
        time.sleep(1)
        if self.impact3.compare_color(960,376, 0.99, '798ba1'):
            self.impact3.click(960,376)
            time.sleep(1)
        while self.impact3.compare_color(1226,681, 0.99, 'ffe14b') and time.time() - pre < 6:
            self.impact3.click(1226,681)
        return True

    @time_checker(timeout=180)
    def choose(self):
        logger.info('检查进入战斗界面')
        pre = time.time()
        while time.time() - pre < 60:
            time.sleep(0.5)
            while not self.impact3.compare_color(728,670, 1, '00d3ff') and time.time() - pre < 100:
                if self.impact3.compare_color(694,656, 0.98, 'ffde4a') or self.impact3.compare_color(769,675, 0.98, 'ffe14b')\
                        or self.impact3.compare_color(635,640, 0.96, '9fd03b'):
                    self.impact3.click(646, 645)
                time.sleep(1)
            if time.time() - pre <= 100:
                self.on_battle = True
                logger.info('即将开始战斗')
                break
            time.sleep(1)
        return True

    @time_checker(timeout=240)
    def battle(self):
        pre = time.time()
        logger.info('检查是否进入战斗界面的读条')
        while not self.impact3.compare_color(728,670, 1, '00d3ff') and time.time() - pre < 100:
            time.sleep(1)
        if time.time() - pre > 100:
            logger.info('进入战斗界面失败')
            return
        logger.info('battle start~!')
        self.impact3.press_key('w')
        time.sleep(0.1)
        self.impact3.press_key('w')
        time.sleep(0.1)
        self.impact3.press_key('w')
        i = 0
        thread = TimeoutThreading(target=self.while_bottle_press_2)
        thread.setDaemon(True)
        start = False
        while not (self.impact3.compare_color(589,662, 0.9, 'ffde4a') and self.impact3.compare_color(644,8, 0.9, '050f18') \
                and self.impact3.compare_color(54,37, 0.9, 'c6c7c8')):
            if not i % 7:
                key = random.choice('wad')
                self.impact3.dm.KeyDownChar(key)
                time.sleep(0.08)
                if random.random() > 0.5:
                    self.impact3.press_key('k')
                self.impact3.dm.KeyUpChar(key)
                time.sleep(0.03)
            print('alive')
            time.sleep(0.03)
            self.impact3.press_key('i')
            self.impact3.press_key_long('w', random.random()/4)
            time.sleep(0.03)
            if not start:
                print('开始执行子任务, 无限按2')
                thread.start()
                start = True
            for i in range(random.randint(1, 4)):
                self.impact3.press_key('j')
                time.sleep(0.05)
            for i in range(random.randint(1, 3)):
                self.impact3.press_key('j')
                time.sleep(0.05)
                self.impact3.press_key_long('j', 1)
                time.sleep(0.2)
                self.impact3.press_key_long('j', 1)
            i += 1
        time.sleep(1)
        print('杀死线程')
        thread.raise_error(Exception)
        logger.info('战斗结束')
        logger.info('点击点击')
        time.sleep(2)
        while not self.impact3.compare_color(1143,657, 0.98, 'ffe14b'):
            self.impact3.click(694, 656)
            time.sleep(1)
        time.sleep(1)
        while not self.impact3.compare_color(61,581, 0.98, 'ffffff'):
            self.impact3.click(1143,657)
            time.sleep(1)
        logger.info('本轮结束, 即将开始下一轮')
        self.on_battle = False

    @page_checker_register(retry_times=1, fail_to_check=['self.add_pass("download_music")'], binding="self.add_pass('home')")
    def check_home(self):
        return self.impact3.compare_color(1210, 676, 1, 'fd8a82') and self.impact3.compare_color(1226, 692, 0.8, '8ab33e') and \
               not self.impact3.compare_color(734, 202, 1, '00c0fc') and not self.impact3.compare_color(747, 496, 1, 'ffe14b')

    @page_checker_register(retry_times=3, fail_to_check=['self.add_pass("download_music")', 'home', 'world_map'], binding="self.add_pass('download_music')")
    def check_download_music(self):
        return self.impact3.compare_color(734, 202, 0.95, '00c0fc') and self.impact3.compare_color(747, 496, 0.95, 'ffe14b')

    @page_checker_register(retry_times=3, fail_to_check=['home', 'self.add_pass("world_map")'], binding="self.add_pass('world_map')")
    def check_world_map(self):
        return self.impact3.compare_color(78, 21, 0.95, 'ffdf4d') and self.impact3.compare_color(1196, 685, 0.95, 'ffdd51')

    @page_checker_register(retry_times=2, fail_to_check=['world_map', 'home'], binding="self.add_pass('teamwork')")
    def check_teamwork(self):
        return self.impact3.compare_color(598, 115, 'ffffff') or self.impact3.compare_color(697, 108, 'ffffff')

    @page_checker_register(retry_times=6, fail_to_check='teamwork', binding="self.add_pass('dog_feed')")
    def check_dog_feed(self):
        return self.impact3.compare_color(1232,105, 'ffffff') and self.impact3.compare_color(49,473, 'ffffff')

    @page_checker_register(retry_times=3)
    def check_advanced_equipment(self):
        logger.info('开始检查高级装备页面')
        result = self.impact3.compare_color(800, 100, '0f6d93') and self.impact3.compare_color(317, 383, 'ffffff')
        if not result:
            time.sleep(1)
            self.impact3.click(856, 428)
            time.sleep(1)
            result = self.impact3.compare_color(800, 100, '0f6d93') and self.impact3.compare_color(317, 383, 'ffffff')
        return result

    @page_checker_register(retry_times=0, timeout=90, fail_to_check='advanced_equipment')
    def check_choose(self):
        logger.info('开始检查是否进入选人界面')
        if self.impact3.compare_color(1020, 666, '686e73'):
            logger.info('协作次数已经到达上限')
            self.impact3.click(64, 39)
            time.sleep(3)
            self.impact3.click(64, 39)
            if self.impact3.factory_i.click_po != (966, 366):
                self.impact3.factory_i.click_po = (966, 366)
            else:
                self.over = True
            # impact3.factory_instance.over = True
            return False
        pre = time.time()
        while time.time() - pre < 60:
            if self.impact3.compare_color(694, 656, 0.8, 'ffde4a') or self.impact3.compare_color(769, 675, 0.8,
                                                                                       'ffe14b') or self.impact3.compare_color(
                    635, 640, 0.8, '9fd03b') \
                    or self.impact3.compare_color(633, 640, 0.8, 'a2d23b'):
                logger.info('检查是否进入战斗界面')
                return True
            time.sleep(1)
            self.impact3.factory_i.page_list = self.impact3.pages
        self.impact3.factory_i.on_battle = False
        return False

    @page_checker_register(retry_times=0, timeout=180)
    def check_battle(self):
        logger.info('开始检查是否进入战斗界面')
        return True if self.impact3.factory_i.on_battle else False

    def while_bottle_press_2(self):
        while True:
            self.impact3.press_key('2')
            time.sleep(0.6)


