Photon Laser Tag Entry Screen and Splash Screen
By : Preston Martin

Run the install script 

chmod +x install.sh
./install.sh

This installs Pygame and Psycopg2

Start programs individually by running:
python3 splash-screen.py
python3 entry-screen.py

Splash-screen : 
    Shows splash screen image "logo.jpg" for 3 seconds, then exits 

Entry-screen : 
    Shows window with two tables, one for each team, red and green.

    Tab > Moves to next entry field
    Enter > Confirms entry
    F3 > Start Game
    F12 > Clear all entries 
    Click Entry > Edit entry


    Enter Player Id, Then press ENTER, if ID already exists in database, codename is filled. Fill codename, press ENTER, then enter equipment ID, thenpress ENTER. 

    Names are added in alternating order, red, green, red, green, and so on.

    This system connects to Photon to store and retrieve player information

