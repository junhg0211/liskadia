class Participant:
    def __init__(self, user_id: str, game_id: int):
        self.user_id = user_id
        self.game_id = game_id


def get_participant_ids(game_id: int, participants: list[Participant]) -> list[str]:
    return list(map(
        lambda x: x.user_id,
        filter(lambda x: x.game_id == game_id, participants)
    ))


def leave(user_id: str, game_id: int, participants: list[Participant]):
    for participant in participants:
        if participant.user_id == user_id and participant.game_id == game_id:
            participants.remove(participant)
            break


def get_user_games(user_id: str, participants: list[Participant]) -> list[int]:
    return list(map(lambda x: x.game_id, filter(lambda x: x.user_id == user_id, participants)))
