from core import Core
from game_input import Button, InputBox, BoxManager
import pygame
import json


class Game:
    def __init__(self, screen, size):
        with open('config.json') as f:
            self.data = json.load(f)

        self.commands = self.data['commands']
        self.core = Core(**self.data['core'])
        self.size = size
        self.pause = False

        self.move_down = pygame.USEREVENT + 1
        pygame.time.set_timer(self.move_down, 400)

        self.screen = screen
        self.off_width = (screen.get_width() -
                          self.core.width * self.size) // 2
        self.offset = (
            (screen.get_width() - self.core.width * self.size) // 2,
            (screen.get_height() - self.core.height * self.size) // 2
        )

        self.playfield = pygame.Surface(
            (self.core.width*self.size, self.core.height*self.size), pygame.SRCALPHA)

        self.font = pygame.font.SysFont('Arial', 30)

        self.input_offset = InputBox('offset', (150, 200), 150, 50, 1, float)
        self.input_angle = InputBox('angle', (150, 300), 150, 50, 90, float)
        self.input_threshold = InputBox(
            'threshold', (150, 400), 150, 50, 1, float)
        self.box_manager = BoxManager(
            [self.input_offset, self.input_angle, self.input_threshold]
        )

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            if pygame.key.name(event.key) in self.commands:
                command = self.commands[pygame.key.name(event.key)]
            else:
                command = ''

            if self.pause and self.box_manager.selected:
                self.box_manager.add(pygame.key.name(event.key))
                if command == 'pause':
                    self.pause = False
                    self.selected = None

                return 'game'

            if self.core.end or self.pause:
                if command == 'pause':
                    self.pause = False
                elif command == 'quit':
                    return 'menu'
                elif command == 'retry':
                    return 'retry'
                return 'game'

            if command == 'left':
                self.core.move(-self.input_offset.get_value(), 0)
            elif command == 'right':
                self.core.move(self.input_offset.get_value(), 0)
            elif command == 'down':
                self.core.move(0, self.input_offset.get_value())
            elif command == 'cw':
                self.core.rotate(-self.input_angle.get_value())
            elif command == 'ccw':
                self.core.rotate(self.input_angle.get_value())
            elif command == 'cw2x':
                self.core.rotate(-self.input_angle.get_value()*2)
            elif command == 'ccw2x':
                self.core.rotate(self.input_angle.get_value()*2)
            elif command == 'harddrop':
                self.core.harddrop(self.input_offset.get_value())
            elif command == 'pause':
                self.pause = True

        elif event.type == pygame.MOUSEBUTTONDOWN and self.pause:
            self.box_manager.set_selected(event)

        elif event.type == self.move_down and self.pause == False:
            self.core.move(0, self.input_offset.get_value())

        if not self.pause:
            self.core.threshold = self.input_threshold.get_value()
            self.core.clear_line()

        return 'game'

    def render(self):
        def render_text(screen, text: str, x: int, y: int):
            text = self.font.render(
                text, True, (255, 255, 255))
            text_rect = text.get_rect(
                center=(self.screen.get_width() // 2, self.screen.get_height()//3))
            screen.blit(text, text_rect)

        self.screen.fill((0, 0, 0))
        self.input_offset.render(self.screen)
        self.input_angle.render(self.screen)
        self.input_threshold.render(self.screen)

        board = self.core.merge(self.core.mino)
        if board is None:
            board = self.core.board

        for row in board[:-1]:
            for cell in row[1:-1]:
                xy = [(i * self.size, j * self.size) for i, j in cell.xy]
                pygame.draw.polygon(self.playfield, cell.get_color(), xy)

        self.screen.blit(self.playfield, self.offset)

        if self.core.end:
            render_text(self.screen, 'Top out',
                        self.screen.get_width() // 2, self.screen.get_height()//3)

        if self.pause:
            render_text(self.screen, 'Pause',
                        self.screen.get_width() // 2, self.screen.get_height()//2)


class Menu:
    def __init__(self, screen):
        self.screen = screen

        width = screen.get_width()
        height = screen.get_height()

        self.button_start = Button(
            'Start', (width / 2, 100), 100, 50, pygame.Color('white')
        )
        self.button_exit = Button(
            'Exit', (width / 2, 300), 100, 50, pygame.Color('white')
        )

    def handle(self, event):
        if self.button_start.ispressed(event):
            return 'game'
        elif self.button_exit.ispressed(event):
            return 'quit'
        return 'menu'

    def render(self):
        self.screen.fill((0, 0, 0))
        self.button_start.render(self.screen)
        self.button_exit.render(self.screen)


class Render:
    def __init__(self, width: int, height: int):
        pygame.init()
        pygame.display.set_caption('Tetris')
        screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()

        current = Menu(screen)
        current_render = 'menu'

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                next_render = current.handle(event)
                if current_render != next_render:
                    if next_render == 'menu':
                        current = Menu(screen)
                    elif next_render == 'game':
                        current = Game(screen, 20)
                    elif next_render == 'retry':
                        current = Game(screen, 20)
                        next_render = 'game'
                    elif next_render == 'quit':
                        running = False
                current_render = next_render

            current.render()

            pygame.display.update()
            self.clock.tick(60)


if __name__ == '__main__':
    render = Render(800, 600)
    pygame.quit()
