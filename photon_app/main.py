#photon_app/main.py
from __future__ import annotations

import os
import runpy
import importlib.util
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

#main function to run the splash screen and entry point, and print the final roster of players
def main() -> None:
    app_dir = Path(__file__).resolve().parent
    assets_dir = app_dir / "assets"

    load_sockets_module(app_dir)

    splash_script = app_dir / "splash-screen.py"
    if splash_script.exists():
        run_script(splash_script, chdir=assets_dir)
    
    entry_script = app_dir / "entry-screen.py"
    if entry_script.exists():
        run_script(entry_script, chdir=app_dir)

#run the main function if this file is executed as the main program
if __name__ == "__main__":
    main()
