import pygame as pg
import enum
from mathematics import *
from pygame import draw
from pygame import gfxdraw
from pygame.draw import line

pg.init()
pg.display.set_caption('2D Sin.py')
# icon = pg.image.load("../sprites/icons/chessie_logo.png")
# pg.display.set_icon(icon)

WINDOW_W = WINDOW_H = 900
FPS = 60

zoom = 100.0
g = 9.8

class Origin:
    world_coordinate = (0,0)
    screen_coordinate = (WINDOW_W / 2, WINDOW_H / 2)

    def translate(self):
        pass

    def get_screen_coords(self):
        pass

class Units(enum.Enum):
    meter = 100
    centimeter = 1
    kilogram = 1


class Graphics:
    def unit_to_pixel(number_of_units, unit_type=Units.meter):
        to_pixels = unit_type * number_of_units
        render_size = to_pixels * zoom/100.0
        return render_size
        

class Particle:
    def __init__(self, position : tuple = (0,0), size : float = 0, mass : float = 1.0, velocity : tuple = (0,0), color : tuple = (111,111,111)):
        self.mass = mass
        self.material = None

        self.position = position    # Particle's position in world coordinates
        self.velocity = velocity

        self.radius = size
        self.color = color
        self.line_width = 0

    def draw(self):
        draw_circle(position=self.get_world_position(),color=self.color,radius=self.radius,line_width=self.line_width)

    def get_world_position(self):
        return tuple_add(self.position, world_origin.world_coordinate) # Element-wise tuple addition


"""
    Draw a circle. If line_width = 0 : Fill the circle. Po
"""
def draw_circle(position : tuple = (0.0,0.0), radius : float = 1.0, color : tuple = (255,0,0), line_width : int = 0):
    screen_position = tuple_add(world_origin.screen_coordinate, position)
    draw.circle(screen, color, screen_position, radius, line_width)

def render_frame():
    for entity in entities:
        if (hasattr(entity, 'draw')):
            entity.draw()

def main():
    global screen
    global entities
    global world_origin

    world_origin = Origin()

    screen = pg.display.set_mode((WINDOW_W,WINDOW_H))
    clock = pg.time.Clock()

    entities = [Particle((0,0), size=20)]

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