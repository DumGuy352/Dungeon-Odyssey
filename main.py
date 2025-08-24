import pygame
import random
import math
import mysql.connector
import Entities

# Colors
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (200,0,0)
GREEN = (0,200,0)
BLUE = (0,0,200)
YELLOW = (200,200,0)
LIGHT_GREY = (40, 40, 40)

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


# --- Game Setup ---
pygame.init()
GAME_AREA_WIDTH, GAME_AREA_HEIGHT = 800, 600

screen = pygame.display.set_mode((GAME_AREA_WIDTH, GAME_AREA_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Dungeon Game")
clock = pygame.time.Clock()

enemies = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

player_x, player_y, player_hp = load_player_data("Player1")
player = Entities.Player(player_x, player_y)
player.hp = player_hp
all_sprites.add(player)
    
def show_mode_select():
    font_big = pygame.font.SysFont(None, 60)
    endless_text = font_big.render("1: Endless Mode", True, WHITE)
    dungeon_text = font_big.render("2: Dungeon Maze", True, WHITE)
    title = font_big.render("Select Game Mode", True, YELLOW)
    while True:
        window_width, window_height = screen.get_size()
        offset_x = (window_width - GAME_AREA_WIDTH) // 2
        offset_y = (window_height - GAME_AREA_HEIGHT) // 2
        screen.fill(BLACK)
        pygame.draw.rect(screen, LIGHT_GREY, (offset_x, offset_y, GAME_AREA_WIDTH, GAME_AREA_HEIGHT))
        pygame.draw.rect(screen, WHITE, (offset_x, offset_y, GAME_AREA_WIDTH, GAME_AREA_HEIGHT), 4)
        screen.blit(title, (offset_x + GAME_AREA_WIDTH//2 - title.get_width()//2, offset_y + 100))
        screen.blit(endless_text, (offset_x + GAME_AREA_WIDTH//2 - endless_text.get_width()//2, offset_y + 220))
        screen.blit(dungeon_text, (offset_x + GAME_AREA_WIDTH//2 - dungeon_text.get_width()//2, offset_y + 320))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "endless"
                if event.key == pygame.K_2:
                    return "dungeon"

# --- Endless Mode ---
def endless_mode():
    player.rect.x, player.rect.y = GAME_AREA_WIDTH//2, GAME_AREA_HEIGHT//2
    player.hp = 100
    enemies.empty()
    projectiles.empty()
    all_sprites.empty()
    all_sprites.add(player)
    score = 0
    spawn_timer = 0
    spawn_interval = 120  # frames (2 seconds at 60 FPS)
    frame_count = 0

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
                global screen
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

        # Remove dead enemies and increase score
        for enemy in list(enemies):
            if enemy.hp <= 0:
                enemies.remove(enemy)
                all_sprites.remove(enemy)
                score += 1

        # Spawn new enemies at intervals (limit total enemies)
        spawn_timer += 1
        if spawn_timer >= spawn_interval and len(enemies) < 8:
            spawn_timer = 0
            enemy_type = random.choice(["normal", "ranged", "boss"])
            x, y = random.randint(50, GAME_AREA_WIDTH-50), random.randint(50, GAME_AREA_HEIGHT-50)
            if enemy_type == "normal":
                color = random.choice([RED, BLUE, YELLOW])
                hp = random.randint(10, 20)
                speed = random.randint(2, 4)
                e = Entities.Enemy(x, y, color, hp, speed)
            elif enemy_type == "ranged":
                hp = random.randint(10, 15)
                speed = random.randint(2, 3)
                e = Entities.RangedEnemy(x, y, hp, speed)
            else:  # boss (rare)
                if not any(isinstance(en, Entities.Boss) for en in enemies):
                    e = Entities.Boss(x, y)
                else:
                    # fallback to normal if boss already exists
                    color = random.choice([RED, BLUE, YELLOW])
                    hp = random.randint(10, 20)
                    speed = random.randint(2, 4)
                    e = Entities.Enemy(x, y, color, hp, speed)
            enemies.add(e)
            all_sprites.add(e)

        projectiles.update()
        for proj in projectiles:
            if player.rect.colliderect(proj.rect):
                player.hp -= 5
                proj.kill()

        # Death condition
        if player.hp <= 0:
            result = show_end_screen(f"Game Over! Score: {score}", RED)
            if result == "restart":
                return "endless"
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

        for sprite in all_sprites:
            sprite_rect = sprite.rect.move(offset_x, offset_y)
            screen.blit(sprite.image, sprite_rect)
        for proj in projectiles:
            proj_rect = proj.rect.move(offset_x, offset_y)
            screen.blit(proj.image, proj_rect)

        font = pygame.font.SysFont(None, 24)
        hp_text = font.render(f'HP: {int(player.hp)}', True, WHITE)
        score_text = font.render(f'Score: {score}', True, WHITE)
        screen.blit(hp_text, (offset_x + 10, offset_y + 10))
        screen.blit(score_text, (offset_x + 10, offset_y + 40))

        pygame.display.flip()

# --- Dungeon Maze Mode ---
MAZE_WIDTH, MAZE_HEIGHT = 5, 5

class MazeRoom:
    def __init__(self, x, y, is_boss=False):
        self.x = x
        self.y = y
        self.visited = False
        self.is_boss = is_boss
        self.doors = {'N': False, 'S': False, 'E': False, 'W': False}
        self.cleared = False

def connect_rooms(dungeon):
    for x in range(MAZE_WIDTH):
        for y in range(MAZE_HEIGHT):
            if x > 0:
                dungeon[x][y].doors['W'] = True
            if x < MAZE_WIDTH - 1:
                dungeon[x][y].doors['E'] = True
            if y > 0:
                dungeon[x][y].doors['N'] = True
            if y < MAZE_HEIGHT - 1:
                dungeon[x][y].doors['S'] = True

def setup_maze_room(room):
    enemies.empty()
    projectiles.empty()
    all_sprites.empty()
    all_sprites.add(player)
    if not room.cleared:  # Only spawn if not cleared
        if room.is_boss:
            boss = Entities.Boss(GAME_AREA_WIDTH//2, GAME_AREA_HEIGHT//2)
            enemies.add(boss)
            all_sprites.add(boss)
        else:
            for _ in range(random.randint(1, 3)):
                color = random.choice([RED, GREEN, BLUE])
                hp = random.randint(10, 20)
                speed = random.randint(2, 4)
                if color == GREEN:
                    e = Entities.RangedEnemy(random.randint(100, GAME_AREA_WIDTH-100), random.randint(100, GAME_AREA_HEIGHT-100), hp, speed)
                else:
                    e = Entities.Enemy(random.randint(100, GAME_AREA_WIDTH-100), random.randint(100, GAME_AREA_HEIGHT-100), color, hp, speed)
                enemies.add(e)
                all_sprites.add(e)
    player.rect.x, player.rect.y = GAME_AREA_WIDTH//2, GAME_AREA_HEIGHT//2
    room.visited = True

def try_move_room(direction, dungeon, player_room):
    x, y = player_room
    room = dungeon[x][y]
    if room.doors[direction]:
        if direction == 'N':
            y -= 1
        elif direction == 'S':
            y += 1
        elif direction == 'E':
            x += 1
        elif direction == 'W':
            x -= 1
        return x, y
    return player_room

def draw_minimap(dungeon, player_room, boss_room):
    minimap_size = 120
    cell_size = minimap_size // MAZE_WIDTH

    window_width, window_height = screen.get_size()
    offset_x = window_width - minimap_size - 20
    offset_y = 20

    for x in range(MAZE_WIDTH):
        for y in range(MAZE_HEIGHT):
            room = dungeon[x][y]
            color = (60, 60, 60)
            if room.visited:
                color = (120, 120, 120)
            if (x, y) == player_room:
                color = (0, 255, 0)
            if (x, y) == boss_room:
                color = (255, 215, 0)

            rect = pygame.Rect(offset_x + x*cell_size, offset_y + y*cell_size, cell_size-2, cell_size-2)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, WHITE, rect, 1)

            cx = offset_x + x*cell_size
            cy = offset_y + y*cell_size
            door_thick = 3
            door_len = cell_size // 4
            if room.doors['N']:
                pygame.draw.line(screen, (200,200,0), (cx + cell_size//2 - door_len//2, cy), (cx + cell_size//2 + door_len//2, cy), door_thick)
            if room.doors['S']:
                pygame.draw.line(screen, (200,200,0), (cx + cell_size//2 - door_len//2, cy + cell_size-2), (cx + cell_size//2 + door_len//2, cy + cell_size-2), door_thick)
            if room.doors['W']:
                pygame.draw.line(screen, (200,200,0), (cx, cy + cell_size//2 - door_len//2), (cx, cy + cell_size//2 + door_len//2), door_thick)
            if room.doors['E']:
                pygame.draw.line(screen, (200,200,0), (cx + cell_size-2, cy + cell_size//2 - door_len//2), (cx + cell_size-2, cy + cell_size//2 + door_len//2), door_thick)

def maze_mode():
    # Generate dungeon and place player/boss
    dungeon = [[MazeRoom(x, y) for y in range(MAZE_HEIGHT)] for x in range(MAZE_WIDTH)]
    connect_rooms(dungeon)
    player_room = (random.randint(0, MAZE_WIDTH-1), random.randint(0, MAZE_HEIGHT-1))
    while True:
        boss_room = (random.randint(0, MAZE_WIDTH-1), random.randint(0, MAZE_HEIGHT-1))
        if boss_room != player_room:
            break
    dungeon[boss_room[0]][boss_room[1]].is_boss = True
    setup_maze_room(dungeon[player_room[0]][player_room[1]])
    frame_count = 0
    running = True
    player.hp = 100

    while running:
        frame_count += 1
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.VIDEORESIZE:
                global screen
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            if event.type == pygame.KEYDOWN:
                # Only allow room movement if all enemies are cleared
                if event.key == pygame.K_UP:
                    if len(enemies) == 0:
                        new_room = try_move_room('N', dungeon, player_room)
                        if new_room != player_room:
                            player_room = new_room
                            setup_maze_room(dungeon[player_room[0]][player_room[1]])
                elif event.key == pygame.K_DOWN:
                    if len(enemies) == 0:
                        new_room = try_move_room('S', dungeon, player_room)
                        if new_room != player_room:
                            player_room = new_room
                            setup_maze_room(dungeon[player_room[0]][player_room[1]])
                elif event.key == pygame.K_LEFT:
                    if len(enemies) == 0:
                        new_room = try_move_room('W', dungeon, player_room)
                        if new_room != player_room:
                            player_room = new_room
                            setup_maze_room(dungeon[player_room[0]][player_room[1]])
                elif event.key == pygame.K_RIGHT:
                    if len(enemies) == 0:
                        new_room = try_move_room('E', dungeon, player_room)
                        if new_room != player_room:
                            player_room = new_room
                            setup_maze_room(dungeon[player_room[0]][player_room[1]])
                elif event.key == pygame.K_p:
                    show_pause_screen()
                elif event.key == pygame.K_SPACE:
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
            
        current_room = dungeon[player_room[0]][player_room[1]]
        if len(enemies) == 0 and not current_room.cleared and not current_room.is_boss:
            current_room.cleared = True

        projectiles.update()
        for proj in projectiles:
            if player.rect.colliderect(proj.rect):
                player.hp -= 5
                proj.kill()

        # Win condition: boss defeated in boss room
        if dungeon[player_room[0]][player_room[1]].is_boss and not any(isinstance(e, Entities.Boss) for e in enemies):
            result = show_end_screen("You Win!", YELLOW)
            if result == "restart":
                return "dungeon"
            else:
                pygame.quit()
                exit()

        # Death condition
        if player.hp <= 0:
            result = show_end_screen("You Died", RED)
            if result == "restart":
                return "dungeon"
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

        for sprite in all_sprites:
            sprite_rect = sprite.rect.move(offset_x, offset_y)
            screen.blit(sprite.image, sprite_rect)
        for proj in projectiles:
            proj_rect = proj.rect.move(offset_x, offset_y)
            screen.blit(proj.image, proj_rect)

        font = pygame.font.SysFont(None, 24)
        hp_text = font.render(f'HP: {int(player.hp)}', True, WHITE)
        screen.blit(hp_text, (offset_x + 10, offset_y + 10))

        # Draw minimap
        draw_minimap(dungeon, player_room, boss_room)

        pygame.display.flip()

# --- Main Loop ---
mode = show_mode_select()
while True:
    if mode == "endless":
        mode = endless_mode()
    elif mode == "dungeon":
        mode = maze_mode()