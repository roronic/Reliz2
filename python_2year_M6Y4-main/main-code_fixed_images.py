import pygame
import random
from pathlib import Path

pygame.init()

WIDTH, HEIGHT = 600, 500
TILE = 50
COLS, ROWS = WIDTH // TILE, HEIGHT // TILE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Гном-шахтер: Еволюція")

font = pygame.font.SysFont("Arial", 20)
big_font = pygame.font.SysFont("Arial", 50, bold=True)

IMAGE_URLS = {
    "gold": "goldblock.jfif",
    "silver": "ironblock.png",
    "diamond": "diamondblock.jfif",
    "emerald": "emeraldblock.jfif",
    "redstone": "redstoneblock.jfif",
    "mystery": "ChatGPT Image 20 вер. 2026 р., 11_06_58.png",
    "dirt": "dirt.jpg",
    "bomb": "TNT.png",
    "player": "ChatGPT Image 20 вер. 2026 р., 11_17_25.png"
}

# Ищем картинки в папке с программой и во всех её подпапках.
# Поэтому картинки можно хранить, например, в папке "картинки майнкрафт".
images = {}
BASE_DIR = Path(__file__).resolve().parent

def find_image(filename):
    # Сначала ищем рядом с программой.
    direct = BASE_DIR / filename
    if direct.is_file():
        return direct

    # Потом ищем во всех подпапках проекта.
    filename_lower = filename.lower()
    for path in BASE_DIR.rglob("*"):
        if path.is_file() and path.name.lower() == filename_lower:
            return path

    return None

def load_image(name, size=(TILE, TILE)):
    path = find_image(IMAGE_URLS[name])

    if path is None:
        print(f"[ПРЕДУПРЕЖДЕНИЕ] Не найдена картинка: {IMAGE_URLS[name]}")
        return None

    try:
        image = pygame.image.load(str(path)).convert_alpha()
        print(f"[OK] Загружена картинка: {path}")
        return pygame.transform.scale(image, size)
    except pygame.error as error:
        print(f"[ОШИБКА] Не удалось загрузить {path}: {error}")
        return None

for image_name in IMAGE_URLS:
    images[image_name] = load_image(image_name)

money = 0
pickaxe = 1
level = 1
state = "MENU"

backpack = {
    "gold": 0,
    "silver": 0,
    "emerald": 0,
    "redstone": 0,
    "diamond": 0,
    "mystery": 0
}

prices = {
    "gold": 50,
    "silver": 120,
    "emerald": 250,
    "redstone": 500,
    "diamond": 1000,
    "mystery": 5000
}

pickaxe_costs = {
    2: 300,
    3: 1000,
    4: 2500,
    5: 6000
}

# Цвета блоков. В исходном коде эти переменные не были объявлены,
# из-за чего программа падала с NameError ещё до запуска игры.
AIR = (35, 39, 46)
DIRT = (125, 78, 45)
GOLD = (255, 215, 0)
BASE = (90, 90, 100)
SILVER = (180, 180, 190)
DIAMOND = (80, 220, 255)
EMERALD = (40, 200, 120)
REDSTONE = (220, 50, 50)
MYSTERY = (150, 80, 220)
BOMB = (70, 20, 20)
PLAYER = (70, 140, 255)

colors = {
    0: AIR,
    1: DIRT,
    2: GOLD,
    3: BASE,
    4: SILVER,
    5: DIAMOND,
    6: EMERALD,
    7: REDSTONE,
    8: MYSTERY,
    9: BOMB
}

grid = []
mystery_hits = {}
player_x = COLS // 2
player_y = 1
jump = 0

def button(text, x, y, w, h, color):
    r = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, color, r, border_radius=6)
    t = font.render(text, True, (255, 255, 255))
    screen.blit(t, (x + (w - t.get_width()) // 2,
                    y + (h - t.get_height()) // 2))
    return r

def generate_map(lvl):
    global grid, player_x, player_y, mystery_hits

    player_x, player_y = COLS // 2, 1
    mystery_hits = {}
    grid = []

    for y in range(ROWS):
        row = []

        for x in range(COLS):
            if y == 0 and x == COLS // 2:
                block = 3
            elif y < 2:
                block = 0
            else:
                r = random.random()

                if lvl == 1:
                    block = 2 if r < .15 else 1

                elif lvl == 2:
                    block = 2 if r < .10 else 4 if r < .18 else 1

                elif lvl == 3:
                    block = 6 if r < .10 else 4 if r < .18 else 2 if r < .30 else 1

                elif lvl == 4:
                    block = 7 if r < .08 else 6 if r < .16 else 4 if r < .24 else 2 if r < .36 else 1

                elif lvl == 5:
                    block = 5 if r < .07 else 7 if r < .14 else 6 if r < .21 else 4 if r < .29 else 2 if r < .42 else 1

                else:
                    block = (
                        9 if r < .15 else
                        2 if r < .30 else
                        8 if r < .34 else
                        5 if r < .40 else
                        7 if r < .48 else
                        6 if r < .56 else
                        4 if r < .64 else
                        1
                    )

            row.append(block)

            if block == 8:
                mystery_hits[(x, y)] = 10

        grid.append(row)

def reset():
    global money, pickaxe, level, state, backpack
    money = 0
    pickaxe = 1
    level = 1
    state = "MENU"
    backpack = {
        "gold": 0,
        "silver": 0,
        "emerald": 0,
        "redstone": 0,
        "diamond": 0,
        "mystery": 0
    }

def sell():
    global money, backpack

    for ore, count in backpack.items():
        money += count * prices[ore] * level

    for ore in backpack:
        backpack[ore] = 0

pygame.time.set_timer(pygame.USEREVENT, 350)
clock = pygame.time.Clock()
running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.USEREVENT and state == "GAME":
            if jump:
                jump -= 1
            elif player_y < ROWS - 1 and grid[player_y + 1][player_x] in (0, 3):
                player_y += 1

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            pos = event.pos

            if state == "MENU":
                if play.collidepoint(pos):
                    state = "LEVELS"
                elif quit_btn.collidepoint(pos):
                    running = False

            elif state == "LEVELS":

                for b, lvl in level_buttons:
                    if b.collidepoint(pos):
                        level = lvl
                        generate_map(level)
                        state = "GAME"

                if level6 and level6.collidepoint(pos):
                    level = 6
                    generate_map(6)
                    state = "GAME"

                if shop.collidepoint(pos):
                    state = "SHOP"

                elif back.collidepoint(pos):
                    state = "MENU"

            elif state == "SHOP":

                if upgrade and upgrade.collidepoint(pos):
                    nxt = pickaxe + 1
                    if nxt <= 5 and money >= pickaxe_costs[nxt]:
                        money -= pickaxe_costs[nxt]
                        pickaxe = nxt

                if shop_back.collidepoint(pos):
                    state = "LEVELS"

            elif state == "WIN":

                if reset_btn.collidepoint(pos):
                    reset()

        elif event.type == pygame.KEYDOWN and state == "GAME":

            if event.key == pygame.K_RETURN:
                state = "LEVELS"
                continue

            nx, ny = player_x, player_y
            allowed = False
            jumping = False

            if event.key == pygame.K_LEFT and player_x > 0:
                nx -= 1
                allowed = True

            elif event.key == pygame.K_RIGHT and player_x < COLS - 1:
                nx += 1
                allowed = True

            elif event.key == pygame.K_DOWN and player_y < ROWS - 1:
                ny += 1
                allowed = True

            elif event.key == pygame.K_UP and player_y > 0:
                ground = (
                    player_y == ROWS - 1 or
                    grid[player_y + 1][player_x] not in (0, 3)
                )
                if ground or grid[player_y][player_x] == 3:
                    ny -= 1
                    allowed = True
                    jumping = True

            elif event.key == pygame.K_SPACE:
                if player_y < ROWS - 1 and grid[player_y + 1][player_x] == 0:
                    grid[player_y + 1][player_x] = 1

            if allowed:
                block = grid[ny][nx]

                if block == 9:
                    running = False
                    continue

                if block == 1:
                    grid[ny][nx] = 0
                    player_x, player_y = nx, ny

                elif block == 2:
                    backpack["gold"] += 1
                    grid[ny][nx] = 0
                    player_x, player_y = nx, ny

                elif block == 4 and pickaxe >= 2:
                    backpack["silver"] += 1
                    grid[ny][nx] = 0
                    player_x, player_y = nx, ny

                elif block == 6 and pickaxe >= 3:
                    backpack["emerald"] += 1
                    grid[ny][nx] = 0
                    player_x, player_y = nx, ny

                elif block == 7 and pickaxe >= 4:
                    backpack["redstone"] += 1
                    grid[ny][nx] = 0
                    player_x, player_y = nx, ny

                elif block == 5 and pickaxe >= 5:
                    backpack["diamond"] += 1
                    grid[ny][nx] = 0
                    player_x, player_y = nx, ny

                elif block == 8 and pickaxe >= 5:
                    key = (nx, ny)
                    mystery_hits[key] -= 1

                    if mystery_hits[key] <= 0:
                        backpack["mystery"] += 1
                        grid[ny][nx] = 0
                        del mystery_hits[key]
                        player_x, player_y = nx, ny
                        state = "WIN"

                elif block in (0, 3):
                    player_x, player_y = nx, ny

                if jumping:
                    jump = 2

    if state == "GAME":
        if grid[player_y][player_x] == 3 or (
            player_y < ROWS - 1 and grid[player_y + 1][player_x] == 3
        ):
            sell()

    screen.fill((40, 44, 52))

    if state == "MENU":

        title = big_font.render("ГНОМ-ШАХТЕР", True, GOLD)
        screen.blit(title, ((WIDTH - title.get_width()) // 2, 80))

        play = button("ГРАТИ", 200, 200, 200, 50, (46, 204, 113))
        quit_btn = button("ВИЙТИ", 200, 280, 200, 50, (231, 76, 60))

    elif state == "LEVELS":

        title = font.render("ВИБІР РІВНЯ", True, (255, 255, 255))
        screen.blit(title, ((WIDTH - title.get_width()) // 2, 35))

        level_buttons = []

        for i in range(1, 6):
            b = button(
                f"Рівень {i}",
                40,
                80 + (i - 1) * 60,
                220,
                45,
                (52, 152, 219)
            )
            level_buttons.append((b, i))

        if pickaxe >= 5:
            level6 = button("Рівень 6 💣", 320, 80, 230, 50, (90, 30, 110))
        else:
            button("Рівень 6 🔒", 320, 80, 230, 50, (80, 80, 80))
            level6 = None

        shop = button("КРАМНИЦЯ", 320, 160, 230, 55, (155, 89, 182))
        back = button("НАЗАД", 320, 235, 230, 50, (149, 165, 166))

    elif state == "SHOP":

        title = font.render("КРАМНИЦЯ КАЙЛА", True, (255, 255, 255))
        screen.blit(title, ((WIDTH - title.get_width()) // 2, 50))

        txt = font.render(
            f"Монети: {money}   Кирка: {pickaxe}",
            True,
            (255, 255, 255)
        )
        screen.blit(txt, (150, 120))

        nxt = pickaxe + 1

        if nxt <= 5:
            upgrade = button(
                f"Кирка {nxt} — {pickaxe_costs[nxt]}",
                100,
                210,
                400,
                60,
                (46, 204, 113)
            )
        else:
            upgrade = None
            button(
                "МАКСИМАЛЬНЕ КАЙЛО!",
                80,
                210,
                440,
                60,
                (127, 140, 141)
            )

        shop_back = button("НАЗАД", 200, 330, 200, 50, (149, 165, 166))

    elif state == "GAME":

        for y in range(ROWS):
            for x in range(COLS):

                rect = pygame.Rect(x * TILE, y * TILE, TILE, TILE)
                block = grid[y][x]

                image_name = {
                    1: "dirt",
                    2: "gold",
                    4: "silver",
                    5: "diamond",
                    6: "emerald",
                    7: "redstone",
                    8: "mystery",
                    9: "bomb"
                }.get(block)

                if image_name and images.get(image_name):
                    screen.blit(images[image_name], rect)
                else:
                    pygame.draw.rect(screen, colors[block], rect)

                pygame.draw.rect(screen, (50, 50, 50), rect, 1)

                if block == 8:
                    n = mystery_hits.get((x, y), 10)
                    t = font.render(str(n), True, (255, 255, 255))
                    screen.blit(t, (rect.x + 17, rect.y + 12))

                if block == 9:
                    pygame.draw.circle(screen, (180, 0, 0), rect.center, 10)

        player = pygame.Rect(
            player_x * TILE,
            player_y * TILE,
            TILE,
            TILE
        )
        if images.get("player"):
            screen.blit(images["player"], player)
        else:
            pygame.draw.rect(screen, PLAYER, player)

        info = (
            f"Рівень {level} | Кайло {pickaxe} | Монети: {money} | "
            f"G:{backpack['gold']} S:{backpack['silver']} "
            f"E:{backpack['emerald']} R:{backpack['redstone']} "
            f"D:{backpack['diamond']} M:{backpack['mystery']}"
        )

        screen.blit(
            pygame.font.SysFont("Arial", 13, bold=True).render(
                info, True, (0, 0, 0)
            ),
            (8, 14)
        )

        if level == 6:
            warning = font.render(
                "БОМБИ ВБИВАЮТЬ!",
                True,
                (255, 50, 50)
            )
            screen.blit(warning, (10, HEIGHT - 30))

    elif state == "WIN":

        title = big_font.render(
            "ПЕРЕМОГА!",
            True,
            (255, 215, 0)
        )

        screen.blit(
            title,
            (
                (WIDTH - title.get_width()) // 2,
                120
            )
        )

        text = font.render(
            "Ти здобув фінальну руду!",
            True,
            (255, 255, 255)
        )

        screen.blit(
            text,
            (
                (WIDTH - text.get_width()) // 2,
                200
            )
        )

        reset_btn = button(
            "ЗАНОВО",
            200,
            290,
            200,
            60,
            (231, 76, 60)
        )

    pygame.display.flip()

pygame.quit()