from settings import *
from sprites import *
import os

os.chdir(RESOURCES_DIR)

class Battle:
    def __init__(self):
        self.game_width, self.game_height = LANDSCAPE_WIDTH, LANDSCAPE_HEIGHT
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (50, 50)

        print(f"self.game_width: {self.game_width} self.game_height: {self.game_height}")
        self.screen = pg.display.set_mode((self.game_width, self.game_height))
        pg.display.set_caption(TITLE)

        self.clock = pg.time.Clock()
        self.running = True
        self.playing = True
        self.fps = FPS

        pg.font.init()
        pg.mixer.init()

        self.player_country = "Shu"
        self.enemy_country = "Wei"
        self.deployed_player_units = 0
        self.deployed_enemy_units = 0

        self.all_sprites = pg.sprite.Group()
        self.player_unit_sprites = pg.sprite.Group()
        self.enemy_unit_sprites = pg.sprite.Group()

    def new(self):
        self.player_selected_slot = 0
        self.enemy_selected_slot = 0
        self.player_moral = 100
        self.enemy_moral = 100
        self.enemy_last_deployment_time = 0

        self.background = Static(0, 0, os.path.join(RESOURCES_DIR, "battleground_sand.png"))
        self.all_sprites.add(self.background)

        self.player_deployment_action_bar = Static(0, 0, "sprite_action_bar.png")
        self.all_sprites.add(self.player_deployment_action_bar)

        self.general_deployment_action_bar = Static(400, 0, "sprite_action_bar.png")
        self.all_sprites.add(self.general_deployment_action_bar)

        self.enemy_deployment_action_bar = Static(800, 0, "sprite_action_bar.png")
        self.all_sprites.add(self.enemy_deployment_action_bar)

        self.slot_indicator = Static(30, self.player_selected_slot * 60 + 160, "sprite_slot_indicator_1.png")
        self.all_sprites.add(self.slot_indicator)

        self.run()

    def events(self):
        for events in pg.event.get():
            if events.type == pg.KEYUP:
                if events.key == pg.K_SPACE:
                    self.deploy_unit("left", "elite_sword_infantry", self.player_selected_slot)
            
                if events.key == pg.K_UP:
                    self.change_slot(-1)
                if events.key == pg.K_DOWN:
                    self.change_slot(1)
    
    def change_slot(self, change):
        if self.player_selected_slot + change >= 0 and self.player_selected_slot + change <= 7:
            self.player_selected_slot += change
            self.slot_indicator.rect.x, self.slot_indicator.rect.y = 30, self.player_selected_slot * 60 + 160

    def update(self):
        now = pg.time.get_ticks()
        self.all_sprites.update()
        if self.player_moral <= 0:
            self.player_moral = 0
            self.show_game_over_screen()
        elif self.enemy_moral <= 0:
            self.enemy_moral = 0
            self.show_game_over_screen(True)
        
        if now - self.enemy_last_deployment_time >= 500:
            self.enemy_last_deployment_time = now
            self.enemy_selected_slot = randrange(7)
            self.deploy_unit("right", "elite_sword_infantry", self.enemy_selected_slot)
    
    def show_game_over_screen(self, won=False):
        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 200))
        self.screen.blit(self.dim_screen, (0, 0))
        if won:
            self.draw_text("You Won!", 105, WHITE, self.game_width/2, self.game_height/2)
        else:
            self.draw_text("You Lost!", 105, RED, self.game_width/2, self.game_height/2)
        pg.display.flip()
        self.listen_for_key()
    
    def listen_for_key(self):
        waiting = True
        while waiting:
            if self.running:
                self.clock.tick(self.fps)
            for event in pg.event.get():
                if event.type == pg.KEYUP:
                    if event.key == pg.K_q:
                        self.playing = False
                        self.running = False
                        waiting = False

    
    def draw_text(self, text, size, color, x, y, anchor="midtop"):
        font = pg.font.Font("freesansbold.ttf", size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if anchor == "center":
            text_rect.center = (x, y)
        else:
            text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def draw(self):
        if self.playing:
            self.screen.fill(BLACK)
            self.all_sprites.draw(self.screen)
            self.draw_text("Player Moral: {}".format(self.player_moral), 10, WHITE, 100, 30)
            self.draw_text("Enemy Moral: {}".format(self.enemy_moral), 10, WHITE, 1100, 30)
            pg.display.flip()

    def run(self):
        while self.playing:
            self.clock.tick(self.fps)
            self.events()
            self.update()
            self.draw()
    
    def deploy_unit(self, side, unit_type, slot=1):
        if side == "left":
            self.deployed_player_units += 1
            unit = Elite_Sword_Infantry(self, 50, self.player_selected_slot*60+180, "Melee", unit_type, self.player_country, self.deployed_player_units, side, slot)
            self.player_unit_sprites.add(unit)
        else:
            self.deployed_enemy_units += 1
            unit = Elite_Sword_Infantry(self, self.game_width-50, self.enemy_selected_slot*60+180, "Melee", unit_type, self.enemy_country, self.deployed_enemy_units, side, slot)
            self.enemy_unit_sprites.add(unit)

        self.all_sprites.add(unit)


b = Battle()
b.new()