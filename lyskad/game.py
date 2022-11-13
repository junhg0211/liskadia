from datetime import datetime


class State:
    IDLE = 0
    PLAYING = 1
    END = 2


class Direction:
    HORIZONTAL = False
    VERTICAL = True


class Game:
    next_id = 0

    def __init__(self, id_: int, direction: bool = Direction.HORIZONTAL):
        self.id = id_
        self.state = State.IDLE
        self.created_at = datetime.now()
        self.direction = direction

    def jsonify(self):
        return {'id': self.id, 'state': self.state, 'created_at': self.created_at, 'direction': self.direction}

    @classmethod
    def new(cls):
        result = cls(cls.next_id)
        cls.next_id += 1
        return result
