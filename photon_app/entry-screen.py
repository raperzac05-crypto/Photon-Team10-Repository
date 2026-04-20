import pygame
import psycopg2
import sys
import random
import time
import json
from pathlib import Path

pygame.mixer.pre_init(44100, -16, 2, 4096)

TRACK_DIR = Path(__file__).resolve().parent / "assets" / "photon_tracks"

tracks = list(TRACK_DIR.glob("*.mp3"))

if not tracks:
    raise RuntimeError("No music tracks found in", TRACK_DIR)

MUSIC_PATH = random.choice(tracks)
print("Selected music track:", MUSIC_PATH)

sys.path.append(str(Path(__file__).resolve().parent))  # Ensure current directory is in path for sockets import
from sockets import broadcast_message, create_udp_sockets

# -------------------------------
# Database connection
# -------------------------------

#take out the host part, don't think it's needed
connection = psycopg2.connect(dbname="photon")

cursor = connection.cursor()
countdown_start = None
countdown_time = 30  # seconds
music_start_time = None
music_started = False

def get_codename(player_id):
    if not player_id.strip():
        return None
    cursor.execute("SELECT codename FROM players WHERE id = %s", (player_id,))
    result = cursor.fetchone()
    return result[0] if result else None

def was_manually_entered(player_id):
    """Check if this player was manually entered (has entry in players table)"""
    if not player_id.strip():
        return False
    cursor.execute("SELECT COUNT(*) FROM players WHERE id = %s", (player_id,))
    result = cursor.fetchone()
    return result[0] > 0 if result else False

def add_player(player_id, codename):
    # Check if player already exists
    cursor.execute("SELECT COUNT(*) FROM players WHERE id = %s", (player_id,))
    exists = cursor.fetchone()[0] > 0
    
    if exists:
        # Update existing player
        cursor.execute(
            "UPDATE players SET codename = %s WHERE id = %s",
            (codename, player_id)
        )
    else:
        # Insert new player
        cursor.execute(
            "INSERT INTO players (id, codename) VALUES (%s, %s)",
            (player_id, codename)
        )
    connection.commit()

def broadcast_hardware_ids():
    # This function would contain the logic to send hardware IDs to the play-action-display
    # For example, it could write them to a file or send them over a socket
    for player in players_list:
        hw_id = player.get("equipment_id")
        if hw_id:
            broadcast_message(transmit_socket, str(hw_id))
            print(f"Broadcasted {hw_id}")

def start_music():
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.load(str(MUSIC_PATH))
        pygame.mixer.music.play(0)

# -------------------------------
# Pygame setup
# -------------------------------
pygame.init()

if not pygame.mixer.get_init():
    pygame.mixer.init()

pygame.mixer.music.load(str(MUSIC_PATH))

screen = pygame.display.set_mode((1000, 600))
pygame.display.set_caption("Player Entry")

font = pygame.font.Font(None, 32)
big_font = pygame.font.Font(None, 40)

transmit_socket, receive_socket = create_udp_sockets()

# -------------------------------
# Input fields
# -------------------------------
fields = {
    "player_id": pygame.Rect(50, 500, 200, 40),
    "codename": pygame.Rect(260, 500, 250, 40),
    "equipment_id": pygame.Rect(520, 500, 200, 40),
}

active_field = "player_id"
input_text = ""
player_data = {}
players_list = []
data_file = Path(__file__).resolve().parent / "game_data.json"
entered_player_ids = set()  # Track IDs entered in this session
MAX_PLAYERS_PER_TEAM = 15
next_team = "red"  # alternates between "red" and "green"
auto_codename = None
editing_index = None  # index of player being edited

# -------------------------------
# Drawing functions
# -------------------------------
def draw_input_boxes():
    for name, rect in fields.items():
        color = (255, 255, 255) if active_field == name else (180, 180, 180)
        pygame.draw.rect(screen, color, rect, 2)
        label = font.render(name.replace("_", " ").title(), True, (255, 255, 255))
        screen.blit(label, (rect.x, rect.y - 25))

    active_rect = fields[active_field]
    txt_surface = font.render(input_text, True, (255, 255, 255))
    screen.blit(txt_surface, (active_rect.x + 5, active_rect.y + 5))

def draw_team_table(x, team_color, title):
    table_width = 400
    table_height = 450
    row_height = 28

    pygame.draw.rect(screen, (40, 40, 40), (x, 30, table_width, table_height), border_radius=6)
    screen.blit(big_font.render(title, True, team_color), (x + 10, 35))

    headers = ["Player ID", "Codename", "Equip ID"]
    col_x = [x + 10, x + 130, x + 280]
    for text, cx in zip(headers, col_x):
        screen.blit(font.render(text, True, (255, 255, 255)), (cx, 80))

    start_y = 115
    team_key = "red" if title == "Red Team" else "green"
    team_players = [p for p in players_list if p["team"] == team_key]

    for i in range(MAX_PLAYERS_PER_TEAM):
        row_y = start_y + i * row_height
        if i < len(team_players):
            p = team_players[i]
            # Highlight if this player is being edited
            global_index = players_list.index(p)
            if global_index == editing_index:
                bg = (255, 255, 100) if team_key == "red" else (100, 255, 100)
            else:
                bg = (team_color[0] // 3, team_color[1] // 3, team_color[2] // 3)
            pygame.draw.rect(screen, bg, (x + 5, row_y, table_width - 10, row_height))
            row_data = [p.get("player_id", ""), p.get("codename", ""), p.get("equipment_id", "")]
            for text, cx in zip(row_data, col_x):
                text_color = (0, 0, 0) if global_index == editing_index else (255, 255, 255)
                screen.blit(font.render(str(text), True, text_color), (cx, row_y + 4))
        else:
            pygame.draw.rect(screen, (30, 30, 30), (x + 5, row_y, table_width - 10, row_height))

# -------------------------------
# Commit / Reset player
# -------------------------------
def commit_player():
    global player_data, input_text, active_field, next_team, auto_codename, editing_index, entered_player_ids
    if editing_index is not None:
        # Preserve team when editing
        player_data["team"] = players_list[editing_index]["team"]
        players_list[editing_index] = player_data.copy()
        editing_index = None
    else:
        # New player - assign to next team
        player_data["team"] = next_team
        players_list.append(player_data.copy())
        if player_data.get("equipment_id"):
            broadcast_message(transmit_socket, str(player_data["equipment_id"]))
        # Alternate to the other team
        next_team = "green" if next_team == "red" else "red"
    
    # Track this player ID as entered in this session
    if "player_id" in player_data:
        entered_player_ids.add(player_data["player_id"])

    print("Player added/updated:", player_data)
    player_data = {}
    input_text = ""
    active_field = "player_id"
    auto_codename = None

# -------------------------------
# Main loop
# -------------------------------
clock = pygame.time.Clock()
running = True
while running:
    screen.fill((15, 15, 15))

    draw_team_table(50, (255, 50, 50), "Red Team")
    draw_team_table(550, (50, 255, 50), "Green Team")
    draw_input_boxes()
    screen.blit(font.render("TAB=Next | ENTER=Confirm | F3=Start | F12=Clear", True, (255, 255, 255)), (50, 560))

    #music start timer
    if music_start_time is not None and not music_started:
        if time.time() - music_start_time >= 13: # Start music after 14 seconds
            pygame.mixer.music.play(0)
            music_started = True

    #Added Timer
    if countdown_start is not None:
        elapsed = time.time() - countdown_start
        seconds_left = max(0, int(countdown_time - elapsed))
        timer_text = f"00:{seconds_left:02d}"
        surf = big_font.render(timer_text, True, (240, 240, 255))
        screen.blit(surf, surf.get_rect(center=(500,300)))
        if elapsed >= countdown_time:
            next_file = Path(__file__).resolve().parent / "next_screen.txt"
            next_file.write_text("play")
            running = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Click input field
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked_field = False
            for name, rect in fields.items():
                if rect.collidepoint(event.pos):
                    active_field = name
                    # If we're editing and switch fields, populate with current data
                    if editing_index is not None:
                        if name == "player_id":
                            input_text = str(players_list[editing_index].get("player_id", ""))
                        elif name == "codename":
                            input_text = players_list[editing_index].get("codename", "")
                        elif name == "equipment_id":
                            input_text = str(players_list[editing_index].get("equipment_id", ""))
                    else:
                        input_text = ""
                        auto_codename = None  # Clear auto_codename when clicking fields
                    clicked_field = True
                    break
            if not clicked_field:
                # check table cells
                for team_idx, team_x in enumerate([50, 550]):
                    team_name = "Red Team" if team_idx == 0 else "Green Team"
                    col_x = [team_x + 10, team_x + 130, team_x + 280]
                    row_start_y = 115
                    row_height = 28
                    team_key = "red" if team_name=="Red Team" else "green"
                    team_players = [p for p in players_list if p["team"] == team_key]
                    for i, player in enumerate(team_players):
                        row_rect = pygame.Rect(team_x + 5, row_start_y + i*row_height, 390, row_height)
                        if row_rect.collidepoint(event.pos):
                            editing_index = players_list.index(player)
                            player_data = player.copy()
                            # Determine which column was clicked
                            if event.pos[0] < col_x[1]:
                                active_field = "player_id"
                                input_text = str(player.get("player_id", ""))
                            elif event.pos[0] < col_x[2]:
                                active_field = "codename"
                                input_text = player.get("codename", "")
                            else:
                                active_field = "equipment_id"
                                input_text = str(player.get("equipment_id", ""))
                            break

        # Key handling
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                raise SystemExit
            elif event.key == pygame.K_F12:
                players_list = []
                player_data = {}
                input_text = ""
                active_field = "player_id"
                auto_codename = None
                next_team = "red"
                editing_index = None
                # Note: We intentionally do NOT clear entered_player_ids
                # This prevents re-fetching codenames from database for IDs already entered
                print("Data cleared.")
            elif event.key == pygame.K_F3:
            # Signal play-action-display to start
                missing = [p for p in players_list if not p.get("equipment_id")]

                if missing:
                    print("Cannot start game. The following players are missing equipment IDs:")
                else:
                    print("Game starting... players:", players_list)
                    if countdown_start is None:
                        countdown_start = time.time()
                        music_start_time = time.time()  # Start music timer when game starts
            elif event.key == pygame.K_TAB:
                order = ["player_id", "codename", "equipment_id"]
                idx = order.index(active_field)
                active_field = order[(idx + 1) % 3]
                # Clear auto_codename when starting a new entry cycle
                if active_field == "player_id":
                    auto_codename = None
                # If we're editing, populate the field with existing data
                if editing_index is not None:
                    if active_field == "player_id":
                        input_text = str(players_list[editing_index].get("player_id", ""))
                    elif active_field == "codename":
                        input_text = players_list[editing_index].get("codename", "")
                    elif active_field == "equipment_id":
                        input_text = str(players_list[editing_index].get("equipment_id", ""))
                elif active_field == "codename" and auto_codename:
                    input_text = auto_codename
                else:
                    input_text = ""
            elif event.key == pygame.K_RETURN:
                if active_field == "player_id":
                    player_data["player_id"] = input_text.strip()
                    # Check if this player ID has been entered before (in session OR in database)
                    # Only auto-fetch codename if: not editing AND never been entered before
                    if editing_index is None:
                        auto_codename = get_codename(player_data["player_id"])
                        input_text = auto_codename if auto_codename else ""
                    else:
                        auto_codename = None
                        input_text = ""
                    active_field = "codename"
                elif active_field == "codename":
                    player_data["codename"] = input_text.strip()
                    # Only add to database if codename provided and not already in database
                    if player_data["codename"] and player_data.get("player_id"):
                        add_player(player_data["player_id"], player_data["codename"])
                    input_text = ""
                    active_field = "equipment_id"
                    auto_codename = None
                elif active_field == "equipment_id":
                    try:
                        player_data["equipment_id"] = int(input_text)
                        commit_player()
                    except ValueError:
                        print("Equipment ID must be an integer.")
                    input_text = ""
            elif event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                input_text += event.unicode

    pygame.display.flip()
    clock.tick(60)  # Limit to 60 FPS

#save player data for the play-action-display
red_team = [p for p in players_list if p["team"] == "red"]
green_team = [p for p in players_list if p["team"] == "green"]

game_data = {
    "red_team": red_team,
    "green_team": green_team,
    "actions": []  # This will be populated by the play-action-display
}
data_file = Path(__file__).resolve().parent / "game_data.json"

with open(data_file, "w") as f:
    json.dump(game_data, f, indent=2)

pygame.display.quit()
cursor.close()
connection.close()
transmit_socket.close()
receive_socket.close()
