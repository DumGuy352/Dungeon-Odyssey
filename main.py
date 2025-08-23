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

def show_win_screen():
    win_font = pygame.font.SysFont(None, 72)
    win_text = win_font.render("You Win!", True, YELLOW)
    info_font = pygame.font.SysFont(None, 36)
    quit_text = info_font.render("Press Q to Quit", True, WHITE)
    restart_text = info_font.render("Press R to Restart", True, WHITE)

    choice_made = False
    while not choice_made:
        screen.fill(BLACK)
        screen.blit(win_text, (GAME_WIDTH//2 - win_text.get_width()//2, GAME_HEIGHT//2 - 80))
        screen.blit(quit_text, (GAME_WIDTH//2 - quit_text.get_width()//2, GAME_HEIGHT//2))
        screen.blit(restart_text, (GAME_WIDTH//2 - restart_text.get_width()//2, GAME_HEIGHT//2 + 50))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                choice_made = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    choice_made = True
                if event.key == pygame.K_r:
                    return "restart"
    return "quit"

def reset_round():
    player.rect.x, player.rect.y = 100, 100
    player.hp = 100
    enemies.empty()
    enemies.add(Entities.Enemy(random.randint(0, WIDTH), random.randint(0, HEIGHT), RED, 10, 4))
    enemies.add(Entities.Enemy(random.randint(0, WIDTH), random.randint(0, HEIGHT), GREEN, 15, 2))
    enemies.add(Entities.Enemy(random.randint(0, WIDTH), random.randint(0, HEIGHT), WHITE, 20, 3))
    boss = Entities.Boss(700, 500)
    enemies.add(boss)
    all_sprites.empty()
    all_sprites.add(player)
    all_sprites.add(enemies)

def show_end_screen(message, color):
    font_big = pygame.font.SysFont(None, 72)
    text = font_big.render(message, True, color)
    font_small = pygame.font.SysFont(None, 36)
    quit_text = font_small.render("Press Q to Quit", True, WHITE)
    restart_text = font_small.render("Press R to Restart", True, WHITE)
    while True:
        screen.fill(BLACK)
        screen.blit(text, (GAME_WIDTH//2 - text.get_width()//2, GAME_HEIGHT//2 - 80))
        screen.blit(quit_text, (GAME_WIDTH//2 - quit_text.get_width()//2, GAME_HEIGHT//2))
        screen.blit(restart_text, (GAME_WIDTH//2 - restart_text.get_width()//2, GAME_HEIGHT//2 + 50))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return "quit"
                if event.key == pygame.K_r:
                    return "restart"

def setup_room(room_index):
    enemies.empty()
    all_sprites.empty()
    all_sprites.add(player)
    room = ROOMS[room_index]
    for enemy_info in room["enemies"]:
        if enemy_info[0] == "normal":
            color, hp, speed = enemy_info[1], enemy_info[2], enemy_info[3]
            x, y = random.randint(100, GAME_WIDTH-100), random.randint(100, GAME_HEIGHT-100)
            e = Entities.Enemy(x, y, color, hp, speed)
            enemies.add(e)
            all_sprites.add(e)
        elif enemy_info[0] == "boss":
            boss = Entities.Boss(GAME_WIDTH//2, GAME_HEIGHT//2)
            enemies.add(boss)
            all_sprites.add(boss)
    player.rect.x, player.rect.y = 100, GAME_HEIGHT//2

def next_room():
    global current_room
    current_room += 1
    if current_room < len(ROOMS):
        setup_room(current_room)
        return True
    return False  # No more rooms, game won

# --- Game Setup ---
pygame.init()
GAME_WIDTH, GAME_HEIGHT = WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dungeon Game")
clock = pygame.time.Clock()

# Colors
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (200,0,0)
GREEN = (0,200,0)
BLUE = (0,0,200)
YELLOW = (200,200,0)

DOOR_COLOR = (150, 75, 0)
DOOR_WIDTH, DOOR_HEIGHT = 40, 80
DOOR_X = GAME_WIDTH - DOOR_WIDTH - 10
DOOR_Y = (GAME_HEIGHT - DOOR_HEIGHT) // 2
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
# Three different monsters
enemies.add(Entities.Enemy(random.randint(0, WIDTH), random.randint(0, HEIGHT), RED, 10, 4))
enemies.add(Entities.Enemy(random.randint(0, WIDTH), random.randint(0, HEIGHT), GREEN, 15, 2))
enemies.add(Entities.Enemy(random.randint(0, WIDTH), random.randint(0, HEIGHT), BLUE, 20, 3))
# Boss
boss = Entities.Boss(700, 500)
enemies.add(boss)

all_sprites = pygame.sprite.Group()
all_sprites.add(player)
all_sprites.add(enemies)
setup_room(current_room)

# --- Main Loop ---
while True:
    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_player_data(player.name, player.rect.x, player.rect.y, player.hp)
                pygame.quit()
                exit()
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

        keys = pygame.key.get_pressed()
        player.update(keys)
        player.clamp_to_game_area(GAME_WIDTH, GAME_HEIGHT)
        for enemy in enemies:
            enemy.ai(player)
            enemy.clamp_to_game_area(GAME_WIDTH, GAME_HEIGHT)
            if player.rect.colliderect(enemy.rect):
                player.hp -= 0.1

        for enemy in list(enemies):
            if enemy.hp <= 0:
                enemies.remove(enemy)
                all_sprites.remove(enemy)

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
        screen.fill(BLACK)
        all_sprites.draw(screen)
        font = pygame.font.SysFont(None, 24)
        hp_text = font.render(f'HP: {int(player.hp)}', True, WHITE)
        room_text = font.render(f'Room: {current_room+1}', True, WHITE)
        screen.blit(hp_text, (10, 10))
        screen.blit(room_text, (10, 40))
        # Draw door if active
        if door_active:
            pygame.draw.rect(screen, DOOR_COLOR, door_rect)
            door_font = pygame.font.SysFont(None, 28)
            door_text = door_font.render("DOOR", True, WHITE)
            screen.blit(door_text, (door_rect.x + 2, door_rect.y + DOOR_HEIGHT//2 - 10))
        pygame.display.flip()