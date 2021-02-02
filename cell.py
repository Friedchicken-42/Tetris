from shapely.geometry import box
from shapely.affinity import translate
from typing import List


class Cell:
    def __init__(self, x: int, y: int, area: float = 0.0):
        self.box = box(x, y, x + 1, y + 1)
        self.area = area
        self.color = [20, 20, 20]

    def intersect(self, block: box, color: List[int]):
        x = block.box.intersection(self.box).area * \
            block.density / self.box.area
        self.area += round(x, 1)

        if self.area != 0:
            if self.color == [20, 20, 20]:
                self.color = color
            elif x > 0.1:
                self.blend(color)
        else:
            self.color = [20, 20, 20]

    def move(self, xoff: int, yoff: int):
        self.box = translate(self.box, xoff=xoff, yoff=yoff)

    def blend(self, c: List[int]):
        color = [0, 0, 0]
        for i in range(3):
            color[i] = self.color[i] ** 2 + c[i] ** 2
            color[i] /= 2
            color[i] = int(color[i]**(1 / 2))

        self.color = color

    def get_color(self):
        if self.area == 0:
            return self.color
        else:
            return [*self.color, self.area * 255]

    @property
    def xy(self):
        return list(self.box.exterior.coords)

    def __repr__(self) -> str:
        return str(self.area)
