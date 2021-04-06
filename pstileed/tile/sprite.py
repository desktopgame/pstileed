from PIL import Image
from typing import Tuple, List
import PIL.ImageTk as ImageTK

class Sprite(object):
    def __init__(self) -> None:
        self.cache = {}
        self.tk_cache = {}
        self.raw = []


    def make_single(self, files: List[str], size: Tuple[int, int]) -> ImageTK.PhotoImage:
        key: str = ','.join(files)
        if key in self.tk_cache:
            return self.tk_cache[key]
        print(f'make_single {files}')
        images: List[ImageTK.PhotoImage] = list(map(lambda x: self._load_prim(x, size), files))
        car = images[0]
        cdr = images[1:]
        while len(cdr) > 0:
            car = Image.alpha_composite(car, cdr[0])
            cdr = cdr[1:]
        self.raw.append(car)
        tkImage = ImageTK.PhotoImage(car)
        self.tk_cache[key] = tkImage
        return tkImage

    def _load_prim(self, file: str, size: Tuple[int, int]) -> Image.Image:
        if file in self.cache:
            return self.cache[file]
        self.load(file, size)
        return self._load_prim(file, size)

    def load(self, file: str, size: Tuple[int, int]) -> ImageTK.PhotoImage:
        if file in self.tk_cache:
            return self.tk_cache[file]
        if file == '!assets/filter.png':
            image = Image.new('RGBA', size, (0, 0, 0, 128))
            self.raw.append(image)
            tkImage = ImageTK.PhotoImage(image)
            self.tk_cache[file] = tkImage
            self.cache[file] = image
            return tkImage
        else:
            print(f'load {file}')
            # 対象の画像を読み込み
            img = Image.open(file)
            self.raw.append(img)
            # リサイズ
            resizedImg = self._rgb_to_rgba(img.resize(size).convert('RGB'))
            self.raw.append(resizedImg)
            # Tkむけに変換
            tkImg: ImageTK.PhotoImage = ImageTK.PhotoImage(resizedImg)
            self.tk_cache[file] = tkImg
            self.cache[file] = resizedImg
            return tkImg

    def _rgb_to_rgba(self, img: Image.Image):
        trans = Image.new('RGBA', img.size, (0, 0, 0, 0))
        width = img.size[0]
        height = img.size[1]
        for x in range(width):
            for y in range(height):
                pixel = img.getpixel( (x, y) )
                if pixel[0] == 0 and pixel[1] == 0 and pixel[2] == 0:
                    continue
                trans.putpixel( (x, y), pixel )
        return trans

