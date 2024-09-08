import pygame
import sys
import math
import random

def random_point_on_circumference(center_x, center_y, radius):
    theta = 2 * math.pi * random.random()
    x = center_x + radius * math.cos(theta)
    y = center_y + radius * math.sin(theta)
    return x, y

class GameSprite(pygame.sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y):
        pygame.sprite.Sprite.__init__(self)
        self.original_image = pygame.image.load(player_image)
        self.image = pygame.transform.scale(self.original_image, (size_x, size_y))
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
        self.position = (player_x, player_y)
        self.angle = 0
        self.health = 100  # Initialize player's health

    def rotate(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        rel_x, rel_y = mouse_x - self.rect.centerx, mouse_y - self.rect.centery
        self.angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
        self.image = pygame.transform.rotate(self.original_image, int(self.angle))
        self.rect = self.image.get_rect(center=self.rect.center)

    def get_bullet_position(self):
        offset_x = math.cos(math.radians(self.angle)) * (self.rect.width / 2)
        offset_y = -math.sin(math.radians(self.angle)) * (self.rect.height / 2)
        bullet_x = self.rect.centerx + offset_x
        bullet_y = self.rect.centery + offset_y
        return bullet_x, bullet_y

    def take_damage(self, amount):
        self.health -= amount

class Bullet(pygame.sprite.Sprite):
    def __init__(self, bullet_img, bullet_x, bullet_y, bsize_x, bsize_y, bullet_spd, angle):
        pygame.sprite.Sprite.__init__(self)
        self.original_image = pygame.image.load(bullet_img)
        self.image = pygame.transform.scale(self.original_image, (bsize_x, bsize_y))
        self.rect = self.image.get_rect()
        self.rect.centerx = bullet_x
        self.rect.centery = bullet_y
        self.speed = bullet_spd
        self.angle = angle
        self.dx = self.speed * math.cos(math.radians(self.angle))
        self.dy = -self.speed * math.sin(math.radians(self.angle))

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if (self.rect.x < 0 or self.rect.x > width or
            self.rect.y < 0 or self.rect.y > height):
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_image, enemy_x, enemy_y, esize_x, esize_y):
        pygame.sprite.Sprite.__init__(self)
        self.original_image = pygame.image.load(enemy_image)
        self.image = pygame.transform.scale(self.original_image, (esize_x, esize_y))
        self.rect = self.image.get_rect()
        self.rect.x = enemy_x
        self.rect.y = enemy_y
        self.position = (enemy_x, enemy_y)
        self.speed = 2
        self.angle = 0

    def update(self, target_x, target_y):
        dx = target_x - self.rect.centerx
        dy = target_y - self.rect.centery
        distance = math.hypot(dx, dy)
        if distance != 0:
            dx /= distance
            dy /= distance
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        self.angle = math.degrees(-math.atan2(dy, dx))
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

pygame.init()
width, height = 750, 750
wd = pygame.display.set_mode((width, height))
pygame.display.set_caption("Aegon")
white = (255, 255, 255)
black = (31, 31, 31)
Font = pygame.font.SysFont("arial", 32)

delay_factor = 0.03
circle_center_x = width / 2
circle_center_y = height / 2
circle_radius = 500

running = True
game_over = False  # Flag to track game over state
score = 0  # Initialize the score
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
player = GameSprite('turret.png', circle_center_x, circle_center_y, 68, 60)

t = 0  # Timer system
enemy_spawn_interval = 60  # Initial interval (every 60 frames)
enemy_spawn_counter = 0  # Counter for spawned enemies

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                player.rotate()
                bullet_x, bullet_y = player.get_bullet_position()
                new_bullet = Bullet('bullet.png', bullet_x, bullet_y, 20, 20, 15, player.angle)
                bullets.add(new_bullet)

    if not game_over:
        t += 1  # Timer system

        # Check for enemy spawning
        if t >= enemy_spawn_interval:
            enemy_x, enemy_y = random_point_on_circumference(circle_center_x, circle_center_y, circle_radius)
            enemy = Enemy('turret.png', enemy_x + random.randint(0, 50), enemy_y + random.randint(0, 50), 68, 60)
            enemies.add(enemy)
            enemy_spawn_counter += 1
            t = 0  # Reset timer

            # Every 5 enemies, decrease the spawn interval
            if enemy_spawn_counter % 5 == 0:
                enemy_spawn_interval = max(10, enemy_spawn_interval - 10)  # Decrease spawn interval but not below 10 frames

        mx, my = pygame.mouse.get_pos()
        circle_center_x += (mx - circle_center_x) * delay_factor
        circle_center_y += (my - circle_center_y) * delay_factor 
        player.rect.centerx = circle_center_x
        player.rect.centery = circle_center_y

        wd.fill(black)

        player.rotate()
        turret = pygame.sprite.Group()
        turret.add(player)
        turret.draw(wd)

        bullets.update()
        bullets.draw(wd)

        # Check for collisions between bullets and enemies
        collisions = pygame.sprite.groupcollide(bullets, enemies, True, True)
        score += len(collisions)  

        # Check for collisions between enemies and the player
        player_collisions = pygame.sprite.spritecollide(player, enemies, True)
        for enemy in player_collisions:
            player.take_damage(10)  
            if player.health <= 0:
                game_over = True
                player.kill()  # Ensure player is removed from all groups
                break  # Break out of the loop to avoid further collision checks

        # Update enemies' positions and rotations
        for enemy in enemies:
            enemy.update(circle_center_x, circle_center_y)
        
        enemies.draw(wd)

        # Display player's health
        health_text = Font.render(f"Health: {player.health}", True, white)
        wd.blit(health_text, (20, 60))

        # Display score
        score_text = Font.render(f"Score: {score}", True, white)
        wd.blit(score_text, (20, 100))

    else:
        # Display the game over screen
        game_over_text = Font.render("You Lose!", True, white)
        score_text = Font.render(f"Final Score: {score}", True, white)
        wd.blit(game_over_text, (width / 2 - game_over_text.get_width() / 2, height / 2 - game_over_text.get_height() / 2))
        wd.blit(score_text, (width / 2 - score_text.get_width() / 2, height / 2 + 40))

    pygame.display.flip()
    pygame.time.Clock().tick(60)
