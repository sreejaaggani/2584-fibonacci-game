import sys
import random
import itertools
import enum
import copy
import pygame as pg
import pygame.freetype
import pygame.locals as pgl
from tkinter import *
import tkinter



SCREEN_SIZE = (800, 600)

class GameOverException(Exception):
    pass

class GameWonException(Exception):
    pass


@enum.unique
class Direction(enum.Enum):
    UP, DOWN, LEFT, RIGHT = 273, 274, 276, 275


class ThreesGame():
    high_number_probability = 0.3
    numbers = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584]

    def __init__(self, grid_size=(4, 4), num_numbers=12):
        self.grid = self.make_new_grid(grid_size)   # access like grid[col][row]
        self.grid_size = grid_size

        if num_numbers > len(self.numbers):
            num_numbers = len(self.numbers)

        self.numbers = self.numbers[:num_numbers]
        self.num_numbers = len(self.numbers)
        self.max_value = self.numbers[-1]

        self._score = 0
        self.finished = False

        self.latest_score = 0
        self.latest_tile = None


    def move(self, direction):
        new_grid, score = self.move_to_direction(self.grid, direction)

        if not self.grids_are_equal(self.grid, new_grid):   # Grids are the same
            self.grid = new_grid
            new_tile_ix = self.add_tile()

            self._score += 1 + score

            self.latest_score = 1 + score
            self.latest_tile = new_tile_ix


    def initialize(self):
        """Add two tiles to the game."""
        self.add_tile()
        self.add_tile()

    def add_tile(self):
        # Find non-zero elements
        nz = []
        for x in range(self.grid_size[0]):
            for y in range(self.grid_size[1]):
                if self.grid[x][y] == 0:
                    nz.append((x,y))

        if len(nz) < 1:
            raise GameOverException()

        # Select random tile
        ix = random.choice(nz)

        # Add either 1 or 2
        self.grid[ix[0]][ix[1]] = 2 if random.uniform(0,1) < self.high_number_probability else 1

        # Check for win
        if self.game_won():
            self.finished = True
            raise GameWonException()

        # Check for game over
        if not self.valid_moves():
            self.finished = True
            raise GameOverException()

        return ix


    def game_won(self):
        """Checks whether the max_number exists in the grid."""
        for col in self.grid:
            for elem in col:
                if elem == self.max_value:
                    return True
        return False


    def valid_moves(self):
        """Returns True if there are valid moves."""
        orig_grid = self.copy_grid(self.grid)

        # Try moving and return True if the grid changes
        for direction in Direction:
            new_grid, _ = self.move_to_direction(orig_grid, direction)
            if not self.grids_are_equal(orig_grid, new_grid):
                return True

        return False


    @property
    def score(self):
        """Returns current score."""
        return self._score


    @classmethod
    def copy_grid(cls, grid):
        """Returns a copy of a grid."""
        return copy.deepcopy(grid)

    @classmethod
    def grids_are_equal(cls, grid1, grid2):
        """Returns true if all elements are equal."""
        return grid1 == grid2   # It's this easy!

    @classmethod
    def make_new_grid(cls, grid_size):
        return [[0]*grid_size[1] for _ in range(grid_size[0])]

    @classmethod
    def stack_col(cls, col):
        """Stacks a col upwards."""
        if len(col) == 1:
            return col

        if col[0] == 0:   # Move first element to last
            col = cls.stack_col(col[1:]) + [0]
        else:
            col = col[0:1] + cls.stack_col(col[1:])

        return col

    @classmethod
    def combine_col(cls, col):
        """Combines adjacent tiles."""
        score = 0

        for i in range(len(col)-1):
            elem1, elem2 = col[i], col[i+1]
            if elem1 == 0 or elem2 == 0:
                continue   # If either is zero, we skip the rest

            ix1, ix2 = cls.numbers.index(elem1), cls.numbers.index(elem2)

            if ix1 == 0 and ix2 == 0:   # 1 and 1
                col[i] = 2
                col[i+1] = 0
                score += 2
            elif abs(ix1-ix2) == 1:   # Adjacent numbers in sequence
                col[i] = elem1 + elem2
                col[i+1] = 0
                score += elem1 + elem2

        return col, score


    @classmethod
    def move_to_direction(cls, grid, direction):
        score = 0
        new_grid = cls.copy_grid(grid)

        if direction == Direction.UP:
            for x in range(len(new_grid)):
                new_grid[x] = cls.stack_col(new_grid[x])
                new_grid[x], score = cls.combine_col(new_grid[x])
                new_grid[x] = cls.stack_col(new_grid[x])
        elif direction == Direction.DOWN:
            # Flip and stack and flip
            for x in range(len(new_grid)):
                new_grid[x] = cls.stack_col(new_grid[x][::-1])
                new_grid[x], score = cls.combine_col(new_grid[x])
                new_grid[x] = cls.stack_col(new_grid[x])[::-1]
        elif direction == Direction.LEFT:
            for x, col in enumerate(map(list, itertools.zip_longest(*new_grid))):
                new_grid[x] = cls.stack_col(col)  # Rows are now cols
                new_grid[x], score = cls.combine_col(new_grid[x])
                new_grid[x] = cls.stack_col(new_grid[x])
            new_grid = list(map(list, itertools.zip_longest(*new_grid)))
        elif direction == Direction.RIGHT:
            for x, col in enumerate(map(list, itertools.zip_longest(*new_grid))):
                new_grid[x] = cls.stack_col(col[::-1])  # Rows are now cols
                new_grid[x], score = cls.combine_col(new_grid[x])
                new_grid[x] = cls.stack_col(new_grid[x])[::-1]
            new_grid = list(map(list, itertools.zip_longest(*new_grid)))

        return new_grid, score


class GameTile(pg.sprite.Sprite):
    def __init__(self, tile_size, tile_color, tile_pos, font, value=0, text_color=(255, 255, 255),
                 border_color=(0, 0,0 ), border_width=20):
        super().__init__()

        self.font = font

        self.tile_size = tile_size
        self.surface = pg.Surface(tile_size)

        self.tile_color = tile_color
        self.rect = self.surface.get_rect(center=tile_pos)
        self.value = value

        self.border_color = border_color
        self.border_width = border_width

        self.text_color = text_color

        #self.label = self.font.render(str(self.value), fgcolor=(255, 255, 255))

        self.update()


    def update(self):
        self.surface.fill(self.border_color)
        surface_rect = self.surface.get_rect()
        pg.draw.rect(self.surface, self.tile_color,
                     (self.border_width, self.border_width,
                      self.tile_size[0]-2*self.border_width,
                      self.tile_size[0] - 2 * self.border_width))
        #self.font.rende(self.surface, (self.tile_size[0]/2, self.tile_size[1]/2),
        #                            str(self.value), fgcolor=self.text_color)
        text_surf, text_rect = self.font.render(str(self.value), fgcolor=self.text_color)
        self.surface.blit(text_surf, ((surface_rect.width-text_rect.width)/2, (surface_rect.height-text_rect.height)/2))





class ThreesGameUI():
    BACKGROUND_COLOR = (0, 0, 0)
    TILE_COLOR_INACTIVE = (127, 127, 127)
    TILE_COLORS = [(247, 112, 137),
     (248, 118, 59),
     (210, 142, 49),
     (184, 153, 49),
     (158, 162, 49),
     (124, 170, 49),
     (49, 179, 69),
     (51, 176, 129),
     (53, 174, 155),
     (54, 172, 173),
     (55, 170, 193),
     (58, 166, 221),
     (118, 153, 245),
     (176, 135, 245),
     (224, 109, 245),
     (246, 98, 216),
     (246, 106, 179)]
    TILE_COLORS_ACTIVE = [(138, 22, 15),
     (138, 66, 15),
     (138, 109, 15),
     (123, 138, 15),
     (80, 138, 15),
     (36, 138, 15),
     (15, 138, 37),
     (15, 138, 80),
     (15, 138, 123),
     (15, 109, 138),
     (15, 65, 138),
     (15, 22, 138),
     (51, 15, 138),
     (95, 15, 138),
     (138, 15, 138),
     (138, 15, 94),
     (138, 15, 51)]


    def __init__(self, screen_size, grid_size=(4, 4)):
        pg.init()
        self.font = pg.freetype.SysFont("Arial", 48)

        self.screen_size = screen_size
        self.screen = pg.display.set_mode(self.screen_size)
        self.game = ThreesGame(grid_size=grid_size, num_numbers=16)

        self.tile_colors = {x: self.TILE_COLORS[i] for i, x in enumerate(self.game.numbers)}
        self.tile_colors[0] = self.TILE_COLOR_INACTIVE
        self.tile_colors_active = {x: self.TILE_COLORS_ACTIVE[i] for i, x in enumerate(self.game.numbers)}

        self.grid_width = min(*self.screen_size)
        self.play_area = None

        self.score_board = None

        self.tiles = None

        self.running = False


    def run(self):
        self.game.initialize()

        self.play_area = pg.Surface((self.grid_width, self.grid_width))
        self.play_area.fill(self.BACKGROUND_COLOR)
        self._initialize_tiles()

        self.score_board = pg.Surface((self.screen_size[0] - self.grid_width, 100))
        self.score_board.fill(self.BACKGROUND_COLOR)
        self.font.render_to(self.score_board, ((self.screen_size[0] - self.grid_width)/2, 50),
                            str(0), fgcolor=(255, 255, 255))

        self.running = True
        self._main_loop()

    def _main_loop(self):
        """Blocking main event loop."""
        while self.running:
            self._update_tiles()
            self._draw_tiles()
            self._update_score()
            pg.display.flip()

            for event in pg.event.get():
                if event.type == pgl.KEYDOWN:
                    try:
                        if event.key == pgl.K_ESCAPE:
                            self.running = False
                            sys.exit()

                        elif event.key == pgl.K_UP:
                            self.game.move(Direction.UP)
                        elif event.key == pgl.K_DOWN:
                            self.game.move(Direction.DOWN)
                        elif event.key == pgl.K_LEFT:
                            self.game.move(Direction.LEFT)
                        elif event.key == pgl.K_RIGHT:
                            self.game.move(Direction.RIGHT)
                    except GameOverException as e:
                        print("Game Over!")
                        self._update_tiles()
                        self._draw_tiles()
                        self._update_score()
                        self.screen.blit(self.score_board, (self.grid_width, 0))
                        game_over_text = pg.Surface((self.grid_width, 100))
                        game_over_text.fill(self.BACKGROUND_COLOR)
                        self.font.render_to(game_over_text, (self.grid_width/2, 50),
                                            "Game Over", fgcolor=(255, 255, 255))

                        self.screen.blit(game_over_text, (0, self.grid_width/2))
                        pg.display.flip()
                        self.running = False
                    except GameWonException as e:
                        print("You win!")
                        self._update_tiles()
                        self._draw_tiles()
                        self._update_score()
                        self.screen.blit(self.score_board, (self.grid_width, 0))
                        game_won_text = pg.Surface((self.grid_width, 100))
                        game_won_text.fill(self.BACKGROUND_COLOR)
                        self.font.render_to(game_won_text, (self.grid_width / 2, 50),
                                            "You win!", fgcolor=(255, 255, 255))

                        self.screen.blit(game_won_text, (0, self.grid_width / 2))
                        pg.display.flip()
                        self.running = False

                elif event.type == pgl.QUIT:
                    self.running = False
                    sys.exit()

        while True:
            for event in pg.event.get():
                if event.type == pgl.KEYDOWN:
                    if event.key == pgl.K_ESCAPE:
                        sys.exit()
                elif event.type == pgl.QUIT:
                    sys.exit()


    def _initialize_tiles(self):
        self.tile_size = (self.grid_width / self.game.grid_size[0], self.grid_width / self.game.grid_size[1])

        self.tiles = [[GameTile(tile_size=self.tile_size,
                                tile_color=self.TILE_COLOR_INACTIVE,
                                tile_pos=((x+0.5)*self.tile_size[0], (y+0.5)*self.tile_size[1]),
                                border_color=self.BACKGROUND_COLOR,
                                border_width=10,
                                font=self.font,
                                value=self.game.grid[x][y])
                       for y in range(self.game.grid_size[0])]
                      for x in range(self.game.grid_size[1])]


    def _update_tiles(self):
        latest_tile_ix = self.game.latest_tile
        for col in range(self.game.grid_size[0]):
            for row in range(self.game.grid_size[1]):
                self.tiles[col][row].value = self.game.grid[col][row]
                if (col, row) == latest_tile_ix:
                    self.tiles[col][row].tile_color = self.tile_colors_active[self.game.grid[col][row]]
                    self.tiles[col][row].border_color = (10, 10, 10)
                else:
                    self.tiles[col][row].tile_color = self.tile_colors[self.game.grid[col][row]]
                    self.tiles[col][row].border_color = self.BACKGROUND_COLOR
                self.tiles[col][row].update()

    def _draw_tiles(self):
        for col in range(self.game.grid_size[0]):
            for row in range(self.game.grid_size[1]):
                tile = self.tiles[col][row]
                self.play_area.blit(tile.surface, tile.rect)

        #for tile in itertools.chain.from_iterable(self.tiles):
        #    self.play_area.blit(tile.surface, tile.rect)

        self.screen.blit(self.play_area, (0, 0))   # Draw at top left corner


    def _update_score(self):
        self.score_board.fill(self.BACKGROUND_COLOR)
        #score_board_rect = self.score_board.get_rect()
        #score_surf, score_rect = self.font.render(str(self.game.score), fgcolor=(255, 255, 255))
        #self.score_board.blit(score_surf, 0, 0)
        self.font.render_to(self.score_board, ((self.screen_size[0] - self.grid_width) / 2, 50),
                            str(self.game.score), fgcolor=(255, 255, 255))
        self.screen.blit(self.score_board, (self.grid_width, 0))
        
    

    

game_ui = ThreesGameUI(SCREEN_SIZE)
game_ui.run()
"""def main():
    game_ui = ThreesGameUI(SCREEN_SIZE)
    game_ui.run()
   
    



if __name__ == "__main__":
    main()"""
