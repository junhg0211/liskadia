from datetime import datetime


class Nema:
    @classmethod
    def get(cls, data: dict) -> 'Nema':
        user_id = data['user_id']
        game_id = data['game_id']
        position = data['position']

        result = Nema(user_id, game_id, position)
        result.created_at = data['created_at']
        return result

    def __init__(self, user_id: str, game_id: int, position: int):
        self.user_id = user_id
        self.game_id = game_id
        self.position = position
        self.created_at = datetime.now()

    def get_position(self, width: int = 10) -> tuple[int, int]:
        y = self.position // width
        x = self.position % width
        return x, y

    def jsonify(self):
        return {
            'user_id': self.user_id,
            'game_id': self.game_id,
            'position': self.position,
            'created_at': self.created_at
        }


def get_position_value(x: int, y: int, w: int = 10):
    return w * y + x


def is_valid_position(position: int, width: int = 10, height: int = 10):
    return 0 <= position < width * height
