from typing import Any


class TileInfo:
    def __init__(self, asset: str, id: int) -> None:
        self.asset = asset
        self.id = id
        self.attributes = {}

    def overwrite_attributes(self, a: dict):
        self.attributes = a.copy()

    def merge_attributes(self, a: dict):
        for k, v in a.items():
            self.attributes[k] = v

    def put_attribute(self, k: str, v):
        self.attributes[k] = v

    def remove_attribute(self, k: str):
        self.attributes.pop(k, None)

    def duplicate(self):
        ret = TileInfo(self.asset, self.id)
        ret.overwrite_attributes(self.attributes)
        return ret