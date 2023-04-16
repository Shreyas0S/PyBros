import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join
pygame.init()

pygame.display.set_caption("Platformer")

WIDTH, HEIGHT = 1000, 800-800%96
FPS = 60
PLAYER_VEL = 5
PLAYER_X=100
PLAYER_Y=HEIGHT-300

orb_count=0
GRAVITY=1

offset_x = 0
window = pygame.display.set_mode((WIDTH, HEIGHT))

def flip(sprites):
    '''flips sprites
    pygame.transform.flip(sprite,flip_in_x_dir?,flip_in_y_dir?)'''
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites

def get_key(size):
    width=size
    height=size
    path = join("assets", "Items/Keys", "key.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0, 0, width, height)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale_by(surface,1/16)


def get_Doors(width,height):
    path=join("assets","Items/Doors","animatedcastledoors.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((width,height), pygame.SRCALPHA,32)
    rect = pygame.Rect(0,0,width,height)
    surface.blit(image,(0,0),rect)
    rect=pygame.Rect(328,0,width,height)
    surface.blit(image,(5,0),rect)
    surfaces=[]
    surfaces.append(surface.copy())
    rect=pygame.Rect(72,0,width,height)
    surface.blit(image,(6,0),rect)
    surfaces.append(surface)
    return surfaces

def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

def get_moving_block(size):
    path = join("assets", "Items/Boxes/Box1", "Idle.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


def get_spike(width,height,flip):
    path = join("assets", "Traps/Spikes", "Idle.png")
    image = pygame.image.load(path).convert_alpha()
    if flip:
        image=pygame.transform.flip(image,False,flip)
        surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
        rect = pygame.Rect(0, 0, width, height)
    else:
        image=pygame.transform.flip(image,False,flip)
        surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
        rect = pygame.Rect(0, 8, width, height)

    surface.blit(image,(0,0), rect)
    return pygame.transform.scale2x(pygame.transform.scale2x(surface))

def get_platform(width,height):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((width,height), pygame.SRCALPHA, 32)
    rect = pygame.Rect(48, 0, width,height)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

class Player(pygame.sprite.Sprite):
    global GRAVITY
    COLOR = (255, 0, 0)
    SPRITES = load_sprite_sheets("MainCharacters", "VirtualGuy", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0

    def reset(self):
        global offset_x
        offset_x=0
        self.rect.x = PLAYER_X
        self.rect.y = PLAYER_Y
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0

    def jump(self):
        self.y_vel = -GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        if(self.rect.y>HEIGHT):  #changed 
            self.reset()


    def make_hit(self):
        self.hit = True

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0
        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        if self.hit:
            if self.animation_count//self.ANIMATION_DELAY > 3*len(sprites):   #changed to reset once hit
                self.reset()
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)#tells where there are pixels of characters , not of rectangle box

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

class Key(Object):
    def __init__(self, x, y, width=16, height=16):
        super().__init__(x, y, width, height, "key")
        self.key = load_sprite_sheets("Items", "Keys", width, height)
        self.image = self.key["On"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "On"

    def on(self):
        self.animation_name = "On"

    def off(self):
        self.animation_name = "Off"

    def update(self):
        self.image=self.key[self.animation_name][0]


class Spike(Object):
    def __init__(self, x, y,width=64,height=32,flip=False):
        super().__init__(x, y,width,height,"trap")
        spike = get_spike(width,height,flip)
        self.image.blit(spike, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)           

class Block(Object):
    def __init__(self, x, y,size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class Platform(Object):
    ANIMATION_DELAY = 3
    width=32 
    height=8
    def __init__(self, x, y,vel):
        super().__init__(x, y, Platform.width, Platform.height,"platform")
        self.vel=vel
        self.platform = load_sprite_sheets("Traps", "Platforms", Platform.width, Platform.height)
        self.image = self.platform["Grey Off"][0]
        self.mask = pygame.mask.from_surface(self.image)

        self.animation_count = 0
        self.animation_name = "Grey Off"
        self.state="right" #whether to move right or left

    def update(self, x1, x2, player):
        if self.state == "right":
            self.animation_name = "Grey On"
        elif self.state == "left":
            self.animation_name = "Grey On"

        self.animation_count += 1
        if self.animation_count >= len(self.platform[self.animation_name]) * Platform.ANIMATION_DELAY:
            self.animation_count = 0
        self.image = self.platform[self.animation_name][self.animation_count // Platform.ANIMATION_DELAY]

        if self.state == "right":
            if pygame.sprite.collide_mask(player, self):
                player.move_right(self.vel)
            self.rect.x += self.vel
        elif self.state == "left":
            if pygame.sprite.collide_mask(player, self):
                player.move_left(self.vel)
            self.rect.x -= self.vel

        if self.rect.right >= x2:
            self.state = "left"
        elif self.rect.left <= x1:
            self.state = "right"

    def on(self):
        self.animation_name = "Grey On"

    def off(self):
        self.animation_name = "Grey Off"

class Doors(Object):
    ANIMATION_DELAY=30
    def __init__(self,x,y,width,height,):
        super().__init__(x,y,width,height,"door")
        self.base_surface,self.image=get_Doors(width,height)
        self.open_door= load_sprite_sheets("Items", "Doors", self.width, self.height)
        self.mask=pygame.mask.from_surface(self.image)
        self.animation_count=0
        self.state="closed"
        self.isKey = False
        for i in range(1,len(self.open_door["animatedcastledoors"])-1):
            self.open_door["animatedcastledoors"][i]=pygame.transform.scale_by(self.open_door["animatedcastledoors"][i],0.5)
        
    def open(self):
        self.animation_count += 1
        if self.animation_count >= (len(self.open_door["animatedcastledoors"])-2) * Doors.ANIMATION_DELAY:
            self.state="open"
            return None
        self.image=self.base_surface.copy()
        self.image.blit(self.open_door["animatedcastledoors"][1+(self.animation_count // Doors.ANIMATION_DELAY)],(0,0))


class Orb(Object): #fire
    ANIMATION_DELAY = 3
    #64,96\
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "orb")
        self.orb = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.orb["on"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "on"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.orb[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image


def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)

    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    collided_objects = []

    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:      
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_move(player, objects):
    global orb_count
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if not player.hit:
        if keys[pygame.K_LEFT] and not collide_left:
            player.move_left(PLAYER_VEL)
        if keys[pygame.K_RIGHT] and not collide_right:
            player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    key_check=[collide_left,collide_right]
    to_check = [collide_left, collide_right, *vertical_collide]
    
    for obj in to_check:
        if obj and obj.name == "orb":
            orb_count+=1
            obj.off()
        if obj and obj.name=="trap":
            player.make_hit()
        if obj and obj.name=="door" and obj.state=="open":
            return False
        if obj and obj.name=="key" and obj in objects:
            obj.off()
            objects.remove(obj)
        if obj and obj.name=="moving_block":
            if player.rect.bottom!=obj.rect.top:
                if player.direction == "right":
                    obj.rect.x+=PLAYER_VEL 
                elif player.direction=="left":
                    obj.rect.x-=PLAYER_VEL
                    
    return True

def display(win,font,x,y):
    global orb_count
    color=(255,255,255)
    score=font.render("Orbs : " + str(orb_count),True,color)
    win.blit(score,(x,y))

def main(window):
    menu() 
    global orb_count
    global offset_x
    font=pygame.font.Font('freesansbold.ttf',32)

    textX= 10 + offset_x
    textY= 10

    clock = pygame.time.Clock()
    background, bg_image = get_background("brick.png")

    block_size = 96
    pit_width=block_size*4

    platform=Platform(864+pit_width//2 , HEIGHT - block_size - 64-10,0)

    player = Player(PLAYER_X, PLAYER_Y, 50, 50)
    orb = [Orb(364-16, HEIGHT - block_size - 150-32, 16, 16),Orb(364+2*96+64+16, HEIGHT - block_size - 150-32, 16, 16),Orb(2*WIDTH-3*block_size-16, HEIGHT - block_size -32, 16, 16)]
    spike=[Spike(300, HEIGHT - block_size - 32),Spike(364,HEIGHT-block_size-32),Spike(364+2*96,HEIGHT-block_size-32),Spike(364+2*96+64,HEIGHT-block_size-32),Spike(364+2*96+2*64,HEIGHT-block_size-32)]
    door=Doors(2*WIDTH-3*block_size+16,HEIGHT - block_size - 96,64,96)
    wall1=[Block(0,i*block_size,block_size) for i in range(1,HEIGHT//block_size-1)] 

    floor1 = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-WIDTH // block_size, (864) // block_size)]
    floor2=[Block(i*block_size,HEIGHT-block_size,block_size) for i in range((864+pit_width)//block_size,2*WIDTH//block_size)]
    ceiling=[Block(i * block_size,0, block_size)
             for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)]
    wall2=[Block(2*WIDTH-2*block_size+16,i*block_size,block_size) for i in range(1,HEIGHT//block_size-1)]

    objects = [*floor1,*floor2,*ceiling,*wall1,*wall2, Block(0, HEIGHT - block_size * 2, block_size), *orb, *spike,platform,door]

    scroll_area_width = 200

    orb_count=0
    run = True
    while run:
        clock.tick(FPS) 

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if not player.hit and event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()
        if not run:
            break

        pygame.display.update()
        #player
        player.loop(FPS)

        #orb
        for i in orb:
            i.loop()
        
        
        #platform
        if platform.animation_name=="Grey On":
            platform.update(100,500,player)

        #door
        if(door.state=="closed" and offset_x>=WIDTH-96): 
            door.open()
 
        run=handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)

        display(window,font,textX,textY)
        pygame.display.update()
        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel
    player.reset()
    run=True
    player.reset()
    door=Doors(block_size*2-16,HEIGHT - block_size - 96,64,96)
    floor1 = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-WIDTH // block_size, 300 // block_size)]
    key=Key(300+pit_width*2,HEIGHT-block_size-32)
    platform1=Platform(300,HEIGHT-block_size-64,3)
    platform1.on()
    floor2=[Block(i*block_size,HEIGHT-block_size,block_size) for i in range((300+pit_width*2)//block_size,2*WIDTH//block_size)]
    orb1=[Orb(block_size*2+56, HEIGHT - block_size -32, 16, 16),Orb(300+pit_width,HEIGHT-block_size-64,16,16),Orb(300+pit_width*2+32,HEIGHT-block_size-32,16,16)]
    objects = [*floor1,*floor2,*ceiling,*wall1,*wall2, Block(0, HEIGHT - block_size * 2, block_size),door,key,platform1,*orb1]
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                if not player.hit and event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()
        if not run:
            break

        pygame.display.update()
        #player
        player.loop(FPS)

        #orb
        for i in orb1:
            i.loop()

        #key
        key.update()

        #platform
        if platform1.animation_name=="Grey On":
            platform1.update(300,300+pit_width*2,player)

        #door
        if(door.state=="closed" and offset_x<=40 and key.animation_name=="Off"): 
            door.open()
        run=handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)
        display(window,font,textX,textY)
        pygame.display.update()

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel
    player.reset()
    run=True
    floor1 = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-WIDTH // block_size, 300 // block_size)]
    floor2=[Block(i*block_size,HEIGHT-block_size,block_size) for i in range((300+pit_width*2)//block_size,2*WIDTH//block_size)]
    platform2=Platform(300,HEIGHT-block_size-64,3)
    platform3=Platform(300+pit_width,HEIGHT-block_size-64,5)
    platform2.on()
    platform3.on()
    orb2=[Orb(300,HEIGHT-block_size-64,16,16),Orb(300+pit_width,HEIGHT-block_size-64,16,16),Orb(300+pit_width*2+32,HEIGHT-block_size-32,16,16),Orb(300+pit_width*2+3*block_size,HEIGHT-4*block_size,16,16)]
    door=Doors(300+pit_width*2+2*block_size+block_size,HEIGHT-4*block_size-96,64,96)
    big_block=[Block(300+pit_width*2+2*block_size+i*block_size,HEIGHT-block_size-j*block_size,block_size) for i in range(3) for j in range(1,4)]
    key1=Key(300+pit_width*2,HEIGHT-block_size-32)
    objects = [*orb2,*floor1,*floor2,*ceiling,*wall1,*wall2, Block(0, HEIGHT - block_size * 2, block_size),platform2,platform3,*big_block,door,key1]
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if not player.hit and event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()
        if not run:
            break

        pygame.display.update()
        #player
        player.loop(FPS)

        #orb
        for i in orb2:
            i.loop()

        #key
        key1.update()

        #platform
        if platform2.animation_name=="Grey On":
            platform2.update(300,300+pit_width,player)
        if platform3.animation_name=="Grey On":
            platform3.update(300+pit_width,300+pit_width*2,player)
        #door
        if(door.state=="closed" and offset_x>=WIDTH-5*block_size and key1.animation_name=="Off"): 
            door.open()
        run=handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)
        display(window,font,textX,textY)
        pygame.display.update()

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel
    player.reset()
    run=True
    pit_width=0
    platform4=Platform(300,HEIGHT-block_size-64-32,5)
    platform5=Platform(300+block_size,HEIGHT-2*block_size-64-32,5)
    platform6=Platform(300,HEIGHT-3*block_size-64-32,5)
    platform7=Platform(300+block_size,HEIGHT-4*block_size-64-32,5)
    platform4.on()
    platform5.on()
    platform6.on()
    platform7.on()
    block1=Block(300,HEIGHT-5*block_size-64-32,block_size)
    key2=Key(300,HEIGHT-5*block_size-64-32-32)
    spikes1=[Spike(700, HEIGHT - block_size - 32),Spike(764,HEIGHT-block_size-32),Spike(764+64,HEIGHT-block_size-32),Spike(764+2*64,HEIGHT-block_size-32),Spike(764+2*64+48,HEIGHT-block_size-32)]
    door=Doors(1064,HEIGHT-block_size-96,64,96)
    floor1 = [Block(i * block_size, HEIGHT - block_size, block_size)
        for i in range(-WIDTH // block_size, 300 // block_size)]
    floor2=[Block(i*block_size,HEIGHT-block_size,block_size) for i in range((300+pit_width*2)//block_size,2*WIDTH//block_size)]
    orb3=[Orb(300,HEIGHT-block_size-64-32,16,16),Orb(300,HEIGHT-3*block_size-64-32,16,16),Orb(1200,HEIGHT-block_size-64,16,16)]
    objects = [*orb3,door,*spikes1,*floor1,*floor2,*ceiling,*wall1,*wall2, Block(0, HEIGHT - block_size * 2, block_size),block1,platform5,platform4,platform6,platform7,key2]
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                if not player.hit and event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()
        if not run:
            break

        pygame.display.update()
        #player
        player.loop(FPS)

        #orb
        for i in orb3:
            i.loop()
        #key
        key2.update()

        #platform
        if platform4.animation_name=="Grey On":
            platform4.update(300,300+2*block_size,player)
        if platform5.animation_name=="Grey On":
            platform5.update(300,300+2*block_size,player)
        if platform6.animation_name=="Grey On":
            platform6.update(300,300+2*block_size,player)
        if platform7.animation_name=="Grey On":
            platform7.update(300,300+2*block_size,player)
        #door
        if(door.state=="closed" and offset_x>=900 and key2.animation_name=="Off"): 
            door.open()
        run=handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)
        display(window,font,textX,textY)
        pygame.display.update()

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)
