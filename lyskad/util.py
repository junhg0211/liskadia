from math import ceil

from lyskad import Game, Nema
from util import is_even, is_odd


def check_lane(
        fixed_coordinate: int, start_index: int, coordinate_max: int, position_nemas: dict[tuple[int, int], str],
        is_attack_pos: callable, is_horizontal: bool = True) -> tuple[dict, list]:
    attack = None
    attack_pos = -1
    defence = None
    scores = dict()
    attacks = list()
    for i in range(start_index, coordinate_max):
        position = (i, fixed_coordinate) if is_horizontal else (fixed_coordinate, i)
        now = position_nemas.get(position)

        if now is None:
            attack = None
            defence = None
            continue

        if is_attack_pos(i):
            if attack is None:
                attack = now
                attack_pos = i
                defence = None
                continue

            if attack == now:
                if now in scores:
                    scores[now] += 1
                else:
                    scores[now] = 1

                attacks.append(((attack_pos + i) / 2, now))

                attack_pos = i
                defence = None
                continue

            attack = now
            attack_pos = i
            defence = None
        else:
            if attack == now:
                attack = None
                defence = None
                continue

            if defence is None:
                defence = now
                continue

    return scores, attacks


def calculate_score(game: Game, nemas: list[Nema]) -> tuple[dict[str, int], list]:
    width, height = 10, 10
    scores = dict()
    position_nemas = dict()

    if game.direction:
        width, height = height, width

    for nema in nemas:
        if nema.position in position_nemas:
            raise ValueError('네마의 목록이 유효하지 않습니다. 같은 자리에 2개 이상의 네마가 있습니다.')

        position = nema.get_position(width)
        if game.direction:
            position = tuple(reversed(position))

        position_nemas[position] = nema.user_id

    total_attacks = list()

    for y in range(1, height):
        if y % 2 == 1:
            delta_scores, attacks = check_lane(y, 0, width, position_nemas, is_even, True)
        else:
            delta_scores, attacks = check_lane(y, 1, width, position_nemas, is_odd, True)
        for attack in attacks:
            total_attacks.append((attack[0], y, attack[1]))
        for key, value in delta_scores.items():
            if key in scores:
                scores[key] += value
            else:
                scores[key] = value
    for x in range(width):
        if x % 2 == 0:
            delta_scores, attacks = check_lane(x, 0, height, position_nemas, is_even, False)
        else:
            delta_scores, attacks = check_lane(x, 1, height, position_nemas, is_odd, False)
        for attack in attacks:
            total_attacks.append((x, attack[0], attack[1]))
        for key, value in delta_scores.items():
            if key in scores:
                scores[key] += value
            else:
                scores[key] = value

    return scores, total_attacks
