import pygame
import os
import time
import random
pygame.font.init() # Get the font ready to go

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT)) # Window
pygame.display.set_caption("Space Shooter")

# Load Images
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# Player ship
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Background, scaled
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
    
    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
    # tells if the laser is off the screen based on the height
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
    # tells if the laser collided with something
        return collide(self, obj)



class Ship:
    COOLDOWN = 30 # 0.5 sec, since fps is 60

    def __init__(self, x, y, health=100):
        self.x = x # x position
        self.y = y # y position
        self.health = health # health of the ship
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        # draw lasers
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            # check if off screen
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            # check if laser collided
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)


    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1


    def shoot(self):
        # we can shoot, countdown is over
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img) # perfect pixel collision
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            # check if off screen
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                # check if laser collided with every single enemy
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)


    def healthbar(self, window):
        # draw a rectangle
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))



class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_SPACE_SHIP, RED_LASER),
        "green": (GREEN_SPACE_SHIP, GREEN_LASER),
        "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel): # vel = velocity
        self.y += vel

    def shoot(self):
        # we can shoot, countdown is over
        if self.cool_down_counter == 0:
            laser = Laser(self.x-15, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
        

def collide(obj1, obj2):
    # distance from obj1 to obj2
    offset_x = obj2.x - obj1.x 
    offset_y = obj2.y - obj1.y

    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


# Main loop
def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)


    enemies = []
    wave_length = 5
    enemy_velocity = 1

    player_velocity = 5
    laser_velocity = 5

    player = Player(300, 650)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():    
        WIN.blit(BG, (0,0)) # draw background in location (0,0)
        # Draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        # draw enemies
        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN) # draw ship

        # if player lost
        if lost:
            lost_label = lost_font.render("You Lost!", 1, (255,255,255))
            # text appear at the center
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update() # refresh the display



    while run:
        clock.tick(FPS)

        redraw_window()

        # check if player lost
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
    
        if lost:
            # we've got passed our 3 seconds timer, quit the game
            if lost_count > FPS * 3: 
                run = False
            else:
                continue

        if len(enemies) == 0: # no more enemies, passed the level
            level += 1
            wave_length += 5 # add 5 enemies to next wave
            # spawn new enemies
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), random.choice(['red', 'blue', 'green']))
                enemies.append(enemy)

        # Quit the game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        
        # Move ship with WASD
        keys = pygame.key.get_pressed() # returns a dict with the keys I pressed
        if keys[pygame.K_a] and player.x - player_velocity > 0: # moving left
            player.x -= player_velocity 
        if keys[pygame.K_d] and player.x + player_velocity + player.get_width() < WIDTH: # moving right
            player.x += player_velocity
        if keys[pygame.K_w] and player.y - player_velocity > 0: # moving up
            player.y -= player_velocity
        if keys[pygame.K_s] and player.y + player_velocity + player.get_height() + 15 < HEIGHT: # moving down
            player.y += player_velocity
        if keys[pygame.K_SPACE]: # shoot lasers
            player.shoot()
        
        # move enemies
        for enemy in enemies[:]:
            enemy.move(enemy_velocity)
            enemy.move_lasers(laser_velocity, player)

            # 50% change of enemy shooting 
            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            # if enemy collided with player
            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            # if enemy is gone, reduce 1 from lives
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        # move player's lasers
        player.move_lasers(-laser_velocity, enemies)


def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render('Press the mouse to begin...', 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()

    pygame.quit()

main_menu()
