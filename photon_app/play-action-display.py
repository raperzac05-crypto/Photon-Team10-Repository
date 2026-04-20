#this is the main game action display screen. It shows the current scores for each player, a log of recent actions, and a timer counting down the remaining game time. It also listens for incoming hit events from the traffic generator and updates scores and logs accordingly.

import pygame
import sys
import time
import socket
import json
from pathlib import Path
from datetime import timedelta

pygame.init()

if not pygame.mixer.get_init():
    pygame.mixer.init()

from sockets import create_udp_sockets, close_sockets, broadcast_message

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game Action Screen")

BASE_ICON_PATH = Path(__file__).resolve().parent / "assets" / "baseicon.jpg"

base_icon = pygame.image.load(str(BASE_ICON_PATH)).convert_alpha()
base_icon = pygame.transform.smoothscale(base_icon, (20, 20))

# Fonts
title_font = pygame.font.SysFont("arial", 48)
header_font = pygame.font.SysFont("arial", 28)
text_font = pygame.font.SysFont("arial", 22)

# Colors
BLACK = (0,0,0)
WHITE = (255,255,255)
YELLOW = (255,255,0)
BLUE = (60,80,200)
RED = (200,0,0)
GOLD = (255,215,0)
GREEN = (0,150,0)

#scoring
base_hit_players = set()
HIT_POINTS = 10
BASE_HIT_POINTS = 100

FRIENDLY_FIRE_PENALTY = -10

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

players = []
actions = []
red_team = {}
green_team = {}
equipment_map = {}

if data_file.exists():
    with open(data_file, "r") as f:
        game_data = json.load(f)

    red_players = game_data.get("red_team", [])
    green_players = game_data.get("green_team", [])
    actions = game_data.get("actions", [])

    for p in red_players:
        p["team"] = "red"
        players.append(p)

    for p in green_players:
        p["team"] = "green"
        players.append(p)

    # scoreboards by codename
    red_team = {p["codename"]: 0 for p in red_players if p.get("codename")}
    green_team = {p["codename"]: 0 for p in green_players if p.get("codename")}

    # equipment_id -> player dict
    for p in players:
        eq = p.get("equipment_id")
        if eq != "" and eq is not None:
            try:
                equipment_map[int(eq)] = p
            except ValueError:
                pass
else:
    red_team = {"Player1": 0}
    green_team = {"Player2": 0}
    actions = []

#UDP setup
transmit_socket, receive_socket = create_udp_sockets()
receive_socket.setblocking(False)

transmit_socket.sendto("202".encode("utf-8"), ("127.0.0.1", 7500))
print("Sent start signal to traffic generator")

#helpers
def add_action(text):
    actions.append(text)
    if len(actions) > 50:
        actions.pop(0)

# def is_in_timeout(player):
#     eq = player.get("equipment_id")
#     if eq is None:
#         return False
#     return time.time() < timeout_until.get(int(eq), 0)

# def apply_timeout(player):
#     eq = player.get("equipment_id")
#     if eq is None:
#         return
#     timeout_until[int(eq)] = time.time() + FRIENDLY_FIRE_TIMEOUT

def get_player_by_equipment_id(equipment_id):
    return equipment_map.get(equipment_id)

def update_score(player, delta):
    if player["team"] == "red":
        red_team[player["codename"]] += delta
    else:
        green_team[player["codename"]] += delta

def process_hit(attacker_id, target_id):
    attacker = get_player_by_equipment_id(attacker_id)
    target = get_player_by_equipment_id(target_id)

    #invalid hit handling
    if attacker is None or target is None:
        add_action(f"Invalid hit event: {attacker_id} -> {target_id}")
        return
    #self hit handling
    if attacker["player_id"] == target["player_id"]:
        add_action(f"{attacker['codename']} hit themselves! No points awarded.")
        return
    #friendly fire handling
    if attacker["team"] == target["team"]:
        update_score(attacker, FRIENDLY_FIRE_PENALTY)
        add_action(f"{attacker['codename']} hit teammate {target['codename']}! {FRIENDLY_FIRE_PENALTY} points.")
        return
    #valid hit
    update_score(attacker, HIT_POINTS)
    add_action(f"{attacker['codename']} hit {target['codename']}! {HIT_POINTS} points.")

def handle_base_hit(attacker_id, base_team):
    attacker = get_player_by_equipment_id(attacker_id)

    #invalid hit handling
    if attacker is None:
        add_action(f"Invalid base hit event: {attacker_id}")
        return
    #friendly fire handling
    if attacker["team"] == base_team:
        add_action(f"{attacker['codename']} tried to hit their own base! No points awarded.")
        return
    update_score(attacker, BASE_HIT_POINTS)
    add_action(f"{attacker['codename']} hit the base! {BASE_HIT_POINTS} points.")

def parse_event_message(message):
    msg = message.strip().lower()

    if not msg or ":" not in msg:
        return None
    
    parts = msg.split(":")
    if len(parts) != 2:
        return None
    
    try:
        attacker_id = int(parts[0].strip())
        target_id = int(parts[1].strip())
    except ValueError:
        return None
    
    if target_id == 43:
        return ("base", attacker_id, "green")
    elif target_id == 53:
        return ("base", attacker_id, "red")
    else:
        return ("hit", attacker_id, target_id)

def process_network_events():
    while True:
        try:
            data, _ = receive_socket.recvfrom(1024)
        except BlockingIOError:
            break
        except OSError:
            break
        
        #get and parse message
        raw_message = data.decode("utf-8").strip()
        parsed = parse_event_message(raw_message)

        if parsed is None:
            add_action(f"Unknown event: {raw_message}")
            continue

        #handle hit events
        if parsed[0] == "hit":
            _, attacker_id, target_id = parsed
            attacker = get_player_by_equipment_id(attacker_id)
            target = get_player_by_equipment_id(target_id)

            if attacker is None or target is None:
                add_action(f"Invalid hit event: {attacker_id} -> {target_id}")
                continue

            if attacker["player_id"] == target["player_id"]:
                add_action(f"{attacker['codename']} hit themselves! No points awarded.")
                continue

            if attacker["team"] == target["team"]:
                update_score(attacker, FRIENDLY_FIRE_PENALTY)
                update_score(target, FRIENDLY_FIRE_PENALTY)
                add_action(
                    f"{attacker['codename']} hit teammate {target['codename']}! "
                    f"Both lose 10 points."
                )
                transmit_socket.sendto(str(attacker_id).encode("utf-8"), ("127.0.0.1", 7500))
                transmit_socket.sendto(str(target_id).encode("utf-8"), ("127.0.0.1", 7500))
                continue

            update_score(attacker, HIT_POINTS)
            add_action(f"{attacker['codename']} hit {target['codename']}! {HIT_POINTS} points.")
            transmit_socket.sendto(str(target_id).encode("utf-8"), ("127.0.0.1", 7500))

        #handle base hit events
        elif parsed[0] == "base":
            _, attacker_id, base_team = parsed
            attacker = get_player_by_equipment_id(attacker_id)
            if attacker is None:
                add_action(f"Invalid base hit event: {attacker_id}")
                continue
            if attacker["team"] == base_team:
                add_action(f"{attacker['codename']} tried to hit their own base! No points awarded.")
                continue
            update_score(attacker, BASE_HIT_POINTS)
            
            base_hit_players.add(attacker["codename"])
            
            add_action(f"{attacker['codename']} hit the {base_team} base! {BASE_HIT_POINTS} points.")
            transmit_socket.sendto(str(attacker_id).encode("utf-8"), ("127.0.0.1", 7500))

#main loop setup
start_time = time.time()
game_length = 360

clock = pygame.time.Clock()

return_button = pygame.Rect(300, 540, 300, 40)
show_return = False

#main loop
running = True
next_screen = "quit"
game_over_sent = False

while running:
    process_network_events()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if show_return and return_button.collidepoint(event.pos):
                if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                # Clear game data file and return to entry screen
                running = False
                next_screen = "entry"

    screen.fill(BLACK)  # orange/yellow background

    # Title
    #title = title_font.render("Game Action Screen", True, YELLOW)
    #screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))

    # Scoreboard box
    pygame.draw.rect(screen, BLACK, (50,120,800,150), 3)

    #red cumulative score
    red_score = sum(red_team.values())
    red_score_text = header_font.render(f"Total Score: {red_score}", True, (200,0,0))
    screen.blit(red_score_text, (150,130))

    #green cumulative score
    green_score = sum(green_team.values())
    green_score_text = header_font.render(f"Total Score: {green_score}", True, (0,150,0))
    screen.blit(green_score_text, (550,130))

    if red_score > green_score:
        leader = "red"
    elif green_score > red_score:
        leader = "green"
    flash = int(pygame.time.get_ticks() // 400) % 2 == 0

    # Headers
    red_header_color = GOLD if leader == "red" and flash else RED
    green_header_color = GOLD if leader == "green" and flash else GREEN
    red_score_color = GOLD if leader == "red" and flash else RED
    green_score_color = GOLD if leader == "green" and flash else GREEN

    screen.blit(header_font.render("Red Team", True, red_header_color), (150,99))
    screen.blit(header_font.render("Green Team", True, green_header_color), (550,99))
    screen.blit(header_font.render(f"Total Score: {red_score}", True, red_score_color), (150,130))
    screen.blit(header_font.render(f"Total Score: {green_score}", True, green_score_color), (550,130))

    # Red team player
    sorted_red = sorted(red_team.items(), key=lambda x: x[1], reverse=True)
    for i,(name,score) in enumerate(sorted_red):
        y = 170 + i*30
        
        text = text_font.render(f"{name}   {score}", True, WHITE)
        icon_x = 100
        text_x = 130 if name in base_hit_players else 100

        if name in base_hit_players:
            screen.blit(base_icon, (icon_x, y))
            
        screen.blit(text,(text_x, y))

    # Green team player
    sorted_green = sorted(green_team.items(), key=lambda x: x[1], reverse=True)
    for i,(name,score) in enumerate(sorted_green):
        y = 170 + i*30

        text = text_font.render(f"{name}   {score}", True, WHITE)
        icon_x = 500
        text_x = 530 if name in base_hit_players else 500

        if name in base_hit_players:
            screen.blit(base_icon, (icon_x, y))
            
        screen.blit(text,(text_x, y))

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
        show_return = True
        if not game_over_sent:
            for _ in range(3):
                transmit_socket.sendto("221".encode("utf-8"), ("127.0.0.1", 7500))
            game_over_sent = True

    pygame.display.flip()
    clock.tick(60)

if data_file.exists():
    with open(data_file, "r") as f:
        game_data = json.load(f)
else:
    game_data = {"red_team": [], "green_team": [], "actions": []}

game_data["actions"] = actions

with open(data_file, "w") as f:
    json.dump(game_data, f, indent=2)

next_file = Path(__file__).resolve().parent / "next_screen.txt"
next_file.write_text(next_screen)

close_sockets(transmit_socket, receive_socket)
pygame.quit()

