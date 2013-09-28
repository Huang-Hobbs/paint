import pygame
import maingame
import os

placeholder_graphic = pygame.image.load(os.getcwd()+"/res/player.png")
placeholder_graphic.set_colorkey(pygame.color.Color(255,255,255))

def get_rect_overlap(rect1, rect2):
     return (
        rect1.right-rect2.left if rect1.centerx<rect2.centerx else -(rect2.right - rect1.left),
        rect1.bottom-rect2.top if rect1.centery<rect2.centery else -(rect2.bottom - rect1.top),
        rect1,
        rect2
        )

class Point(object):
    def __init__(self,x,y):
        self.x = x
        self.y = y

class Entity(Point):
    """the basic superclass for game entities"""
    def __init__(self, x, y):
        super(Entity,self).__init__(x,y)
        self.velocity = Point(0,0)
        self.friction = 0
        self.size=Point(0,0)
    
    def set_parent(self, parent):
        self.parent = parent
    
    def update(self, elapsed):
        #update position with velocity
        self.x+=self.velocity.x*elapsed
        self.y+=self.velocity.y*elapsed
        
        #momentum decay
        self.velocity.x = self.velocity.x*((1-self.friction)**elapsed)
        self.velocity.y = self.velocity.y*((1-self.friction)**elapsed)
        
        #binding to map limits
        self._map_bounds()
    
    def _map_bounds(self):
        if(self.x < 0):
            self.x = 0
            self.velocity.x = 0
        if(self.y < 0):
            self.y = 0
            self.velocity.y = 0
        if(self.x + self.size.x >= maingame.MAP_SIZE.x):
            self.x = maingame.MAP_SIZE.x - self.size.x - 1
            self.velocity.x = 0
        if(self.y >= maingame.MAP_SIZE.y):
            self.y = maingame.MAP_SIZE.y - 1
            self.velocity.y = 0
    
    def _get_tile(self):
        return self.parent.map_tiles[int(self.y/maingame.GRID_RESOLUTION)][int(round(self.x/maingame.GRID_RESOLUTION))]
    
    def _terrain_collision(self):
        selfrect = self.get_rect()
        for row in self.parent.map_tiles:
             for tile in row:
                  if(tile.raised and tile.get_rect().colliderect(selfrect)):
                    overlap = get_rect_overlap(tile.get_rect(), selfrect)
                    if(abs(overlap[0])<abs(overlap[1])):
                         self.x+=overlap[0]
                         self.velocity.x=0
                    else:
                         self.y+=overlap[1]
                         self.velocity.y=0
                    return
                
    
    def get_rect(self):
        return pygame.rect.Rect(self.x+self.rect_offset.x, self.y-self.size.y+self.rect_offset.y, self.size.x, self.size.y)
    
    def render(self,canvas):
        pass

class LivingEntity(Entity):
    
    def __init__(self,x,y):
        super(LivingEntity, self).__init__(x,y)
        #TODO animation definitions
    
    def update(self,elapsed):
        super(LivingEntity, self).update(elapsed)
        self._terrain_collision()
    
    def render(self,canvas):
        #TODO frame selection from animation
        pass

class Player(LivingEntity):
    
    SPEED = 1000
    
    def __init__(self,x,y,color,
                 keybindings = {"LEFT": pygame.K_LEFT,
                                "RIGHT": pygame.K_RIGHT,
                                "UP": pygame.K_UP,
                                "DOWN": pygame.K_DOWN,
                                "PAINT": pygame.K_z,
                                "BOMB": pygame.K_x,
                                "ITEM": pygame.K_c}):
        super(Player,self).__init__(x,y)
        self.color = color
        self.keybindings = keybindings
        self.friction = 0.9
        self.size = Point(20,20)
        self.rect_offset = Point(15,10)
    
    def update(self,elapsed):
        super(Player,self).update(elapsed)
        
        if(self._pressed("LEFT")):
            self.velocity.x -= Player.SPEED * elapsed
        if(self._pressed("RIGHT")):
            self.velocity.x += Player.SPEED * elapsed
        if(self._pressed("UP")):
            self.velocity.y -= Player.SPEED * elapsed
        if(self._pressed("DOWN")):
            self.velocity.y += Player.SPEED * elapsed
        
        if(self._pressed("PAINT")):
            self._get_tile().paint_color = self.color
    
    def render(self,canvas):
        canvas.blit(placeholder_graphic,
                    (self.x - maingame.camerax,
                     self.y - maingame.cameray -
                         placeholder_graphic.get_size()[1])
                    )
    
    def _pressed(self,code):
        return pygame.key.get_pressed()[self.keybindings[code]]