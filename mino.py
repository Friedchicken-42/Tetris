from shapely.geometry import box
from shapely.ops import unary_union
from shapely.affinity import rotate, translate
from typing import List, Tuple
Coord = Tuple[int, int]


class Mino:
    def __init__(self, name: str, coords: List[Coord], color: List[int], center: Coord = None):
        self.name = name
        self.blocks = [box(i, j, i + 1, j + 1) for i, j in coords]
        self.color = color
        self.can_fall = True

        if center:
            x, y = center
            self.center = box(x, y, x + 1, y + 1).centroid
        else:
            self.center = unary_union(self.blocks).centroid

    def move(self, xoff: int, yoff: int):
        for i, b in enumerate(self.blocks):
            self.blocks[i] = translate(b, xoff=xoff, yoff=yoff)
        self.center = translate(self.center, xoff=xoff, yoff=yoff)

    def rotate(self, angle: float):
        for i, b in enumerate(self.blocks):
            self.blocks[i] = rotate(b, angle, origin=self.center)

    def __repr__(self) -> str:
        return self.name

    def _print(self) -> str:
        return ' '.join(f'[{b.centroid.x} {b.centroid.y}]' for b in self.blocks)


if __name__ == '__main__':
    x = Mino('I', [(0, 0), (0, 1), (0, 2), (0, 3)],
             [255, 255, 255], (0, 0))
    print(x)
    x.rotate(-90)
    print(x)
