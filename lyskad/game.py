from datetime import datetime
from typing import Optional


class State:
    IDLE = 0
    PLAYING = 1
    END = 2


class Direction:
    HORIZONTAL = False
    VERTICAL = True

    DEFAULT = HORIZONTAL


class Game:
    next_id = 0

    def __init__(self, id_: int, created_by: str, direction: bool = Direction.DEFAULT):
        self.id = id_
        self.created_by = created_by
        self.direction = direction

        self.state = State.IDLE
        self.created_at = datetime.now()

    def jsonify(self):
        return {
            'id': self.id,
            'direction': self.direction,
            'created_by': self.created_by,
            'state': self.state,
            'created_at': self.created_at,
        }

    @classmethod
    def new(cls, created_by, direction: Optional[bool] = None):
        if direction is None:
            direction = Direction.DEFAULT
        result = cls(cls.next_id, created_by, direction)
        cls.next_id += 1
        return result