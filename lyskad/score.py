from dataclasses import dataclass


@dataclass
class Score:
    game_id: int
    position: int
    user_id: str
    by_nema_position: int

    @classmethod
    def get(cls, data: dict):
        return Score(data['game_id'], data['position'], data['user_id'], data['by_nema_position'])

    def jsonify(self) -> dict:
        return {
            'game_id': self.game_id,
            'position': self.position,
            'user_id': self.user_id,
            'by_nema_position': self.by_nema_position
        }
