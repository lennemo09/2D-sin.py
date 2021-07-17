import pygame as pg
import enum
import math
from mathematics import *
from pygame import draw
from pygame import gfxdraw
from pygame.draw import line
import random

pg.init()
pg.display.set_caption('2D Sin.py')
# icon = pg.image.load("../sprites/icons/chessie_logo.png")
# pg.display.set_icon(icon)

WINDOW_W = WINDOW_H = 900
FPS = 60
DELTA_T = 1/FPS

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
    def __init__(self, position : tuple = (0,0), size : float = 0, mass : float = 1.0, velocity : tuple = (0,0), acceleration : tuple = (0,0), color : tuple = (111,111,111), gravity : bool = True, fixed : bool = False, name="Particle"):
        self.name = name
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

        self.collision_checked = False

    def draw(self):
        draw_circle(position=self.get_world_position(),color=self.color,radius=self.get_pixel_size(),line_width=self.line_width)

    def get_pixel_size(self):
        return Graphics.unit_to_pixel(self.radius) 

    def get_world_position(self):
        return vector2D_add(self.position, world_origin.world_coordinate) # Element-wise tuple addition
    
    def get_speed(self):
        return vector2D_get_length(self.velocity)**2

    def get_kinetic_energy(self):
        return 0.5 * self.mass * vector2D_get_length(self.velocity)**2
        
class SolidRectangle(PhysicsEntity):
    def __init__(self, position : tuple = (0,0), size : tuple = (10,10), mass : float = 1.0, velocity : tuple = (0,0), acceleration : tuple = (0,0), color : tuple = (111,111,111), gravity : bool = True, fixed : bool = False, name="Rectangle"):
        self.name = name

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

        self.collision_checked = False

    def draw(self):
        draw_rectangle(startpoint=self.get_world_position(),size=self.get_pixel_size(),color=self.color,line_width=self.line_width)

    def get_pixel_size(self):
        return Graphics.tuple_in_unit_to_pixels(self.size)

    def get_world_position(self):
        return vector2D_add(self.position, world_origin.world_coordinate) # Element-wise tuple addition

    def get_speed(self):
        return vector2D_get_length(self.velocity)

    def get_kinetic_energy(self):
        return 0.5 * self.mass * self.get_speed()**2


#################################### PHYSICS UPDATE ###########################################
def is_colliding(entity1, entity2):
    """
    Cases:
        0. 2 fixed entities: Ignore collision.
        1. Particle vs. Particle : Circle collision.
        2. Particle vs. Rectangle: Cirlce & rectangle collision.
    """
    # Case 0: 2 fixed entities:
    if entity1.is_fixed and entity2.is_fixed:
        return False

    # Case 1: Particle vs Particle:
    if type(entity1) == Particle and type(entity2) == Particle:
        if check_particles_collision(entity1,entity2):
            elastic_collision(entity1,entity2)
    
    # Case 2: Particle vs. Rectangle
    # Note: Can reduce this boolean, left for clarity
    if (type(entity1) == Particle and type(entity2) == SolidRectangle) or (type(entity1) == SolidRectangle and type(entity2) == Particle):
        particle, solid = (entity1,entity2) if (type(entity1) == Particle and type(entity2) == SolidRectangle) else (entity2,entity1)
        if check_particle_solid_collision(particle,solid):
            #print(f"COLLISION DETECTED with {solid.name}")
            elastic_collision(particle,solid)

def check_particle_solid_collision(particle : Particle, solid : SolidRectangle):
    cx, cy = particle.position
    vx, vy = particle.velocity
    r = particle.radius

    sx, sy = solid.position
    w,h = solid.size

    next_cx = cx + vx * DELTA_T
    next_cy = cy + vy * DELTA_T

    distX = abs(next_cx - sx-w/2)
    distY = abs(next_cy - sy-h/2)

    if (distX > (w/2 + r)): return False
    if (distY > (h/2 + r)): return False

    if (distX <= w/2): return True
    if (distY <= h/2): return True

    dx = distX - w/2
    dy = distY - h/2

    return (dx**2 + dy**2 <= r**2)

def check_particles_collision(entity1, entity2):
    cx1, cy1 = entity1.position
    vx1, vy1 = entity1.velocity
    new_pos1 = (cx1 + vx1 * DELTA_T, cy1 + vy1 * DELTA_T)

    cx2, cy2 = entity2.position
    vx2, vy2 = entity2.velocity
    new_pos2 = (cx2 + vx2 * DELTA_T, cy2 + vy2 * DELTA_T)

    distance = vector2D_get_length(vector2D_sub(new_pos2,new_pos1))
    return distance <= entity1.radius + entity2.radius


def elastic_collision(entity1, entity2):
    m1 = entity1.mass
    v1x, v1y = entity1.velocity

    m2 = entity2.mass
    v2x, v2y = entity2.velocity

    if not entity1.is_fixed:
        vx = ((m1 - m2)*v1x + 2*m2*v2x) / (m1 + m2)
        vy = ((m1 - m2)*v1y + 2*m2*v2y) / (m1 + m2)
        entity1.velocity = (vx,vy)
    
    if not entity2.is_fixed:
        vx = ((m2 - m1)*v2x + 2*m1*v1x) / (m1 + m2)
        vy = ((m2 - m1)*v2y + 2*m1*v1y) / (m1 + m2)
        entity2.velocity = (vx,vy)

def update_all_positions():
    for entity in entities:
        entity.collision_checked = False
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

################################## HELPER FUNCTIONS ############################################
def create_bounding_walls(entities):
    lower = SolidRectangle((-WINDOW_W/2,300), (WINDOW_W,200), mass=999999999999, color=(0,0,0), gravity=False, fixed=True, name="lower")
    upper = SolidRectangle((-WINDOW_W/2,-WINDOW_H/2), (WINDOW_W,200), mass=999999999999, color=(0,0,0), gravity=False, fixed=True, name ="upper")
    left = SolidRectangle((-WINDOW_W/2,-WINDOW_H/2), (200,WINDOW_H), mass=999999999999, color=(0,0,0), gravity=False, fixed=True, name="left")
    right = SolidRectangle((WINDOW_W/2-200,-WINDOW_H/2), (200,WINDOW_H), mass=999999999999, color=(0,0,0), gravity=False, fixed=True, name="right")
    return [lower,upper,left,right] + entities


def update_fps(clock):
    font = pg.font.SysFont("Arial", 18)
    fps = str(int(clock.get_fps()))
    fps_text = font.render(fps, 1, pg.Color("coral"))
    return fps_text

######################################## MAIN ###################################################
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

    entities = []
    for _ in range(1):
        pos = (random.uniform(-150,150),random.uniform(-150,150))
        mass = random.uniform(1,50)
        r = random.randint(5,30)
        vel = (random.uniform(-300,300),random.uniform(-300,300))
        color = (random.randint(0,256),random.randint(0,256),random.randint(0,256))
        particle = Particle(position=pos,size=r,mass=mass,velocity=vel,color=color)
        entities.append(particle)
    entities = create_bounding_walls(entities)

    background_colour = (255,255,255)
    
    running = True

    while running:
        screen.fill(background_colour)
        dt = clock.get_time() / 1000
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        for i in range(len(entities)):
            entity1 = entities[i]
            for j in range(len(entities)):
                if j == i:
                    continue
                else:
                    entity2 = entities[j]
                    if not entity2.collision_checked:
                        is_colliding(entity1,entity2)
            entity1.collision_checked = True
        update_all_positions()
        render_frame()
        # Do stuff before this
        screen.blit(update_fps(clock), (10,0))   # Shows current FPS
        clock.tick(FPS)
        pg.display.flip()


if __name__ == '__main__':
    main()