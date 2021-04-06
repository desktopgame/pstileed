class Setting:
    def __init__(self, panel_width: int, panel_height: int, row_count: int, col_count: int, layer_count) -> None:
        self.__panel_width = panel_width
        self.__panel_height = panel_height
        self.__row_count = row_count
        self.__col_count = col_count
        self.__layer_count = layer_count

    @property
    def panel_width(self) -> int:
        return self.__panel_width

    @property
    def panel_height(self) -> int:
        return self.__panel_height

    @property
    def panel_size(self) -> int:
        return (self.__panel_width, self.__panel_height)

    @property
    def row_count(self) -> int:
        return self.__row_count

    @property
    def col_count(self) -> int:
        return self.__col_count

    @property
    def layer_count(self) -> int:
        return self.__layer_count

    @property
    def slot_width(self) -> int:
        return int(self.panel_width / self.col_count)

    @property
    def slot_height(self) -> int:
        return int(self.panel_height / self.row_count)