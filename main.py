import pygame, os
import spritesheet

pygame.init()       # Initialize Pygame with all the modules avaialable in pygame
pygame.display.set_caption("Dungeon Crawler")       # Set the window title
pygame.display.set_icon(pygame.image.load("Assets/Ghost Sprite.png"))  # Set the window icon

size = SCREEN_WIDTH, SCREEN_HEIGHT = 500, 500
speed = [0, 0]
BG = 50, 50, 50
BLACK = 0, 0, 0

clock = pygame.time.Clock()         # Create a clock object to control the frame rate

screen = pygame.display.set_mode(size,pygame.RESIZABLE)  # Create a window with the specified size and make it resizable

ball = pygame.image.load("Assets/Ghost Sprite.png").convert()
ballrect = ball.get_rect()

dirname = os.path.dirname(__file__)
assets_dir = os.path.join(dirname, 'Assets')
frog_boss_dir = os.path.join(assets_dir, 'Frog Boss')

spritesheet_image = pygame.image.load(os.path.join(frog_boss_dir, "FROG BOSS SPRITESHEET.png")).convert_alpha()
spritesheet_instance = spritesheet.SpriteSheet(spritesheet_image)

animation_list = []
animation_steps = [5, 8, 11, 8]
action = 0
last_update = pygame.time.get_ticks()
animation_cooldown = 100
step_count = 0

for animation in animation_steps:
    temp_list = []
    for _ in range(animation):
        temp_list.append(spritesheet_instance.get_image(step_count, 64, 161, 2, BLACK))
        step_count += 1
    animation_list.append(temp_list)


running = True
while running:  # Main game loop
    for event in pygame.event.get():            # To handle quiting the game without issues
        if event.type == pygame.QUIT:
            running = False

    clock.tick(60)

    key = pygame.key.get_pressed()  # Get the current state of all keys
 
    if key[pygame.K_a] and not key[pygame.K_d]:
        speed[0] = -2
    elif key[pygame.K_d] and not key[pygame.K_a]:
        speed[0] = 2
    else:
        speed[0] = 0
    if key[pygame.K_w] and not key[pygame.K_s]:
        speed[1] = -2
    elif key[pygame.K_s] and not key[pygame.K_w]:
        speed[1] = 2
    else:
        speed[1] = 0
    # Normalize diagonal movement speed
    if speed[0] != 0 and speed[1] != 0:
        speed[0] /= 1.4142  # sqrt(2)
        speed[1] /= 1.4142

    ballrect = ballrect.move(speed)  # Move the ball based on the speed

    screen.fill(BG)
    screen.blit(ball, ballrect)
    pygame.display.flip()