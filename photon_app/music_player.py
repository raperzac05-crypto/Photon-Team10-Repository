import pygame
import time
import random
from pathlib import Path

pygame.mixer.init()

music_started = False
TRACK_DIR = Path(__file__).resolve().parent / "assets" / "photon_tracks"

tracks = list(TRACK_DIR.glob("*.mp3"))

if not tracks:
    print("No music tracks found in", TRACK_DIR)

MUSIC_PATH = random.choice(tracks)
print("Selected music track:", MUSIC_PATH)

def update_music(countdown_start):
    global music_started

    if countdown_start is None:
        return

    elapsed = time.time() - countdown_start

    if not music_started and elapsed >= 13:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            
        pygame.mixer.music.load(str(MUSIC_PATH))
        pygame.mixer.music.play()
        music_started = True