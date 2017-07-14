import pygame
import sys
import random
import math
from pygame.locals import *


FPS = 30
MAPWIDTH = 500
LEFTPANNEL = 0
RIGHTPANNEL = 100
BOTTOMPANNEL = 0
MAPHEIGHT = 300
WINDOWWIDTH = MAPWIDTH + LEFTPANNEL + RIGHTPANNEL
WINDOWHEIGHT = MAPHEIGHT + BOTTOMPANNEL
DIMENSIONX = 20
DIMENSIONY = 15
SCROLLSPEED = 5

pygame.display.set_caption('rpga')


#Colors
BLACK = (0,0,0)
WHITE = (255, 255, 255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)



def main():
    global DISPLAYSURF, HEXIMG, GRASSIMG, UNITIMG, GAP
    pygame.init()
    fontObj = pygame.font.Font('freesansbold.ttf', 16)
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    GAP = 0
    HEXIMG = pygame.image.load('hextile.png')
    GRASSIMG = pygame.image.load('grass.png')
    UNITIMG = pygame.image.load('unittest.png')


    CAMERAMAXX = (DIMENSIONX - 2)*48 + 16 - MAPWIDTH
    CAMERAMAXY = (DIMENSIONY)*56 - 28 - MAPHEIGHT
    new_map = generate_map_hexes_coordinates(DIMENSIONX, DIMENSIONY)
    camera = Camera(0, 0, SCROLLSPEED, CAMERAMAXX, CAMERAMAXY)
    moveTuple = (False,False,False,False)
    hexClick = False
    DISPLAYSURF.fill(BLACK)

    unit_selected = None
    mousex = 0
    mousey = 0

    while True:
        mouseClicked = False
        movement = False

        checkForQuit()
        moveTuple = movementManager(camera, moveTuple)
        mousex, mousey, mouseClicked = mouseManager(mousex, mousey, mouseClicked)


        unit_selected = move_unit(mousex, mousey, camera, mouseClicked, unit_selected, new_map)

        draw_map(new_map,camera)

        #menu drawing
        pygame.draw.rect(DISPLAYSURF, WHITE, (LEFTPANNEL+MAPWIDTH, 0, RIGHTPANNEL, WINDOWHEIGHT) )
        displayCoordinates(mousex, mousey, camera, fontObj)
        displayUnitInfo(unit_selected, mousex, mousey, camera, new_map, fontObj)

        #loop update
        pygame.display.update()
        FPSCLOCK.tick(FPS)


########################
#                      #
#   Event Management   #
#                      #
########################


def move_unit(mousex, mousey, camera, mouseClicked, unit_selected, new_map):
    (x,y) = camera.camera_to_game((mousex, mousey))
    (hx, hy) = pixel_to_hex(x,y)

    if mouseClicked == True and is_on_map((mousex,mousey)):
        if unit_selected == None:
            unit_selected = new_map[hx][hy].get_unit()
        elif unit_selected != None :
            unit_x, unit_y = unit_selected.get_location()
            ux, uy, uz = cube_coord(unit_x,unit_y)
            distance = new_map[hx][hy].distance(ux,uy,uz)
            if distance == 0:
                unit_selected = None
            elif unit_selected.get_movement() >= distance and moveable_location(hx,hy) and new_map[hx][hy].get_unit() == None:
                unit_selected.set_location(hx,hy)
                new_map[unit_x][unit_y].set_unit(None)
                new_map[hx][hy].set_unit(unit_selected)
                unit_selected = None

    return unit_selected


def draw_map(new_map, camera):
    for x in new_map:
        for h in x:
            #Map layer
            DISPLAYSURF.blit(h.img(),camera.game_to_camera(h.pix()))
            #Unit layer
            unit = h.get_unit()
            if unit:
                DISPLAYSURF.blit(unit.img(),camera.game_to_camera(h.pix()))


def displayCoordinates(mousex, mousey, camera, fontObj):
    xmargin = 32
    ymargin = 28
    (x,y) = camera.camera_to_game((mousex, mousey))
    (hx, hy) = pixel_to_hex(x,y)
    if is_on_map((mousex,mousey)):
        textSurfaceObj = fontObj.render("{},{}".format(hx,hy),True, BLACK)
        textRectObj = textSurfaceObj.get_rect()
        textRectObj.center = (MAPWIDTH+xmargin,ymargin)
        DISPLAYSURF.blit(textSurfaceObj, textRectObj)


def displayUnitInfo(unit, mousex, mousey, camera, new_map, fontObj):
    #If no unit is selected, display info for unit hovered over
    info_unit = None
    if unit == None and is_on_map((mousex, mousey)):
        (x,y) = camera.camera_to_game((mousex, mousey))
        (hx, hy) = pixel_to_hex(x,y)
        info_unit = new_map[hx][hy].get_unit()
    else:
        info_unit = unit
    if info_unit != None:
        ux, uy = info_unit.get_location()
        movement = info_unit.get_movement()
        name = info_unit.get_name()
        health = info_unit.get_health()

        nameObj = fontObj.render("{}".format(name), True, BLACK)
        nameRect = nameObj.get_rect()
        nameRect.center = (MAPWIDTH+10,50)
        DISPLAYSURF.blit(nameObj, nameRect)

        locObj = fontObj.render("{},{}".format(ux,uy),True, BLACK)
        locRect = locObj.get_rect()
        locRect.center = (MAPWIDTH+10,65)
        DISPLAYSURF.blit(locObj, locRect)

        healthObj = fontObj.render("health: {}".format(health), True, BLACK)
        healthRect = healthObj.get_rect()
        healthRect.center = (MAPWIDTH+10,80)
        DISPLAYSURF.blit(healthObj, healthRect)

        moveObj = fontObj.render("speed: {}".format(movement), True, BLACK)
        moveRect = moveObj.get_rect()
        moveRect.center = (MAPWIDTH+10,95)
        DISPLAYSURF.blit(moveObj, moveRect)


def mouseManager(mousex, mousey, mouseClicked):
    for event in pygame.event.get():
        if event.type == MOUSEMOTION:
            mousex, mousey = event.pos
        elif event.type == MOUSEBUTTONUP:
            mousex, mousey = event.pos
            mouseClicked = True
    return mousex, mousey, mouseClicked


def movementManager(camera, moveTuple):
    (moveUp, moveDown, moveLeft, moveRight) = moveTuple

    #check for movement input
    for event in pygame.event.get():
        #last key down use
        if event.type == KEYDOWN:
            if event.key == K_w:
                moveUp = True
                moveDown = False
            elif event.key == K_s:
                moveDown = True
                moveUp = False
            elif event.key == K_a:
                moveLeft = True
                moveRight = False
            elif event.key == K_d:
                moveRight = True
                moveLeft = False

        #Stop on key up
        elif event.type == KEYUP:
            if event.key == K_w:
                moveUp = False
            elif event.key == K_s:
                moveDown = False
            elif event.key == K_a:
                moveLeft = False
            elif event.key == K_d:
                moveRight = False

        pygame.event.post(event)

    #change camera
    if moveUp:
        camera.move_up()
    if moveDown:
        camera.move_down()
    if moveLeft:
        camera.move_left()
    if moveRight:
        camera.move_right()

    return (moveUp,moveDown,moveLeft,moveRight)


def checkForQuit():
    for event in pygame.event.get(QUIT):
        terminate()
    key_q = False
    key_command = False
    for event in pygame.event.get(KEYUP):
        if event.key == K_ESCAPE:
            terminate()
        pygame.event.post(event)
    


########################
#                      #
#        Misc          #
#                      #
########################


def terminate():
    pygame.quit()
    sys.exit()


########################
#                      #
# Coordinate Functions #
#                      #
########################

def reachable(start, movement, new_map):
    visited = [start]
    fringes = []
    fringes.append(visited)

    for k in range(1, movement + 1):
        fringes.append([])
        for hexes in fringe[k - 1]:
            for location in hexes.neighbors():
                (x, y, z) = location
                hx, hy = offset_coord(x, y, z)
                if is_on_map((hx,hy)) and new_map[hx][hy] not in visited and new_map[hx][hy].is_open():
                    visited.append(new_map[hx][hy])
                    fringes[k].append(new_map[hx][hy])
    return visited


def is_on_map(location):
    x, y = location
    left = (x >= LEFTPANNEL)
    right = (x < LEFTPANNEL + MAPWIDTH)
    bottom = (y < MAPHEIGHT)
    return left and right and bottom


def moveable_location(hx,hy):
    #left check
    if hx == 0:
        return False
    #top check
    if hy == 0 and hx % 2 == 0:
        return False
    #right check
    if hx == DIMENSIONX -1:
        return False
    #bottom check
    if hy == DIMENSIONY -1 and hx % 2 ==1: #check for other map dimesions
        return False
    return True



def generate_map_hexes_coordinates(width, height):
    offset_map = []
    for x in  range(width):
        offset_map.append([])
        for y in range(height):
            if x == 2 and y ==2:
                offset_map[x].append(Hex(col=x, row=y, unit=Unit('Saul', 4, x, y)))
            else:
                offset_map[x].append(Hex(x,y))

    return offset_map


def offset_coord(x, y, z):
    #odd-q offset coordinates
    col = x
    row = z + (x- (x&1)) / 2
    return (col, row)


def cube_coord(col, row):
    x = col
    z = row - (col - (col&1)) / 2
    y = -x - z
    return (x, y, z)


def pixel_coord(col, row):
    start_x = -48
    start_y = -28
    x = start_x + col*(48 + GAP)
    y = start_y + row*(56 +GAP) + (col&1)*28
    return (x,y)


def pixel_to_hex(x, y):
    """
    1. Partitions map into rectanges with corners at each hex images relative (0,0) coordinate
    2. Guesses the hex column from the rectange column
    3. Finds the slope direction of the hex
    4. Uses this in combination with slope equation to determine which column is correct
        a or b in the diragram below
    --------------------------------
    | b /          |\              |
    |  /           | \      a      | 
    | /      a     |  \            |  
    |/             | b \           |
    --------------------------------
    5. Use column parity and y value to determine row
    """
    start_x = -48
    start_y = -28
    # Guesses at the proper column. Will never underestimate
    guess_col = int(math.floor(1.0*(x - start_x)/48))

    # determines slope direction of guess_col hex at y local
    # 1 is up & right, 0 is down & right
    slope = ( (guess_col&1) + int(math.floor(1.0*y/28)) )&1

    x_1 = x % 48
    y_1 = y % 28
    if slope == 1:
        slope_sum = y_1 + 27.0*x_1/16 #slope of edge
        if  slope_sum> 26.25:
            col = guess_col
        else:
            col = guess_col -1
    elif slope == 0:
        slope_sum = 27.0*x_1/16
        if y_1 < slope_sum:
            col = guess_col
        else:
            col = guess_col -1

    row = int(math.floor(1.0* (y+((col+1)&1)*28) /56))

    return (col, row)


#######################
#                     #
#      Hex Class      #
#                     #
#######################

class Hex:
    def __init__(self, col, row, terrain = 'grass', unit = None):
        (x, y, z) = cube_coord(col, row)
        (pixx, pixy) = pixel_coord(col, row)
        self.x = x
        self.y = y
        self.z = z
        self.col = col
        self.row = row
        self.pixx = pixx
        self.pixy = pixy
        self.terrain = terrain
        self.unit = unit


    def neighbors(self):
        return [(self.x + 1, self.y - 1, self.z), (self.x + 1, self.y, self.z - 1), (self.x, self.y + 1, self.z - 1)
                (self.x - 1, self.y + 1, self.z), (self.x - 1, self.y, self.z + 1), (self.x, self.y - 1, self.z + 1)
                ]


    def distance(self,x,y,z):
        distance = (abs(self.x-x)+abs(self.y-y)+abs(self.z-z)) / 2
        return distance


    def pix(self):
        return (self.pixx, self.pixy)


    def get_unit(self):
        return self.unit


    def set_unit(self, unit):
        self.unit = unit


    def is_open(self):
        if self.unit == None:
            return True
        else:
            return False

    def img(self):
        if self.terrain == 'grass':
            return GRASSIMG
        else:
            return HEXIMG


#######################
#                     #
#      Unit Class     #
#                     #
#######################

class Unit:
    def __init__(self, name, movement, col, row, kind = 'test', health = 10):
        self.name = name
        self.movement = movement
        self.col = col
        self.row = row
        self.kind = kind
        self.health = health

    def get_health(self):
        return self.health


    def get_location(self):
        return (self.col, self.row)


    def set_location(self, col, row):
        self.col = col
        self.row = row


    def get_name(self):
        return self.name


    def get_movement(self):
        return self.movement


    def img(self):
        if self.kind == 'test':
            return UNITIMG
        else:
            return


#######################
#                     #
#    Camera Class     #
#                     #
#######################


class Camera:
    def __init__(self, x, y, scrollspeed, maxx, maxy):
        self.x = x
        self.y = y
        self.scrollspeed = scrollspeed
        self.maxx = maxx
        self.maxy = maxy


    def get_camera(self):
        return (self.x, self.y)


    def set_camera(self,x,y):
        if x > self.maxx:
            self.x = self.maxx
        elif x< 0:
            self.x = 0
        else:
            self.x = x

        if y > self.maxy:
            self.y = self.maxy
        elif y < 0:
            self.y = 0
        else:
            self.y = y 


    def move_up(self):
        y = self.y - self.scrollspeed
        self.set_camera(self.x,y)


    def move_down(self):
        y = self.y + self.scrollspeed
        self.set_camera(self.x,y)


    def move_left(self):
        x = self.x - self.scrollspeed
        self.set_camera(x,self.y)


    def move_right(self):
        x = self.x + self.scrollspeed
        self.set_camera(x,self.y)


    def game_to_camera(self, pixel):
        #convert game coordinates to camera coordinates
        (pixx,pixy) = pixel
        return (pixx-self.x, pixy-self.y)


    def camera_to_game(self, location):
        #convert camera coordinates (location on screen) to camera coordinates
        (locx,locy) = location
        return (self.x+locx,self.y+locy)


if __name__ == '__main__':
    main()