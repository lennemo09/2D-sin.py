import pygame as pg
import enum
from pygame import draw

from pygame.draw import line

pg.init()
pg.display.set_caption('2D Sin.py')
# icon = pg.image.load("../sprites/icons/chessie_logo.png")
# pg.display.set_icon(icon)

WINDOW_W = WINDOW_H = 900
FPS = 60

zoom = 100.0
g = 9.8


class Units(enum.Enum):
    meter = 100
    centimeter = 1
    kilogram = 1


class Graphics:
    def unit_to_pixel(number_of_units, unit_type=Units.meter):
        to_pixels = unit_type * number_of_units
        render_size = to_pixels * zoom/100.0
        return render_size
        

class Particle():
    def __init__(self, position : tuple = (0,0), size : float = 0, mass : float = 1.0, velocity : tuple = (0,0), color : tuple = (111,111,111)):
        self.mass = mass
        self.material = None

        self.position = position
        self.velocity = velocity

        self.radius = size
        self.color = color
        self.line_width = 0

    def draw(self):
        draw_circle(position=self.position,color=self.color,radius=self.radius,line_width=self.line_width)


"""
    Draw a circle. If line_width = 0 : Fill the circle.
"""
def draw_circle(position : tuple = (0.0,0.0), radius : float = 1.0, color : tuple = (255,0,0), line_width : int = 0):
    pg.draw.circle(screen, color, position, radius, line_width)


def render_frame():
    for entity in entities:
        if (hasattr(entity, 'draw')):
            entity.draw()

def main():
    global screen
    global entities

    screen = pg.display.set_mode((WINDOW_W,WINDOW_H))
    clock = pg.time.Clock()

    entities = [Particle((10,10), size=20)]

    background_colour = (255,255,255)
    screen.fill(background_colour)

    running = True

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
        
        render_frame()

        # Do stuff before this
        clock.tick(FPS)
        pg.display.flip()


if __name__ == '__main__':
    main()