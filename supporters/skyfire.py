import time
import random

from utils import time_checker, page_checker_register, TimeoutThreading
from base import BaseFactory
from logger import logger


class SkyFireTeamWork(BaseFactory):
    page_list = ['home', 'download_a', 'map_choose', 'lv_choose', 'join', 'car_choose', 'bottle']
    is_active = True

    def home(self):
        logger.info('点击"天火出鞘"按钮')
        self.impact3.click(1229,172)

    @page_checker_register(retry_times=1, fail_to_check=['self.add_pass("home")'], binding="self.add_pass('home')")
    def check_home(self):
        return self.impact3.compare_color(1210, 676, 1, 'fd8a82') and \
               self.impact3.compare_color(1226, 692, 0.8, '8ab33e') and \
               not self.impact3.compare_color(734, 202, 1, '00c0fc') and \
               not self.impact3.compare_color(747, 496, 1, 'ffe14b')

    def download_a(self):
        logger.info('当前是download_a页面, 点击取消按钮')
        self.impact3.click(370,512)

    @page_checker_register(retry_times=3, fail_to_check=['self.add_pass("download_a")', 'home'],
                           binding="self.add_pass('download_a')")
    def check_download_a(self):
        return self.impact3.compare_color(718,496, 0.95, 'ffe14b') and \
               self.impact3.compare_color(370,512, 0.95, '00c3ff')

    def map_choose(self):
        logger.info('当前是map_choose页面, 点击中间的地图')
        self.impact3.click(642,356)

    @page_checker_register(retry_times=3, fail_to_check=['self.add_pass("download_a")', 'home'], binding="self.add_pass('map_choose')")
    def check_map_choose(self):
        return self.impact3.compare_color(391,237, 0.95, 'ff723b') and \
               self.impact3.compare_color(637,241, 0.95, '58bb47') and \
               self.impact3.compare_color(858,236, 0.95, '58bb47') and \
               self.impact3.compare_color(122,105, 0.95, 'ffffff')

    def lv_choose(self):
        logger.info('当前是lv_choose页面, 点击左边的难度')
        self.impact3.click(620, 367)

    @page_checker_register(retry_times=3, fail_to_check='map_choose')
    def check_lv_choose(self):
        return self.impact3.compare_color(785,681, 0.95, 'ff980a') and \
               self.impact3.compare_color(3,362, 0.95, '00ffff') and \
               self.impact3.compare_color(477,385, 0.95, '6adbff')

    @time_checker(timeout=90, retry=1)
    def join(self):
        logger.info('当前是lv_choose页面, 点击左边的难度')
        while not (self.impact3.compare_color(447,13, 0.98, '423652') and
                       self.impact3.compare_color(1000,7, 0.98, '34284c')):
            if self.impact3.compare_color(673,514, 0.98, 'ffe14b'):
                time.sleep(1)
                self.impact3.click(507,508)
                break
            time.sleep(2)
            if not self.impact3.compare_color(921,673, 0.98, '6a491b'):
                time.sleep(2)
                self.impact3.click(1105, 673)
            time.sleep(1)
        logger.info('进入人物选择界面')
        return True

    @page_checker_register(retry_times=3, fail_to_check='lv_choose')
    def check_join(self):
        return self.impact3.compare_color(684,497, 0.95, 'bb5bde') and \
               self.impact3.compare_color(582,466, 0.95, 'ff980b') and \
               self.impact3.compare_color(1017,674, 0.95, 'ffe14b') and \
               self.impact3.compare_color(402,353, 0.95, 'e5d3c9')

    @time_checker(timeout=120, callback_f='self.impact3.check_page("join")')
    def car_choose(self):
        while not self.impact3.compare_color(1060,587, 0.98, '6a491b'):
            if self.impact3.compare_color(694, 656, 0.95, 'ffde4a') or\
                    self.impact3.compare_color(769, 675, 0.95, 'ffe14b') or\
                    self.impact3.compare_color(635, 640, 0.95, '9fd03b'):
                time.sleep(1)
                if self.impact3.compare_color(617,658, 0.96, 'ffffff'):
                    break
                self.impact3.click(646, 645)
            time.sleep(1)
        logger.info('开始进入战斗读条')
        return True

    @page_checker_register(retry_times=4, fail_to_check='join')
    def check_car_choose(self):
        time.sleep(2)
        return True

    @time_checker(timeout=240)
    def bottle(self):
        logger.info('battle start~!')
        # self.impact3.press_key('w')
        # time.sleep(0.1)
        # self.impact3.press_key('w')
        # time.sleep(0.1)
        # self.impact3.press_key('w')
        i = 0
        time.sleep(10)
        thread = TimeoutThreading(target=self.while_bottle_press_2)
        thread.setDaemon(True)
        start = False
        while not (self.impact3.compare_color(562,668, 0.9, 'ffde4a') and
                       self.impact3.compare_color(627,671, 0.9, '323232') and
                       self.impact3.compare_color(42,39, 0.9, 'cececf')):
            if not i % 5:
                key = random.choice('wad')
                self.impact3.dm.KeyDownChar(key)
                time.sleep(0.08)
                if random.random() > 0.5:
                    self.impact3.press_key('k')
                self.impact3.dm.KeyUpChar(key)
                time.sleep(0.03)
            time.sleep(0.03)
            self.impact3.press_key('i')
            self.impact3.press_key_long('s', random.random() / 2)
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
        while not self.impact3.compare_color(319,380, 0.98, 'ffffff'):
            if self.impact3.compare_color(656,190, 0.98, '00c3ff') or self.impact3.compare_color(723,511, 0.98, 'ffe14b'):
                time.sleep(2)
                self.impact3.click(723,511)
                time.sleep(2)
                break
            self.impact3.click(694, 656)
            time.sleep(1)
        logger.info('本轮结束, 即将开始下一轮')

    @page_checker_register(timeout=120, retry_times=0)
    def check_bottle(self):
        while not self.impact3.compare_color(728,670, 1, '00d3ff'):
            time.sleep(1)
        logger.info('进入战斗页面')
        return True

    def while_bottle_press_2(self):
        while True:
            self.impact3.press_key('2')
            time.sleep(0.6)