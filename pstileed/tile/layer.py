from .slot import Slot
from typing import List, Tuple

class Layer:
    def __init__(self) -> None:
        self.__slots = []

    @property
    def slots(self) -> List[Slot]:
        return self.__slots

    def dirty_positions(self) -> List[Tuple[int, int]]:
        ret: List[Tuple[int, int]] = []
        for slot in self.slots:
            if slot.dirty:
                ret.append((slot.row, slot.col))
        return ret

    def select_slots(self, row: int, col: int) -> List[Slot]:
        return list(filter(lambda x: x.row == row and x.col == col, self.slots))