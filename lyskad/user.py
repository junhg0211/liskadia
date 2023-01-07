from datetime import datetime
from math import log


class User:
    @classmethod
    def get(cls, data: dict) -> 'User':
        result = User(data['id'], '')
        result.wins = data.get('wins')
        result.games = data.get('games')
        result.token = data.get('password')
        result.joined_at = data.get('joined_at')
        result.color = data.get('color')
        result.language = data.get('language')
        result.rating = data.get('rating')
        result.last_interaction = data.get('last_interaction')
        return result

    def __init__(self, id_: str, encrypted_token: str):
        self.id = id_
        self.token = encrypted_token
        self.wins = 0
        self.games = 0
        self.joined_at = datetime.now()
        self.color = 0
        self.language = ''
        self.rating = 0.0
        self.last_interaction = self.joined_at

    def jsonify(self) -> dict:
        return {
            'id': self.id,
            'wins': self.wins,
            'games': self.games,
            'joined_at': self.joined_at,
            'color': self.color,
            'language': self.language,
            'rating': self.rating,
            'last_interaction': self.last_interaction,
        }

    def calculate_rating(self) -> float:
        if self.games == 0:
            return 0.0

        rate = self.wins / self.games
        play_rating = 40 * (1 - 0.975 ** self.games)
        win_rating = 20 * rate * log(self.wins / 20 + 1)
        return play_rating + win_rating

    def get_formatted_rating(self) -> str:
        return format(self.calculate_rating(), '.3f')

    def get_color_code(self) -> str:
        return f'#{self.color:06x}'
