from .setting import Setting
from .stack import Stack
from .layer import Layer
from .slot import Slot
from .tile_info import TileInfo
from .sprite import Sprite
from typing import List, Callable
import tkinter as Tk
import time

class Board:
    def __init__(self, setting: Setting, tkCanvas: Tk.Canvas, sprite: Sprite) -> None:
        self.__setting = setting
        self.__tkCanvas = tkCanvas
        self.__sprite = sprite
        stack: Stack = Stack()
        # 全てのレイヤに空画像を設定する
        for L in range(0, setting.layer_count):
            layer: Layer = Layer()
            for i in range(0, setting.row_count):
                y = i * setting.slot_height
                for j in range(0, setting.col_count):
                    x = j * setting.slot_width
                    slot: Slot = Slot(i, j, x, y, setting.slot_width, setting.slot_height)
                    layer.slots.append(slot)
                    slot.tile_info = TileInfo('assets/empty.png', 0)
            stack.layers.append(layer)
        self.__stack = stack
        self.__focus_row = -1
        self.__focus_col = -1
        self.__select_row = -1
        self.__select_col = -1
        self.__on_focus = None
        self.__on_select = None
        self.__line = False
        self.__press = False


    @property
    def setting(self) -> Setting:
        return self.__setting

    @property
    def stack(self) -> Stack:
        return self.__stack

    @property
    def first_layer(self) -> Layer:
        return self.__stack.layers[0]

    @property
    def last_layer(self) -> Layer:
        return self.__stack.layers[len(self.__stack.layers)-1]

    @property
    def focus_layer(self) -> Layer:
        return self.__stack.layers[len(self.__stack.layers)-1]

    @property
    def select_layer(self) -> Layer:
        return self.__stack.layers[len(self.__stack.layers)-2]

    @property
    def focus_row(self) -> int:
        return self.__focus_row

    @property
    def focus_col(self) -> int:
        return self.__focus_col

    @property
    def select_row(self) -> int:
        return self.__select_row

    @property
    def select_col(self) -> int:
        return self.__select_col

    @property
    def on_focus(self) -> Callable[[int, int], None]:
        return self.__on_focus

    @on_focus.setter
    def on_focus(self, fn: Callable[[int, int], None]):
        self.__on_focus = fn

    @property
    def on_select(self) -> Callable[[int, int], None]:
        return self.__on_select

    @on_select.setter
    def on_select(self, fn: Callable[[int, int], None]):
        self.__on_select = fn

    def batch(self):
        updateSlots = 0
        # 変更のあったスロットを取得
        dirty_positions = []
        for l in self.stack.layers:
            tmp = l.dirty_positions()
            for t in tmp:
                dirty_positions.append(t)
        dirty_positions = set(dirty_positions)
        # 変更のあったスロットのみ描画
        for pos in dirty_positions:
            row = pos[0]
            col = pos[1]
            tiles: List[TileInfo] = []
            dirty = False
            for l in self.stack.layers:
                slots = l.select_slots(row, col)
                for slot in slots:
                    tiles.append(slot.tile_info)
                    if slot.dirty:
                        dirty = True
            if not dirty:
                continue
            updateSlots += 1
            targets = self.first_layer.select_slots(row, col)
            target = targets[0]
            # 全てのレイヤーの現在処理中スロットをリフレッシュする
            for l in self.stack.layers:
                rTargets = l.select_slots(row, col)
                for e in rTargets:
                    e.refresh()
            tag: str = f't{row}_{col}'
            files: List[str] = list(map(lambda x: x.asset, tiles))
            self.__tkCanvas.delete(tag)
            self.__tkCanvas.create_image(target.center_x, target.center_y, image=self.__sprite.make_single(files, (target.w, target.h)), tag=tag)
        # グリッドの描画
        if(self.__line):
            return
        self.__line = True
        setting = self.__setting
        self.__tkCanvas.create_line(setting.panel_width-1, 0, setting.panel_width-1, setting.panel_height)
        self.__tkCanvas.create_line(0, setting.panel_height-1, setting.panel_width, setting.panel_height-1)
        for i in range(0, setting.row_count):
            y = i * setting.slot_height
            self.__tkCanvas.create_line(0, y, setting.panel_width, y)

        for i in range(0, setting.col_count):
            x = i * setting.slot_width
            self.__tkCanvas.create_line(x, 0, x, setting.panel_height)

    @staticmethod
    def y_to_row(setting: Setting, y: int) -> int:
        return int(y / setting.slot_height)

    @staticmethod
    def x_to_col(setting: Setting, x: int) -> int:
        return int(x / setting.slot_width)

    def on_mouse_motion(self, e):
        if self.focus_row >= 0 and self.focus_col >= 0:
            slots: List[Slot] = self.focus_layer.select_slots(self.focus_row, self.focus_col)
            for slot in slots:
                slot.tile_info = TileInfo('assets/empty.png', 0)
        self.__focus_row = Board.y_to_row(self.__setting, e.y)
        self.__focus_col = Board.x_to_col(self.__setting, e.x)
        slots: List[Slot] = self.focus_layer.select_slots(self.focus_row, self.focus_col)
        for slot in slots:
            slot.tile_info = TileInfo('assets/cursor.png', 0)
        if self.on_focus != None:
            self.on_focus(self.focus_row, self.focus_col)
        if self.__press:
            self.on_mouse_press(e)
        self.batch()

    def on_mouse_press(self, e):
        if self.select_row >= 0 and self.select_col >= 0:
            slots: List[Slot] = self.select_layer.select_slots(self.select_row, self.select_col)
            for slot in slots:
                slot.tile_info = TileInfo('assets/empty.png', 0)
        self.__select_row = Board.y_to_row(self.__setting, e.y)
        self.__select_col = Board.x_to_col(self.__setting, e.x)
        slots: List[Slot] = self.select_layer.select_slots(self.select_row, self.select_col)
        for slot in slots:
            slot.tile_info = TileInfo('assets/frame.png', 0)
        if self.on_select != None:
            self.on_select(self.select_row, self.select_col)
        self.batch()
        self.__press = True

    def on_mouse_release(self, e):
        self.__press = False