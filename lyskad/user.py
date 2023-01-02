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
        return result

    def __init__(self, id_: str, encrypted_token: str):
        self.id = id_
        self.token = encrypted_token
        self.wins = 0
        self.games = 0
        self.joined_at = datetime.now()
        self.color = 0
        self.language = ''

    def jsonify(self) -> dict:
        return {
            'id': self.id,
            'wins': self.wins,
            'games': self.games,
            'joined_at': self.joined_at,
            'color': self.color
        }

    def calculate_rating(self) -> float:
        rate = self.wins / self.games
        play_rating = 200 * (1 - 0.995 ** self.games)
        win_rating = 160 * rate * log(self.wins / 160 + 1)
        return play_rating + win_rating

    def get_formatted_rating(self) -> str:
        return format(self.calculate_rating(), '.2f')
