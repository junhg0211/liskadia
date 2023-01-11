from dataclasses import dataclass
from datetime import datetime


@dataclass
class RatingHistory:
    user_id: str
    rating: float
    time: datetime

    @classmethod
    def get(cls, data: dict):
        user_id = data.get('user_id')
        rating = data.get('rating')
        time = data.get('time')

        return RatingHistory(user_id, rating, time)
