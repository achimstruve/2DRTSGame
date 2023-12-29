import pygame as pg
from random import randrange
import os

class Static(pg.sprite.Sprite):
    def __init__(self, x, y, filename):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load(filename).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = x, y

class Unit(pg.sprite.Sprite):
    def __init__(self, game, x, y, unit_class, unit_type, unit_country, unit_id, side, slot,
                 walk_frames, attack_frames, damage_frame, attacking_range, health, attack, defense, walking_acc):
        pg.sprite.Sprite.__init__(self)
        self.game = game

        self.unit_class = unit_class
        self.unit_type = unit_type
        self.unit_country = unit_country
        self.id = unit_id

        self.side = side
        self.slot = slot
        self.walking_animation_length = walk_frames
        self.attacking_animation_length = attack_frames

        self.health = health
        self.attack = attack
        self.defense = defense
        self.walking_acc = walking_acc

        self.attacking = False
        self.attacking_range = attacking_range
        self.position_x, self.position_y = x, y

        self.last_update = 0
        self.current_frame = 0
        self.damage_frame = damage_frame
        self.load_animation()

        self.image = self.walking_animations[0]
        self.rect = self.image.get_rect()

        if self.side == "left":
            self.enemy_sprite = self.game.enemy_unit_sprites
            self.rect.left, self.rect.centery = self.position_x, self.position_y
        if self.side == "right":
            self.enemy_sprite = self.game.player_unit_sprites
            self.rect.right, self.rect.centery = self.position_x, self.position_y

        self.health_bar_front = UnitHealthBar(self.rect.centerx, self.rect.top, "generic_health_bar_front.png", self.game, master=self)
        self.health_bar_back = UnitHealthBar(self.rect.centerx, self.rect.top, "generic_health_bar_back.png", self.game, master=self, front=False)

        self.game.all_sprites.add(self.health_bar_back)
        self.game.all_sprites.add(self.health_bar_front)

        self.game.all_sprites.add(self)

        print(f"Sprite {self.id}|{self.unit_country} in slot {self.slot} deployed!")


    def load_animation(self):
        self.walking_animations = [pg.image.load("sprite_{}_walking_{}_{}.png".format(self.unit_type, i, self.unit_country)) for i in range(1, self.walking_animation_length+1)]
        self.attacking_animations = [pg.image.load("sprite_{}_attacking_{}_{}.png".format(self.unit_type, i, self.unit_country)) for i in range(1, self.attacking_animation_length+1)]

        if self.side == "right":
            for i in range(len(self.walking_animations)):
                self.walking_animations[i] = pg.transform.flip(self.walking_animations[i], True, False)
            for i in range(len(self.attacking_animations)):
                self.attacking_animations[i] = pg.transform.flip(self.attacking_animations[i], True, False)
    
    def update(self):
        self.animate()

        self.enemy_sprite_same_slot = pg.sprite.Group()
        for enemy_sprite in self.enemy_sprite:
            if enemy_sprite.slot == self.slot:
                self.enemy_sprite_same_slot.add(enemy_sprite)
        
        if not self.attacking:
            
            for enemy_unit_sprites in self.enemy_sprite_same_slot:
                if abs(self.rect.centerx - enemy_unit_sprites.rect.centerx) <= self.attacking_range:
                    self.attacking = True
                    self.current_frame = 0
                    self.image = self.attacking_animations[self.current_frame]
                    break
            
            if self.side == "left":
                self.position_x += self.walking_acc
                self.rect.left = self.position_x
                if self.rect.centerx >= self.game.game_width + 50:
                    self.kill()
                    self.health_bar_front.kill()
                    self.health_bar_back.kill()
                    self.game.enemy_moral -= self.health/10
                    print(f"Sprite {self.id}|{self.unit_country} went off screen, killed!")
            else:
                self.position_x -= self.walking_acc
                self.rect.right = self.position_x
                if self.rect.centerx < -50:
                    self.kill()
                    self.health_bar_front.kill()
                    self.health_bar_back.kill()
                    self.game.player_moral -= self.health/10
                    print(f"Sprite {self.id}|{self.unit_country} in slot {self.slot} went off screen, killed!")
        else:
            if self.current_frame == self.damage_frame:
                enemy_collision = pg.sprite.spritecollide(self, self.enemy_sprite_same_slot, False)
                if enemy_collision:
                    closest_enemy = enemy_collision[0]
                    damage_dealt = (self.attack+2) / (closest_enemy.defense+2)*randrange(10,13)
                    closest_enemy.got_hit(damage_dealt)
                else:
                    self.attacking = False  

    
    def animate(self):
        now = pg.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now

            if not self.attacking:
                self.current_frame = (self.current_frame + 1) % len(self.walking_animations)
                self.image = self.walking_animations[self.current_frame]
            else:
                self.current_frame = (self.current_frame + 1) % len(self.attacking_animations)
                self.image = self.attacking_animations[self.current_frame]
                self.rect = self.image.get_rect()
                if self.side == "left":
                    self.rect.left = self.position_x
                    self.rect.centery = self.position_y
                else:
                    self.rect.right = self.position_x
                    self.rect.centery = self.position_y
        else:
            pass
    
    def got_hit(self, damage):
        self.health -= damage
        print(f"Sprite {self.unit_country} got hit, health: {self.health}")
        if self.health <= 0:
            self.kill()
            self.health_bar_front.kill()
            self.health_bar_back.kill()
            print(f"Sprite {self.id}|{self.unit_country} in slot {self.slot} died, killed!")
        else:
            pass

class Elite_Sword_Infantry(Unit):
    def __init__(self, game, x, y, unit_class, unit_type, unit_country, unit_id, side, slot):
        Unit.__init__(self, game, x, y, unit_class, unit_type, unit_country, unit_id, side, slot,
                      walk_frames=9, attack_frames=6, damage_frame=4, attacking_range=60, health=100, attack=7, defense=10, walking_acc=6)

class UnitHealthBar(pg.sprite.Sprite):
    def __init__(self, x, y, filename, game, master, front=True):
        pg.sprite.Sprite.__init__(self)
        self.filename = filename
        self.game = game
        self.master = master
        self.front = front
        self.max = self.master.health

        self.image = pg.image.load(self.filename)
        self.image = pg.transform.scale(self.image, (20,3))
        self.rect = self.image.get_rect()
        self.rect.left = x - 10
        self.rect.centery = y
    
    def update(self):
        if self.front:
            self.image = pg.transform.scale(self.image, (int(self.master.health/self.max*20) if self.master.health>=0 else 0,3))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.centery = self.master.position_x+20 if self.master.side == "left" else self.master.position_x-45, self.master.rect.top


        
        