import random
import pyglet
import queue


SCREEN_WIDTH = 400
SCREEN_HEIGHT = 400

GRID_WIDTH = 10
GRID_HEIGHT = 10

COLOUR_RED = (255, 0, 0)
COLOUR_GREEN = (0, 255, 0)
COLOUR_GREY = (100, 100, 100)


class Rect:
    def __init__(self, x_location, y_location, width, height, colour):
        self.x = x_location
        self.y = y_location
        self.w = width
        self.h = height
        self.colour = colour + colour + colour + colour
        # The tuple self.colour must contain 4 colours; one for each corner of the rectangle. However we want our
        # rectangle to be one colour, so we duplicate the same colour 4 times for each corner.

    def draw(self):
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2i', (self.x, self.y,
                                                     self.x+self.w, self.y,
                                                     self.x+self.w, self.y+self.h,
                                                     self.x, self.y + self.h)), ('c3B', self.colour))


class Snake:
    def __init__(self, location, direction, colour):
        self.pieces = [[location[0], location[1]]]
        self.colour = colour
        self.direction = direction

        self.movements = {'N':(0, 1), 'E':(1, 0), 'W':(-1, 0), 'S':(0, -1)}
        # N, E, W, S stand for North, East, West, South. This dictionary stores their respective translations.

        self.opposites = {'N':'S', 'E':'W', 'W':'E', 'S':'N'}
        # This dictionary tells us which directions we cannot currently turn in. E.g, if we're moving South we cannot
        # suddenly turn to move north, as we would be inside of our own tail.

        self.length = 5

        self.is_alive = True

    def draw(self):
        for piece in self.pieces:
            rect = Rect(piece[0] * GRID_WIDTH, piece[1] * GRID_HEIGHT, GRID_WIDTH - 1, GRID_HEIGHT - 1, self.colour)
            rect.draw()

    def change_direction(self, new_direction):
        if new_direction != self.opposites[self.direction]:
            self.direction = new_direction

    def move(self):
        if self.is_alive:
            this_movement = self.movements[self.direction]
            last_piece = self.pieces[-1]
            new_piece = [last_piece[0] + this_movement[0], last_piece[1] + this_movement[1]]

            self.pieces.append(new_piece)

        while len(self.pieces) > self.length:
            del self.pieces[0]
        # This loop gives the illusion that the snake is moving

        # This handles the snake going off the edge of the screen
        if self.pieces[-1][0] < 0:
            self.pieces[-1][0] = (SCREEN_WIDTH//GRID_WIDTH) - 1
        elif self.pieces[-1][0] >= SCREEN_WIDTH//GRID_WIDTH:
            self.pieces[-1][0] = 0

        if self.pieces[-1][1] < 0:
            self.pieces[-1][1] = (SCREEN_HEIGHT//GRID_HEIGHT) - 1
        elif self.pieces[-1][1] >= SCREEN_HEIGHT//GRID_HEIGHT:
            self.pieces[-1][1] = 0

    def check_if_dead(self):
        return self.pieces[-1] in self.pieces[:-1]


class Game:
    def __init__(self, restart=False):
        if not restart:
            self.window = pyglet.window.Window(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)

        self.snake = Snake((random.randrange(0, SCREEN_WIDTH//GRID_WIDTH),
                           random.randrange(0, SCREEN_HEIGHT//GRID_HEIGHT)), random.choice('NEWS'), COLOUR_RED)

        self.key_to_directions = {pyglet.window.key.A:'W', pyglet.window.key.D:'E', pyglet.window.key.S:'S', pyglet.window.key.W:'N',
                                  pyglet.window.key.LEFT:'W', pyglet.window.key.RIGHT:'E', pyglet.window.key.DOWN:'S', pyglet.window.key.UP:'N'}
        self.direction_change_queue = queue.Queue()

        self.apple = [random.randrange(0, SCREEN_WIDTH//GRID_WIDTH), random.randrange(0, SCREEN_HEIGHT//GRID_HEIGHT)]
        self.apples_eaten = 0

        self.game_over = False

        # This controls the difficulty of the game and will increase gradually to speed up the game
        self.snake_length_increase = 1

    def on_draw(self):
        self.window.clear()

        number_of_apples_eaten_label = pyglet.text.Label(text=str(self.apples_eaten), font_name='Consolas', font_size=100,
                                                         color=COLOUR_GREY + (255,), x=SCREEN_WIDTH//2, y=SCREEN_HEIGHT//2,
                                                         anchor_x='center', anchor_y='center')
        number_of_apples_eaten_label.draw()

        if self.game_over:
            pyglet.text.Label(text='Game Over', font_name='Consolas', font_size=20,
                              color=COLOUR_GREY + (255,), x=SCREEN_WIDTH//2, y=SCREEN_HEIGHT//2 - 60,
                              anchor_x='center', anchor_y='center').draw()

            pyglet.text.Label(text='SPACE to Restart', font_name='Consolas', font_size=15,
                              color=COLOUR_GREY + (255,), x=SCREEN_WIDTH // 2, y=SCREEN_HEIGHT // 2 - 85,
                              anchor_x='center', anchor_y='center').draw()

            pyglet.text.Label(text='ESCAPE to Quit', font_name='Consolas', font_size=15,
                              color=COLOUR_GREY + (255,), x=SCREEN_WIDTH // 2, y=SCREEN_HEIGHT // 2 - 100,
                              anchor_x='center', anchor_y='center').draw()

        self.snake.draw()

        apple_rect = Rect(self.apple[0] * GRID_WIDTH, self.apple[1] * GRID_HEIGHT, GRID_WIDTH - 1, GRID_HEIGHT - 1, COLOUR_GREEN)
        apple_rect.draw()

    def check_if_apple_eaten(self):
        if self.snake.pieces[-1] == self.apple:

            self.apple = [random.randrange(0, SCREEN_WIDTH//GRID_WIDTH), random.randrange(0, SCREEN_HEIGHT//GRID_HEIGHT)]
            while self.apple in self.snake.pieces:
                self.apple = [random.randrange(0, SCREEN_WIDTH//GRID_WIDTH), random.randrange(0, SCREEN_HEIGHT//GRID_HEIGHT)]
            # This block prevents the apple from spawning within the snake

            self.snake.length += self.snake_length_increase
            self.snake_length_increase += 1
            self.apples_eaten += 1

    def update(self, dt):
        self.snake.move()

        if not self.direction_change_queue.empty():
            direction = self.direction_change_queue.get()
            self.snake.change_direction(direction)

        self.check_if_apple_eaten()

        if not self.game_over:
            self.game_over = self.snake.check_if_dead()
            self.snake.is_alive = not self.game_over

    def on_key_press(self, symbol, modifiers):
        if symbol in self.key_to_directions.keys():
            self.direction_change_queue.put(self.key_to_directions[symbol])

        elif symbol == pyglet.window.key.SPACE:
            self.__init__(restart=True)

    def main(self):
        self.window.event(self.on_draw)
        self.window.event(self.on_key_press)
        pyglet.clock.schedule_interval(self.update, 1/15.0) # 1/15.0 means execute this function 15 times per second

        pyglet.app.run()


if __name__ == '__main__':
    game = Game()
    game.main()
