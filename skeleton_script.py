from dataclasses import dataclass, field
from typing import List, Optional
import time

#friendly fire knocks both players down and times them out, -10 points
# -------------------------------
# Data models
# -------------------------------

@dataclass
class Player:
    player_id: int
    codename: str
    team: str          # "red" or "green"
    equipment_id: int
    score: int = 0
    hits_made: int = 0
    times_hit: int = 0
    base_hits: int = 0
    friendly_fire_count: int = 0


@dataclass
class Event:
    timestamp: float
    event_type: str    # "player_hit", "base_hit", "friendly_fire"
    attacker_id: int
    target_id: Optional[int] = None
    description: str = ""


@dataclass
class GameState:
    players: List[Player] = field(default_factory=list)
    events: List[Event] = field(default_factory=list)

    def get_player_by_equipment(self, equipment_id: int) -> Optional[Player]:
        for player in self.players:
            if player.equipment_id == equipment_id:
                return player
        return None

    def get_player_by_id(self, player_id: int) -> Optional[Player]:
        for player in self.players:
            if player.player_id == player_id:
                return player
        return None


# -------------------------------
# Scoring constants
# -------------------------------

HIT_POINTS = 10
BASE_HIT_POINTS = 100
FRIENDLY_FIRE_PENALTY = -10


# -------------------------------
# Event handlers
# -------------------------------

def handle_player_hit(game: GameState, attacker_equipment: int, target_equipment: int) -> None:
    attacker = game.get_player_by_equipment(attacker_equipment)
    target = game.get_player_by_equipment(target_equipment)

    if attacker is None or target is None:
        print("Invalid hit event: attacker or target not found.")
        return

    # Prevent self-hit if needed
    if attacker.player_id == target.player_id:
        print("Ignored self-hit event.")
        return

    # Friendly fire check
    if attacker.team == target.team:
        attacker.score += FRIENDLY_FIRE_PENALTY
        attacker.friendly_fire_count += 1

        event = Event(
            timestamp=time.time(),
            event_type="friendly_fire",
            attacker_id=attacker.player_id,
            target_id=target.player_id,
            description=f"{attacker.codename} hit teammate {target.codename}"
        )
        game.events.append(event)

        print(event.description)
        return

    # Normal player hit
    attacker.score += HIT_POINTS
    attacker.hits_made += 1
    target.times_hit += 1

    event = Event(
        timestamp=time.time(),
        event_type="player_hit",
        attacker_id=attacker.player_id,
        target_id=target.player_id,
        description=f"{attacker.codename} hit {target.codename}"
    )
    game.events.append(event)

    print(event.description)


def handle_base_hit(game: GameState, attacker_equipment: int, base_team: str) -> None:
    attacker = game.get_player_by_equipment(attacker_equipment)

    if attacker is None:
        print("Invalid base hit event: attacker not found.")
        return

    # Prevent hitting your own base if desired
    if attacker.team == base_team:
        print(f"{attacker.codename} attempted to hit own base. Ignored.")
        return

    attacker.score += BASE_HIT_POINTS
    attacker.base_hits += 1

    event = Event(
        timestamp=time.time(),
        event_type="base_hit",
        attacker_id=attacker.player_id,
        description=f"{attacker.codename} hit the {base_team} base"
    )
    game.events.append(event)

    print(event.description)


# -------------------------------
# Utility / display
# -------------------------------

def print_scoreboard(game: GameState) -> None:
    print("\n--- SCOREBOARD ---")
    for player in game.players:
        print(
            f"{player.codename} ({player.team}) | "
            f"Score: {player.score} | "
            f"Hits: {player.hits_made} | "
            f"Times Hit: {player.times_hit} | "
            f"Base Hits: {player.base_hits} | "
            f"Friendly Fire: {player.friendly_fire_count}"
        )


def print_event_log(game: GameState) -> None:
    print("\n--- EVENT LOG ---")
    for event in game.events:
        print(f"[{event.event_type}] {event.description}")


# -------------------------------
# Example usage
# -------------------------------

if __name__ == "__main__":
    game = GameState(players=[
        Player(player_id=1, codename="Alpha", team="red", equipment_id=101),
        Player(player_id=2, codename="Bravo", team="red", equipment_id=102),
        Player(player_id=3, codename="Charlie", team="green", equipment_id=201),
        Player(player_id=4, codename="Delta", team="green", equipment_id=202),
    ])

    # Normal hit
    handle_player_hit(game, attacker_equipment=101, target_equipment=201)

    # Friendly fire
    handle_player_hit(game, attacker_equipment=101, target_equipment=102)

    # Base hit
    handle_base_hit(game, attacker_equipment=201, base_team="red")

    print_scoreboard(game)
    print_event_log(game)