# This Python file uses the following encoding: utf-8
# @author runhey
# github https://github.com/runhey
import random
import re
from module.base.timer import Timer
from module.logger import logger
from module.exception import TaskEnd

from tasks.GameUi.game_ui import GameUi
from tasks.GameUi.page import page_main
from tasks.Nikki_daily.assets import Nikki_dailyAssets
from module.exception import TaskEnd, RequestHumanTakeover, GameTooManyClickError, GameStuckError
from tasks.Nikki_restart.assets import Nikki_restartAssets


class ScriptTask(GameUi, Nikki_dailyAssets):
    def handle_daily_task(self) -> bool:
        logger.hr('start daily_task')
        daily_task_method = [
            self.heart_gate,
            self.back_home,
            self.friend_power,
            self.union_task,
            self.shop_task,
            self.welfare_task,
            self.companion_task,
            self.corridor_task,
            self.memory_ocean,
            self.diamond_arena,
            self.receive_mail,
            self.nail_art,
            self.expend_power,
            self.daily_reward,
            self.collocation_arena,
        ]
        task_fail = False
        for task in daily_task_method:
            if not task():
                task_fail = True
                logger.info('daily_task fail')
                break
        return not task_fail

    def run(self):
        try:
            self.ui_get_current_page()
            self.handle_daily_task()
        except (GameTooManyClickError, GameStuckError) as e:
            logger.warning(e)
            logger.critical('handle daily tasks failed')
            raise RequestHumanTakeover

        self.set_next_run(task='Pets', success=True, finish=True)
        raise TaskEnd('Pets')

    # 1. 心之门抽卡
    def heart_gate(self) -> bool:
        logger.hr('start hear_gate')
        handle_success = False
        count = 0
        # 进入心之门
        while 1:
            self.screenshot()
            if self.appear_then_click(self.I_HEART_GATE_ENTRANCE_1, interval=1):
                continue
            if self.appear_then_click(self.I_HEART_GATE_ENTRANCE_2, interval=1):
                continue
            if self.appear_then_click(self.I_HEART_GATE_ENTRANCE_3, interval=1):
                continue
            if self.appear_then_click(self.I_HEART_GATE_ENTRANCE_4, interval=1):
                continue
            if self.ocr_appear(self.O_HEART_GATE_DETAIL, interval=1):
                self.click(self.C_HEART_GATE_INVALID_AREA)
                break
        logger.info('Enter hear_gate_entrance')

        # 先到绮海抽，如果有免费抽
        while 1:
            self.screenshot()
            # 匹配到“绮之券”文本，则为绮之海阁
            if self.ocr_appear(self.O_HEART_GATE_QI, interval=0.5):
                logger.info('Enter hear_gate_qi')
                # 判断有没有免费抽，没有则直接跳出
                if self.ocr_appear(self.O_HEART_GATE_MAGICAL_FREE, interval=0.2):
                    # 点击感应
                    self.ui_click_until_disappear(self.I_HEART_GATE_MAGICAL_INDUCE)
                    count += 1
                    logger.info('qi induce free one')
                    # 出现分享按钮则代表抽完，点击无效区域退出界面
                    self.wait_until_appear(self.I_SHARE_BUTTON, True, 10)
                    self.ui_click_until_smt_disappear(self.C_HEART_GATE_INVALID_AREA, self.I_SHARE_BUTTON)
                break
            # 非绮之海阁则点击切换
            else:
                self.click(self.C_HEART_GATE_SWITCH, 3)

        # 先到幻之海抽，如果有免费抽
        while 1:
            self.screenshot()
            # 匹配到“幻之海”文本并且没有匹配到“下期预告”文本，则为幻之海阁
            if self.ocr_appear(self.O_HEART_GATE_MAGICAL, interval=0.5) and not self.ocr_appear(self.O_HEART_GATE_NEXT, interval=0.5):
                logger.info('Enter hear_gate_magical')
                # 判断有没有免费抽，没有则直接跳出
                if self.ocr_appear(self.O_HEART_GATE_MAGICAL_FREE, interval=0.2):
                    # 点击感应
                    self.ui_click_until_disappear(self.I_HEART_GATE_MAGICAL_INDUCE)
                    count += 1
                    logger.info('magical induce free one')
                    # 出现分享按钮则代表抽完，点击无效区域退出界面
                    self.wait_until_appear(self.I_SHARE_BUTTON, True, 10)
                    self.ui_click_until_smt_disappear(self.C_HEART_GATE_INVALID_AREA, self.I_SHARE_BUTTON)
                break
            # 非幻之海阁则点击切换
            else:
                self.click(self.C_HEART_GATE_SWITCH, 3)


        # 到谜之海抽
        while count < 3:
            self.screenshot()
            if self.ocr_appear(self.O_HEART_GATE_PUZZLE, interval=0.5):
                logger.info('Enter hear_gate_puzzle')
                # 点击感应
                self.ui_click_until_disappear(self.I_HEART_GATE_PUZZLE_INDUCE)
                count += 1
                logger.info('puzzle induce one')
                # 出现分享按钮则代表抽完，点击无效区域退出界面
                self.wait_until_appear(self.I_SHARE_BUTTON, True, 10)
                self.ui_click_until_smt_disappear(self.C_HEART_GATE_INVALID_AREA, self.I_SHARE_BUTTON)
            # 非谜之海阁则点击切换
            else:
                self.click(self.C_HEART_GATE_SWITCH, 3)

        if count == 3 and self.back_main_page():
            logger.hr('end hear_gate')
            handle_success = True
        return handle_success

    # 2. 美甲（包括每隔两天领取，以及每周兑换，每日雇佣等）
    def nail_art(self) -> bool:
        logger.hr('start nail_art')
        handle_success = False
        # 进入美甲
        while 1:
            self.screenshot()
            if self.ocr_appear(self.O_DESIGN_CENTER_ENTRANCE_TEXT, interval=2):
                self.click(self.C_DESIGN_CENTER_ENTRANCE, 0.5)
                continue
            if self.ocr_appear(self.O_NAIL_ART_ENTRANCE_TEXT, interval=2):
                self.click(self.C_NAIL_ART_ENTRANCE, 0.5)
                continue
            if self.ocr_appear(self.O_NAIL_ART_PAGE, interval=1):
                break
        logger.info('Enter nail_art_entrance')

        self.screenshot()
        # 判断”前往采购“是否有东西可以领取
        if self.ocr_appear(self.O_NAIL_ART_PAGE) and self.appear(self.I_NAIL_ART_PURCHASE_TIP, interval=0.5):
            self.ui_click(self.C_NAIL_ART_PURCHASE_ENTRANCE, self.I_NAIL_ART_PURCHASE_PAGE)
            self.ui_click(self.C_NAIL_ART_PURCHASE_DESIGN_ZONE, self.I_NAIL_ART_PURCHASE_DESIGN_ZONE_PAGE)
            logger.info('Enter nail_art_purchase_design_zone')
            self.click(self.C_NAIL_ART_PURCHASE_DESIGN_ZONE_FREE)
            logger.info('get free one')
            self.wait_until_appear(self.I_NAIL_ART_PURCHASE_DESIGN_ZONE_GET_TICKET, True, 30)
            self.ui_click_until_smt_disappear(self.C_HEART_GATE_INVALID_AREA, self.I_NAIL_ART_PURCHASE_DESIGN_ZONE_GET_TICKET, interval=2)
            # 判断是否有星券可以兑换（每周一次）
            if self.appear(self.I_NAIL_ART_PURCHASE_DESIGN_ZONE_WEEK_TICKET, interval=1):
                self.ui_click(self.I_NAIL_ART_PURCHASE_DESIGN_ZONE_WEEK_BUTTON, self.I_NAIL_ART_PURCHASE_DESIGN_ZONE_WEEK_EXCHANGE, interval=2)
                # 设置为最大兑换数量
                cu, res, total = self.O_NAIL_ART_EXCHANGE_COUNT.ocr(self.device.image)
                while 1:
                    self.screenshot()
                    if cu == self.O_NAIL_ART_EXCHANGE_NUM.ocr(self.device.image):
                        break
                    self.click(self.C_NAIL_ART_PURCHASE_DESIGN_ZONE_ADD_BUTTON, interval=1)
                # 点击兑换
                self.ui_click(self.I_NAIL_ART_PURCHASE_DESIGN_ZONE_WEEK_EXCHANGE, self.I_NAIL_ART_PURCHASE_DESIGN_ZONE_GET_TICKET)
                logger.info('get week ticket')
            # 点击返回按钮直至到美甲页
            while 1:
                self.screenshot()
                if self.appear_then_click(self.I_EXIT_BUTTON, interval=2):
                    continue
                if self.ocr_appear(self.O_NAIL_ART_PAGE, interval=1):
                    logger.info('exit nail_art_purchase_design_zone')
                    break

        # ”我的店铺“
        if self.ocr_appear(self.O_NAIL_ART_PAGE) and self.appear_then_click(self.I_NAIL_ART_SHOP_ENTRANCE, interval=0.5):
            logger.info('Enter nail_art_shop')
            # 点击无效区域直到出现“雇佣店员”按钮
            self.ui_click(self.C_NAIL_ART_SHOP_INVALID_AREA, self.I_NAIL_ART_SHOP_EMPLOYMENT_BUTTON)
            # 雇佣店员
            while 1:
                self.screenshot()
                if self.appear_then_click(self.I_NAIL_ART_SHOP_EMPLOYMENT_BUTTON, interval=0.5):
                    continue
                if self.appear_then_click(self.I_NAIL_ART_SHOP_EMPLOYMENT_PERSON, interval=0.5):
                    break
            # 点击无效区域直到弹窗都关闭
            self.ui_click(self.C_NAIL_ART_SHOP_INVALID_AREA, self.I_NAIL_ART_SHOP_SPECIAL)
            logger.info('deal employment success')

            # 周好评礼包领取
            self.ui_click(self.I_NAIL_ART_SHOP_PACKAGE, self.I_NAIL_ART_SHOP_PACKAGE_BOARD)
            click_button = [getattr(self, f"O_NAIL_ART_SHOP_PACKAGE_RECEIVE_{i+1}") for i in range(4)]
            index = 0
            while index < len(click_button):
                self.screenshot()
                text = click_button[index].ocr(self.device.image)
                if "已领取" in text:
                    index += 1
                elif "领取" in text:
                    self.click(click_button[index], interval=0.5)
                    break
                else:
                    index += 1
            logger.info('get rewards success')
            # 提取心意币
            self.ui_click_until_disappear(self.I_NAIL_ART_SHOP_EXTRACT_BUTTON, interval=2)
            logger.info('extract currency success')

        if self.back_main_page():
            logger.hr('end nail_art')
            handle_success = True
        return handle_success

    # 3. 回家（日程，送礼物，手账点击）
    def back_home(self) -> bool:
        logger.hr('start back_home')
        handle_success = False
        # 进入回家
        while 1:
            self.screenshot()
            if self.ocr_appear(self.O_BACK_HOME_ENTRANCE_TEXT, interval=1):
                self.click(self.C_BACK_HOME_ENTRANCE, 0.5)
                continue
            if self.appear_then_click(self.I_BACK_HOME_CANCEL_TIP, interval=1):
                continue
            if self.appear(self.I_BACK_HOME_PAGE, interval=5):
                break
        logger.info('Enter back_home_entrance')

        # 暖暖手账点击
        while 1:
            self.screenshot()
            if self.appear_then_click(self.I_BACK_HOME_NOTEBOOK, interval=1):
                continue
            if self.appear_then_click(self.I_BACK_HOME_NOTEBOOK_OPEN, interval=1):
                break
        self.ui_click(self.C_BACK_HOME_NOTEBOOK_INVALID_AREA, self.I_BACK_HOME_PAGE, interval=2)
        logger.info('Finish open and close notebook')

        # 进入日常采购
        while 1:
            self.screenshot()
            if self.appear_then_click(self.I_BACK_HOME_PURCHASE, interval=1):
                continue
            if self.appear(self.I_BACK_HOME_PURCHASE_BUY, interval=1):
                break
        # 购买小物
        thing_dict = {
            1930: self.C_BACK_HOME_PURCHASE_MOVIE,
            2050: self.C_BACK_HOME_PURCHASE_DRAW,
            2000: self.C_BACK_HOME_PURCHASE_UMBRELLA
        }
        for price, click_area in thing_dict.items():
            exit_loop = False
            while 1:
                self.screenshot()
                if self.appear_then_click(self.I_BACK_HOME_CANCEL_TIP, interval=1):
                    continue
                text = self.O_TIP_TEXT.ocr(self.device.image)
                if "每天只能赠送2次哦" in text or "置物架已满" in text:
                    exit_loop = True
                if exit_loop and text == "":
                    break
                if exit_loop:
                    continue
                if price == int(self.O_BACK_HOME_PURCHASE_PRICE.ocr(self.device.image)):
                    self.appear_then_click(self.I_BACK_HOME_PURCHASE_BUY, interval=1)
                else:
                    self.click(click_area, interval=1)
        logger.info('Finish buy things')
        # 切换到零食购买零食
        self.ui_click(self.C_BACK_HOME_PURCHASE_TAB_SNACK, self.I_BACK_HOME_PURCHASE_SNACK_CHECKED)
        while 1:
            self.screenshot()
            if 3500 == int(self.O_BACK_HOME_PURCHASE_PRICE.ocr(self.device.image)):
                self.appear_then_click(self.I_BACK_HOME_PURCHASE_BUY, interval=1)
            else:
                self.click(self.C_BACK_HOME_PURCHASE_SNACK_CHIPS, interval=1)
            text = self.O_TIP_TEXT.ocr(self.device.image)
            if "每天只能赠送3次哦" in text or "置物架已满" in text or "已达到最大限购次数" in text:
                break
        logger.info('Finish buy snack')

        if self.back_main_page():
            logger.hr('end back_home')
            handle_success = True
        return handle_success

    # 4. 好友（送体力领体力）
    def friend_power(self) -> bool:
        logger.hr('start friend_power')
        handle_success = False
        # 进入好友
        temp = False
        while 1:
            self.screenshot()
            if self.appear_then_click(self.I_FRIEND_POWER_ENTRANCE, interval=1):
                logger.info('Enter friend_power_entrance')
                continue
            if self.appear_then_click(self.I_FRIEND_POWER_SEND_BUTTON, interval=5):
                temp = True
                continue
            if temp:
                text = self.O_TIP_TEXT.ocr(self.device.image)
                if "成功送出" in text or "没有可赠送的好友" in text:
                    logger.info('send power success')
                    break
        # 领取体力
        while 1:
            self.screenshot()
            if self.appear(self.I_FRIEND_POWER_RECEIVE_POP, interval=1):
                self.ui_click_until_disappear(self.I_FRIEND_POWER_ONE_CLICK_RECEIVE)
                logger.info('receive power success')
                break
            if self.appear_then_click(self.I_FRIEND_POWER_RECEIVE_BUTTON, interval=5):
                continue
        if self.back_main_page():
            logger.hr('end friend_power')
            handle_success = True
        return handle_success

    # 5. 联盟（每日领取，贡献，刷；以及每周兑换）
    def union_task(self) -> bool:
        logger.hr('start union_task')
        handle_success = False
        # 进入联盟
        while 1:
            self.screenshot()
            if self.appear_then_click(self.I_UNION_TASK_ENTRANCE, interval=5):
                continue
            if self.appear(self.I_UNION_TASK_MISSION, interval=1):
                break
        logger.info('Enter union_task_entrance')
        # 1联盟福利
        while 1:
            self.screenshot()
            if self.appear(self.I_UNION_TASK_WELFARE_POP, interval=1):
                self.ui_click_until_disappear(self.I_UNION_TASK_WELFARE_RECEIVE)
                logger.info('receive welfare success')
                self.ui_click(self.I_EXIT_BUTTON, self.I_UNION_TASK_MISSION, interval=3)
                break
            if self.appear_then_click(self.I_UNION_TASK_WELFARE, interval=5):
                continue
        # 2联盟捐献
        while 1:
            self.screenshot()
            if self.appear(self.I_UNION_TASK_DONATE_POP, interval=1):
                self.ui_click_until_disappear(self.I_UNION_TASK_DONATE_FREE, interval=1)
                while 1:
                    self.screenshot()
                    text = self.O_TIP_TEXT.ocr(self.device.image)
                    if "其他" in text:
                        break
                    if self.appear_then_click(self.I_UNION_TASK_DONATE_GOLD, interval=1):
                        continue
                logger.info('donate free success')
                self.ui_click(self.I_EXIT_BUTTON, self.I_UNION_TASK_MISSION, interval=3)
                break
            if self.appear_then_click(self.I_UNION_TASK_DONATE, interval=5):
                continue
        # 3机密任务
        while 1:
            self.screenshot()
            if self.appear_then_click(self.I_UNION_TASK_MISSION, interval=5):
                continue
            if self.appear(self.I_UNION_TASK_MISSION_PAGE, interval=1):
                break
        while 1:
            self.screenshot()
            if self.appear_then_click(self.I_UNION_TASK_MISSION_GOTO_BUTTON, interval=1):
                continue
            cu, res, total = self.O_UNION_TASK_MISSION_COUNT.ocr(self.device.image)
            if total:
                if cu > 0:
                    if cu == 1:
                        self.appear_then_click(self.I_UNION_TASK_MISSION_RUN_ALONE, interval=1)
                    else:
                        self.click(self.C_UNION_TASK_MISSION_RUN_REPEAT, interval=1)
                else:
                    break
        logger.info('finish mission success')
        self.ui_click(self.I_EXIT_BUTTON_3, self.I_UNION_TASK_MISSION, interval=3)

        # 4联盟商店
        while 1:
            self.screenshot()
            if self.appear_then_click(self.I_UNION_TASK_SHOP, interval=5):
                continue
            if self.appear(self.I_UNION_TASK_SHOP_PAGE, interval=1):
                break
        num = 3
        while 1:
            self.screenshot()
            if num == 0:
                break
            if not self.appear(self.I_UNION_TASK_SHOP_TICKET, interval=2):
                num -= 1
                continue
            cu, res, total = self.O_UNION_TASK_SHOP_COUNT.ocr(self.device.image)
            if total:
                if cu > 0:
                    self.ui_click(self.C_UNION_TASK_SHOP_EXCHANGE, self.I_UNION_TASK_SHOP_EXCHANGE_BUTTON)
                    while 1:
                        self.screenshot()
                        if cu == self.O_UNION_TASK_SHOP_NUM.ocr(self.device.image):
                            break
                        else:
                            self.click(self.C_UNION_TASK_SHOP_MAX_BUTTON, interval=2)
                    self.ui_click_until_disappear(self.I_UNION_TASK_SHOP_EXCHANGE_BUTTON, interval=3)
                    break
                else:
                    break
        logger.info('get tickets success')
        if self.back_main_page():
            logger.hr('end union_task')
            handle_success = True
        return handle_success

    # 6. 商城
    def shop_task(self) -> bool:
        logger.hr('start shop_task')
        handle_success = False
        # 进入商城
        while 1:
            self.screenshot()
            if self.appear_then_click(self.I_SHOP_TASK_ENTRANCE, interval=1):
                continue
            if self.appear(self.I_SHOP_TASK_PAGE, interval=1):
                break
        logger.info('Enter shop_task_entrance')
        # 推荐-材料专区-试剂周免费礼包
        x, y, w, h = self.I_SHOP_TASK_WEEK_FREE_BUTTON_1.roi_front
        button_list = [getattr(self, f"I_SHOP_TASK_WEEK_FREE_BUTTON_{i+1}") for i in range(3)]
        num = 3
        wait_timer = Timer(30).start()
        while 1:
            self.screenshot()
            if self.appear_then_click(self.I_SHOP_TASK_STUFF_1, interval=1):
                continue
            if self.appear_then_click(self.I_SHOP_TASK_STUFF_2, interval=1):
                continue
            if self.appear(self.I_SHOP_TASK_STUFF_CHECKED_1, interval=3) or self.appear(self.I_SHOP_TASK_STUFF_CHECKED_2, interval=3):
                checked_image = self.I_SHOP_TASK_STUFF_CHECKED_1
                if self.appear(self.I_SHOP_TASK_STUFF_CHECKED_2):
                    checked_image = self.I_SHOP_TASK_STUFF_CHECKED_2
                #   w 238 h 373
                for i in range(6):
                    temp_index = [x+238*(i % 3), y+373*int(i / 3), w, h]
                    for button in button_list:
                        button.roi_front = temp_index
                        button.roi_back = temp_index
                    if self.appear_then_click(self.I_SHOP_TASK_WEEK_FREE_BUTTON_2):
                        self.ui_click(self.I_SHOP_TASK_PAGE, checked_image, interval=2)
                    if self.appear(self.I_SHOP_TASK_WEEK_FREE_BUTTON_1) or self.appear(self.I_SHOP_TASK_WEEK_FREE_BUTTON_3):
                        temp_click = self.I_SHOP_TASK_WEEK_FREE_BUTTON_1
                        if self.appear(self.I_SHOP_TASK_WEEK_FREE_BUTTON_3):
                            temp_click = self.I_SHOP_TASK_WEEK_FREE_BUTTON_3
                        self.ui_click(temp_click, self.I_SHOP_TASK_WEEK_FREE_BUY)
                        self.ui_click_until_disappear(self.I_SHOP_TASK_WEEK_FREE_BUY, interval=2)
                        self.ui_click(self.I_SHOP_TASK_PAGE, checked_image, interval=2)
                        logger.info('get free week package successfully')
                        num = 1
                        break
                num -= 1
            if num == 0:
                break
            if wait_timer.reached():
                break
        # 还原按钮的坐标信息
        for button in button_list:
            button.roi_front = [x, y, w, h]
            button.roi_back = [x, y, w, h]
        # 充值-特权领取
        num = 3
        while 1:
            self.screenshot()
            if self.appear(self.I_SHOP_TASK_VIP_TIP, interval=3):
                self.ui_click(self.C_SHOP_TASK_VIP_TAB_AREA, self.I_SHOP_TASK_VIP_TEXT, interval=3)
                self.ui_click(self.C_SHOP_TASK_VIP_BUTTON, self.I_SHOP_TASK_VIP_WEEK_PACKAGE, interval=3)
                self.appear_then_click(self.I_SHOP_TASK_VIP_WEEK_PACKAGE)
                logger.info('get vip week package successfully')
                break
            else:
                num -= 1
            if num == 0:
                break
        if self.back_main_page():
            logger.hr('end shop_task')
            handle_success = True
        return handle_success

    # 7. 福利（每日签到，以及体力补给）
    def welfare_task(self) -> bool:
        logger.hr('start welfare_task')
        handle_success = False
        # 进入福利
        while 1:
            self.screenshot()
            if self.appear_then_click(self.I_WELFARE_TASK_ENTRANCE, interval=1):
                continue
            if self.appear(self.I_WELFARE_TASK_PAGE, interval=1):
                break
        logger.info('Enter welfare_task_entrance')
        # 每日签到
        num = 3
        while 1:
            self.screenshot()
            if self.appear(self.I_WELFARE_TASK_SIGN_TIP):
                self.ui_click(self.C_WELFARE_TASK_SIGN_TAB_AREA, self.I_WELFARE_TASK_SIGN_TAB_CHECKED)
                break
            else:
                num -= 1
            if num == 0:
                break
        if num:
            click_areas = [getattr(self, f"C_WELFARE_TASK_RESIGN_AREA_{i+1}") for i in range(5)]
            for i in range(16):
                click_areas.append(getattr(self, f"C_WELFARE_TASK_SIGN_AREA_{i+1}"))
            for _ in range(5):
                index = 0
                while index < len(click_areas):
                    self.screenshot()
                    self.click(click_areas[index], interval=3)
                    if self.appear_then_click(self.I_WELFARE_TASK_PAGE, interval=3):
                        index += 1
                    if not self.appear(self.I_WELFARE_TASK_SIGN_TIP):
                        break
                if not self.appear(self.I_WELFARE_TASK_SIGN_TIP):
                    break
            logger.info('daily sign up success')
        else:
            logger.info('no need to sign up')

        # 方舟补给
        while 1:
            self.screenshot()
            if self.appear_then_click(self.I_WELFARE_TASK_SUPPLY_TAB_UNCHECKED):
                continue
            else:
                self.swipe(self.S_WELFARE_TASK_SWIPE, interval=3)
            if self.appear(self.I_WELFARE_TASK_SUPPLY_TAB_CHECKED, interval=1):
                self.wait_until_appear(self.I_WELFARE_TASK_SUPPLY_HEART, wait_time=10)
                # 两个领取按钮
                self.appear_then_click(self.I_WELFARE_TASK_SUPPLY_RECEIVE_BUTTON_1)
                self.appear_then_click(self.I_WELFARE_TASK_SUPPLY_RECEIVE_BUTTON_2)
                break
        if self.back_main_page():
            logger.hr('end welfare_task')
            handle_success = True
        return handle_success

    # 8. 结伴—>(时光钟表铺，不落帷幕，印象航旅)
    def companion_task(self) -> bool:
        logger.hr('start companion_task')
        handle_success = False
        # 进入结伴
        while 1:
            self.screenshot()
            if self.ocr_appear(self.O_START_JOURNEY_ENTRANCE_TEXT, interval=2):
                self.click(self.C_START_JOURNEY_ENTRANCE, 0.5)
                continue
            if self.appear_then_click(self.I_COMPANION_TASK_TAB_UNCHECKED, interval=1):
                continue
            if self.appear(self.I_COMPANION_TASK_TAB_CHECKED, interval=1):
                break
        logger.info('Enter companion_task_entrance')
        # 时光钟表铺
        self.wait_until_appear(self.I_COMPANION_TASK_TIME)
        self.click(self.I_COMPANION_TASK_TIME)
        while 1:
            self.screenshot()
            if self.appear_then_click(self.I_COMPANION_TASK_TIME_LEVEL_UNCHECKED, interval=0.5):
                continue
            if self.appear(self.I_COMPANION_TASK_TIME_LEVEL_CHECKED, interval=0.5):
                break
        self.companion_task_quick()
        # 不落的帷幕
        self.wait_until_appear(self.I_COMPANION_TASK_CURTAIN)
        self.click(self.I_COMPANION_TASK_CURTAIN)
        self.wait_until_appear(self.I_COMPANION_TASK_CURTAIN_PAGE, wait_time=10)
        click_areas = [getattr(self, f"C_COMPANION_TASK_CURTAIN_AREA_{i+1}") for i in range(5)]
        for area in click_areas:
            self.click(area, 0.5)
            num = 0
            while 1:
                self.screenshot()
                if self.appear_then_click(self.I_COMPANION_TASK_TAB_LEVEL_UNCHECKED, interval=0.5):
                    continue
                if self.appear_then_click(self.I_COMPANION_TASK_CURTAIN_LEVEL_UNCHECKED, interval=0.5):
                    continue
                if self.appear(self.I_COMPANION_TASK_TAB_LEVEL_CHECKED, interval=0.5):
                    if self.appear(self.I_COMPANION_TASK_CURTAIN_LEVEL_CHECKED, interval=0.5):
                        num += 1
                if num == 2:
                    break
            if self.appear(self.I_COMPANION_TASK_ALONE_BUTTON, interval=0.5):
                self.companion_task_quick()
                break
            else:
                self.ui_click(self.I_EXIT_BUTTON, self.I_COMPANION_TASK_CURTAIN_PAGE, interval=2)
        # 印象旅航
        self.wait_until_appear(self.I_COMPANION_TASK_TRAVEL)
        self.click(self.I_COMPANION_TASK_TRAVEL)
        while 1:
            self.screenshot()
            if self.appear(self.I_COMPANION_TASK_TAB_LEVEL_CHECKED, interval=0.5):
                if self.appear(self.I_COMPANION_TASK_TRAVEL_LEVEL_CHECKED, interval=0.5):
                    break
            if self.appear_then_click(self.I_COMPANION_TASK_TAB_LEVEL_UNCHECKED, interval=0.5):
                continue
            if self.appear_then_click(self.I_COMPANION_TASK_TRAVEL_LEVEL_UNCHECKED, interval=0.5):
                continue
        self.companion_task_quick()

        if self.back_main_page():
            logger.hr('end companion_task')
            handle_success = True
        return handle_success

    def companion_task_quick(self):
        num = 3
        while 1:
            cu, res, total = self.O_POWER_COUNT.ocr(self.device.image)
            if total:
                if cu < num*5:
                    logger.info('power not enough')
                else:
                    while 1:
                        self.screenshot()
                        if self.O_COMPANION_TASK_NUM.ocr(self.device.image) > num:
                            self.click(self.C_COMPANION_TASK_REDUCE_BUTTON, interval=0.5)
                        elif self.O_COMPANION_TASK_NUM.ocr(self.device.image) < num:
                            self.click(self.C_COMPANION_TASK_ADD_BUTTON, interval=0.5)
                        else:
                            self.click(self.C_COMPANION_TASK_QUICK_BUTTON, interval=0.5)
                            logger.info('companion_task_quick success')
                            break
                break
        self.ui_click(self.I_EXIT_BUTTON, self.I_COMPANION_TASK_TAB_CHECKED, interval=2)

    # 9. 时空回廊
    def corridor_task(self) -> bool:
        logger.hr('start corridor_task')
        handle_success = False
        # 进入时空回廊
        while 1:
            self.screenshot()
            if self.ocr_appear(self.O_START_JOURNEY_ENTRANCE_TEXT, interval=2):
                self.click(self.C_START_JOURNEY_ENTRANCE, 0.5)
                continue
            if self.appear_then_click(self.I_CORRIDOR_TASK_ENTRANCE, interval=2):
                continue
            if self.appear(self.I_CORRIDOR_TASK_EXCHANGE_1, interval=0.5):
                break
            if self.appear(self.I_CORRIDOR_TASK_EXCHANGE_2, interval=0.5):
                break
        logger.info('Enter corridor_task_entrance')
        # 分享
        while 1:
            self.screenshot()
            if self.appear_then_click(self.I_CORRIDOR_TASK_SHARE_BUTTON, interval=0.5):
                self.wait_until_appear(self.I_CORRIDOR_TASK_SHARE_WEIXIN)
                self.ui_click_until_disappear(self.I_CORRIDOR_TASK_SHARE_WEIXIN, interval=5)
                self.ui_click(self.C_CORRIDOR_TASK_BACK_GAME, self.I_CORRIDOR_TASK_EXCHANGE_2)
                break
            if self.appear(self.I_CORRIDOR_TASK_POP_PAGE, interval=1):
                self.ui_click(self.C_CORRIDOR_TASK_FIRST_ISSUE, self.I_CORRIDOR_TASK_SHARE_BUTTON)
                continue
            self.click(self.C_CORRIDOR_TASK_EXCHANGE_BUTTON, interval=2)
        logger.info('share success')
        # 扫荡最后三期
        ocr_list = [getattr(self, f"O_CORRIDOR_TASK_POP_TEXT_{i+1}") for i in range(4)]
        click_list = [getattr(self, f"C_CORRIDOR_TASK_POP_CLICK_{i+1}") for i in range(4)]
        for i in range(4):
            self.ui_click(self.C_CORRIDOR_TASK_EXCHANGE_BUTTON, self.I_CORRIDOR_TASK_POP_PAGE)
            for _ in range(2):
                self.swipe(self.S_CORRIDOR_TASK_SWIPE)
            swipe_timer = Timer(3).start()
            while 1:
                if swipe_timer.reached():
                    self.screenshot()
                    text = ocr_list[i].ocr(self.device.image)
                    if re.match(f"第[零一二三四五六七八九十百千万]+期", text) or text == "白塔旧事":
                        while 1:
                            self.screenshot()
                            if self.appear(self.I_CORRIDOR_TASK_EXCHANGE_1, interval=0.5):
                                break
                            if self.appear(self.I_CORRIDOR_TASK_EXCHANGE_2, interval=0.5):
                                break
                            self.click(click_list[i], interval=5)
                        temp_click = self.C_CORRIDOR_TASK_CLICK_1
                        if text == "第七期":
                            temp_click = self.C_CORRIDOR_TASK_CLICK_3
                        elif text == "第四期" or text == "白塔旧事":
                            temp_click = self.C_CORRIDOR_TASK_CLICK_2
                        while 1:
                            self.screenshot()
                            if self.appear(self.I_CORRIDOR_TASK_MAKE_TAB_CHECKED, interval=0.5):
                                self.ui_click(self.C_CORRIDOR_TASK_MAKE_TAB_CLICK, self.I_GET_WAY_PAGE, interval=2)
                                break
                            if self.appear(self.I_CORRIDOR_TASK_WAKE_TAB_CHECKED, interval=0.5):
                                self.ui_click(self.C_CORRIDOR_TASK_WAKE_TAB_CLICK, self.I_GET_WAY_PAGE, interval=2)
                                break
                            self.click(temp_click, interval=2)
                        self.consume_power(True)
                        logger.info(f'corridor_task success {i+1}')
                        break
            while 1:
                self.screenshot()
                if self.appear(self.I_CORRIDOR_TASK_EXCHANGE_1, interval=0.5):
                    break
                if self.appear(self.I_CORRIDOR_TASK_EXCHANGE_2, interval=0.5):
                    break
                self.click(self.I_EXIT_BUTTON, interval=3)
        if self.back_main_page():
            logger.hr('end corridor_task')
            handle_success = True
        return handle_success

    # 10. 忆海心阶
    def memory_ocean(self) -> bool:
        logger.hr('start memory_ocean')
        handle_success = False
        # 进入忆海心阶
        while 1:
            self.screenshot()
            if self.ocr_appear(self.O_START_JOURNEY_ENTRANCE_TEXT, interval=2):
                self.click(self.C_START_JOURNEY_ENTRANCE, 0.5)
                continue
            if self.appear_then_click(self.I_MEMORY_OCEAN_ENTRANCE, interval=2):
                logger.info('Enter memory_ocean_entrance')
                continue
            # 快速挑战
            if self.appear(self.I_MEMORY_OCEAN_QUICK_BUTTON, interval=1):
                while 1:
                    self.screenshot()
                    text = self.O_TIP_TEXT.ocr(self.device.image)
                    if "没有可以快速挑战的" in text:
                        logger.info('memory_ocean_quick success')
                        break
                    else:
                        self.appear_then_click(self.I_MEMORY_OCEAN_QUICK_BUTTON, interval=1)
                break

        # 真我之境
        self.ui_click(self.C_MEMORY_OCEAN_MAIN_TASK, self.I_MEMORY_OCEAN_MAIN_TASK_PAGE, interval=2)
        if not self.appear(self.I_MEMORY_OCEAN_MAIN_TASK_SKIP_CHECKED):
            self.ui_click(self.C_MEMORY_OCEAN_MAIN_TASK_SKIP, self.I_MEMORY_OCEAN_MAIN_TASK_SKIP_CHECKED, interval=2)
        while 1:
            self.screenshot()
            text = self.O_TIP_TEXT.ocr(self.device.image)
            if "三套搭配后方可开始" in text:
                click_list = [getattr(self, f"C_MEMORY_OCEAN_MAIN_TASK_COLLOCATION_{i+1}") for i in range(3)]
                for click_area in click_list:
                    self.wait_until_appear(self.I_MEMORY_OCEAN_MAIN_TASK_PAGE, True, 60)
                    self.click(click_area)
                    self.collocation_process("memory")
                continue
            if self.appear_then_click(self.I_MEMORY_OCEAN_MAIN_TASK_START_BUTTON, interval=2):
                continue
            if not self.appear(self.I_MEMORY_OCEAN_MAIN_TASK_PAGE):
                self.ui_click(self.I_MEMORY_OCEAN_PAGE, self.I_MEMORY_OCEAN_MAIN_TASK, interval=3)
                break
        # 两个境遇
        for area in [self.C_MEMORY_OCEAN_SUB_TASK_1, self.C_MEMORY_OCEAN_SUB_TASK_2]:
            flag = False
            while 1:
                self.screenshot()
                if self.appear(self.I_MEMORY_OCEAN_SUB_TASK_START_BUTTON):
                    break
                if "此境遇暂未解锁" in self.O_TIP_TEXT.ocr(self.device.image):
                    flag = True
                    break
                self.click(area, interval=2)
            if flag:
                continue
            if self.ocr_appear(self.O_MEMORY_OCEAN_SUB_TASK_OBTAINED):
                self.ui_click(self.I_MEMORY_OCEAN_PAGE, self.I_MEMORY_OCEAN_MAIN_TASK, interval=3)
                continue
            self.appear_then_click(self.I_MEMORY_OCEAN_SUB_TASK_START_BUTTON)
            self.collocation_process("memory_sub")
            if not self.appear(self.I_MEMORY_OCEAN_SUB_TASK_PAGE):
                self.ui_click(self.I_MEMORY_OCEAN_PAGE, self.I_MEMORY_OCEAN_MAIN_TASK, interval=3)
        if self.back_main_page():
            logger.hr('end memory_ocean')
            handle_success = True
        return handle_success

    # 11. 钻石竞技场
    def diamond_arena(self) -> bool:
        logger.hr('start diamond_arena')
        handle_success = False
        # 进入钻石竞技场
        wait_timer = Timer(30).start()
        while 1:
            self.screenshot()
            if self.ocr_appear(self.O_START_JOURNEY_ENTRANCE_TEXT, interval=10):
                self.click(self.C_START_JOURNEY_ENTRANCE, 0.5)
                continue
            if self.appear_then_click(self.I_DIAMOND_ARENA_ENTRANCE, interval=10):
                continue
            if self.appear_then_click(self.I_DIAMOND_ARENA_SEASON, interval=10):
                continue
            if self.appear(self.I_DIAMOND_ARENA_RANKED, interval=2):
                if wait_timer.reached():
                    if self.appear(self.I_DIAMOND_ARENA_COLLOCATION, interval=0.5):
                        break
                    elif self.appear_then_click(self.I_DIAMOND_ARENA_WEEK, interval=0.5):
                        continue
                    else:
                        self.ui_click(self.I_DIAMOND_ARENA_RANKED, self.I_DIAMOND_ARENA_COLLOCATION, interval=20)
        logger.info('Enter diamond_arena_entrance')
        if not self.appear(self.I_DIAMOND_ARENA_SKIP_CHECKED):
            self.ui_click(self.C_DIAMOND_ARENA_SKIP, self.I_DIAMOND_ARENA_SKIP_CHECKED, interval=2)
        # 获取竞技场战力
        my_num = self.O_DIAMOND_ARENA_NUM.ocr(self.device.image)
        # 偶尔识别有误，战力只有6位数时识别成7位
        if my_num < 1500000 or my_num > 4000000:
            self.appear_then_click(self.I_DIAMOND_ARENA_COLLOCATION)
            self.collocation_process("diamond")
            self.ui_click(self.I_EXIT_BUTTON, self.I_DIAMOND_ARENA_COLLOCATION, interval=5)
            my_num = self.O_DIAMOND_ARENA_NUM.ocr(self.device.image)

        ocr_list = [getattr(self, f"O_DIAMOND_ARENA_OTHER_NUM_{i+1}") for i in range(3)]
        click_list = [getattr(self, f"C_DIAMOND_ARENA_CHALLENGE_{i+1}") for i in range(3)]
        change_timer = Timer(2)
        num = 10
        while 1:
            if change_timer.reached():
                self.screenshot()
                # 剩余次数
                cu, res, total = self.O_DIAMOND_ARENA_REMAIN.ocr(self.device.image)
                if total and cu == 0:
                    break
                for i in range(3):
                    other_num = ocr_list[i].ocr(self.device.image)
                    if my_num > other_num:
                        while 1:
                            self.screenshot()
                            if self.appear(self.I_DIAMOND_ARENA_CHALLENGE_PAGE, interval=1):
                                break
                            if self.appear(self.I_DIAMOND_ARENA_OTHER_SURE, interval=1):
                                self.ui_click(self.I_DIAMOND_ARENA_OTHER_SURE, self.I_DIAMOND_ARENA_COLLOCATION, interval=3)
                                break
                            self.click(click_list[i], interval=2)
                        self.ui_click(self.C_DIAMOND_ARENA_CHANGE, self.I_DIAMOND_ARENA_COLLOCATION, interval=3)
                        change_timer.reset()
                        break
                    if i == 2:
                        self.click(self.C_DIAMOND_ARENA_CHANGE)
                        num -= 1
                        change_timer.reset()
                if num == 0:
                    break
        if self.back_main_page():
            logger.hr('end diamond_arena')
            handle_success = True
        if num == 0:
            return self.diamond_arena()
        return handle_success

    # 12. 搭配评选赛
    def collocation_arena(self) -> bool:
        logger.hr('start collocation_arena')
        handle_success = False
        wait_timer = Timer(30).start()
        # 进入搭配评选赛
        while 1:
            self.screenshot()
            if self.ocr_appear(self.O_START_JOURNEY_ENTRANCE_TEXT, interval=5):
                self.click(self.C_START_JOURNEY_ENTRANCE, 0.5)
                continue
            if self.appear_then_click(self.I_COLLOCATION_ARENA_ENTRANCE, interval=5):
                continue
            if self.appear(self.I_COLLOCATION_ARENA_PAGE, interval=5) and wait_timer.reached():
                break
        logger.info('Enter collocation_arena_entrance')

        if self.appear(self.I_COLLOCATION_ARENA_BUTTON):
            self.ui_click(self.I_COLLOCATION_ARENA_BUTTON, self.I_COLLOCATION_ARENA_VS, interval=5)
            click_list = [self.C_COLLOCATION_ARENA_LIKE_1, self.C_COLLOCATION_ARENA_LIKE_2]
            while 1:
                self.screenshot()
                if self.appear(self.I_COLLOCATION_ARENA_PAGE, interval=5):
                    break
                if not self.wait_until_appear(self.I_COLLOCATION_ARENA_VS, True, 60):
                    continue
                self.appear_then_click(self.I_COLLOCATION_ARENA_VS)
                self.ui_click_until_smt_disappear(click_list[random.randint(0, len(click_list) - 1)], self.I_COLLOCATION_ARENA_VS, interval=10)
        if self.back_main_page():
            logger.hr('end collocation_arena')
            handle_success = True
        return handle_success

    # 13. 每日任务领取
    def daily_reward(self) -> bool:
        logger.hr('start daily_reward')
        handle_success = False
        # 进入任务
        while 1:
            self.screenshot()
            if self.appear_then_click(self.I_DAILY_REWARD_ENTRANCE, interval=1):
                continue
            if self.appear(self.I_DAILY_REWARD_TODAY_TAB_CHECKED, interval=1):
                break
        logger.info('Enter daily_reward_entrance')

        # 每日任务
        self.ui_click_until_disappear(self.I_DAILY_REWARD_ONE_CLICK, interval=2)
        while 1:
            self.screenshot()
            if self.appear(self.I_DAILY_REWARD_PACKAGE_OPEN, interval=0.5):
                break
            self.click(self.C_DAILY_REWARD_PACKAGE, interval=2)
            self.appear_then_click(self.I_DAILY_REWARD_TODAY_TAB_CHECKED, interval=1)
        # 时尚任务
        if self.appear(self.I_DAILY_REWARD_FASHION_TIP):
            self.ui_click(self.C_DAILY_REWARD_FASHION_TAB, self.I_DAILY_REWARD_FASHION_TAB_CHECKED, interval=2)
            self.wait_until_appear(self.I_DAILY_REWARD_ONE_CLICK, True, 10)
            self.ui_click_until_disappear(self.I_DAILY_REWARD_ONE_CLICK, interval=2)
        if self.back_main_page():
            logger.hr('end daily_reward')
            handle_success = True
        return handle_success

    # 14. 邮件领取
    def receive_mail(self) -> bool:
        logger.hr('start receive_mail')
        handle_success = False
        # 进入邮件
        while 1:
            self.screenshot()
            if self.appear(self.I_RECEIVE_MAIL_PAGE, interval=1):
                break
            if self.appear_then_click(self.I_RECEIVE_MAIL_ENTRANCE, interval=1):
                continue
        logger.info('Enter receive_mail_entrance')
        self.appear_then_click(self.I_RECEIVE_MAIL_ALL_RECEIVE)
        self.ui_click(self.C_RECEIVE_MAIL_INVALID_AREA, Nikki_restartAssets.I_MAIN_PAGE_POST, interval=1)
        if self.back_main_page():
            logger.hr('end receive_mail')
            handle_success = True
        return handle_success

    # 15. 多余体力消耗
    def expend_power(self) -> bool:
        logger.hr('start expend_power')
        handle_success = False
        # 进入制衣引导
        while 1:
            self.screenshot()
            if self.ocr_appear(self.O_DESIGN_CENTER_ENTRANCE_TEXT, interval=2):
                self.click(self.C_DESIGN_CENTER_ENTRANCE, 0.5)
                continue
            if self.ocr_appear(self.O_EXPEND_POWER_ENTRANCE_TEXT, interval=2):
                self.click(self.C_EXPEND_POWER_ENTRANCE, 0.5)
                continue
            if self.appear(self.I_EXPEND_POWER_PAGE, interval=2):
                break
        logger.info('Enter expend_power_entrance')

        image_list = [self.I_EXPEND_POWER_TARGET_1, self.I_EXPEND_POWER_TARGET_2]
        img_click_list = [self.C_EXPEND_POWER_TARGET_CLICK_1, self.C_EXPEND_POWER_TARGET_CLICK_2]
        for i in range(2):
            if self.appear(image_list[i]):
                make_type = 1
                while 1:
                    self.screenshot()
                    if self.appear(self.I_CORRIDOR_TASK_MAKE_TAB_CHECKED, interval=0.5):
                        break
                    if self.appear(self.I_CORRIDOR_TASK_WAKE_TAB_CHECKED, interval=0.5):
                        make_type = 2
                        break
                    self.click(img_click_list[i], interval=2)
                text = self.O_EXPEND_POWER_RARITY.ocr(self.device.image)
                if make_type == 1:
                    text = self.O_EXPEND_POWER_RARITY2.ocr(self.device.image)
                ocr_list = []
                click_list = []
                if "闪耀" in text:
                    if make_type == 1:
                        ocr_list = [self.O_EXPEND_POWER_SHINE_MAKE]
                        click_list = [self.C_EXPEND_POWER_SHINE_MAKE]
                    else:
                        ocr_list = [self.O_EXPEND_POWER_SHINE_WAKE_2, self.O_EXPEND_POWER_SHINE_WAKE_1]
                        click_list = [self.C_EXPEND_POWER_SHINE_WAKE_2, self.C_EXPEND_POWER_SHINE_WAKE_1]
                else:
                    if make_type == 1:
                        ocr_list = [self.O_EXPEND_POWER_RARE_MAKE_1, self.O_EXPEND_POWER_RARE_MAKE_2]
                        click_list = [self.C_EXPEND_POWER_RARE_MAKE_1, self.C_EXPEND_POWER_RARE_MAKE_2]
                    else:
                        ocr_list = [self.O_EXPEND_POWER_RARE_WAKE_1, self.O_EXPEND_POWER_RARE_WAKE_2, self.O_EXPEND_POWER_RARE_WAKE_3]
                        click_list = [self.C_EXPEND_POWER_RARE_WAKE_1, self.C_EXPEND_POWER_RARE_WAKE_2, self.C_EXPEND_POWER_RARE_WAKE_3]
                for i in range(len(ocr_list)):
                    wait_timer = Timer(5).start()
                    while 1:
                        self.screenshot()
                        cu, res, total = ocr_list[i].ocr(self.device.image)
                        if total:
                            if cu < total or (self.appear(self.I_CORRIDOR_TASK_WAKE_TAB_CHECKED) and ("闪耀" in text) and i ==1):
                                self.ui_click(click_list[i], self.I_GET_WAY_PROCEED_BUTTON_2, interval=2)
                                self.consume_power()
                                self.ui_click_until_smt_disappear(self.I_EXIT_BUTTON_4, self.I_GET_WAY_PROCEED_BUTTON_2, interval=2)
                            break
                        if wait_timer.reached():
                            break
                self.ui_click(self.I_EXIT_BUTTON_4, self.I_EXPEND_POWER_PAGE, interval=2)
        if self.back_main_page():
            logger.hr('end expend_power')
            handle_success = True
        return handle_success

    def collocation_process(self, process_type: str):
        if process_type == "memory":
            self.wait_until_appear(self.I_COLLOCATION_PROCESS_RECOMMEND_BUTTON, True, 60)
            self.ui_click(self.I_COLLOCATION_PROCESS_RECOMMEND_BUTTON, self.I_COLLOCATION_PROCESS_SURE_BUTTON, interval=2)
            self.ui_click_until_disappear(self.I_COLLOCATION_PROCESS_SURE_BUTTON, interval=2)
            self.appear_then_click(self.I_COLLOCATION_PROCESS_NEXT_BUTTON)
            self.wait_until_appear(self.I_COLLOCATION_PROCESS_EQUIP, True, 60)
            self.ui_click(self.I_COLLOCATION_PROCESS_EQUIP, self.I_COLLOCATION_PROCESS_EQUIP_ONECLICK, interval=2)
            self.appear_then_click(self.I_COLLOCATION_PROCESS_EQUIP_ONECLICK)
            self.ui_click(self.I_COLLOCATION_PROCESS_EQUIP_SURE, self.I_COLLOCATION_PROCESS_EQUIP, interval=10)
            self.ui_click_until_disappear(self.I_COLLOCATION_PROCESS_SURE, interval=10)
        elif process_type == "diamond":
            self.wait_until_appear(self.I_COLLOCATION_PROCESS_RECOMMEND_BUTTON, True, 60)
            self.ui_click(self.I_COLLOCATION_PROCESS_RECOMMEND_BUTTON, self.I_COLLOCATION_PROCESS_SURE_BUTTON, interval=2)
            self.appear_then_click(self.I_COLLOCATION_PROCESS_SURE_BUTTON)
            for _ in range(3):
                self.wait_until_appear(self.I_COLLOCATION_PROCESS_NEXT_BUTTON, True, 60)
                self.appear_then_click(self.I_COLLOCATION_PROCESS_NEXT_BUTTON)
                self.wait_until_appear(self.I_COLLOCATION_PROCESS_EQUIP, True, 60)
                self.ui_click(self.I_COLLOCATION_PROCESS_EQUIP, self.I_COLLOCATION_PROCESS_EQUIP_ONECLICK, interval=2)
                self.appear_then_click(self.I_COLLOCATION_PROCESS_EQUIP_ONECLICK)
                self.ui_click(self.I_COLLOCATION_PROCESS_EQUIP_SURE, self.I_COLLOCATION_PROCESS_EQUIP, interval=10)
                self.ui_click_until_disappear(self.I_COLLOCATION_PROCESS_SURE, interval=10)
        elif process_type == "memory_sub":
            self.wait_until_appear(self.I_COLLOCATION_PROCESS_RECOMMEND_BUTTON, True, 60)
            self.appear_then_click(self.I_COLLOCATION_PROCESS_RECOMMEND_BUTTON)
            self.ui_click(self.C_COLLOCATION_PROCESS_SKIP_AREA, self.I_COLLOCATION_PROCESS_SKIP_CHECKED, interval=5)
            self.ui_click_until_disappear(self.I_COLLOCATION_PROCESS_NEXT_BUTTON, interval=10)

    def consume_power(self, one_time: bool = False) -> bool:
        no_power = False
        wait_timer = Timer(5)
        while 1:
            self.screenshot()
            if self.appear_then_click(self.I_GET_WAY_PROCEED_BUTTON, interval=2):
                wait_timer.start()
                continue
            if self.appear_then_click(self.I_GET_WAY_PROCEED_BUTTON_2, interval=2):
                wait_timer.start()
                continue
            if wait_timer.reached():
                if self.appear(self.I_GET_WAY_PROCEED_START_BUTTON_1, interval=0.5):
                    if self.appear(self.I_GET_WAY_PROCEED_CHALLENGE_1, interval=0.5):
                        self.ui_click_until_disappear(self.I_GET_WAY_PROCEED_CHALLENGE_1, interval=1)
                        if one_time:
                            break
                    else:
                        no_power = True
                        break
                if self.appear(self.I_GET_WAY_PROCEED_START_BUTTON_2, interval=0.5):
                    if self.appear(self.I_GET_WAY_PROCEED_CHALLENGE_2, interval=0.5):
                        self.ui_click_until_disappear(self.I_GET_WAY_PROCEED_CHALLENGE_2, interval=1)
                        if one_time:
                            break
                    else:
                        no_power = True
                        break
                if self.appear(self.I_GET_WAY_PROCEED_START_BUTTON_4, interval=0.5):
                    if self.appear(self.I_GET_WAY_PROCEED_CHALLENGE_4, interval=0.5):
                        self.ui_click_until_disappear(self.I_GET_WAY_PROCEED_CHALLENGE_4, interval=1)
                        if one_time:
                            break
                    else:
                        no_power = True
                        break
                if self.appear(self.I_GET_WAY_PROCEED_SURVEY_PAGE, interval=0.5):
                    wait_timer = Timer(2).start()
                    # num = 4
                    # while 1:
                    #     if wait_timer.reached():
                    #         self.swipe(self.S_GET_WAY_PROCEED_SURVEY_SWIPE)
                    #         wait_timer.reset()
                    #         num -= 1
                    #     if num == 0:
                    #         break
                    self.wait_until_appear(self.I_GET_WAY_PROCEED_START_BUTTON_3, True, 10)
                    if self.appear(self.I_GET_WAY_PROCEED_CHALLENGE_3, interval=0.5):
                        self.ui_click_until_disappear(self.I_GET_WAY_PROCEED_CHALLENGE_3, interval=1)
                        if one_time:
                            break
                    else:
                        no_power = True
                        break
                if self.appear_then_click(self.I_EXIT_BUTTON, interval=3):
                    continue
                if self.appear_then_click(self.I_EXIT_BUTTON_3, interval=3):
                    continue
        while 1:
            self.screenshot()
            if self.appear(self.I_GET_WAY_PROCEED_BUTTON, interval=0.5):
                break
            if self.appear(self.I_GET_WAY_PROCEED_BUTTON_2, interval=0.5):
                break
            if self.appear_then_click(self.I_EXIT_BUTTON, interval=3):
                continue
            if self.appear_then_click(self.I_EXIT_BUTTON_3, interval=3):
                continue
        return no_power

    def back_main_page(self) -> bool:
        while 1:
            self.screenshot()
            if self.appear_then_click(self.I_EXIT_BUTTON, interval=6):
                continue
            if self.appear_then_click(self.I_EXIT_BUTTON_2, interval=6):
                continue
            if self.appear_then_click(self.I_EXIT_BUTTON_3, interval=6):
                continue
            if self.appear_then_click(self.I_EXIT_BUTTON_4, interval=6):
                continue
            if self.appear(Nikki_restartAssets.I_MAIN_PAGE_POWER, interval=1):
                return True


if __name__ == '__main__':
    from module.config.config import Config
    from module.device.device import Device
    c = Config('oas1')
    d = Device(c)
    t = ScriptTask(c, d)
    t.screenshot()

    t.run()
