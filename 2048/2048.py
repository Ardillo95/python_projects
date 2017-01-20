from random import choice, randrange

from kivy.app import App
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.utils import get_color_from_hex


DOWN_RIGHT_ORDER = [-1, -2, -3, -4]
UP_LEFT_ORDER = [0, 1, 2, 3]


class Cell(Label):
    """
    This class represents the blocks of the game.

    Basically, each block contains a value (2, 4, 8, 16...), a cell 
    coordinate ((0,0), (2,3)) and some properties that decides font size,
    color and text to represent.
    """
    def __init__(self, **kwargs):
        self.row = kwargs.pop('row')
        self.col = kwargs.pop('col')
        self._value = None              # 2, 4, 8, 16, 32, 64, 128, 256, 512...

        super(Cell, self).__init__(**kwargs)

        self.font_size = 50

        # add instructions rendered before
        with self.canvas.before:
            # set the background color, size and position
            self.bg_color = Color(.5, .5, 1)
            self.rectangle = Rectangle(size=self.size, pos=self.pos)

        # important!:   update rectangle position and size
        self.bind(pos=self.update_rect, size=self.update_rect)

        # cell colors depending on his value
        self.colors = {
            2: get_color_from_hex('#00ff00'),
            4: get_color_from_hex('#ccff00'),
            8: get_color_from_hex('#ffff00'),
            16: get_color_from_hex('#ffffaa'),
            32: get_color_from_hex('#ff0000'),
            64: get_color_from_hex('#0000ff'),
            128: get_color_from_hex('#ff00ff'),
            256: get_color_from_hex('#00ffff'),
            512: get_color_from_hex('#ffff00'),
            1024: get_color_from_hex('#ff0000'),
            2048: get_color_from_hex('#0000ff'),
        }

    # manual binding settup is required in Kivy
    def update_rect(self, instance, value):
        self.rectangle.pos = self.pos
        self.rectangle.size = self.size

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

        if value is None:
            self.text = ''
            self.bg_color.rgb = get_color_from_hex('#ed4c2e')
            return

        self.text = str(value)
        self.bg_color.rgb = self.colors[value]

    def __repr__(self):
        return '<Cell object in position ({}, {}) value={}>'.format(
            self.row, self.col, self.value)


class GameScreen(Screen):
    """
    GameScreen, determines the area of view of the application.

    There is only one screen, which is composed by the 4x4 grid and the
    background rectangle.
    """
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)

        self._score = 0
        self.grid = list()

        # generating the empty 4x4 grid
        for row in range(4):
            self.grid.append([])

            for col in range(4):
                cell = Cell(row=row, col=col)               # default cell

                # adding cell to the 4x4 grid
                self.ids.grid_layout.add_widget(cell)
                self.grid[row].append(cell)

        self.new_game()

    def new_game(self):
        self.reset()
        self.score = 0

        # adding the random value (2 or 4) to the two random positions
        for __ in range(2):
            self.spawn_randon_number()

    def reset(self):
        for row in self.grid:
            for cell in row:
                cell.value = None

    def spawn_randon_number(self):
        has_value = True

        while has_value:
            coord_x = randrange(4)
            coord_y = randrange(4)
            has_value = self.grid[coord_x][coord_y].value

            if has_value is None:
                self.grid[coord_x][coord_y].value = choice([2, 4])

    def win(self):
        self.reset()

        for i, letter in enumerate([('Y', 'W'),('O', 'I'),('U', 'N')]):
            self.grid[1][i].text = letter[0]
            self.grid[2][i+1].text = letter[1]

    def get_row(self, x, order):
        """ Return a list of cells of a given row coordinate. """
        row = []

        for index in order:
            row.append(self.grid[x][index])

        return row
        
    def get_col(self, y, order):
        """ Return a list of cells of a given column coordinate. """
        col = []
        
        for index in order:
            col.append(self.grid[index][y])

        return col

    def make_move(self, x, y, col_row, value):
        join = 1
        actual_x = x
        while actual_x>0 and join==1:
            actual_x -= 1
            if col_row[actual_x].value == value:
                join = 2
            elif col_row[actual_x].value is not None:
                actual_x += 1
                break

        return actual_x, join


    def vertical_move(self, order):
        has_joined = False
        has_moved = False
        win = False

        # for each column
        for y in range(4):
            col = self.get_col(y, order)
            # for each element of the column
            for x, cell in enumerate(col):
                value = cell.value
                # check if the current cell has a value
                if value is not None:
                    new_x, join = self.make_move(x, y, col, value)
                    if new_x != x:
                        x = order[new_x]
                        self.grid[x][y].value, cell.value = value * join, None
                        win = self.update_score_and_win_check(value, join)
                        has_moved = True

        if has_moved and not win:
            self.spawn_randon_number()

    def horizontal_move(self, order):
        has_joined = False
        has_moved = False
        win = False

        # for each row
        for x in range(4):
            row = self.get_row(x, order)
            # for each element of the row
            for y, cell in enumerate(row):
                # check if the current cell has a value
                value = cell.value
                if value is not None:
                    new_y, join = self.make_move(y, x, row, value)
                    if new_y != y:
                        y = order[new_y]
                        self.grid[x][y].value, cell.value = value * join, None
                        win = self.update_score_and_win_check(value, join)
                        has_moved = True

        if has_moved and not win:
            self.spawn_randon_number()

    def update_score_and_win_check(self, value, join):
        
        if join == 2:
            self.score = value * 2
        
        if value * join == 2048:
            self.win()
            return True
        
        return False
    
    @property
    def score(self):
        return self._score
    
    @score.setter
    def score(self, value):
        self._score += value
        self.ids.lbl_score.text = str(self.score)
    

class MainApp(App):
    """
    Main class of the application
    """
    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)

        # we want to receive all key down events
        Window.bind(on_key_down=self.on_key_down)
            
    def build(self):
        """
        To initialize the app with a widget tree.
            return -- the widget tree constructed.
        """
        self.game_screen = Factory.GameScreen(name='2048')
        self.game_screen.app = self

        sm = ScreenManager()
        sm.add_widget(self.game_screen)

        return sm

    def on_key_down(self, window, key, *args):
        """ Handle the key events """

        if key == 273:              # key:  UP
            self.game_screen.vertical_move(UP_LEFT_ORDER)
        elif key == 274:            # key:  DOWN
            self.game_screen.vertical_move(DOWN_RIGHT_ORDER)
        elif key == 276:            # key:  _left
            self.game_screen.horizontal_move(UP_LEFT_ORDER)
        elif key == 275:            # key:  _right
            self.game_screen.horizontal_move(DOWN_RIGHT_ORDER)


if __name__ == '__main__':
    MainApp().run()
