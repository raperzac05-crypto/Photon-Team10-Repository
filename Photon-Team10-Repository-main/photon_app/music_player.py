import pygame
import time
from pathlib import Path

pygame.mixer.init()

music_started = False



def update_music(countdown_start):
    global music_started

    if countdown_start is None:
        return

    elapsed = time.time() - countdown_start

    if not music_started and elapsed >= 13:
        if not mygame.mixer.get_init():
            pygame.mixer.init()
            
        pygame.mixer.music.load(str(MUSIC_PATH))
        pygame.mixer.music.play()
        music_started = True