from shapely.geometry import box
from shapely.ops import unary_union
from shapely.affinity import rotate, translate
from typing import List, Tuple
Coord = Tuple[int, int]


class Block:
    def __init__(self, minx: int, miny: int, maxx: int, maxy: int, density: float):
        self.box = box(minx, miny, maxx, maxy)
        self.density = density


class Mino:
    def __init__(self, name: str, coords: List[Tuple[int, int, float]], color: List[int], center: Coord = None):
        self.name = name
        self.blocks = [Block(i, j, i + 1, j + 1, d) for i, j, d in coords]
        self.color = color
        self.can_fall = True

        if center:
            x, y = center
            self.center = box(x, y, x + 1, y + 1).centroid
        else:
            self.center = unary_union([b.box for b in self.blocks]).centroid

    def move(self, xoff: int, yoff: int):
        for i, b in enumerate(self.blocks):
            self.blocks[i].box = translate(b.box, xoff=xoff, yoff=yoff)
        self.center = translate(self.center, xoff=xoff, yoff=yoff)

    def rotate(self, angle: float):
        for i, b in enumerate(self.blocks):
            self.blocks[i].box = rotate(b.box, angle, origin=self.center)

    def __repr__(self) -> str:
        return self.name


if __name__ == '__main__':
    x = Mino('I', [(0, 0, 1), (0, 1, 1), (0, 2, 1), (0, 3, 1)],
             [255, 255, 255], (0, 0))
    print(x)
    x.rotate(-90)
    print(x)
