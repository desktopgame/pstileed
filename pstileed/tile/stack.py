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

    def to_json(self) -> dict:
        ret = {}
        layerData = []
        for i in range(0, len(self.layers)):
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

    def from_json(self, j: dict, s: Setting):
        self.layers.clear()
        layerData = j['m_layerData']
        for layer in layerData:
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
                newSlot.tile_info = TileInfo(slot['m_asset'], slot['m_id'])
                for k, v in slot.items():
                    if k == 'm_position' or k == 'm_asset' or k == 'm_id':
                        continue
                    newSlot.tile_info.attributes[k] = v
                newLayer.slots.append(newSlot)
            self.layers.append(newLayer)
