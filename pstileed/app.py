from pstileed.tile.tile_info import TileInfo
import PySimpleGUI as sg
import tkinter as Tk
import PIL.ImageTk as ImageTK
import pstileed.tile as tile
import json
import os.path
from PIL import Image
from typing import Set, Tuple, List

class App:
    def __init__(self) -> None:
        self.editor_setting: tile.Setting = tile.Setting(400, 720, 10, 4, 1 + 2)
        self.setting: tile.Setting = tile.Setting(600, 720, 20, 20, 3 + 2)

        # GUI作成
        self.table_sprite = tile.Sprite()
        tables = []
        for i in range(0, self.setting.layer_count-2):
            tables.append([sg.Text(f'Layer [{i}]')])
            for p in range(0, 4):
                tables.append([sg.Input(size=(10, 1), readonly=True, key=f'k{i}_{p}'), sg.Input(size=(10, 1), enable_events=True, key=f'v{i}_{p}')])
        tables.append([sg.Text('', size=(10, 30))])
        layout = [
            [sg.Input(os.path.join(os.path.expanduser("~"), 'data.json'), key='File'), sg.Button('Open'), sg.Button('Save'), sg.Button('SaveAs')],
            [sg.Text('Pallet'), sg.Text('Board', pad=(380, 0)), sg.Text('Property', pad=(195, 0))],
            [sg.Canvas(size=self.editor_setting.panel_size, key='editor_canvas'), sg.Canvas(size=self.setting.panel_size, key='canvas'), sg.Column(tables)]
        ]
        self.window = sg.Window('pstileed', layout, finalize=True, resizable=True)
        # 盤面を作成
        self.canvas: sg.Canvas = self.window['canvas']
        self.tkCanvas: Tk.Canvas = self.canvas.TKCanvas
        self.editor_canvas: sg.Canvas = self.window['editor_canvas']
        self.editor_tkCanvas: Tk.Canvas = self.editor_canvas.TKCanvas

        self.sprite = tile.Sprite()
        self.editor_sprite = tile.Sprite()
        self.board: tile.Board = tile.Board(self.setting, self.tkCanvas, self.sprite)
        self.editor_board: tile.Board = tile.Board(self.editor_setting, self.editor_tkCanvas, self.editor_sprite)
        # 配置可能ピースの読み込み
        def json_from_file(file: str):
            with open(file, 'r') as fp:
                return json.load(fp)
        config = json_from_file('config.json')
        items: List[tile.TileInfo] = []
        for tile_item in config['tiles']:
            e = TileInfo(tile_item['asset'], tile_item['id'])
            e.merge_attributes(tile_item['attributes'])
            e.put_attribute('layer', tile_item['layer'])
            items.append(e)
        item_i = 0
        for row in range(0, self.editor_setting.row_count):
            for col in range(0, self.editor_setting.col_count):
                if item_i >= len(items):
                    break
                slots = filter(lambda x: x.row == row and x.col == col, self.editor_board.first_layer.slots)
                for slot in slots:
                    slot.tile_info = items[item_i].duplicate()
                item_i += 1
        # 盤面の初期化
        self.board.batch()
        self.editor_board.batch()
        self.tkCanvas.pack()
        self.editor_tkCanvas.pack()

        # イベントハンドラの追加
        self.tkCanvas.bind('<ButtonPress>', self.board.on_mouse_press)
        self.tkCanvas.bind('<ButtonRelease>', self.board.on_mouse_release)
        self.tkCanvas.bind('<Motion>', self.board.on_mouse_motion)
        self.editor_tkCanvas.bind('<ButtonPress>', self.editor_board.on_mouse_press)
        self.editor_tkCanvas.bind('<ButtonRelease>', self.editor_board.on_mouse_release)
        self.editor_tkCanvas.bind('<Motion>', self.editor_board.on_mouse_motion)
        # 選択中のピースをレイヤーへ配置する
        def on_select(row: int, col: int):
            # ピースが選択されていないので何もしない
            if self.editor_board.select_row < 0 or self.editor_board.select_col < 0:
                return
            # 選択されているスロットの取得
            from_slot: tile.Slot = self.editor_board.first_layer.select_slots(self.editor_board.select_row, self.editor_board.select_col)[0]
            from_tile = from_slot.tile_info
            # 書き込み先のスロットの取得
            to_slot: tile.Slot = self.board.stack.layers[from_tile.attributes.get('layer', 0)].select_slots(row, col)[0]
            to_tile = to_slot.tile_info
            # 種別が違うなら配置
            if from_tile.id != to_tile.id:
                new_tile = from_tile.duplicate()
                new_tile.remove_attribute('layer')
                to_slot.tile_info = new_tile
                self._edit_props(row, col)
            else:
                self._edit_props(row, col)

        self.board.on_select = on_select

    def _edit_props(self, row: int, col: int):
        for i in range(0, self.setting.layer_count-2):
            slot = self.board.stack.layers[i].select_slots(row, col)[0]
            index = 0
            # プロパティ入力領域を空っぽに
            for p in range(0, 4):
                key_input: sg.Input = self.window[f'k{i}_{p}']
                val_input: sg.Input = self.window[f'v{i}_{p}']
                key_input.update('')
                val_input.update('')
            # タイルに入っている情報を入れる
            for k, v in slot.tile_info.attributes.items():
                if index >= 3:
                    break
                key_input: sg.Input = self.window[f'k{i}_{index}']
                val_input: sg.Input = self.window[f'v{i}_{index}']
                key_input.update(k)
                val_input.update(v)
                index += 1

    def _scan_props(self, event, values):
        for i in range(0, self.setting.layer_count-2):
            # プロパティ入力領域を空っぽに
            for p in range(0, 4):
                if event == f'v{i}_{p}':
                    self._apply_props(values, i, p)
                    break

    def _apply_props(self, values, layer: int, prop_index: int):
        sel_row: int = self.board.select_row
        sel_col: int = self.board.select_col
        if sel_row < 0 or sel_col < 0:
            return
        slot: tile.Slot = self.board.stack.layers[layer].select_slots(sel_row, sel_col)[0]
        slot.tile_info.put_attribute(values[f'k{layer}_{prop_index}'], values[f'v{layer}_{prop_index}'])

    def _open_board(self):
        file: str = sg.popup_get_file('Open a file.')
        with open(file, 'r') as f:
            self.board.stack.from_json(json.load(f), self.setting, 3)
        self.window['File'].update(file)
        self.board.batch()

    def _save_board(self):
        file_input: sg.Input = self.window[f'File']
        file: str = file_input.get()
        if file == '':
            sg.popup('Error', 'Enter a file name.')
            return
        with open(file, 'w+') as f:
            json.dump(self.board.stack.to_json(3), f)

    def _save_as_board(self):
        file: str = sg.popup_get_file('Save a file.')
        self.window['File'].update(file)
        self._save_board()

    def start(self):
        # イベントループ
        while True:
            event, values = self.window.read()
            if event == sg.WIN_CLOSED:
                break
            elif event == 'Open':
                self._open_board()
            elif event == 'Save':
                self._save_board()
            elif event == 'SaveAs':
                self._save_as_board()
            else:
                self._scan_props(event, values)
        self.window.close()