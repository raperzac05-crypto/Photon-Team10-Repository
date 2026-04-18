#photon_app/main.py
from __future__ import annotations

import os
os.environ["SDL_AUDIODRIVER"] = "pulseaudio"
import runpy
import importlib.util

import pygame
from pathlib import Path


#load the sockets module if it exists, this is where the server and client code will be located
def load_sockets_module(app_dir: Path) -> None:
    sockets_path = app_dir / "Sockets"
    if not sockets_path.exists():
        return
    
    spec = importlib.util.spec_from_file_location("photon_app.sockets", sockets_path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

#function to run a script in a separate process, this is used to run the splash screen and entry point without blocking the main thread
def run_script(script_name: Path, chdir: Path | None = None) -> None:
    old_cwd = Path.cwd()
    try:
        if chdir:
            os.chdir(chdir)
        runpy.run_path(script_name, run_name="__main__")
    finally:
        os.chdir(old_cwd)

#resets game_data.json when program is first ran
def reset_game_data(app_dir: Path) -> None:
    data_file = app_dir / "game_data.json"
    if data_file.exists():
        data_file.unlink()

#writes the name of the next screen to a text file, this is used for the play-action-display to know when to return to the entry screen
def write_next_screen(app_dir: Path, screen_name: str) -> None:
    next_file = app_dir / "next_screen.txt"
    next_file.write_text(screen_name)

#reads the name of the next screen from a text file, this is used for the play-action-display to know when to return to the entry screen
def read_next_screen(app_dir: Path, default: str = "quit") -> None:
    next_file = app_dir / "next_screen.txt"
    if next_file.exists():
        return next_file.read_text().strip()
    return default

#main function to run the splash screen and entry point, and print the final roster of players
def main() -> None:
    app_dir = Path(__file__).resolve().parent
    assets_dir = app_dir / "assets"

    MUSIC_PATH = assets_dir / "photon_tracks" / "Track01.mp3"

    def start_music():
        if pygame.mixer.get_init() is None:
            print("Pygame mixer not initialized, cannot play music.")
            return
        if not pygame.mixer.music.get_busy():
            print("Music started")
            

    load_sockets_module(app_dir)
    reset_game_data(app_dir)

    splash_script = app_dir / "splash-screen.py"
    if splash_script.exists():
        run_script(splash_script, chdir=assets_dir)
    
    current_screen = "entry"

    #added loop to check which script to run instead of a hardcoded sequence
    while True:
        #entry-screen.py
        if current_screen == "entry":
            write_next_screen(app_dir, "quit")
            entry_script = app_dir / "entry-screen.py"
            if entry_script.exists():
                run_script(entry_script, chdir=assets_dir)
            
            current_screen = read_next_screen(app_dir)
        
        #play-action-display.py
        elif current_screen == "play":
            write_next_screen(app_dir, "quit")
            play_action_script = app_dir / "play-action-display.py"
            if play_action_script.exists():
                run_script(play_action_script, chdir=assets_dir)
            current_screen = read_next_screen(app_dir)

        else:
            break

    pygame.mixer.music.stop()

#run the main function if this file is executed as the main program
if __name__ == "__main__":
    main()
