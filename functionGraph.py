import pygame
import sys
import configparser
import os
from sympy import sin, cos, tan, pi
from sympy.core.numbers import ComplexInfinity

# WARNING: this code uses eval()

pygame.init()
pygame.font.init()

font = pygame.font.SysFont('Segoe UI', 12)

if len(sys.argv) <= 1:
    raise TypeError('Missing function that is passed when executing the program, example: python <filename> "5*x + 7"')

function = str(sys.argv[1:]).replace('[','').replace(']','').replace(',','').replace('\'','')

cfg = configparser.ConfigParser()
config_filename = os.path.basename(__file__) + '.ini' # it will have '.py': main.py.ini

if os.path.exists(config_filename):
    cfg.read(config_filename)
else:
    cfg['DEFAULT']['iter_start'] = '-255'
    cfg['DEFAULT']['iter_end'] = '255'
    cfg['DEFAULT']['iter_step'] = '1'
    cfg['DEFAULT']['count_float_numbers'] = 'true'
    cfg['DEFAULT']['background_color'] = '45,45,45'
    cfg['DEFAULT']['font_color'] = '255,255,255'
    cfg['DEFAULT']['x_axis_color'] = '125,125,125'
    cfg['DEFAULT']['y_axis_color'] = '125,125,125'
    cfg['DEFAULT']['vertex_color'] = '140,140,140'

    with open(config_filename,'w') as f:
        cfg.write(f)

iter_start = int(cfg['DEFAULT']['iter_start'])
iter_end = int(cfg['DEFAULT']['iter_end'])
iter_step = int(cfg['DEFAULT']['iter_step'])

def str_to_bool(value: str):
    """
    returns None if not bool
    """
    value = value.lower()
    if value == '1' or value == 'true':
        return True
    elif value == '0' or value == 'false':
        return False
    return None

count_float_numbers = str_to_bool(cfg['DEFAULT']['count_float_numbers'])
if count_float_numbers == None:
    print('count_float_numbers value is not a boolean value.')
    quit()

def str_to_rgb(string: str):
    return [int(i) for i in string.split(',')]

DEFAULT_FONT_COLOR = str_to_rgb(cfg['DEFAULT']['font_color'])
BACKGROUND_COLOR = str_to_rgb(cfg['DEFAULT']['background_color'])
X_AXIS_COLOR = str_to_rgb(cfg['DEFAULT']['x_axis_color'])
Y_AXIS_COLOR = str_to_rgb(cfg['DEFAULT']['y_axis_color'])
VERTEX_COLOR = str_to_rgb(cfg['DEFAULT']['vertex_color'])

def write_text(text: str, color: tuple=DEFAULT_FONT_COLOR):
    return font.render(text, True, color)

def get_sin(x):
    return sin(x*pi/180).n()

def get_cos(x):
    return cos(x*pi/180).n()

cancel_value = False

def get_tan(x):
    global cancel_value
    
    value = tan(x*pi/180).n()
    
    if type(value) == ComplexInfinity:
        cancel_value = True
    
    return value

def function_get_y(x: int | float):
    return eval(function, {'x':x, 'sin':get_sin, 'cos':get_cos, 'tan':get_tan, 'pi':pi})

WIDTH, HEIGHT = 500, 500
LINE_SIZE_RATIO_DEFAULT = 1
line_size_ratio = LINE_SIZE_RATIO_DEFAULT

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Function Graph')

FPS = 60
clock = pygame.time.Clock()

x_axis = pygame.Rect(0,HEIGHT//2, WIDTH,1)
y_axis = pygame.Rect(WIDTH//2,0, 1,HEIGHT)

function_line = []

for x in range(iter_start, iter_end, iter_step):
    for i in range(0,10, 1):
        x += i/10
        y = function_get_y(x)
        if cancel_value: # IMPORTANT SLICE OF CODE TO PUT TOGETHER WITH THE y(x) FUNCTION!! (for example: for "int(tan(x*100))")
            cancel_value = False
            continue

        rect = pygame.Rect(x+x_axis.width//2,-y+y_axis.height//2, line_size_ratio,line_size_ratio)
        
        if rect in function_line:
            continue

        function_line.append(rect)
        if not count_float_numbers:
            break

def get_rect_pos_in_graph(rect: pygame.Rect):
    return (rect.x-x_axis.width//2, -(rect.y-y_axis.height//2))

offset_x = 0
offset_y = 0

pos_text_surface = None
show_pos_rect = None

running = True
while running:
    clock.tick(FPS)
    window.fill(BACKGROUND_COLOR)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        elif event.type == pygame.MOUSEWHEEL:
            if event.y == 1:
                line_size_ratio += 5
            elif event.y == -1:
                line_size_ratio -= 5
                if line_size_ratio <= 0:
                    line_size_ratio = 1
    
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_a]:
        offset_x += 5
    elif keys[pygame.K_d]:
        offset_x -= 5
    
    if keys[pygame.K_w]:
        offset_y += 5
    elif keys[pygame.K_s]:
        offset_y -= 5

    mouse_pos = pygame.mouse.get_pos()

    x_axis.y += offset_y
    y_axis.x += offset_x

    pygame.draw.rect(window, X_AXIS_COLOR, x_axis)
    pygame.draw.rect(window, Y_AXIS_COLOR, y_axis)

    x_axis.y -= offset_y
    y_axis.x -= offset_x

    show_pos = False
    for rect in function_line:
        rect.size = (line_size_ratio, line_size_ratio)
        
        rect.topleft = (rect.x+offset_x-line_size_ratio//2, rect.y+offset_y-line_size_ratio//2)
        
        pygame.draw.rect(window, VERTEX_COLOR, rect)

        if rect.colliderect([*mouse_pos, 1,1]):
            show_pos = True
            if rect != show_pos_rect:
                show_pos_rect = rect
                pos_text_surface = None
        
        rect.topleft = (rect.x-offset_x+line_size_ratio//2, rect.y-offset_y+line_size_ratio//2)

        if show_pos and not pos_text_surface:
            pos_text_surface = write_text(str(get_rect_pos_in_graph(rect)))

    if show_pos:
        window.blit(pos_text_surface, (mouse_pos[0]+10, mouse_pos[1]-10))
    else:
        pos_text_surface = None

    pygame.display.flip()