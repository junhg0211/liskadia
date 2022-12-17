from datetime import datetime


class GameState:
    IDLE = 0
    PLAYING = 1
    END = 2


class HjulienDirection:
    HORIZONTAL = False
    VERTICAL = True

    DEFAULT = HORIZONTAL


class Game:
    @classmethod
    def get(cls, data: dict) -> 'Game':
        game_id = data['id']
        created_by = data['created_by']
        direction = data['direction']

        result = Game(game_id, created_by, 3, direction)
        result.state = data['state']
        result.created_at = data['created_at']
        return result

    def __init__(self, id_: int, created_by: str, max_score: int = 3, direction: bool = HjulienDirection.DEFAULT):
        self.id = id_
        self.created_by = created_by
        self.max_score = max_score
        self.direction = direction

        self.state = GameState.IDLE
        self.created_at = datetime.now()

    def jsonify(self):
        return {
            'id': self.id,
            'direction': self.direction,
            'created_by': self.created_by,
            'state': self.state,
            'created_at': self.created_at,
            'max_score': self.max_score
        }
