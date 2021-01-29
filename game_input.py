import pygame
from typing import Tuple, List
Coord = Tuple[int, int]


class Input:
    def __init__(self, name: str, center: Coord, width: int, height: int, color: List[int], text_color: List[int]):
        self.name = name
        self.center = center
        self.width = width
        self.height = height
        self.area = pygame.Surface((width, height))
        self.area.fill(color)
        self.position = (
            center[0] - width / 2, center[1] - height / 2
        )
        self.font = pygame.font.SysFont('Arial', 20)
        self.text = self.font.render(name, True, text_color)

    def render(self, screen):
        self.screen_area = screen.blit(self.area, self.position)


class Button(Input):
    def __init__(self, name: str, center: Coord, width: int, height: int, color: List[int]):
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
    def __init__(self, name: str, center: Coord, width: int, height: int, value, conversion: type):
        super().__init__(name, center, width, height, (20, 20, 20), (255, 255, 255))
        self.value = str(value)
        self.conversion = conversion

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

    def get_value(self):
        if self.value:
            return self.conversion(self.value)
        return 0

    def render(self, screen):
        self.input_box.fill((255, 255, 255))
        value = self.font.render(str(self.value), False, (0, 0, 0))
        self.input_box.blit(value, (5, 0))
        self.area.blit(self.input_box, self.box_pos)

        self.screen_area = screen.blit(self.area, self.position)


class BoxManager:
    def __init__(self, input_boxes: List[InputBox]):
        self.boxes = input_boxes
        self.selected = None

    def set_selected(self, event):
        self.selected = None
        for b in self.boxes:
            if b.screen_area.collidepoint(pygame.mouse.get_pos()):
                self.selected = b
                b.value = ''

    def delete(self):
        if len(self.selected.value) > 0:
            self.selected.value = self.selected.value[:-1]

    def add(self, char):
        if char in {'escape', 'return'}:
            pass
        elif char == 'backspace':
            self.delete()
        else:
            self.selected.value += char
