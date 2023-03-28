# Tank game for two players
# Python 3.8.10
import pygame
import math
from copy import deepcopy
import random

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((1280, 720))
font = pygame.freetype.SysFont('Comic Sans MS', 30)

clock = pygame.time.Clock()
running = True
dt = 0
message = ""
waiting_for_restart = False
waiting_for_start = True
max_damage = 1

# tank 1
angle = 90
tank1dx = -math.cos(math.radians(angle))
tank1dy = math.sin(math.radians(angle))
turrent_angle = angle
tank1damage = 0
tank1_pos = pygame.Vector2(screen.get_width()/5, screen.get_height() / 2)
bullet1_pos = []
firedtime1 = 0
tank1speed=1.0
savedtank1speed = tank1speed
blownup1= False

# tank 2
angle2 = 270
tank2dx = -math.cos(math.radians(angle2))
tank2dy = math.sin(math.radians(angle2))
turrent_angle2 = angle2
tank2damage = 0
tank2_pos = pygame.Vector2(screen.get_width()*4/5, screen.get_height() / 2)
bullet2_pos = []
firedtime2 = 0
tank2speed=1.0
savedtank2speed = tank2speed
blownup= False

s = "*"
caption = "Tank1 health: "+''.join([char*(max_damage+1-tank1damage) for char in s])+"                                         Tank2 health: "+''.join([char*(max_damage+1-tank2damage) for char in s])
pygame.display.set_caption(caption) 

# walls, can't drive or shoot through
walls = []
for i in range(0,10):
    while True: # Don't trap tank inside a wall
        wall = pygame.Rect(random.randrange(0,screen.get_width()), random.randrange(0,screen.get_height()), random.randrange(2,screen.get_height()/8), random.randrange(2, screen.get_height()/8))
        if not (wall.colliderect(tank1_pos.x-12,tank1_pos.y-6, 24, 12) or wall.colliderect(tank2_pos.x-12,tank2_pos.y-6, 24, 12)):
            break 
    walls.append(wall)

# forests, tanks can hide in these
forests = []
for i in range(0,6):
    forest = pygame.Rect(random.randrange(0,screen.get_width()), random.randrange(0,screen.get_height()), random.randrange(20,screen.get_height()/4), random.randrange(20,screen.get_height()/4))
    forests.append(forest)

# swamps, slows tank's movement
swamps = []
for i in range(0,10):
    swamp = pygame.Rect(random.randrange(0,screen.get_width()), random.randrange(0,screen.get_height()), random.randrange(10,screen.get_height()/4), random.randrange(10,screen.get_height()/4))
    swamps.append(swamp)    

# mines, blows up tank           
mines = []
for i in range(0,50):
    mine = pygame.Rect(random.randrange(0,screen.get_width()), random.randrange(0,screen.get_height()), 10, 10)
    if not (mine.colliderect(tank1_pos.x-12,tank1_pos.y-6, 24, 12) and mine.colliderect(tank2_pos.x-12,tank2_pos.y-6, 24, 12)):
        mines.append(mine) # Remove mines under tanks 

# Remove mines from swamps and forests
for swamp in swamps:
    for mine in mines:
        if mine.colliderect(swamp):
            mines.remove(mine)

for forest in forests:
    for mine in mines:
        if mine.colliderect(forest):
            mines.remove(mine)

def rectRotated2( surface, color, pos, rotation_angle, rotation_offset_center = (0,0), nAntialiasingRatio = 1 ):
    """
    - rotation_angle: in degree
    - rotation_offset_center: moving the center of the rotation: (-100,0) will turn the rectangle around a point 100 above center of the rectangle,
                                            if (0,0) the rotation is at the center of the rectangle
    - nAntialiasingRatio: set 1 for no antialising, 2/4/8 for better aliasing
    """
    nRenderRatio = nAntialiasingRatio
    
    sw = pos[2]+abs(rotation_offset_center[0])*2
    sh = pos[3]+abs(rotation_offset_center[1])*2

    surfcenterx = sw//2
    surfcentery = sh//2
    s = pygame.Surface( (sw*nRenderRatio,sh*nRenderRatio) )
    s = s.convert_alpha()
    s.fill((0,0,0,0))
    
    rw2=pos[2]//2 # halfwidth of rectangle
    rh2=pos[3]//2

    pygame.draw.rect( s, color, ((surfcenterx-rw2-rotation_offset_center[0])*nRenderRatio,(surfcentery-rh2-rotation_offset_center[1])*nRenderRatio,pos[2]*nRenderRatio,pos[3]*nRenderRatio) )
    s = pygame.transform.rotate( s, rotation_angle )        
    if nRenderRatio != 1: s = pygame.transform.smoothscale(s,(s.get_width()//nRenderRatio,s.get_height()//nRenderRatio))
    incfromrotw = (s.get_width()-sw)//2
    incfromroth = (s.get_height()-sh)//2
    surface.blit( s, (pos[0]-surfcenterx+rotation_offset_center[0]+rw2-incfromrotw,pos[1]-surfcentery+rotation_offset_center[1]+rh2-incfromroth) )  
    
while running:                                                              
    # pygame.QUIT event means the user clicked X to close window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # erase last screen
    screen.fill((158,154,117))
    for wall in walls:
        pygame.draw.rect(screen,(28,34,46),wall)    
        for bullet in bullet1_pos:
            if wall.collidepoint(bullet[0].x, bullet[0].y):
                bullet1_pos.remove(bullet)
        for bullet in bullet2_pos:
            if wall.collidepoint(bullet[0].x, bullet[0].y):
                bullet2_pos.remove(bullet)
        if (wall.colliderect(tank1_pos.x-12,tank1_pos.y-6, 24, 12)):
            tank1_pos.x -= tank1dx*3 # back up tank on collision so doesn't get stuck
            tank1_pos.y -= tank1dy*3
            tank1dx = 0
            tank1dy = 0
        if (wall.colliderect(tank2_pos.x-12,tank2_pos.y-6, 24, 12)):
            tank2_pos.x -= tank2dx*3
            tank2_pos.y -= tank2dy*3
            tank2dx = 0
            tank2dy = 0  

    tank1inswamp = False   
    tank2inswamp = False  
    for swamp in swamps:
        pygame.draw.rect(screen,(96,68,57),swamp) 
        if (swamp.colliderect(tank1_pos.x-12,tank1_pos.y-6, 24, 12)):
            tank1inswamp = True
        if (swamp.colliderect(tank2_pos.x-12,tank2_pos.y-6, 24, 12)):
            tank2inswamp = True 

    if tank1inswamp: # Because the tank slows after 1 hit, need to restore to the movement before entered swamp
        tank1speed=min(tank1speed, 0.33)
    else:
        tank1speed=savedtank1speed

    if tank2inswamp:
        tank2speed=min(tank2speed, 0.33)
    else:
        tank2speed=savedtank2speed              

    if (tank1_pos.x <= 0 or tank1_pos.y <= 0 or tank1_pos.x > screen.get_width() or tank1_pos.y > screen.get_height()):
        tank1_pos.x -= tank1dx*3
        tank1_pos.y -= tank1dy*3
        tank1dx = 0
        tank1dy = 0    

    if (tank2_pos.x <= 0 or tank2_pos.y <= 0 or tank2_pos.x > screen.get_width() or tank2_pos.y > screen.get_height()):
        tank2_pos.x -= tank2dx*3
        tank2_pos.y -= tank2dy*3
        tank2dx = 0
        tank2dy = 0

    for mine in mines:
        pygame.draw.line(screen, "black", mine.topleft, mine.bottomright, 1)
        pygame.draw.line(screen, "black", mine.bottomleft, mine.topright, 1)
        if (mine.colliderect(tank1_pos.x-12,tank1_pos.y-6, 24, 12)): 
            pygame.display.set_caption("Tank 1 blown up by a mine. Tank2 wins!")
            message = "Press spacebar to restart"
            waiting_for_restart = True
        if (mine.colliderect(tank2_pos.x-12,tank2_pos.y-6, 24, 12)): 
            pygame.display.set_caption("Tank 2 blown up by a mine. Tank1 wins!")
            message = "Press spacebar to restart"
            waiting_for_restart = True

    t1rect = pygame.Rect(tank1_pos.x-12,tank1_pos.y-6, 24, 12)                            
    t2rect = pygame.Rect(tank2_pos.x-12,tank2_pos.y-6, 24, 12)                            
    if (t1rect.colliderect(t2rect)):
        tank1_pos.x -= tank1dx*3 # back up tank on collision so doesn't get stuck
        tank1_pos.y -= tank1dy*3
        tank1dx = 0
        tank1dy = 0   
        tank2_pos.x -= tank2dx*3
        tank2_pos.y -= tank2dy*3
        tank2dx = 0
        tank2dy = 0        

    rectRotated2(screen, "black", (tank1_pos.x-12,tank1_pos.y-6, 24, 12), angle)
    rectRotated2(screen, "gray", (tank1_pos.x-12-math.cos(math.radians(turrent_angle))*5,tank1_pos.y-6+6-2+math.sin(math.radians(turrent_angle))*5, 24, 4), turrent_angle)
    pygame.draw.circle(screen, "gray", (tank1_pos.x,tank1_pos.y),5)
    rectRotated2(screen, "black", (tank2_pos.x-12,tank2_pos.y-6, 24, 12), angle2)
    rectRotated2(screen, "gray", (tank2_pos.x-12-math.cos(math.radians(turrent_angle2))*5,tank2_pos.y-6+6-2+math.sin(math.radians(turrent_angle2))*5, 24, 4), turrent_angle2)    
    pygame.draw.circle(screen, "gray", (tank2_pos.x,tank2_pos.y),5)

    if (len(bullet1_pos) > 0):
        for bullet in bullet1_pos: 
            pygame.draw.rect(screen,"red",(bullet[0].x, bullet[0].y, 4, 4))        
            bullet[0].x += bullet[1].x # [1] are the dx and dy values
            bullet[0].y += bullet[1].y
            if ((bullet[0].x > tank2_pos.x-12 and bullet[0].x < tank2_pos.x+12) and (bullet[0].y > tank2_pos.y-12 and bullet[0].y < tank2_pos.y+12)):
                bullet1_pos.remove(bullet) 
                tank2speed = tank2speed * 0.75
                savedtank2speed = tank2speed # saved speed is used to restore speed after leaving a swamp
                tank2damage += 1
                caption = "Tank1 health: "+''.join([char*(max_damage+1-tank1damage) for char in s])+"                                         Tank2 health: "+''.join([char*(max_damage+1-tank2damage) for char in s])
                pygame.display.set_caption(caption) 
                if (tank2damage > max_damage):
                    pygame.display.set_caption("Tank1 wins!")
                    message = "Press spacebar to restart"
                    waiting_for_restart = True

            if (bullet[0].x < 0 or bullet[0].y < 0 or bullet[0].x > screen.get_width() or bullet[0].y > screen.get_height()):
                bullet1_pos.remove(bullet) 

    if (len(bullet2_pos) > 0):
        for bullet in bullet2_pos: 
            pygame.draw.rect(screen,"red",(bullet[0].x, bullet[0].y, 4, 4))        
            bullet[0].x += bullet[1].x
            bullet[0].y += bullet[1].y
            if ((bullet[0].x > tank1_pos.x-12 and bullet[0].x < tank1_pos.x+12) and (bullet[0].y > tank1_pos.y-12 and bullet[0].y < tank1_pos.y+12)):
                bullet2_pos.remove(bullet) 
                tank1speed = tank1speed * 0.75
                savedtank1speed = tank1speed
                tank1damage += 1
                caption = "Tank1 health: "+''.join([char*(max_damage+1-tank1damage) for char in s])+"                                         Tank2 health: "+''.join([char*(max_damage+1-tank2damage) for char in s])
                pygame.display.set_caption(caption)                  
                if (tank1damage > max_damage):
                    pygame.display.set_caption("Tank2 wins!")  
                    message = "Press spacebar to restart"
                    waiting_for_restart = True                 

            if (bullet[0].x < 0 or bullet[0].y < 0 or bullet[0].x > screen.get_width() or bullet[0].y > screen.get_height()):
                bullet2_pos.remove(bullet)    

    for forest in forests:
        pygame.draw.rect(screen,(65,83,59),forest)  

    if (waiting_for_start):
        font.render_to(screen, (screen.get_width()/4-100, 150), "WASD to move", (0, 0, 0))  
        font.render_to(screen, (screen.get_width()/4-100, 200), "B/N rotate turret", (0, 0, 0))          
        font.render_to(screen, (screen.get_width()/4-100, 250), "V to fire", (0, 0, 0))                 
        font.render_to(screen, (screen.get_width()*3/4-100, 150), "Arrows to move", (0, 0, 0))          
        font.render_to(screen, (screen.get_width()*3/4-100, 200), "F9/F10 rotate turret", (0, 0, 0))          
        font.render_to(screen, (screen.get_width()*3/4-100, 250), "F11 to fire", (0, 0, 0))          

    if (waiting_for_restart):
        font.render_to(screen, (screen.get_width()/2-100, 350), "Press spacebar to restart", (0, 0, 0))                  

    keys = pygame.key.get_pressed()

    if waiting_for_restart and keys[pygame.K_SPACE]: # Restart the game
        message = ""
        waiting_for_restart = False
        waiting_for_start = True

        # tank 1
        angle = 90
        tank1dx = -math.cos(math.radians(angle))
        tank1dy = math.sin(math.radians(angle))
        turrent_angle = angle
        tank1damage = 0
        tank1_pos = pygame.Vector2(screen.get_width()/5, screen.get_height() / 2)
        bullet1_pos.clear()
        firedtime1 = 0
        tank1speed=1.0
        savedtank1speed = tank1speed
        blownup1= False

        # tank 2
        angle2 = 270
        tank2dx = -math.cos(math.radians(angle2))
        tank2dy = math.sin(math.radians(angle2))
        turrent_angle2 = angle2
        tank2damage = 0
        tank2_pos = pygame.Vector2(screen.get_width()*4/5, screen.get_height() / 2)
        bullet2_pos.clear()
        firedtime2 = 0
        tank2speed=1.0
        savedtank2speed = tank2speed
        blownup2= False

    if (not waiting_for_restart): # Stop controls when game is over
        # tank 1 controls
        if keys[pygame.K_w]:
            tank1_pos.x += tank1dx*tank1speed
            tank1_pos.y += tank1dy*tank1speed
            waiting_for_start = False
            caption = "Tank1 health: "+''.join([char*(max_damage+1-tank1damage) for char in s])+"                                         Tank2 health: "+''.join([char*(max_damage+1-tank2damage) for char in s])
            pygame.display.set_caption(caption)           
        if keys[pygame.K_s]:
            tank1_pos.x -= tank1dx*tank1speed*0.5
            tank1_pos.y -= tank1dy*tank1speed*0.5
        if keys[pygame.K_a]:
            angle = angle + 1
            turrent_angle = turrent_angle + 1
            tank1dx = -math.cos(math.radians(angle))
            tank1dy = math.sin(math.radians(angle))
        if keys[pygame.K_d]:
            angle = angle - 1
            turrent_angle = turrent_angle - 1
            tank1dx = -math.cos(math.radians(angle))
            tank1dy = math.sin(math.radians(angle))
        if keys[pygame.K_v]:
            if (pygame.time.get_ticks() > firedtime1+1000):
                bulletd = pygame.Vector2(-math.cos(math.radians(turrent_angle))*2, math.sin(math.radians(turrent_angle))*2)
                bullet = [deepcopy(tank1_pos), bulletd]
                bullet1_pos.append(bullet)
                firedtime1= pygame.time.get_ticks()
        if keys[pygame.K_b]:
            turrent_angle += 1 
        if keys[pygame.K_n]:
            turrent_angle -= 1     

        # tank 2 controls
        if keys[pygame.K_UP]:
            tank2_pos.x += tank2dx*tank2speed
            tank2_pos.y += tank2dy*tank2speed
            waiting_for_start = False
            caption = "Tank1 health: "+''.join([char*(max_damage+1-tank1damage) for char in s])+"                                         Tank2 health: "+''.join([char*(max_damage+1-tank2damage) for char in s])
            pygame.display.set_caption(caption)  
        if keys[pygame.K_DOWN]:
            tank2_pos.x -= tank2dx*tank2speed*0.5
            tank2_pos.y -= tank2dy*tank2speed*0.5
        if keys[pygame.K_LEFT]:
            angle2 = angle2 + 1
            turrent_angle2 = turrent_angle2 + 1
            tank2dx = -math.cos(math.radians(angle2))
            tank2dy = math.sin(math.radians(angle2))
        if keys[pygame.K_RIGHT]:
            angle2 = angle2 - 1
            turrent_angle2 = turrent_angle2 - 1
            tank2dx = -math.cos(math.radians(angle2))
            tank2dy = math.sin(math.radians(angle2))
        if keys[pygame.K_F11] or keys[pygame.K_c]: # c/z/x are for when using 2 keyboards
            if (pygame.time.get_ticks() > firedtime2+1000): # fire only once per second
                bulletd = pygame.Vector2(-math.cos(math.radians(turrent_angle2))*2, math.sin(math.radians(turrent_angle2))*2)
                bullet = [deepcopy(tank2_pos), bulletd]
                bullet2_pos.append(bullet)
                firedtime2= pygame.time.get_ticks()
        if keys[pygame.K_F9] or keys[pygame.K_z]:
            turrent_angle2 += 1 
        if keys[pygame.K_F10] or keys[pygame.K_x]:
            turrent_angle2 -= 1   

    # flip() blit drawing to screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()