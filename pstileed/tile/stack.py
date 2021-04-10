from PIL.Image import new
from pstileed.tile.tile_info import TileInfo
from pstileed.tile.setting import Setting
from pstileed.tile.slot import Slot
from .layer import Layer
from typing import List, Tuple

class Stack:
    def __init__(self) -> None:
        self.__layers = []

    @property
    def layers(self) -> List[Layer]:
        return self.__layers

    def to_json(self, layer_count: int) -> dict:
        ret = {}
        layerData = []
        for i in range(0, layer_count):
            layer = self.layers[i]
            # レイヤー情報をJSON化
            slotDataJson = []
            layerJson = {}
            layerJson['m_index'] = i
            for slot in layer.slots:
                slotJson = {}
                slotJson['m_position'] = {
                    'x': slot.col,
                    'y': slot.row
                }
                slotJson['m_asset'] = slot.tile_info.asset
                slotJson['m_id'] = slot.tile_info.id
                for k, v in slot.tile_info.attributes.items():
                    slotJson[k] = v
                slotDataJson.append(slotJson)
            layerJson['m_slotData'] = slotDataJson
            layerData.append(layerJson)
        ret['m_layerData'] = layerData
        return ret

    def from_json(self, j: dict, s: Setting, layer_count: int):
        orig_len = len(self.layers)
        self.layers.clear()
        layerData = j['m_layerData']
        layerData = sorted(layerData, key=lambda l: l['m_index'])
        layerIndex = 0
        for layer in layerData:
            if layerIndex >= layer_count:
                break
            layerIndex += 1
            slots = layer['m_slotData']
            newLayer = Layer()
            for slot in slots:
                newSlot = Slot(
                    slot['m_position']['y'],
                    slot['m_position']['x'],
                    slot['m_position']['x'] * s.slot_width,
                    slot['m_position']['y'] * s.slot_height,
                    s.slot_width,
                    s.slot_height
                )
                if slot['m_id'] > 0:
                    newSlot.tile_info = TileInfo(slot['m_asset'], slot['m_id'])
                    for k, v in slot.items():
                        if k == 'm_position' or k == 'm_asset' or k == 'm_id':
                            continue
                        newSlot.tile_info.attributes[k] = v
                else:
                    newSlot.tile_info = TileInfo('assets/empty.png', 0)
                newLayer.slots.append(newSlot)
            self.layers.append(newLayer)
        # フォーカス用のレイヤーを追加
        while len(self.layers) < orig_len:
            newLayer = Layer()
            for i in range(0, s.row_count):
                for j in range(0, s.col_count):
                    newSlot = Slot(i, j, j * s.slot_width, i * s.slot_height, s.slot_width, s.slot_height)
                    newSlot.tile_info = TileInfo('assets/empty.png', 0)
                    newLayer.slots.append(newSlot)
            self.layers.append(newLayer)
