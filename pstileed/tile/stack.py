from .layer import Layer
from typing import List, Tuple

class Stack:
    def __init__(self) -> None:
        self.__layers = []

    @property
    def layers(self) -> List[Layer]:
        return self.__layers
