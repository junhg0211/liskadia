from util import encrypt


class User:
    def __init__(self, id_: str, password: str):
        self.id = id_
        self.password = encrypt(password, self.id)
        self.wins = 0
        self.games = 0

    def jsonify(self) -> dict:
        return {'id': self.id, 'wins': self.wins, 'games': self.games}
