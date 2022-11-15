from datetime import datetime


class User:
    @classmethod
    def get(cls, data: dict) -> 'User':
        result = User(data['id'], '')
        result.wins = data['wins']
        result.games = data['games']
        result.password_token = data['password']
        result.joined_at = data['joined_at']
        return result

    def __init__(self, id_: str, token: str):
        self.id = id_
        self.password_token = token
        self.wins = 0
        self.games = 0
        self.joined_at = datetime.now()

    def jsonify(self) -> dict:
        return {
            'id': self.id,
            'wins': self.wins,
            'games': self.games,
            'joined_at': self.joined_at
        }
