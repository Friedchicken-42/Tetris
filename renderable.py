import pygame
from cell import Cell
from typing import Tuple, List
Coord = Tuple[int, int]


class Input:
    def __init__(self, name: str, center: Coord, width: int, height: int, color: List[int], text_color: List[int]):
        self.name = name
        self.center = center
        self.width = width
        self.height = height
        self.area = pygame.Surface((width, height), pygame.SRCALPHA)
        self.area.fill(color)
        self.position = (
            center[0] - width / 2, center[1] - height / 2
        )
        self.font = pygame.font.SysFont('Arial', 20)
        self.text_color = text_color
        self.text = self.font.render(name, True, text_color)

    def set_color(self, color: List[int]):
        self.area.fill(color)
        self.text = self.font.render(self.name, True, self.text_color)

    def render(self, screen):
        self.screen_area = screen.blit(self.area, self.position)


class Button(Input):
    def __init__(self, name: str, center: Coord, width: int, height: int, color):
        super().__init__(name, center, width, height, color, (0, 0, 0))

        text_pos = (
            width / 2 - self.text.get_width() / 2,
            height / 2 - self.text.get_height() / 2,
        )
        self.area.blit(self.text, text_pos)

    def ispressed(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.screen_area.collidepoint(pygame.mouse.get_pos()):
                    return True

        return False


class InputBox(Input):
    def __init__(self, name: str, center: Coord, width: int, height: int, value, conversion: type, lenght: int = 0):
        super().__init__(name, center, width, height, (20, 20, 20), (255, 255, 255))
        self.value = str(value)
        self.conversion = conversion
        self.lenght = lenght

        text_pos = (
            10,
            height / 2 - self.text.get_height() / 2
        )

        self.input_box = pygame.Surface(
            (width - self.text.get_width() - 20, height // 2)
        )
        self.input_box.fill((255, 255, 255))
        self.box_pos = (
            text_pos[0] + self.text.get_width() + 5,
            text_pos[1]
        )

        self.area.blit(self.text, text_pos)
        self.area.blit(self.input_box, self.box_pos)

    def delete(self):
        if len(self.value) > 0:
            self.value = self.value[:-1]

    def add(self, char):
        if char in {'return'}:
            pass
        elif char == 'backspace':
            self.delete()
        else:
            if self.lenght != 0 and len(self.value) >= self.lenght:
                self.delete()
            self.value += char

    def get_value(self):
        try:
            return self.conversion(self.value)
        except ValueError:
            return 0

    def render(self, screen):
        self.input_box.fill((255, 255, 255))
        value = self.font.render(str(self.value), True, (0, 0, 0))
        self.input_box.blit(value, (5, 0))
        self.area.blit(self.input_box, self.box_pos)

        self.screen_area = screen.blit(self.area, self.position)


class BoxManager:
    def __init__(self, input_boxes: List[InputBox]):
        self.boxes = input_boxes
        self.selected = None

    def set_selected(self):
        self.selected = None
        for i, b in enumerate(self.boxes):
            if b.screen_area.collidepoint(pygame.mouse.get_pos()):
                self.selected = i
                b.value = ''
                return True
        return False

    def add(self, char):
        if self.selected is not None:
            self.boxes[self.selected].add(char)

    def render(self, screen):
        for b in self.boxes:
            b.render(screen)


class LineStatus:
    def __init__(self, board: List, size: int, pos: Coord):
        self.size = size
        self.pos = pos
        self.font = pygame.font.SysFont('Arial', 15)
        self.weights = [
            pygame.Surface((size, size)) for _ in board[:-1]
        ]

    def render(self, screen, board):
        for i, row in enumerate(board[:-1]):
            self.weights[i].fill((0, 0, 0))
            weight = sum([c.area for c in row[1:-1]])
            text = self.font.render(
                str(round(weight, 1)), True, (255, 255, 255))
            self.weights[i].blit(text, (0, 0))
            screen.blit(
                self.weights[i],
                (self.pos[0], self.pos[1] + i * self.size)
            )


class BoxQueue:
    def __init__(self, box_size: int, size: int, pos: Coord):
        self.box_size = box_size
        self.size = size
        self.pos = pos
        self.box = pygame.Surface(
            (self.box_size, self.box_size), pygame.SRCALPHA)
        self.screen_area = None

    def render(self, screen, mino):
        self.box.fill((20, 20, 20))
        for block in mino.blocks:
            color = (20, 20, 20) if block.density == 0 else \
                (*mino.color, block.density * 255)
            pygame.draw.polygon(
                self.box,
                color,
                [(i * self.size, j * self.size)
                 for i, j in block.box.exterior.coords]
            )
        self.screen_area = screen.blit(self.box, self.pos)


class RenderQueue:
    def __init__(self, queue: List, size: int, pos: Coord, lenght: int = 5):
        self.queue = queue
        self.pos = pos
        self.lenght = lenght
        self.size = size / 2
        self.box_size = self.size * 4
        self.boxes = [
            BoxQueue(self.box_size, self.size,
                     (self.pos[0], self.pos[1] + i * (self.box_size + 1)))
            for i in range(self.lenght)
        ]
        self.selected = None

    def set_selected(self):
        for i, b in enumerate(self.boxes):
            if b.screen_area.collidepoint(pygame.mouse.get_pos()):
                self.selected = i
                return True
        return False

    def set_lenght(self, lenght: int):
        self.lenght = lenght
        self.boxes = [
            BoxQueue(self.box_size, self.size,
                     (self.pos[0], self.pos[1] + i * (self.box_size + 1)))
            for i in range(self.lenght)
        ]

    def render(self, screen):
        for i, mino in enumerate(self.queue[:self.lenght]):
            self.boxes[i].render(screen, mino)
