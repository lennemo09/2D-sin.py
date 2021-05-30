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
FPS = 120

zoom = 1.0
is_topdown = False

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
    def tuple_in_unit_to_pixels(tuple_in_unit, unit_type=Units.meter):
        multiplier = unit_type.value * zoom/100.0
        return vector2D_scalar_multiply(tuple_in_unit, multiplier)

    def unit_to_pixel(number_of_units, unit_type=Units.meter):
        to_pixels = unit_type.value * number_of_units
        render_size = to_pixels * zoom/100.0
        return render_size

class PhysicsEntity:
    """
        Place-holder abstract class for type-inference.
    """
    pass

class Particle(PhysicsEntity):
    def __init__(self, position : tuple = (0,0), size : float = 0, mass : float = 1.0, velocity : tuple = (0,0), acceleration : tuple = (0,0), color : tuple = (111,111,111), gravity : bool = True, fixed : bool = False):
        self.mass = mass
        self.material = None

        self.position = position    # Particle's position in world coordinates in meters
        self.velocity = velocity
        self.acceleration = acceleration

        self.radius = size # Size in meters
        self.color = color
        self.line_width = 0
        self.gravity = gravity
        self.is_fixed = fixed

    def draw(self):
        draw_circle(position=self.get_world_position(),color=self.color,radius=self.get_pixel_size(),line_width=self.line_width)

    def get_pixel_size(self):
        return Graphics.unit_to_pixel(self.radius) 

    def get_world_position(self):
        return vector2D_add(self.position, world_origin.world_coordinate) # Element-wise tuple addition

class SolidRectangle(PhysicsEntity):
    def __init__(self, position : tuple = (0,0), size : tuple = (10,10), mass : float = 1.0, velocity : tuple = (0,0), acceleration : tuple = (0,0), color : tuple = (111,111,111), gravity : bool = True, fixed : bool = False):
        self.mass = mass
        self.material = None

        self.position = position    # Particle's position in world coordinates in meters
        self.velocity = velocity
        self.acceleration = acceleration

        self.size = size # Width and height in meters
        self.color = color
        self.line_width = 0
        self.gravity = gravity
        self.is_fixed = fixed

    def draw(self):
        draw_rectangle(startpoint=self.get_world_position(),size=self.get_pixel_size(),color=self.color,line_width=self.line_width)

    def get_pixel_size(self):
        return Graphics.tuple_in_unit_to_pixels(self.size)

    def get_world_position(self):
        return vector2D_add(self.position, world_origin.world_coordinate) # Element-wise tuple addition


#################################### PHYSICS UPDATE ###########################################
def is_colliding(entity1, entity2):
    """
    Cases:
        1. Particle vs. Particle : Circle collision.
        2. Particle vs. Rectangle: Cirlce & rectangle collision.
    """
    # Case 1: Particle vs Particle:
    if type(entity1) == Particle and type(entity2) == Particle:
        return check_particles_collision(entity1,entity2)
    
    # Case 2: Particle vs. Rectangle
    # Note: Can reduce this boolean, left for clarity
    if (type(entity1) == Particle and type(entity2) == SolidRectangle) or (type(entity1) == SolidRectangle and type(entity2) == Particle):
        particle, solid = (entity1,entity2) if (type(entity1) == Particle and type(entity2) == SolidRectangle) else (entity2,entity1)
        return check_particle_solid_collision(particle,solid)

def check_particle_solid_collision(particle : Particle, solid : SolidRectangle):
    cx, cy = particle.position
    r = particle.radius
    sx, sy = solid.position
    w,h = solid.size

    if (cx + r > sx) and (cy + r > sy) and (cx - r < sx + w) and (cy - r < sy + h + w):
        if (cx + r > sx):
            print(f"(cx + r > sx): cx+r={cx+r} sx={sx}")
        if (cy + r > sy):
            print(f"(cy + r > sy): cy+r={cy + r} sy={sy}")
        if (cx - r < sx + w):
            print(f"(cx - r < sx + w): cx-r={cx-r} sx+w={sx+w}")
        if (cy - r < sy + h + w):
            print(f"(cy - r < sy + h + w): cy-r={cy-r} sy+h+w={sy+h+w}")
        return True
    return False

def check_particles_collision(entity1, entity2):
    pass

def particle_solid_elastic_collision(particle : Particle, solid : SolidRectangle):
    m1 = particle.mass
    v1x, v1y = particle.velocity

    m2 = solid.mass
    v2x, v2y = solid.velocity

    if not particle.is_fixed:
        vx = ((m1 - m2)*v1x + 2*m2*v2x) / (m1 + m2)
        vy = ((m1 - m2)*v1y + 2*m2*v2y) / (m1 + m2)
        particle.velocity = (vx,vy)
    
    if not solid.is_fixed:
        vx = ((m2 - m1)*v2x + 2*m1*v1x) / (m1 + m2)
        vy = ((m2 - m1)*v2y + 2*m1*v1y) / (m1 + m2)
        solid.velocity = (vx,vy)


def update_all_positions():
    for entity in entities:
        if not entity.is_fixed:
            update_position(entity)

def update_position(entity):
    x0, y0 = entity.position
    vx0, vy0 = entity.velocity
    ax, ay = entity.acceleration

    if entity.gravity:
        ay += g

    entity.position = (x0 + vx0*dt + ((ax*dt**2) / 2), y0 + vy0*dt + ((ay*dt**2) / 2))
    entity.velocity = (vx0 + ax, vy0 + ay)

################################# GRAPHICS RENDERING ##########################################
"""
    Draw a circle. If line_width = 0 : Fill the circle.
"""
def draw_circle(position : tuple = (0.0,0.0), radius : float = 1.0, color : tuple = (255,0,0), line_width : int = 0):
    position_in_pixels = Graphics.tuple_in_unit_to_pixels(position)
    screen_position = vector2D_add(world_origin.screen_coordinate, position_in_pixels)
    draw.circle(screen, color, screen_position, radius, line_width)

"""
    Draw a Rectangle. 
"""
def draw_rectangle(startpoint : tuple = (0.0,0.0), size: tuple = (10,10), color : tuple = (255,0,0), line_width : int = 0):
    start_position_in_pixels = Graphics.tuple_in_unit_to_pixels(startpoint)
    start_screen_position = vector2D_add(world_origin.screen_coordinate, start_position_in_pixels)
    rect = pg.Rect(start_screen_position,size)

    draw.rect(screen, color, rect, line_width)

def render_frame():
    for entity in entities:
        if isinstance(entity,PhysicsEntity):
            entity.draw()

def main():
    global screen
    global entities
    global world_origin
    global dt # delta time in seconds
    global g # gravitational accelarator, m/s^2

    if (is_topdown):
        g = 0
    else:
        g = 9.8

    world_origin = Origin()

    screen = pg.display.set_mode((WINDOW_W,WINDOW_H))
    clock = pg.time.Clock()

    ground = SolidRectangle((-WINDOW_W/2,300), (WINDOW_W,200), mass=999999999999, color=(0,0,0), gravity=False, fixed=True)

    entities = [ground,Particle((0,0), mass=10, size=10, velocity=(150,-300))]

    background_colour = (255,255,255)
    
    running = True

    while running:
        screen.fill(background_colour)
        dt = clock.get_time() / 1000
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        if is_colliding(entities[0],entities[1]):
            particle_solid_elastic_collision(entities[1],entities[0])

        update_all_positions()
        render_frame()
        # Do stuff before this
        clock.tick(FPS)
        pg.display.flip()


if __name__ == '__main__':
    main()