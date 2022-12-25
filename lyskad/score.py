from dataclasses import dataclass


@dataclass
class Score:
    game_id: int
    position: int
    user_id: str
