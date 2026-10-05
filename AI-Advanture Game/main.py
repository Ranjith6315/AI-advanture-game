import pygame
import sys
from collections import deque

pygame.init()

# =========================================================
# WINDOW
# =========================================================

WIDTH = 800
HEIGHT = 600
TILE = 40

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(
    "AI-Based Intelligent Adventure Game"
)

clock = pygame.time.Clock()

# =========================================================
# COLORS
# =========================================================

WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
BLUE = (40, 100, 255)
RED = (220, 50, 50)
GREEN = (40, 180, 80)
YELLOW = (240, 200, 40)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
PURPLE = (150, 70, 200)
ORANGE = (255, 140, 40)

font = pygame.font.Font(None, 30)
big_font = pygame.font.Font(None, 60)

# =========================================================
# GAME VARIABLES
# =========================================================

level = 1

player_size = 30
player_speed = 4

player_x = 70
player_y = 70

enemy_size = 30
enemy_x = 650
enemy_y = 450

enemy_speed = 2.5

health = 100
score = 0

keys_collected = 0

game_over = False
level_complete = False
game_finished = False

last_attack = 0
attack_delay = 700
attack_distance = 40

# =========================================================
# LEVEL 1
# =========================================================

level1_key = pygame.Rect(
    350, 250, 20, 20
)

level1_exit = pygame.Rect(
    700, 70, 55, 55
)

# =========================================================
# LEVEL 2
# =========================================================

level2_key1 = pygame.Rect(
    700, 100, 20, 20
)

level2_key2 = pygame.Rect(
    100, 500, 20, 20
)

level2_exit = pygame.Rect(
    700, 500, 55, 55
)

# =========================================================
# LEVEL 2 WALLS
# =========================================================

level2_walls = [

    pygame.Rect(150, 40, 30, 350),

    pygame.Rect(300, 200, 30, 350),

    pygame.Rect(450, 40, 30, 350),

    pygame.Rect(600, 200, 30, 350)
]

# =========================================================
# BFS GRID
# =========================================================

GRID_WIDTH = WIDTH // TILE
GRID_HEIGHT = HEIGHT // TILE


def wall_at_grid(gx, gy):

    rect = pygame.Rect(
        gx * TILE,
        gy * TILE,
        TILE,
        TILE
    )

    for wall in level2_walls:

        if rect.colliderect(wall):

            return True

    return False


def bfs(start, goal):

    """
    Breadth First Search algorithm.

    Finds the shortest path from
    enemy position to player position.
    """

    queue = deque()

    queue.append(start)

    parent = {
        start: None
    }

    directions = [
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1)
    ]

    while queue:

        current = queue.popleft()

        if current == goal:

            break

        for dx, dy in directions:

            nx = current[0] + dx
            ny = current[1] + dy

            if nx < 0 or nx >= GRID_WIDTH:
                continue

            if ny < 0 or ny >= GRID_HEIGHT:
                continue

            next_node = (nx, ny)

            if next_node in parent:
                continue

            if wall_at_grid(nx, ny):
                continue

            parent[next_node] = current

            queue.append(next_node)

    # No path found

    if goal not in parent:

        return []

    # Reconstruct path

    path = []

    current = goal

    while current is not None:

        path.append(current)

        current = parent[current]

    path.reverse()

    return path


# =========================================================
# GET GRID POSITION
# =========================================================

def get_grid_position(x, y):

    gx = int(
        (x + player_size / 2) // TILE
    )

    gy = int(
        (y + player_size / 2) // TILE
    )

    gx = max(
        0,
        min(GRID_WIDTH - 1, gx)
    )

    gy = max(
        0,
        min(GRID_HEIGHT - 1, gy)
    )

    return gx, gy


# =========================================================
# DISTANCE
# =========================================================

def distance(x1, y1, x2, y2):

    dx = x2 - x1
    dy = y2 - y1

    return (dx * dx + dy * dy) ** 0.5


# =========================================================
# PLAYER COLLISION
# =========================================================

def collision_with_walls(x, y):

    player_rect = pygame.Rect(
        int(x),
        int(y),
        player_size,
        player_size
    )

    for wall in level2_walls:

        if player_rect.colliderect(wall):

            return True

    return False


# =========================================================
# PLAYER MOVEMENT
# =========================================================

def move_player(dx, dy):

    global player_x
    global player_y

    if level == 1:

        player_x += dx
        player_y += dy

    else:

        new_x = player_x + dx

        if (
            0 <= new_x <= WIDTH - player_size
            and not collision_with_walls(
                new_x,
                player_y
            )
        ):

            player_x = new_x

        new_y = player_y + dy

        if (
            0 <= new_y <= HEIGHT - player_size
            and not collision_with_walls(
                player_x,
                new_y
            )
        ):

            player_y = new_y

    player_x = max(
        0,
        min(
            WIDTH - player_size,
            player_x
        )
    )

    player_y = max(
        0,
        min(
            HEIGHT - player_size,
            player_y
        )
    )


# =========================================================
# BFS AI ENEMY
# =========================================================

def move_enemy():

    global enemy_x
    global enemy_y

    # Level 1:
    # Direct chase

    if level == 1:

        dx = player_x - enemy_x
        dy = player_y - enemy_y

        dist = (dx * dx + dy * dy) ** 0.5

        if dist > 0:

            enemy_x += (
                dx / dist
            ) * enemy_speed

            enemy_y += (
                dy / dist
            ) * enemy_speed

        return

    # =====================================================
    # LEVEL 2 - BFS PATHFINDING
    # =====================================================

    start = get_grid_position(
        enemy_x,
        enemy_y
    )

    goal = get_grid_position(
        player_x,
        player_y
    )

    path = bfs(
        start,
        goal
    )

    if len(path) < 2:

        return

    # Next grid cell

    next_cell = path[1]

    target_x = (
        next_cell[0] * TILE
        + TILE // 2
    )

    target_y = (
        next_cell[1] * TILE
        + TILE // 2
    )

    dx = target_x - (
        enemy_x + enemy_size / 2
    )

    dy = target_y - (
        enemy_y + enemy_size / 2
    )

    dist = (dx * dx + dy * dy) ** 0.5

    if dist > 0:

        enemy_x += (
            dx / dist
        ) * enemy_speed

        enemy_y += (
            dy / dist
        ) * enemy_speed


# =========================================================
# LOAD LEVEL
# =========================================================

def load_level(new_level):

    global level
    global player_x
    global player_y
    global enemy_x
    global enemy_y
    global health
    global keys_collected
    global game_over
    global level_complete

    level = new_level

    health = 100

    keys_collected = 0

    game_over = False

    level_complete = False

    if level == 1:

        player_x = 70
        player_y = 70

        enemy_x = 650
        enemy_y = 450

    elif level == 2:

        player_x = 70
        player_y = 70

        enemy_x = 650
        enemy_y = 500


# =========================================================
# RESET GAME
# =========================================================

def reset_game():

    global game_finished
    global score

    game_finished = False

    score = 0

    load_level(1)


# =========================================================
# MAIN GAME LOOP
# =========================================================

running = True

while running:

    current_time = pygame.time.get_ticks()

    # =====================================================
    # EVENTS
    # =====================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        if event.type == pygame.KEYDOWN:

            # Restart

            if event.key == pygame.K_r:

                reset_game()

            # Next level

            if (
                event.key == pygame.K_n
                and level_complete
            ):

                if level == 1:

                    load_level(2)

                elif level == 2:

                    game_finished = True

    # =====================================================
    # GAME LOGIC
    # =====================================================

    if (
        not game_over
        and not level_complete
        and not game_finished
    ):

        # =================================================
        # PLAYER INPUT
        # =================================================

        keyboard = pygame.key.get_pressed()

        dx = 0
        dy = 0

        if keyboard[pygame.K_LEFT]:

            dx -= player_speed

        if keyboard[pygame.K_RIGHT]:

            dx += player_speed

        if keyboard[pygame.K_UP]:

            dy -= player_speed

        if keyboard[pygame.K_DOWN]:

            dy += player_speed

        move_player(
            dx,
            dy
        )

        # =================================================
        # AI
        # =================================================

        move_enemy()

        # =================================================
        # PLAYER RECT
        # =================================================

        player_rect = pygame.Rect(
            int(player_x),
            int(player_y),
            player_size,
            player_size
        )

        # =================================================
        # LEVEL 1
        # =================================================

        if level == 1:

            if player_rect.colliderect(
                level1_key
            ):

                if keys_collected == 0:

                    keys_collected = 1

                    score += 100

            if (
                player_rect.colliderect(
                    level1_exit
                )
                and keys_collected == 1
            ):

                level_complete = True

                score += 500

        # =================================================
        # LEVEL 2
        # =================================================

        elif level == 2:

            if (
                player_rect.colliderect(
                    level2_key1
                )
                and level2_key1.x >= 0
            ):

                level2_key1.x = -100

                keys_collected += 1

                score += 100

            if (
                player_rect.colliderect(
                    level2_key2
                )
                and level2_key2.x >= 0
            ):

                level2_key2.x = -100

                keys_collected += 1

                score += 100

            if (
                player_rect.colliderect(
                    level2_exit
                )
                and keys_collected == 2
            ):

                level_complete = True

                score += 500

        # =================================================
        # ENEMY ATTACK
        # =================================================

        enemy_dist = distance(
            player_x,
            player_y,
            enemy_x,
            enemy_y
        )

        if enemy_dist < attack_distance:

            if (
                current_time - last_attack
                > attack_delay
            ):

                health -= 10

                last_attack = current_time

        # =================================================
        # GAME OVER
        # =================================================

        if health <= 0:

            health = 0

            game_over = True

    # =====================================================
    # DRAW BACKGROUND
    # =====================================================

    screen.fill(WHITE)

    # =====================================================
    # LEVEL 2 WALLS
    # =====================================================

    if level == 2:

        for wall in level2_walls:

            pygame.draw.rect(
                screen,
                DARK_GRAY,
                wall
            )

    # =====================================================
    # LEVEL 1 KEY
    # =====================================================

    if level == 1:

        if keys_collected == 0:

            pygame.draw.circle(
                screen,
                YELLOW,
                level1_key.center,
                10
            )

    # =====================================================
    # LEVEL 2 KEYS
    # =====================================================

    if level == 2:

        if level2_key1.x >= 0:

            pygame.draw.circle(
                screen,
                YELLOW,
                level2_key1.center,
                10
            )

        if level2_key2.x >= 0:

            pygame.draw.circle(
                screen,
                YELLOW,
                level2_key2.center,
                10
            )

    # =====================================================
    # EXIT
    # =====================================================

    if level == 1:

        exit_rect = level1_exit

        required_keys = 1

    else:

        exit_rect = level2_exit

        required_keys = 2

    if keys_collected == required_keys:

        pygame.draw.rect(
            screen,
            GREEN,
            exit_rect
        )

    else:

        pygame.draw.rect(
            screen,
            PURPLE,
            exit_rect
        )

    # =====================================================
    # PLAYER
    # =====================================================

    pygame.draw.rect(
        screen,
        BLUE,
        (
            int(player_x),
            int(player_y),
            player_size,
            player_size
        )
    )

    # =====================================================
    # AI ENEMY
    # =====================================================

    pygame.draw.rect(
        screen,
        RED,
        (
            int(enemy_x),
            int(enemy_y),
            enemy_size,
            enemy_size
        )
    )

    ai_text = font.render(
        "AI",
        True,
        BLACK
    )

    screen.blit(
        ai_text,
        (
            int(enemy_x),
            int(enemy_y - 25)
        )
    )

    # =====================================================
    # HEALTH BAR
    # =====================================================

    health_text = font.render(
        "Health:",
        True,
        BLACK
    )

    screen.blit(
        health_text,
        (20, 15)
    )

    pygame.draw.rect(
        screen,
        GRAY,
        (110, 20, 200, 20)
    )

    pygame.draw.rect(
        screen,
        GREEN,
        (
            110,
            20,
            health * 2,
            20
        )
    )

    # =====================================================
    # LEVEL
    # =====================================================

    level_text = font.render(
        f"LEVEL {level}",
        True,
        BLACK
    )

    screen.blit(
        level_text,
        (360, 20)
    )

    # =====================================================
    # KEYS
    # =====================================================

    key_text = font.render(
        f"Keys: {keys_collected}/{required_keys}",
        True,
        BLACK
    )

    screen.blit(
        key_text,
        (20, 55)
    )

    # =====================================================
    # SCORE
    # =====================================================

    score_text = font.render(
        f"Score: {score}",
        True,
        BLACK
    )

    screen.blit(
        score_text,
        (600, 20)
    )

    # =====================================================
    # AI INFORMATION
    # =====================================================

    if level == 1:

        ai_info = "AI: Direct Chase"

    else:

        ai_info = "AI: BFS Pathfinding"

    ai_info_text = font.render(
        ai_info,
        True,
        ORANGE
    )

    screen.blit(
        ai_info_text,
        (300, 55)
    )

    # =====================================================
    # INSTRUCTIONS
    # =====================================================

    instruction = font.render(
        "Arrow Keys: Move | R: Restart | N: Next Level",
        True,
        BLACK
    )

    screen.blit(
        instruction,
        (190, HEIGHT - 30)
    )

    # =====================================================
    # LEVEL COMPLETE
    # =====================================================

    if level_complete:

        text = big_font.render(
            f"LEVEL {level} COMPLETE!",
            True,
            GREEN
        )

        screen.blit(
            text,
            (210, 240)
        )

        if level == 1:

            next_text = font.render(
                "Press N for Level 2",
                True,
                BLACK
            )

        else:

            next_text = font.render(
                "Press N to Finish Game",
                True,
                BLACK
            )

        screen.blit(
            next_text,
            (300, 310)
        )

    # =====================================================
    # GAME OVER
    # =====================================================

    if game_over:

        overlay = pygame.Surface(
            (WIDTH, HEIGHT)
        )

        overlay.set_alpha(180)

        overlay.fill(BLACK)

        screen.blit(
            overlay,
            (0, 0)
        )

        text = big_font.render(
            "GAME OVER",
            True,
            RED
        )

        screen.blit(
            text,
            (280, 240)
        )

        restart = font.render(
            "Press R to Restart",
            True,
            WHITE
        )

        screen.blit(
            restart,
            (300, 310)
        )

    # =====================================================
    # FINAL SCREEN
    # =====================================================

    if game_finished:

        screen.fill(WHITE)

        text = big_font.render(
            "ADVENTURE COMPLETE!",
            True,
            GREEN
        )

        screen.blit(
            text,
            (180, 220)
        )

        sub_text = font.render(
            f"Final Score: {score}",
            True,
            BLACK
        )

        screen.blit(
            sub_text,
            (320, 300)
        )

        restart = font.render(
            "Press R to Play Again",
            True,
            BLACK
        )

        screen.blit(
            restart,
            (300, 350)
        )

    # =====================================================
    # UPDATE SCREEN
    # =====================================================

    pygame.display.flip()

    clock.tick(60)


pygame.quit()
sys.exit()