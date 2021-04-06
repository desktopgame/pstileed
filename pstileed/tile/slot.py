import PySimpleGUI as sg
import tkinter as Tk
import PIL.ImageTk as ImageTK
from .sprite import Sprite
from .tile_info import TileInfo

class Slot:
    def __init__(self, row: int, col: int, x: int, y: int, w: int, h: int) -> None:
        self.__row = row
        self.__col = col
        self.__x = int(x)
        self.__y = int(y)
        self.__w = int(w)
        self.__h = int(h)
        self.__tile_info = None
        self.__dirty = False

    @property
    def center_x(self) -> int:
        return self.x + int(self.w / 2)

    @property
    def center_y(self) -> int:
        return self.y + int(self.h / 2)

    @property
    def name(self) -> str:
        return f'{self.row}_{self.col}'

    @property
    def row(self) -> int:
        return self.__row

    @property
    def col(self) -> int:
        return self.__col

    @property
    def x(self) -> int:
        return self.__x

    @property
    def y(self) -> int:
        return self.__y

    @property
    def w(self) -> int:
        return self.__w

    @property
    def h(self) -> int:
        return self.__h

    @property
    def tile_info(self) -> TileInfo:
        return self.__tile_info

    @tile_info.setter
    def tile_info(self, tile_info: TileInfo):
        self.__tile_info = tile_info
        self.__img = None
        self.__dirty = True

    def refresh(self):
        self.__dirty = False

    @property
    def dirty(self) -> bool:
        return self.__dirty