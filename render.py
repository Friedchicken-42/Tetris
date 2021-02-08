from core import Core, load_mino
from renderable import Button, InputBox, BoxManager, RenderQueue, LineStatus
import pygame
import json

white = pygame.Color('white')


class Game:
    def __init__(self, screen, size):
        with open('config.json') as f:
            self.data = json.load(f)

        self.commands = self.data['commands']
        self.extra = self.data['extra']
        print(self.extra)
        self.core = Core(**self.data['core'])
        self.size = size
        self.pause = False

        self.arr = 3
        self.das = 10
        self.currend_arr = 0
        self.current_das = 0

        self.move_down = pygame.USEREVENT + 1
        self.arr_event = pygame.event.Event(pygame.USEREVENT, arrt1='arr')
        self.x = 0
        pygame.time.set_timer(self.move_down, 400)

        self.screen = screen

        self.offset = (
            (screen.get_width() - self.core.width * self.size) // 2,
            (screen.get_height() - self.core.height * self.size) // 2
        )

        self.queue = RenderQueue(
            self.core.queue, self.size,
            (self.offset[0] + self.core.width * self.size + 10, 100)
        )
        if self.extra['line status']:
            self.linestatus = LineStatus(
                self.core.board,
                self.size,
                (self.offset[0] - self.size - 10, self.offset[1])
            )

        self.playfield = pygame.Surface(
            (self.core.width*self.size, self.core.height*self.size), pygame.SRCALPHA)

        self.font = pygame.font.SysFont('Arial', 30)

        self.input_offset = InputBox('offset', (150, 200), 150, 50, 1, float)
        self.input_angle = InputBox('angle', (150, 300), 150, 50, 90, float)
        self.input_threshold = InputBox(
            'threshold', (150, 400), 150, 50, 100, float)
        self.box_manager = BoxManager(
            [self.input_offset, self.input_angle, self.input_threshold]
        )
        self.movement = ''

    def handle(self, event):
        if 'key' in dir(event) and pygame.key.name(event.key) in self.commands:
            command = self.commands[pygame.key.name(event.key)]
        else:
            command = ''
        if event.type == pygame.KEYUP:
            if command == 'left':
                self.movement = ''
                self.current_das = 0
            elif command == 'right':
                self.movement = ''
                self.current_das = 0
        elif event.type == pygame.KEYDOWN:
            if self.pause and self.box_manager.selected is not None:
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
                self.movement = 'left'
                self.core.move(-self.input_offset.get_value(), 0)
                self.current_das = True
            elif command == 'right':
                self.movement = 'right'
                self.core.move(self.input_offset.get_value(), 0)
                self.current_das = True
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

        elif event == self.arr_event:
            if self.movement == 'left':
                self.core.move(-self.input_offset.get_value(), 0)
            elif self.movement == 'right':
                self.core.move(self.input_offset.get_value(), 0)
        elif event.type == pygame.MOUSEBUTTONDOWN and self.pause:
            self.box_manager.set_selected()

        elif event.type == self.move_down and (self.pause == False and self.core.end == False):
            self.core.move(0, self.input_offset.get_value())

        if not self.pause:
            self.core.threshold = self.input_threshold.get_value()
            cleared = self.core.clear_line()
            self.core.calculate_points(cleared)

        return 'game'

    def render(self):
        def render_text(screen, text: str, x: int, y: int):
            text = self.font.render(
                text, True, (255, 255, 255))
            text_rect = text.get_rect(center=(x, y))
            screen.blit(text, text_rect)

        self.screen.fill((0, 0, 0))
        self.box_manager.render(self.screen)
        self.queue.render(self.screen)

        if self.current_das:
            self.current_das += 1
        if self.current_das > self.das:
            self.currend_arr += 1
        if self.currend_arr > self.arr:
            self.currend_arr = 0
            pygame.event.post(self.arr_event)

        board = self.core.merge(self.core.mino)
        if board is None:
            board = self.core.board

        for row in board[:-1]:
            for cell in row[1:-1]:
                xy = [(i * self.size, j * self.size) for i, j in cell.xy]
                pygame.draw.polygon(self.playfield, cell.get_color(), xy)

        if self.extra['line status']:
            self.linestatus.render(self.screen, self.core.board)

        self.screen.blit(self.playfield, self.offset)

        render_text(self.screen,
                    f'{int(self.core.points):0>10}',
                    self.screen.get_width() // 2, self.offset[1] - self.core.height // 2 - 10)

        if self.core.end:
            render_text(self.screen, 'Top out',
                        self.screen.get_width() // 2, self.screen.get_height()//3)

        if self.pause:
            render_text(self.screen, 'Pause',
                        self.screen.get_width() // 2, self.screen.get_height()//2)


class Option:
    def __init__(self, screen):
        self.screen = screen

        with open('config.json') as f:
            self.data = json.load(f)

        center = (
            self.screen.get_width() // 2,
            self.screen.get_height() // 2
        )

        self.input_width = InputBox(
            'width', (center[0], 50), 400, 50, self.data['core']['width'], int)
        self.input_height = InputBox(
            'height', (center[0], 100), 400, 50, self.data['core']['height'], int)
        self.input_file = InputBox(
            'file', (center[0], 150), 400, 50, self.data['core']['filename'], str)

        self.commands = []
        for i, (key, command) in enumerate(self.data['commands'].items()):
            if i % 2 == 0:
                pos = (center[0] - 100, 200 + i // 2 * 50)
            else:
                pos = (center[0] + 100, 200 + i // 2 * 50)
            self.commands.append(InputBox(command, pos, 200, 50, key, str, 1))
            height = 200 + i // 2 * 50 + 50

        self.extra = []
        for i, (key, value) in enumerate(self.data['extra'].items()):
            if i % 2 == 0:
                pos = (center[0] - 100, height + i // 2 * 50)
            else:
                pos = (center[0] + 100, height + i // 2 * 50)
            self.extra.append(
                InputBox(str(key), pos, 200, 50, str(value), int, 1))
            height = height + i // 2 * 50 + 50

        self.box_manager = BoxManager(
            [self.input_width, self.input_height, self.input_file, *self.commands, *self.extra])

        self.button_confirm = Button(
            'Confirm', (center[0] - 100, height), 150, 50, white)
        self.button_back = Button(
            'Back', (center[0] + 100, height), 150, 50, white)

    def load_config(self):
        data = {
            'core': {
                'width': self.input_width.get_value(),
                'height': self.input_height.get_value(),
                'filename': self.input_file.get_value()
            },
            'commands': {
                item.get_value(): item.name for item in self.commands
            },
            'extra': {
                item.name: item.get_value() for item in self.extra
            }
        }
        with open('config.json', 'w') as f:
            json.dump(data, f)

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            self.box_manager.add(pygame.key.name(event.key))
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.box_manager.set_selected()

        if self.button_confirm.ispressed(event):
            self.load_config()
            return 'menu'
        elif self.button_back.ispressed(event):
            return 'menu'
        return 'option'

    def render(self):
        self.screen.fill((0, 0, 0))
        self.box_manager.render(self.screen)
        self.button_confirm.render(self.screen)
        self.button_back.render(self.screen)


class Edit:
    def __init__(self, screen):
        self.screen = screen

        width = self.screen.get_width()
        height = self.screen.get_height()

        self.input_file = InputBox(
            'filename', (width // 2 - 150, 100), 300, 50, 'pieces', str)
        self.pieces = []

        self.button_load = Button(
            'Load', (width // 2 + 100, 100), 100, 50, white)
        self.button_new = Button(
            'New', (width // 2 + 225, 100), 100, 50, white)

        self.input_r = InputBox(
            'red', (100, height // 2 - 100), 150, 50, 0, int)
        self.input_g = InputBox(
            'green', (100, height // 2 - 50), 150, 50, 0, int)
        self.input_b = InputBox(
            'blue', (100, height // 2), 150, 50, 0, int)
        self.input_density = InputBox(
            'density', (100, height // 2 + 50), 150, 50, 1, float)
        self.input_name = InputBox(
            'name', (100, height // 2 + 100), 150, 50, '', str)

        size = 30
        self.buttons = 6
        offset = size * self.buttons // 2

        self.button_matrix = [[
            Button('',
                   (width // 2 - offset + j * size,
                    height // 2 - offset + i * size),
                   size, size, (20, 20, 20))
            for i in range(self.buttons)] for j in range(self.buttons)]

        self.density_matrix = [
            [0 for _ in range(self.buttons)] for _ in range(self.buttons)]

        self._load()
        self.queue = RenderQueue(
            self.pieces, 20, (width // 2 + 150, 150), len(self.pieces))

        self.button_back = Button('Back', (100, height - 100), 100, 50, white)
        self.button_confirm = Button(
            'Confirm', (250, height - 100), 100, 50, white)
        self.button_add = Button(
            'Add', (width - 100, height - 100), 100, 50, white)
        self.button_save = Button(
            'Save', (width - 250, height - 100), 100, 50, white)

        self.box_manager = BoxManager(
            [self.input_file, self.input_r, self.input_g, self.input_b, self.input_density, self.input_name])

    def _load(self):
        try:
            with open(self.input_file.get_value() + '.json', 'r') as f:
                self.data = json.load(f)

            self.pieces = [load_mino(m) for m in self.data]
        except FileNotFoundError:
            self.pieces = []

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            self.box_manager.add(pygame.key.name(event.key))
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.box_manager.set_selected()
            if self.queue.set_selected():
                self.density_matrix = [
                    [0 for _ in range(self.buttons)] for _ in range(self.buttons)]
                mino = self.data[self.queue.selected]
                self.input_r.value = mino['color'][0]
                self.input_g.value = mino['color'][1]
                self.input_b.value = mino['color'][2]
                for i, j, d in mino['blocks']:
                    self.density_matrix[i][j] = d
                self.input_name.value = mino['name']

            if self.button_back.ispressed(event):
                return 'menu'
            elif self.button_load.ispressed(event):
                self._load()
                self.queue.queue = self.pieces
                self.queue.lenght = len(self.pieces)
            elif self.button_save.ispressed(event):
                new = {
                    'name': self.input_name.get_value(),
                    'color': [
                        min(self.input_r.get_value(), 255),
                        min(self.input_g.get_value(), 255),
                        min(self.input_b.get_value(), 255)
                    ],
                    'blocks': [(i, j, d) for i, row in enumerate(self.density_matrix) for j, d in enumerate(row) if d != 0]
                }
                self.data[self.queue.selected] = new
                self.pieces[self.queue.selected] = load_mino(new)
                self.queue.queue = self.pieces
            elif self.button_confirm.ispressed(event):
                with open(self.input_file.get_value() + '.json', 'w') as f:
                    json.dump(self.data, f)
            elif self.button_add.ispressed(event):
                self.queue.set_lenght(self.queue.lenght + 1)
                empty = {'name': '', 'color': [0, 0, 0], 'blocks': []}
                self.data.append(empty)
                self.pieces.append(load_mino(empty))
                self.queue.queue = self.pieces
            elif self.button_new.ispressed(event):
                self.input_file.value = ''
                self.queue.queue = []
                self.data = []
                self.pieces = []
                self.queue.set_lenght(0)
            for i, row in enumerate(self.button_matrix):
                for j, b in enumerate(row):
                    if b.ispressed(event):
                        self.density_matrix[i][j] = \
                            self.input_density.get_value()

        return 'edit'

    def render(self):
        self.screen.fill((0, 0, 0))
        self.box_manager.render(self.screen)
        self.button_load.render(self.screen)
        self.button_new.render(self.screen)
        for i, row in enumerate(self.density_matrix):
            for j, density in enumerate(row):
                if density == 0:
                    color = [20, 20, 20]
                else:
                    color = [
                        min(self.input_r.get_value(), 255),
                        min(self.input_g.get_value(), 255),
                        min(self.input_b.get_value(), 255),
                        min(density * 255, 255)
                    ]
                self.button_matrix[i][j].set_color(color)
                self.button_matrix[i][j].render(self.screen)
        self.button_back.render(self.screen)
        self.button_confirm.render(self.screen)
        self.button_add.render(self.screen)
        self.button_save.render(self.screen)
        self.queue.render(self.screen)


class Menu:
    def __init__(self, screen):
        self.screen = screen

        width = screen.get_width()
        height = screen.get_height()

        self.button_start = Button(
            'Start', (width / 2, 100), 100, 50, white
        )
        self.button_option = Button(
            'Option', (width / 2, 200), 100, 50, white
        )
        self.button_edit = Button(
            'Edit', (width / 2, 300), 100, 50, white
        )
        self.button_exit = Button(
            'Exit', (width / 2, 400), 100, 50, white
        )

    def handle(self, event):
        if self.button_start.ispressed(event):
            return 'game'
        elif self.button_option.ispressed(event):
            return 'option'
        elif self.button_edit.ispressed(event):
            return 'edit'
        elif self.button_exit.ispressed(event):
            return 'quit'
        return 'menu'

    def render(self):
        self.screen.fill((0, 0, 0))
        self.button_start.render(self.screen)
        self.button_option.render(self.screen)
        self.button_edit.render(self.screen)
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
                    elif next_render == 'option':
                        current = Option(screen)
                    elif next_render == 'edit':
                        current = Edit(screen)
                    elif next_render == 'quit':
                        running = False
                current_render = next_render

            current.render()

            pygame.display.update()
            self.clock.tick(30)


if __name__ == '__main__':
    render = Render(800, 600)
    pygame.quit()
