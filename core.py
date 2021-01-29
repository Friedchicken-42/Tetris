from cell import Cell
from mino import Mino
import json
import random
import copy
from typing import List, Tuple, Union, Any
Coord = Tuple[int, int]


class Core:
    def __init__(self, width: int, height: int, filename: str, threshold: int = 1):
        self.board: List[List[Cell]] = []
        self.filename = filename
        self.width = width
        self.height = height
        self.threshold = 1
        self.end = False

        for i in range(height + 1):
            self.board.append([])
            for j in range(-1, width + 1):
                if j == -1 or j == width or i == height:
                    self.board[i].append(Cell(j, i, 1.0))
                else:
                    self.board[i].append(Cell(j, i, 0.0))

        self.queue = self.new_bag()
        self.mino: Mino = self.new_mino()

    def _load_mino(self, data) -> Mino:
        name: str = data['name']
        color: List[int] = data['color']
        blocks: List[Coord] = [(i, j) for i, j in data['blocks']]

        center = data['center'] if 'center' in data else None

        return Mino(name, blocks, color, center)

    def new_bag(self) -> List[Mino]:
        minos = []
        with open(self.filename) as f:
            data = json.load(f)
            for m in data:
                mino = self._load_mino(m)
                minos.append(mino)

        random.shuffle(minos)
        return minos

    def new_mino(self) -> Mino:
        mino = self.queue.pop(0)
        mino.move(self.width // 2 - 1, 0)
        if len(self.queue) < 6:
            self.queue.extend(self.new_bag())

        return mino

    def check(self, block, tmp_board):
        center = block.centroid
        x, y = int(center.x), int(center.y)
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                c_y, c_x = y + i, x + j
                if 0 <= c_y < len(tmp_board) and 0 <= c_x < len(tmp_board[0]):
                    tmp_board[c_y][c_x].intersect(block)

    def merge(self, mino: Mino) -> Union[List[List[Cell]], Any]:
        '''merge current board with mino
        if not return None'''
        def generate_set(block, _max: Tuple[int, int]):
            center = block.centroid
            x, y = int(center.x), int(center.y)
            s = set()
            for i in (-1, 0, 1):
                for j in (-1, 0, 1):
                    c_x, c_y = x + j, y + i
                    if -1 <= c_x < _max[0] - 1 and 0 <= c_y < _max[1]:
                        s.add((c_x, c_y))

            return s

        tmp_board = copy.deepcopy(self.board)
        cells = set()
        for b in mino.blocks:
            x = generate_set(b, (len(tmp_board[0]), len(tmp_board)))
            cells |= x

        for x, y in cells:
            for b in mino.blocks:
                tmp_board[y][x + 1].intersect(b, mino.color)
            if tmp_board[y][x + 1].area > 1:
                return None
        return tmp_board

    def place(self):
        board = self.merge(self.mino)
        if board:
            self.board = board
        else:
            self.end = True
        self.mino = self.new_mino()

    def move(self, xoff: int, yoff: int):
        tmp_mino = copy.deepcopy(self.mino)
        tmp_mino.move(xoff, yoff)
        if self.merge(tmp_mino):
            self.mino = tmp_mino
        elif yoff != 0:
            if self.mino.can_fall == False:
                self.place()
            else:
                self.mino.can_fall = False

    def rotate(self, angle: float):
        tmp_mino = copy.deepcopy(self.mino)
        tmp_mino.rotate(angle)
        if self.merge(tmp_mino):
            self.mino = tmp_mino

    def harddrop(self, yoff):
        while self.mino.can_fall:
            self.move(0, yoff)
        self.place()

    def clear_line(self) -> int:
        lines_cleared = 0

        for i, row in enumerate(self.board[:-1]):
            weight = sum([cell.area for cell in row[1:-1]])
            if weight >= self.width * self.threshold:
                while i != 0:
                    self.board[i] = self.board[i - 1]
                    for z in self.board[i]:
                        z.move(0, 1)
                    i -= 1

                self.board[0] = [
                    Cell(k, 0, 1)
                    if k == -1 or k == self.width else Cell(k, 0, 0)
                    for k in range(-1, self.width + 1)
                ]

        return lines_cleared

    def print_board(self):
        string = ''
        for i in self.board:
            for j in i:
                string += f'{j.area} '
            string += '\n'
        print(string)


if __name__ == '__main__':
    x = Core(10, 20, "pieces.json")
    print(x.mino)
    x.move(2, 5.5)
    x.place()

    string = ''
    for i in x.board:
        for j in i:
            string += f'{j.area} '
        string += '\n'
    print(string)
    string = ''
    for i in x.board:
        for j in i:
            string += '[' + ' '.join(f'{k:<3}' for k in j.color) + '] '
        string += '\n'
    print(string)
