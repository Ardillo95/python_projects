from threading import Thread
from random import choice
from time import sleep

from kivy.app import App
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.utils import get_color_from_hex

# Sides of a figure
RIGHT = (0, 1)
DOWN = (1, 0)
LEFT = (0, -1)

# Default center position for figure spawning
CENTER = (0, 4)

# Scores
SCORES = {
    1: 40,
    2: 100,
    3: 300,
    4: 1200,
}

# Speed dependng on the level
SPEEDS = {
    1: 1,
    2: 0.9,
    3: 0.8,
    4: 0.7,
    5: 0.6,
    6: 0.5,
    7: 0.4,
    8: 0.3,
    9: 0.2,
}

# Coordinates of each posible rotation for each figure
I = (
    0,                                  # color
    ((0, 0), (1, 0), (2, 0), (3, 0)),   # Standar position
    ((0, 0), (0, 1), (0, 2), (0, 3)),   # clockwise rotation
    ((0, 0), (1, 0), (2, 0), (3, 0)),   # inverse rotation
    ((0, 0), (0, 1), (0, 2), (0, 3)),   # counter-clockwise position
)

J = (
    1,
    ((0, 1), (1, 1), (2, 0), (2, 1)),
    ((1, 0), (2, 0), (2, 1), (2, 2)),
    ((0, 1), (0, 2), (1, 1), (2, 1)),
    ((1, 0), (1, 1), (1, 2), (2, 2)),
)

L = (
    2,
    ((0, 1), (1, 1), (2, 1), (2, 2)),
    ((1, 0), (1, 1), (1, 2), (2, 0)),
    ((0, 0), (0, 1), (1, 1), (2, 1)),
    ((1, 2), (2, 0), (2, 1), (2, 2)),
)

O = (
    3,
    ((0, 0), (0, 1), (1, 0), (1, 1)),
    ((0, 0), (0, 1), (1, 0), (1, 1)),
    ((0, 0), (0, 1), (1, 0), (1, 1)),
    ((0, 0), (0, 1), (1, 0), (1, 1)),
)

S = (
    4,
    ((0, 0), (1, 0), (1, 1), (2, 1)),
    ((0, 1), (0, 2), (1, 0), (1, 1)),
    ((0, 0), (1, 0), (1, 1), (2, 1)),
    ((0, 1), (0, 2), (1, 0), (1, 1)),
)

T = (
    5,
    ((0, 0), (0, 1), (0, 2), (1, 1)),
    ((0, 1), (1, 0), (1, 1), (2, 1)),
    ((0, 1), (1, 0), (1, 1), (1, 2)),
    ((0, 0), (1, 0), (1, 1), (2, 0)),
)

Z = (
    6,
    ((0, 0), (0, 1), (1, 1), (1, 2)),
    ((0, 1), (1, 1), (1, 0), (2, 0)),
    ((0, 0), (0, 1), (1, 1), (1, 2)),
    ((0, 1), (1, 1), (1, 0), (2, 0)),
)

# Set of all possible figures
FIGURES = (I, J, L, O, S, T, Z)


class Cell(Label):
    """
    This class represents the blocks of the game.

    Basically, each block contains a value (color), a cell coordinate ((0,0),
    (2, 3)) some properties that decides color, text to represent (if any).
    """
    def __init__(self, **kwargs):
        self.row = kwargs.pop('row')
        self.col = kwargs.pop('col')
        self._value = None

        super(Cell, self).__init__(**kwargs)

        # Color of the font: black
        self.color = (0, 0, 0, 1)

        # Add instructions rendered before
        with self.canvas.before:
            # Set the background color, size and position
            self.bg_color = Color(.5, .5, 1)
            self.rectangle = Rectangle(size=self.size, pos=self.pos)

        # Update rectangle position and size
        self.bind(pos=self.update_rect, size=self.update_rect)

        # Dictionary with all possible color each cell can have, one per figure
        self.colors = {
            0: get_color_from_hex('#00FFFF'),  # I,      cyan
            1: get_color_from_hex('#0000FF'),  # J,      blue
            2: get_color_from_hex('#FFA500'),  # L,      orange
            3: get_color_from_hex('#FFFF00'),  # O,      yellow
            4: get_color_from_hex('#00FF00'),  # S,      lime
            5: get_color_from_hex('#800080'),  # T,      purple
            6: get_color_from_hex('#FF0000'),  # Z,      red
        }

    def update_rect(self, instance, value):
        self.rectangle.pos = self.pos
        self.rectangle.size = self.size

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

        # Default color (empty cell)
        if value is None:
            self.bg_color.rgb = get_color_from_hex('#ffffff')
            return

        # Cell is part of a figure, draw the cell with the color of the figure.
        self.bg_color.rgb = self.colors[value]

    def __repr__(self):
        return '<Cell object in position ({}, {}) value={}>'.format(self.row,
                                                                    self.col,
                                                                    self.value)


class GameScreen(Screen):
    """
    GameScreen, determines the area of view of the application.

    There is only one screen, which is composed by the 10x20 grid and the
    background rectangle.
    """
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)

        self.grid = list()
        self.grid_aux = list()

        # Generate an empty 10x20 grid and an empty 4x4 grid
        for row in range(20):
            self.grid.append([])
            # For the 4x4 grid
            if row < 4:
                self.grid_aux.append([])

            for col in range(10):
                cell = Cell(row=row, col=col)

                # Add an empty cell to the actual position, 10x20 grid
                self.ids.grid_layout.add_widget(cell)
                self.grid[row].append(cell)

                # Same for the 4x4 grid
                if row < 4 and col < 4:
                    cell_aux = Cell(row=row, col=col)

                    self.ids.grid_layout_aux.add_widget(cell_aux)
                    self.grid_aux[row].append(cell_aux)

        self.new_game()

    def new_game(self):
        """
        Beginning of the game after launching the application or after
        pressing the New Game buttom
        """
        self.reset()
        self.playing = False
        sleep(1)
        self.playing = True
        Thread(target=self.play).start()

    def game_over(self):
        """Clean the grid and show the text 'GAME OVER' in the auxiliar grid"""
        self.reset()

        # Draw 'GAME OVER' in the auxiliar grid
        for i, letter in enumerate([
            ('G', 'O'),
            ('A', 'V'),
            ('M', 'E'),
            ('E', 'R')
        ]):
            self.grid_aux[1][i].text = letter[0]
            self.grid_aux[2][i].text = letter[1]

    def reset(self):
        """ Reset the value of all cells to None """
        for row in range(20):
            for col in range(10):
                self.grid[row][col].value = None

        for row in range(4):
            for col in range(4):
                self.grid_aux[row][col].value = None
                self.grid_aux[row][col].text = ''

        self.lines_counter = 0
        self.score = 0
        self.ids.score_label.text = str(self.score)
        self.level = 1
        self.ids.level_label.text = 'Level 1'
        self.first = True

    def play(self):
        """ Implementation of the game """
        new_figure = True

        while self.playing:
            # Figure on the grid
            if not new_figure:
                new_figure = not self.move_figure(DOWN)
            # Spawn a new figure at the top of the grid
            else:
                new_figure = False

                self.spawn_random_figure()

            # Initial speed, 1 second per move
            speed = SPEEDS[self.level]
            sleep(speed)

    def spawn_random_figure(self):
        """
        Spawn a random figure at the top of the grid (centered)
        """
        self.origin = CENTER

        # Check if there is a completed row
        self.check_lines()

        if not self.first:
            self.color = self.next_figure[0]
            self.figure_set = self.next_figure[1:]
            self.figure = self.figure_set[0]
        else:
            selection = choice(range(7))
            self.color = FIGURES[selection][0]
            self.figure_set = FIGURES[selection][1:]
            self.figure = self.figure_set[0]
            self.first = False

        # Select one random figure
        selection = choice(range(7))
        self.next_figure = FIGURES[selection]

        # Remove old next figure
        for row in range(4):
            for col in range(4):
                self.grid_aux[row][col].value = None

        # check if game over
        for x, y in self.figure_set[0]:
            if self.grid[self.origin[0]+x][self.origin[1]+y].value is not None:
                self.game_over()
                self.playing = False
                return

        # Draw the next figure
        for x, y in self.next_figure[1]:
            self.grid_aux[x][y].value = self.next_figure[0]

        # Draw the figure with the default rotation
        for x, y in self.figure_set[0]:
            self.grid[self.origin[0]+x][self.origin[1]+y].value = self.color

    def check_lines(self):
        """ Check if there are rows to delete (completed rows) """
        for row in range(-1, -20, -1):
            # Precondition: the line is complete
            line = True
            # Number of completed lines
            lines = 0
            # To check if the player has complete 10 more lines (next level)
            next_level = self.lines_counter % 10

            while line:     # while to handle completed rows in a row
                for col in range(10):
                    # If one of the cells is empty, not a completed row
                    if self.grid[row][col].value is None:
                        line = False

                if line:
                    lines += 1
                    for new_row in range(row, -20, -1):
                        for new_col in range(10):
                            # Copy the value of the top cell
                            self.grid[new_row][new_col].value = \
                                self.grid[new_row-1][new_col].value

            # Update the score
            if lines:
                self.lines_counter += lines
                next_level += lines

                # If increase level condition reached
                if next_level >= 10:
                    self.increase_level()

                # Maximum score for 4 lines
                if lines > 4:
                    lines = 4

                self.score += SCORES[lines]
                self.ids.score_label.text = str(self.score)

    def increase_level(self):
        self.level += 1
        self.ids.level_label.text = 'Level ' + str(self.level)

    def move_figure(self, side):
        """
        Makes the actual figure move one row or column to side (param)
                return -- True if it is possible to make the move
        """
        new_figure, side_cells = self.get_moved_figure(side)
        origin_x, origin_y = self.origin[0], self.origin[1]

        # Check if it is possible to make the move
        for x, y in side_cells:
            try:
                down_cell_value = \
                    self.grid[origin_x+x][origin_y+y].value
            # If figure at the bottom, not possible to make the move
            except IndexError:
                return False

            # If the cell value of the row down cell is not None or the value
            # of col is lower than 0, it is not possible to make the move
            if down_cell_value is not None or origin_y + y < 0:
                return False

        # Remove old position
        for x, y in self.figure:
            self.grid[origin_x+x][origin_y+y].value = None

        # Draw the new position
        for x, y in new_figure:
            self.grid[origin_x+x][origin_y+y].value = self.color

        # Update the origin of the figure
        self.origin = (origin_x+side[0], origin_y+side[1])

        return True

    def rotate_figure(self):
        """ change figure to its next rotation state """
        index = self.figure_set.index(self.figure)
        origin_x, origin_y = self.origin[0], self.origin[1]
        is_possible = True

        # figure_set acts as a rotatory data structure
        if index == 3:
            new_index = 0
        else:
            new_index = index + 1

        # Remove old position
        for x, y in self.figure:
            self.grid[origin_x+x][origin_y+y].value = None

        # check if is possible to make the rotation
        for x, y in self.figure_set[new_index]:
            try:
                if self.grid[origin_x+x][origin_y+y].value is not None or \
                        origin_x+x < 0 or \
                        origin_y+y < 0:
                    is_possible = False
            except IndexError:
                is_possible = False

        if is_possible:
            self.figure = self.figure_set[new_index]

        # Draw the new position (or old one if not possible)
        for x, y in self.figure:
            self.grid[origin_x+x][origin_y+y].value = self.color

    def get_moved_figure(self, side):
        """
        Return the coordinates of the figure moved to side (param) and
            the side cells of the figure
        """
        new_figure = [(x + side[0], y + side[1]) for x, y in self.figure]
        side_cells = [(x, y) for x, y in new_figure if (x, y)
                      not in self.figure]

        return new_figure, side_cells


class MainApp(App):
    """
    Main class of the application
    """
    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)

        Window.bind(on_key_down=self.on_key_down)

    def build(self):
        """
        To initialize the app with a widget tree.
            return -- the widget tree constructed.
        """
        self.game_screen = Factory.GameScreen(name='tetris')
        self.game_screen.app = self

        sm = ScreenManager()
        sm.add_widget(self.game_screen)

        return sm

    def on_key_down(self, window, key, *args):
        self.game_screen.lock = False

        if self.game_screen.playing:
            if key == 273:       # key: UP
                self.game_screen.rotate_figure()

            elif key == 275:     # key: RIGHT
                self.game_screen.move_figure(RIGHT)

            elif key == 274:     # key: DOWN
                bottom = False

                # Move down until not possible to keep moving down
                while not bottom:
                    bottom = not self.game_screen.move_figure(DOWN)

                self.game_screen.spawn_random_figure()

            elif key == 276:     # key: LEFT
                self.game_screen.move_figure(LEFT)


if __name__ == '__main__':
    MainApp().run()
