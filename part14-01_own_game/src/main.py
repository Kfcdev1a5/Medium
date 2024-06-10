# Complete your game here
from random import randint, choice
import pygame

class Floor:
    def __init__(self, screen, color, thickness=2, border_radius=0):
        self.screen = screen
        self.color = color
        self.thickness = thickness
        self.border_radius = border_radius
        self.floors = []

    def create_floors(self, x, y, width, height, floor_num, spacing):
        for i in range(floor_num):
            rect = pygame.Rect(x, y - i * (height + spacing), width, height)
            self.floors.append(rect)
    
    def draw(self):
        for rect in self.floors:
            pygame.draw.rect(self.screen, self.color, rect, self.thickness, border_radius=self.border_radius)
            pygame.draw.rect(self.screen, self.color, rect.inflate(-self.thickness * 2, -self.thickness * 2))

    def position(self):
        return [(rect.x, rect.y) for rect in self.floors]

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.won = False
        self.moveup = 0
        self.image = pygame.image.load("robot.png")
        self.rect = self.image.get_rect(midbottom = (80, height-30+self.moveup))
        self.to_right = False
        self.to_left = False

    def move_left(self):
        if self.rect.x > 0:
            self.rect.x -= 8 
    
    def move_right(self):
        if self.rect.x + self.rect.width < 1200:
            self.rect.x += 8
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)
    
    def next_level(self, floor_pos):
        self.moveup -= 187
        self.rect = self.image.get_rect(midbottom = (80, height-30+self.moveup))
    
    def player_won(self):
        if self.rect.y < 0:
            self.won = True
        return self.won

    def player_reset(self):
        self.moveup = 0
        self.to_right = False
        self.to_left = False
        self.won = False
        self.rect = self.image.get_rect(midbottom = (80, height-30+self.moveup))        
    
    def use_door(self, door):
        for item in door.doors:
            if self.rect.colliderect(item):
                return True

    def collect_coin(self, coinlist):
        for row_coins in coinlist:
            for coin_rect in row_coins:
                if self.rect.colliderect(coin_rect):
                    row_coins.remove(coin_rect)
                    return True
        return False

class Coin(pygame.sprite.Sprite):
    def __init__(self, floor_pos, coin_per_row):
        super().__init__()
        self.image = pygame.image.load("coin.png")
        self.initial_coins = []
        
        for row in floor_pos:
            x, y = row
            row_coins = []
            for i in range(coin_per_row):
                self.rect = self.image.get_rect(midbottom = (randint(90,1110), choice([y-5, y-50, y-70])))
                row_coins.append(self.rect)
            self.initial_coins.append(row_coins)
        self.coins = [coin_rect.copy() for coin_rect in self.initial_coins]

    def draw(self, screen):
        for row in self.coins:
            for coin in row:
                screen.blit(self.image, coin)
    
    def get_coins(self):
        return self.coins

    def coin_reset(self):
        self.coins = [coin_rect.copy() for coin_rect in self.initial_coins]

class Door(pygame.sprite.Sprite):
    def __init__(self, floor_pos):
        super().__init__()
        self.image = pygame.image.load("door.png")
        self.image = pygame.transform.scale(self.image, (100,150))
        self.doors = []

        for row in floor_pos:
            x, y = row
            self.rect = self.image.get_rect(bottomright = (width+13, y+12))
            self.doors.append(self.rect)

    def draw(self, screen):
        for door in self.doors:
            screen.blit(self.image, door)

class Monster(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("monster.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = randint(0, width- self.rect.width)
        self.rect.y = - self.rect.height

class MonsterManager(Monster):
    def  __init__(self):
        self.monsters = []
        self.monsters_win = False

    def spawn(self):
        new_monster = Monster()
        self.monsters.append(new_monster)
    
    def update(self):
        for monster in self.monsters:
            monster.rect.y +=  randint(1,3)
    
    def remove_monsters(self, height):
        self.monsters = [monster for monster in self.monsters if monster.rect.y < height]

    def check_collisions(self):
        for monster in self.monsters:
            if pygame.sprite.collide_rect(player, monster):
                self.monsters_win = True
                return True

    def monster_reset(self):
        self.monsters.clear()

    def draw(self, screen):
        for monster in self.monsters:
            screen.blit(monster.image, monster.rect)

class GameManager:
    def __init__(self, game_font):
        self.game_active = False
        self.score = 0
        self.countdown = 50
        self.gameover = False

    def check_game_over(self, player, monster_manager):
        if self.countdown <= 0:
            self.game_active = False
            self.gameover = True
        if player.player_won():
            self.game_active = False
            self.gameover = True
        if monster_manager.check_collisions(): 
            self.game_active = False
            self.gameover = True
        return self.gameover

    def draw_score(self, screen):
        self.score_text = game_font.render("Score: " + str(self.score), True, (255, 0, 0))
        self.score_text_rect = self.score_text.get_rect(topright = (self.score_text.get_width(),0))
        screen.blit(self.score_text, self.score_text_rect)

    def draw_countdown(self, screen):
        self.countdown_text = game_font.render("Countdown: " + str(self.countdown), True, (255, 0, 0))
        self.countdown_text_rect = self.countdown_text.get_rect(topleft = (width-self.countdown_text.get_width()-2,0))
        screen.blit(self.countdown_text, self.countdown_text_rect)

    def score_update(self):
        self.score += 1
    
    def countdown_update(self):
        self.countdown -= 1

    def reset_game(self, player, coin, monster):
        self.game_active = True
        self.score = 0
        self.countdown = 50
        self.gameover = False
        player.player_reset()
        monster.monster_reset()
        coin.coin_reset()
        
class GameInfo:
    def __init__(self, game_font, game_manager):
        self.title = "RoboCoin Rush"
        self.title_text = game_font.render(self.title, True, (255,0,0))
        self.title_text_rect = self.title_text.get_rect(midtop = (width/2,0))
        self.game_manager = game_manager

    def draw(self, screen):
        screen.blit(self.title_text, self.title_text_rect)
        self.game_manager.draw_score(screen)
        self.game_manager.draw_countdown(screen)

    def display_gameover(self, screen, player, monster):
        screen.fill('slategray1')
        gamescreen = pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(50, 50, 1100, 650))
        gametitle = pygame.transform.scale(game_font.render(self.title, True, (0,255,0)), (500,200))
        gametitle_rect = gametitle.get_rect(center = (1200/2, 200))
        screen.blit(gametitle, gametitle_rect)

        if player.won:  # Player won the game
            game_message = game_font.render("CONGRATULATIONS YOU WON! Your Final Score: " + str(game_manager.score) + "  Press Space to Restart, ESC to Quit", True, (255, 0, 0))

        elif game_manager.countdown <= 0 or monster.monsters_win:  # Game over due to countdown reaching zero
            game_message = game_font.render("YOU LOST! Your Final Score: " + str(game_manager.score) + "  Press Space to Restart, ESC to Quit", True, (255, 0, 0))
       
        else:  # Game is just starting
            game_message = game_font.render("Press Space to Start / ESC to Quit, Reach the final door before time runs out! ", True, (255, 0, 0))

        game_message_rect = game_message.get_rect(center=(1200 / 2, 750 / 2))
        screen.blit(game_message, game_message_rect)


# initialise game window / display
pygame.init()

width = 1200
height = 750

screen = pygame.display.set_mode((width,height))
pygame.display.set_caption("RoboCoin Rush")

game_font = pygame.font.SysFont("Comic Sans", 24)
clock = pygame.time.Clock()
timer = pygame.USEREVENT + 1
pygame.time.set_timer(timer, 1000)

#colors 
screen_c = 'slategray1'
boundary_color = 'seagreen'

# create floor object
floor = Floor(screen, boundary_color, thickness=2, border_radius=10)

# create floors (series of rectangles evenly spaced):
floor_x = 2
floor_w = width-4
floor_h = 30
floor_num = 4
spacing = (height-(floor_h*floor_num)-2)/floor_num
floor.create_floors(floor_x, height-floor_h, floor_w, floor_h, floor_num, spacing)

# get floor positions to load items (coins, robot)
floor_pos = floor.position()
# print("floor pos", floor_pos)

# coins
coin_per_row = 5
coin = Coin(floor_pos,coin_per_row)
coinlist = []
# door
door = Door(floor_pos)
# monster
monster_manager = MonsterManager()
# player
player = Player()

# game state
game_manager = GameManager(game_font)
game = GameInfo(game_font,game_manager)

while True:
    if game_manager.game_active:
        for event in pygame.event.get():
            if event.type == timer:
                game_manager.countdown_update()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.to_left = True
                if event.key == pygame.K_RIGHT:
                    player.to_right = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    player.to_left = False
                if event.key == pygame.K_RIGHT:
                    player.to_right = False
            
            if event.type == pygame.QUIT:
                exit()
        
        # player move
        if player.to_right:
            player.move_right()
        if player.to_left:
            player.move_left()

        if player.collect_coin(coinlist):
            game_manager.score_update()

        if player.use_door(door):
            player.next_level(floor_pos)
            player.draw(screen)

        game_manager.check_game_over(player, monster_manager) 

        coinlist = coin.get_coins()
        # clear the screen
        screen.fill('slategray1')
        # draw the assets
        game.draw(screen)
        floor.draw()
        coin.draw(screen)
        player.draw(screen)
        door.draw(screen)

        # spawn random monsters
        if randint(1, 100) <= 2:
            monster_manager.spawn()
        monster_manager.draw(screen)
        monster_manager.update()
        monster_manager.remove_monsters(height)

    else:
        game.display_gameover(screen, player, monster_manager)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    exit()
                if event.key == pygame.K_SPACE:
                    game_manager.reset_game(player, coin, monster_manager)
                    
            if event.type == pygame.QUIT:
                exit()
        
    pygame.display.update()
    pygame.display.flip()
    clock.tick(60)