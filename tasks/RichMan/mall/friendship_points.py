# This Python file uses the following encoding: utf-8
# @author runhey
# github https://github.com/runhey
import time

from module.logger import logger

from tasks.GameUi.page import page_main, page_guild
from tasks.GameUi.game_ui import GameUi
from tasks.Component.Buy.buy import Buy
from tasks.RichMan.assets import RichManAssets
from tasks.RichMan.config import FriendshipPoints as FriendshipPointsConfig


class FriendshipPoints(GameUi, Buy, RichManAssets):

    def execute_friendship(self, con: FriendshipPointsConfig = None):
        pass


if __name__ == '__main__':
    from module.config.config import Config
    from module.device.device import Device

    c = Config('oas1')
    d = Device(c)
    t = FriendshipPoints(c, d)

