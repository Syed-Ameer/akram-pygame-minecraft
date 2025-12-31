import pygame
import random
import pygame.sprite

x1 = random.randint(60, 80)
x2 = random.randint(60, 80)

pygame.init()
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("My Pygame Window")

class SimpleSprite(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))

try:
    Steve = pygame.image.load("image.png").convert_alpha()
except pygame.error:
    print("Error loading image.png.")
    Steve = pygame.Surface([50, 50])
    Steve.fill((0, 0, 255))

x = 0
y = 30
clock = pygame.time.Clock()
speed = 2

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    button = pygame.key.get_pressed()

    if button[pygame.K_RIGHT]:
        x += speed
        if x > screen_width:
            x = -Steve.get_width()

    elif button[pygame.K_LEFT]:
        x -= speed
        if x < -Steve.get_width():
            x = screen_width

    elif button[pygame.K_UP]:
        y -= speed
        if y < -Steve.get_height():
            y = screen_height

    if button[pygame.K_DOWN]:
        y += speed
        if y > screen_height:
            y = -Steve.get_height()

    elif button[pygame.K_SPACE]:
        y = y - 5
        if button[pygame.K_LSHIFT]:
            y = y + 5

    screen.fill((0, 0, 0))

    screen.blit(Steve, (x, y))

    pygame.display.flip()

    clock.tick(60)

pygame.quit()