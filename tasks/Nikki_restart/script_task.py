# This Python file uses the following encoding: utf-8
# @author runhey
# github https://github.com/runhey
from datetime import datetime

from tasks.Nikki_restart.assets import Nikki_restartAssets
from tasks.base_task import BaseTask, Time
from datetime import datetime, time

from module.logger import logger
from module.exception import TaskEnd, RequestHumanTakeover, GameTooManyClickError, GameStuckError
from module.base.timer import Timer


class ScriptTask(BaseTask, Nikki_restartAssets):

    def run(self) -> None:
        """
        主要就是登录的模块
        :return:
        """
        if not self.delay_pending_tasks():
            self.app_restart()
        raise TaskEnd('ScriptTask end')

    def _app_handle_login(self) -> bool:
        """
        最终是在主界面
        :return:
        """
        logger.hr('App login')
        self.device.stuck_record_add('LOGIN_CHECK')

        confirm_timer = Timer(1.5, count=2).start()
        orientation_timer = Timer(10)
        login_success = False

        while 1:
            # Watch device rotation
            if not login_success and orientation_timer.reached():
                # Screen may rotate after starting an app
                self.device.get_orientation()
                orientation_timer.reset()

            self.screenshot()

            # 确认进入主界面
            if self.appear(self.I_MAIN_PAGE_POST, interval=5):
                if confirm_timer.reached():
                    logger.info('Login to main confirm')
                    logger.info('Login success')
                    login_success = True
                    break

            # 更新资源按钮
            if self.appear_then_click(self.I_UPDATE_VERIFY, interval=5):
                logger.info('Download Update Package')
                self.device.stuck_record_clear()
                self.device.stuck_record_add('LOGIN_CHECK')
                continue

            # 开始界面公告关闭
            if self.appear_then_click(self.I_START_PAGE_POST, interval=1):
                logger.info('Close startPage Post')
                continue

            # 主界面公告关闭
            if self.appear(self.I_MAIN_PAGE_POWER, interval=5) and self.ocr_appear(self.O_POST_TIPS, interval=5):
                if self.appear_then_click(self.I_POST_UNCHECK, interval=1):
                    logger.info('check the post tips')
                while self.appear(self.I_POST_CHECK, interval=0.5):
                    self.click(self.C_CLOSE_POST_BTN, 0.5)
                    logger.info('close one post')
                    self.screenshot()
                continue

            # 点击’进入游戏‘
            if not self.appear(self.I_AGE_REMIND, interval=1):
                continue
            if self.ocr_appear_click(self.O_LOGIN_ENTER_GAME, interval=10):
                continue

        # 判断有没有红包领
        wait_timer = Timer(2)
        while 1:
            if wait_timer.reached():
                if self.appear(self.I_RED_ENVELOPE, interval=1):
                    self.ui_click_until_disappear(self.I_RED_ENVELOPE, interval=2)
                    self.ui_click(self.C_CLOSE_POST_BTN, self.I_MAIN_PAGE_POST, interval=1)
                    wait_timer.reset()
                else:
                    break
        return login_success

    def app_handle_login(self) -> bool:
        for _ in range(2):
            self.device.stuck_record_clear()
            self.device.click_record_clear()
            try:
                self._app_handle_login()
                return True
            except (GameTooManyClickError, GameStuckError) as e:
                logger.warning(e)
                self.device.app_stop()
                self.device.app_start()
                continue

        logger.critical('Login failed more than 3')
        logger.critical('shineNikkie server may be under maintenance, or you may lost network connection')
        raise RequestHumanTakeover

    def app_restart(self):
        logger.hr('App restart')
        self.device.app_stop()
        self.device.app_start()
        self.app_handle_login()

        # self.config.task_delay(server_update=True)
        self.set_next_run(task='Restart', success=True, finish=True, server=True)

    def delay_pending_tasks(self) -> bool:
        """
        判断游戏是否在更新
        @return:
        """
        return False


if __name__ == '__main__':
    from module.config.config import Config
    from module.device.device import Device

    config = Config('oas1')
    device = Device(config)
    task = ScriptTask(config, device)
    task.config.update_scheduler()
    task.delay_pending_tasks()
    # task.screenshot()
    # print(task.appear_then_click(task.I_LOGIN_SCROOLL_CLOSE, threshold=0.9))

    t = ScriptTask(config, device)
    t.screenshot()

    t.run()








