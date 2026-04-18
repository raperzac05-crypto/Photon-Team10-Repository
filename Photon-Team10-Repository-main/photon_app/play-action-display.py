import pygame
import sys
import time
import json
from pathlib import Path
from datetime import timedelta

pygame.init()

if not pygame.mixer.get_init():
    pygame.mixer.init()

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game Action Screen")

# Fonts
title_font = pygame.font.SysFont("arial", 48)
header_font = pygame.font.SysFont("arial", 28)
text_font = pygame.font.SysFont("arial", 22)

# Colors
BLACK = (0,0,0)
WHITE = (255,255,255)
YELLOW = (255,255,0)
BLUE = (60,80,200)

# ---------- OLD EXAMPLE DATA (commented out) ----------
# red_team = {"Opus": 6025}
# green_team = {"Scooby Doo": 5000}
# 
# actions = [
#     "Scooby Doo hit Opus",
#     "Scooby Doo hit Opus",
#     "Scooby Doo hit Opus",
#     "Opus hit Scooby Doo",
#     "Opus hit the base",
#     "Opus hit Scooby Doo",
#     "Opus hit Scooby Doo"
# ]
# -------------------------------------------------------

# Load game data from entry screen
data_file = Path(__file__).resolve().parent / "game_data.json"
if data_file.exists():
    with open(data_file, "r") as f:
        game_data = json.load(f)
    # Build team dictionaries: {codename: score}
    red_team = {p["codename"]: 0 for p in game_data.get("red_team", []) if p.get("codename")}
    green_team = {p["codename"]: 0 for p in game_data.get("green_team", []) if p.get("codename")}
    actions = game_data.get("actions", [])
else:
    # Fallback to example data if no game data file
    red_team = {"Player1": 0}
    green_team = {"Player2": 0}
    actions = []

start_time = time.time()
game_length = 360 

clock = pygame.time.Clock()

return_button = pygame.Rect(300, 540, 300, 40)
show_return = False

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if show_return and return_button.collidepoint(event.pos):
                # Clear game data file and return to entry screen
                running = False
                next_screen = "entry"

    screen.fill(BLACK)  # orange/yellow background

    # Title
    #title = title_font.render("Game Action Screen", True, YELLOW)
    #screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))

    # Scoreboard box
    pygame.draw.rect(screen, BLACK, (50,120,800,150), 3)

    # Headers
    red_header = header_font.render("RED TEAM", True, (200,0,0))
    green_header = header_font.render("GREEN TEAM", True, (0,150,0))

    screen.blit(red_header,(150,130))
    screen.blit(green_header,(550,130))

    # Red team player
    for i,(name,score) in enumerate(red_team.items()):
        text = text_font.render(f"{name}   {score}", True, WHITE)
        screen.blit(text,(100,170 + i*30))

    # Green team player
    for i,(name,score) in enumerate(green_team.items()):
        text = text_font.render(f"{name}   {score}", True, WHITE)
        screen.blit(text,(500,170 + i*30))

    # Action log box
    pygame.draw.rect(screen, BLUE, (50,300,800,200))
    pygame.draw.rect(screen, BLACK, (50,300,800,200),3)

    for i,action in enumerate(actions[-8:]):   # last 8 actions
        text = text_font.render(action, True, WHITE)
        screen.blit(text,(70,320 + i*22))

    # Timer
    remaining = max(0, game_length - int(time.time()-start_time))
    time_str = str(timedelta(seconds=remaining))
    time_str = time_str[-5:]
    timer = text_font.render(f"Time Remaining: {time_str}", True, WHITE)
    screen.blit(timer,(600,520))

    # Return button
    if show_return:
        pygame.draw.rect(screen, BLUE, return_button, border_radius=8)
        pygame.draw.rect(screen, WHITE, return_button, 2, border_radius=8)
        button_text = header_font.render("Return to Entry Screen", True, WHITE)
        text_rect = button_text.get_rect(center=return_button.center)
        screen.blit(button_text, text_rect)

    #return to entry screen after time runs out
    if remaining == 0:
        pygame.mixer.music.stop()
        show_return = True

    pygame.display.flip()
    clock.tick(60)

next_file = Path(__file__).resolve().parent / "next_screen.txt"
next_file.write_text(next_screen)
pygame.quit()
