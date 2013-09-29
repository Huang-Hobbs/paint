from gameview import GameView
from maptile import MapTile
from zone import Zone
from random import randint
import pygame
import entities 
from entities import *
import random
import threading
from time import sleep
import types


GRID_RESOLUTION = 48
MAP_GRID_SIZE = Point(14,14)
MAP_SIZE = Point(MAP_GRID_SIZE.x * GRID_RESOLUTION, MAP_GRID_SIZE.y * GRID_RESOLUTION)


class MainGame(GameView):
    """
    The main logic within the game. 
    
    operations:
    """   
    
    def __init__(self,canvas):
        super(MainGame, self).__init__(canvas)
        
        self.zones = []        
        self.map_tiles = self._make_map()
        
        self.entities = []
        self.cameras = []
        self.players = []
        self.police = []
        
        self.camerax = -20
        self.cameray = -40
        
        self._populate_map()
        self.ease_elapsed = 0
        
    def player_one (self, elapsed):
        '''
        Handles the running of all operations that run in player one's thread, as well
        as creation of the player.
        '''
        self.player_1.update(elapsed)
        print (self.player_1.x)
        
        #non-alive entities are removed from the continual updates
        for dead in filter(lambda ent: not ent.alive, self.entities):
            self.entities.remove(dead)
            
    def player_two (self, elapsed):
        '''
        Handles the running of all operations that run in player two's thread, as well 
        as creation of the player.
        '''
        self.player_2.update(elapsed)
            
        #non-alive entities are removed from the continual updates
        for dead in filter(lambda ent: not ent.alive, self.entities):
            self.entities.remove(dead)
        
    def easing(self,elapsed):
        self.ease_elapsed+=elapsed
        self.cameray = -800*(1-(self.ease_elapsed))-20
        print (self.cameray)
    
    def add_player_objects(self):
        '''
        Will create the player objects that are required in the game and assign them to class attributes.
        '''
        self.player_1 = self.add(entities.Player(GRID_RESOLUTION*5,GRID_RESOLUTION*2, 2, pygame.color.Color(232,44,12,255),
            keybindings = {"LEFT": pygame.K_a,
            "RIGHT": pygame.K_d,
            "UP": pygame.K_w,
            "DOWN": pygame.K_s,
            "PAINT": pygame.K_z,
            "BOMB": pygame.K_x,
            "ITEM": pygame.K_c}                                                   
        ))      
        
        self.player_2 = self.add(entities.Player(GRID_RESOLUTION,GRID_RESOLUTION*2, 1, pygame.color.Color(23,71,166,255),
            keybindings = {"LEFT": pygame.K_LEFT,
            "RIGHT": pygame.K_RIGHT,
            "UP": pygame.K_UP,
            "DOWN": pygame.K_DOWN,
            "PAINT": pygame.K_COMMA,
            "BOMB": pygame.K_PERIOD,
            "ITEM": pygame.K_SLASH}
        ))
        
        
    def main_loop(self, elapsed):
        """
        Loops the game logic for cameras and policemen, and starts player threads.
        """
        
        self.add_player_objects()
        
        #Two separate threads run for each individual player.
        self.running = True
        th1 = threading.Thread(target = self.player_one(elapsed))
        th2 = threading.Thread(target = self.player_two(elapsed))
        th1.start()
        th2.start()
        
        for entity in filter(lambda ent: not isinstance(ent, Player), self.entities):
                if(entity.stasis==0):
                    entity.update(elapsed)
                else:
                    entity.stasis-=elapsed
                    entity.stasis = max (entity.stasis,0)
        
        #non-alive entities are removed from the continual updates
        for dead in filter(lambda ent: not ent.alive, self.entities):
            self.entities.remove(dead)
        
        #TODO map behaviors
        for camera in self.cameras:
            for player in self.players:
                if(camera.get_vision_rect().colliderect(player.get_rect())):
                    closest = self.police[0]
                    for i in self.police:
                        if(i._get_tile().manhattan(player._get_tile())<closest._get_tile().manhattan(player._get_tile())):
                            closest=i
                    closest.alert_to(player, player._get_tile())
        
        for police in self.police:
            for player in self.players:
                if(police.get_vision_rect().colliderect(player.get_rect())):
                    police.alert_to(player, player._get_tile(), True)
                    
                #the player checks around for a police officer, then avoids them if one is near
                player.avoid_police(police)
                
        
        

    def render(self):
        for row_number in range(len(self.map_tiles)):
            for tile in self.map_tiles[row_number]:
                tile.render(self.canvas)
            
            for entity in self.entities:
                if( int((entity.y-1)/GRID_RESOLUTION) ==  row_number):
                    entity.render(self.canvas)
        
        for entity in self.entities:
            entity.post_render(self.canvas)
        """
        for zone in self.zones:
            color = zone.get_dominant_color()
            if(color is not None):
                for tile in zone.tile_contents:
                    pygame.draw.rect(self.canvas,
                                     color,
                                     pygame.rect.Rect(
                                         tile.gridx * GRID_RESOLUTION - self.camerax,
                                         tile.gridy * GRID_RESOLUTION - self.cameray,
                                         GRID_RESOLUTION,
                                         GRID_RESOLUTION),
                                     1)
        """
    #begin helper functions
    def add(self, entity):
        entity.set_parent(self)
        self.entities.append(entity)
        
        if(isinstance(entity, entities.Camera)):
            self.cameras.append(entity)
        if(isinstance(entity, entities.Player)):
            self.players.append(entity)
        if(isinstance(entity, entities.Police)):
            self.police.append(entity)        
    
        return entity
    
    
    def _make_map(self):  
        '''
        The map is created for the game. This is a 50x50 tile grid. 
        '''          
        for x in range(MAP_GRID_SIZE.x/3):
            for y in range(MAP_GRID_SIZE.y/3):
                self.zones.append(Zone())
        
        retmap = []
        for y in range(MAP_GRID_SIZE.y):
            retmap.append([])
            for x in range(MAP_GRID_SIZE.x):
                raised = (x == 0 or
                          y == 0 or
                          x == (MAP_GRID_SIZE.x-1) or
                          y == (MAP_GRID_SIZE.y-1)
                          )
                retmap[y].append(MapTile(x,y,self,raised))
                if(y!=0 and x!=0 and x!= (MAP_GRID_SIZE.x-1) and y!=(MAP_GRID_SIZE.y-1)):
                    self.zones[((x-1)/(MAP_GRID_SIZE.x/3))%3 +
                               ((y-1)/(MAP_GRID_SIZE.y/3))*3
                               ].add(retmap[y][-1])
        
        for y in range(len(retmap)):
            for x in range(len(retmap)):
                if(x!=0):
                    retmap[y][x].neighbor_left = retmap[y][x-1]
                if(x!=len(retmap[y])-1):
                    retmap[y][x].neighbor_right = retmap[y][x+1]
                if(y!=0):
                    retmap[y][x].neighbor_up = retmap[y-1][x]
                if(y!=len(retmap)-1):
                    retmap[y][x].neighbor_down = retmap[y+1][x]
            
        return retmap
    
    def _populate_map(self):
        '''
        The different entities excluding player are added to the game. This includes
        cameras and policemen.
        '''
        pol = self.add(entities.Police(GRID_RESOLUTION*5, GRID_RESOLUTION*6+1))        
        self.add(entities.Camera(GRID_RESOLUTION*3,
            GRID_RESOLUTION*3+1,
            random.random(),
            random.random())
        )
        
        pol = self.add(entities.Police(GRID_RESOLUTION*7, GRID_RESOLUTION*6+1))        
        self.add(entities.Camera(GRID_RESOLUTION*3,
                                 GRID_RESOLUTION*9+1,
                                 random.random(),
                                 random.random())
                 )
        
        pol = self.add(entities.Police(GRID_RESOLUTION*7, GRID_RESOLUTION*8+1))        
        self.add(entities.Camera(GRID_RESOLUTION*9,
                                 GRID_RESOLUTION*9+1,
                                 random.random(),
                                 random.random())
                 )
        
        pol = self.add(entities.Police(GRID_RESOLUTION*5,
                                 GRID_RESOLUTION*8+1)
                )        
        self.add(entities.Camera(GRID_RESOLUTION*9,
                                 GRID_RESOLUTION*3+1,
                                 random.random(),
                                 random.random())
                 )

