from collections import deque
from random import randrange
from threading import Thread
from time import sleep

from kivy.app import App
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.utils import get_color_from_hex

MOVE_UP = (-1, 0)
MOVE_RIGHT = (0, 1)
MOVE_DOWN = (1, 0)
MOVE_LEFT = (0, -1)

# Speeds of the game depending of the level
SPEEDS = {
            1:      0.40,
            2:      0.35,
            3:      0.30,
            4:      0.25,
            5:      0.20,
            6:      0.15,
            7:      0.10,
            8:      0.08,
            9:      0.06,
            10:     0.04,
            11:     0.02,
            12:     0.01,
        }

class Cell(Label):
    def __init__(self, **kwargs):
        self.row = kwargs.pop('row')
        self.col = kwargs.pop('col')
        self._value = None                      # State of the cell

        super(Cell, self).__init__(**kwargs)

        self.color = (0, 0, 0, 1)

        # Add instructions rendered before
        with self.canvas.before:
            # Set the background color, size and position
            self.bg_color = Color(.5, .5, 1)
            self.rectangle = Rectangle(size=self.size, pos=self.pos)

        # Update rectangle position and size
        self.bind(pos=self.update_rect, size=self.update_rect)

        # Cell colors (one per possible state)
        self.colors = {
            0: get_color_from_hex('#df9000'), # Wall, orange
            1: get_color_from_hex('#00ff00'), # Food, green
            2: get_color_from_hex('#0000ff'), # Snake, blue
        }

    def update_rect(self, intance, value):
        self.rectangle.pos = self.pos
        self.rectangle.size = self.size

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

        if value is None:
            self.bg_color.rgb = get_color_from_hex('#ffffff')
            return

        self.bg_color.rgb = self.colors[value]

    def __repr__(self):
        return '<Cell object in postion ({}, {}) value={}>'.format(self.row,
            self.col, self.value)
    

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)

        self.grid = list()
        self.level = 1
        self.ids.level_label.text = 'Level 1'

        # Generate an empty 21x21 grid
        for row in range(21):
            self.grid.append([])

            for col in range(21):
                cell = Cell(row=row, col=col)

                # Add an empty cell to the actual position
                self.ids.grid_layout.add_widget(cell)
                self.grid[row].append(cell)

                if row in [0, 20] or col in [0, 20]:
                    self.grid[row][col].value = 0

        self.new_game()

    def new_game(self):
        self.playing = False
        self.pushed = False

        self.reset()
        self.spawn_snake()
        self.spawn_food()

        sleep(0.5)
        self.playing = True

        thread = Thread(target=self.play).start()

    def reset(self):
        for row in range(1, 20):
            for col in range(1, 20):
                self.grid[row][col].value = None
                self.grid[row][col].text = ''

        self.snake = deque()
        self.direction = MOVE_RIGHT

    def game_over(self):
        self.reset()

        for i, letter in enumerate([
            ('G','O'),
            ('A','V'),
            ('M','E'),
            ('E','R')
        ]):
            self.grid[9][i+9].text = letter[0]
            self.grid[10][i+9].text = letter[1]

    def spawn_snake(self):
        row = 10

        for col in [10, 11]:
            self.grid[row][col].value = 2
            self.snake.append((row, col))

    def spawn_food(self):
        has_value = True

        while has_value:
            coord_x = randrange(1, 20)
            coord_y = randrange(1, 20)
            has_value = self.grid[coord_x][coord_y].value

            if has_value is None:
                self.grid[coord_x][coord_y].value = 1                        
    
    def play(self):
        while self.playing:

            sleep(SPEEDS[self.level])

            self.pushed = False

            head_x, head_y = self.snake[-1][0], self.snake[-1][1]
            new_x, new_y = head_x + self.direction[0], head_y + self.direction[1]

            state = self.check_next(new_x, new_y)

            if state == -1:
                self.playing = False
                self.game_over()
            else:
                self.snake.append((new_x, new_y))

                if state == 0:
                    tail_x, tail_y = self.snake.popleft()

                    self.grid[tail_x][tail_y].value = None
                
                self.grid[new_x][new_y].value = 2

    def check_next(self, x, y):
        if self.grid[x][y].value in [0, 2]:
            return -1
        elif self.grid[x][y].value == 1:
            self.spawn_food()
            return 1
        return 0

    def increase_level(self):
        if self.level < 12:
            self.level += 1
            self.ids.level_label.text = 'Level ' + str(self.level)

    def decrease_level(self):
        if self.level > 1:
            self.level -= 1
            self.ids.level_label.text = 'Level ' + str(self.level)

class MainApp(App):
    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)

        Window.bind(on_key_down=self.on_key_down)

    def build(self):
        self.game_screen = Factory.GameScreen(name='snake')
        self.game_screen.app = self

        sm = ScreenManager()
        sm.add_widget(self.game_screen)

        return sm

    def on_key_down(self, window, key, *args):
        if self.game_screen.pushed is False:
            if key == 273:      # key:  UP
                if self.game_screen.direction != MOVE_DOWN:
                    self.game_screen.direction = MOVE_UP
                    self.game_screen.pushed = True
            elif key == 275:    # key:  RIGHT
                if self.game_screen.direction != MOVE_LEFT:
                    self.game_screen.direction = MOVE_RIGHT
                    self.game_screen.pushed = True
            elif key == 274:    # key:  DOWN
                if self.game_screen.direction != MOVE_UP:
                    self.game_screen.direction = MOVE_DOWN
                    self.game_screen.pushed = True
            elif key == 276:    # key:  LEFT
                if self.game_screen.direction != MOVE_RIGHT:
                    self.game_screen.direction = MOVE_LEFT
                    self.game_screen.pushed = True

if __name__ == '__main__':
    MainApp().run()
