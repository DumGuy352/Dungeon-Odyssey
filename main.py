import pygame
import random
import math
import mysql.connector
import Entities

# --- MySQL Setup (example) ---
def save_player_data(name, x, y, hp):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="dungeon_game"
    )
    cursor = conn.cursor()
    cursor.execute("REPLACE INTO players (name, x, y, hp) VALUES (%s, %s, %s, %s)", (name, x, y, hp))
    conn.commit()
    conn.close()

def load_player_data(name):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="dungeon_game"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT x, y, hp FROM players WHERE name=%s", (name,))
    result = cursor.fetchone()
    conn.close()
    return result if result else (100, 100, 100)

def reset_round():
    global current_room
    current_room = 0
    player.rect.x, player.rect.y = 100, 100
    player.hp = 100
    setup_room(current_room)

def show_end_screen(message, color):
    font_big = pygame.font.SysFont(None, 72)
    text = font_big.render(message, True, color)
    font_small = pygame.font.SysFont(None, 36)
    quit_text = font_small.render("Press Q to Quit", True, WHITE)
    restart_text = font_small.render("Press R to Restart", True, WHITE)
    while True:
        window_width, window_height = screen.get_size()
        offset_x = (window_width - GAME_AREA_WIDTH) // 2
        offset_y = (window_height - GAME_AREA_HEIGHT) // 2
        screen.fill(BLACK)
        pygame.draw.rect(screen, LIGHT_GREY, (offset_x, offset_y, GAME_AREA_WIDTH, GAME_AREA_HEIGHT))
        pygame.draw.rect(screen, WHITE, (offset_x, offset_y, GAME_AREA_WIDTH, GAME_AREA_HEIGHT), 4)
        screen.blit(text, (offset_x + GAME_AREA_WIDTH//2 - text.get_width()//2, offset_y + GAME_AREA_HEIGHT//2 - 80))
        screen.blit(quit_text, (offset_x + GAME_AREA_WIDTH//2 - quit_text.get_width()//2, offset_y + GAME_AREA_HEIGHT//2))
        screen.blit(restart_text, (offset_x + GAME_AREA_WIDTH//2 - restart_text.get_width()//2, offset_y + GAME_AREA_HEIGHT//2 + 50))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return "quit"
                if event.key == pygame.K_r:
                    return "restart"

def show_pause_screen():
    font_big = pygame.font.SysFont(None, 72)
    text = font_big.render("Paused", True, WHITE)
    font_small = pygame.font.SysFont(None, 36)
    resume_text = font_small.render("Press P to Resume", True, WHITE)
    while True:
        window_width, window_height = screen.get_size()
        offset_x = (window_width - GAME_AREA_WIDTH) // 2
        offset_y = (window_height - GAME_AREA_HEIGHT) // 2
        screen.fill(BLACK)
        pygame.draw.rect(screen, LIGHT_GREY, (offset_x, offset_y, GAME_AREA_WIDTH, GAME_AREA_HEIGHT))
        pygame.draw.rect(screen, WHITE, (offset_x, offset_y, GAME_AREA_WIDTH, GAME_AREA_HEIGHT), 4)
        screen.blit(text, (offset_x + GAME_AREA_WIDTH//2 - text.get_width()//2, offset_y + GAME_AREA_HEIGHT//2 - 80))
        screen.blit(resume_text, (offset_x + GAME_AREA_WIDTH//2 - resume_text.get_width()//2, offset_y + GAME_AREA_HEIGHT//2))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    return

def setup_room(room_index):
    enemies.empty()
    all_sprites.empty()
    projectiles.empty()
    all_sprites.add(player)
    room = ROOMS[room_index]
    for enemy_info in room["enemies"]:
        if enemy_info[0] == "normal":
            color, hp, speed = enemy_info[1], enemy_info[2], enemy_info[3]
            x, y = random.randint(100, GAME_AREA_WIDTH-100), random.randint(100, GAME_AREA_HEIGHT-100)
            if color == GREEN:
                e = Entities.RangedEnemy(x, y, hp, speed)
            else:
                e = Entities.Enemy(x, y, color, hp, speed)
            enemies.add(e)
            all_sprites.add(e)
        elif enemy_info[0] == "boss":
            boss = Entities.Boss(GAME_AREA_WIDTH//2, GAME_AREA_HEIGHT//2)
            enemies.add(boss)
            all_sprites.add(boss)
    player.rect.x, player.rect.y = 100, GAME_AREA_HEIGHT//2

def next_room():
    global current_room
    current_room += 1
    if current_room < len(ROOMS):
        setup_room(current_room)
        return True
    return False  # No more rooms, game won

# --- Game Setup ---
pygame.init()
GAME_AREA_WIDTH, GAME_AREA_HEIGHT = 800, 600
screen = pygame.display.set_mode((GAME_AREA_WIDTH, GAME_AREA_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Dungeon Game")
clock = pygame.time.Clock()

# Colors
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (200,0,0)
GREEN = (0,200,0)
BLUE = (0,0,200)
YELLOW = (200,200,0)
LIGHT_GREY = (40, 40, 40)

DOOR_COLOR = (150, 75, 0)
DOOR_WIDTH, DOOR_HEIGHT = 40, 80
DOOR_X = (GAME_AREA_WIDTH - DOOR_WIDTH) - 10
DOOR_Y = (GAME_AREA_HEIGHT - DOOR_HEIGHT) // 2
door_rect = pygame.Rect(DOOR_X, DOOR_Y, DOOR_WIDTH, DOOR_HEIGHT)

current_room = 0

# --- Game Objects ---
player_x, player_y, player_hp = load_player_data("Player1")
player = Entities.Player(player_x, player_y)
player.hp = player_hp

ROOMS = [
    {"enemies": []},  # Room 1: spawn, no enemies
    {"enemies": [("normal", RED, 10, 4), ("normal", GREEN, 15, 2)]},  # Room 2
    {"enemies": [("normal", BLUE, 20, 3), ("normal", RED, 10, 4)]},   # Room 3
    {"enemies": [("boss", YELLOW, 50, 2)]}  # Room 4: boss only
]

enemies = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)
setup_room(current_room)
frame_count = 0

# --- Main Loop ---
while True:
    running = True
    while running:
        frame_count += 1
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_player_data(player.name, player.rect.x, player.rect.y, player.hp)
                pygame.quit()
                exit()
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    for enemy in enemies:
                        dx = enemy.rect.centerx - player.rect.centerx
                        dy = enemy.rect.centery - player.rect.centery
                        dist = math.hypot(dx, dy)
                        if dist < 60:
                            enemy.hp -= 5
                            if dist != 0:
                                enemy.knockback[0] = (dx/dist) * 10
                                enemy.knockback[1] = (dy/dist) * 10
                elif event.key == pygame.K_p:
                    show_pause_screen()

        keys = pygame.key.get_pressed()
        player.update(keys)
        player.clamp_to_game_area(GAME_AREA_WIDTH, GAME_AREA_HEIGHT)
        for enemy in enemies:
            if isinstance(enemy, Entities.RangedEnemy):
                enemy.ai(player, projectiles, frame_count)
            elif isinstance(enemy, Entities.Boss):
                enemy.ai(player, projectiles, frame_count)
            else:
                enemy.ai(player)
            enemy.clamp_to_game_area(GAME_AREA_WIDTH, GAME_AREA_HEIGHT)
            if player.rect.colliderect(enemy.rect):
                player.hp -= 0.1

        for enemy in list(enemies):
            if enemy.hp <= 0:
                enemies.remove(enemy)
                all_sprites.remove(enemy)

        projectiles.update()
        for proj in projectiles:
            if player.rect.colliderect(proj.rect):
                player.hp -= 5
                proj.kill()

        # --- Door logic ---
        door_active = len(enemies) == 0 and current_room < len(ROOMS) - 1

        # If in the last room (boss room), show win screen when boss is defeated
        if current_room == len(ROOMS) - 1:
            boss_alive = any(isinstance(e, Entities.Boss) for e in enemies)
            if not boss_alive:
                result = show_end_screen("You Win!", YELLOW)
                if result == "restart":
                    current_room = 0
                    setup_room(current_room)
                    player.hp = 100
                    break
                else:
                    pygame.quit()
                    exit()
        # For other rooms, use the door to go to next room
        elif door_active and player.rect.colliderect(door_rect):
            if next_room():
                break  # Go to next room

        # DEATH CONDITION
        if player.hp <= 0:
            result = show_end_screen("You Died", RED)
            if result == "restart":
                current_room = 0
                setup_room(current_room)
                player.hp = 100
                break
            else:
                pygame.quit()
                exit()

        # Drawing
        window_width, window_height = screen.get_size()
        offset_x = (window_width - GAME_AREA_WIDTH) // 2
        offset_y = (window_height - GAME_AREA_HEIGHT) // 2

        screen.fill(BLACK)
        pygame.draw.rect(screen, LIGHT_GREY, (offset_x, offset_y, GAME_AREA_WIDTH, GAME_AREA_HEIGHT))
        pygame.draw.rect(screen, WHITE, (offset_x, offset_y, GAME_AREA_WIDTH, GAME_AREA_HEIGHT), 4)

        # Draw sprites with offset
        for sprite in all_sprites:
            sprite_rect = sprite.rect.move(offset_x, offset_y)
            screen.blit(sprite.image, sprite_rect)

        # Draw projectiles with offset
        for proj in projectiles:
            proj_rect = proj.rect.move(offset_x, offset_y)
            screen.blit(proj.image, proj_rect)

        # Draw HUD/text with offset
        font = pygame.font.SysFont(None, 24)
        hp_text = font.render(f'HP: {int(player.hp)}', True, WHITE)
        room_text = font.render(f'Room: {current_room+1}', True, WHITE)
        screen.blit(hp_text, (offset_x + 10, offset_y + 10))
        screen.blit(room_text, (offset_x + 10, offset_y + 40))

        # Draw door if active
        if door_active:
            door_rect_offset = door_rect.move(offset_x, offset_y)
            pygame.draw.rect(screen, DOOR_COLOR, door_rect_offset)
            door_font = pygame.font.SysFont(None, 28)
            door_text = door_font.render("DOOR", True, WHITE)
            screen.blit(door_text, (door_rect_offset.x + 2, door_rect_offset.y + DOOR_HEIGHT//2 - 10))

        pygame.display.flip()