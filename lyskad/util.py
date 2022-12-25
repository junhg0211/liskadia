from typing import Optional

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

            if now == defence:
                continue

            attack = now
            attack_pos = i
            defence = None
        else:
            if attack == now:
                attack = None
                defence = None
                continue

            if defence != now:
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


def get_color_generator(start_pos: tuple[int, int], direction: int, position_nemas: dict[tuple[int, int], str]):
    if direction == 0:  # UP
        dx = 0
        dy = -1
    elif direction == 1:  # LEFT
        dx = -1
        dy = 0
    elif direction == 2:  # DOWN
        dx = 0
        dy = 1
    else:  # LEFT
        dx = 1
        dy = 0

    x, y = start_pos
    horizontal_direction = bool(direction % 2)
    now_nema_vertical = bool((x + y) % 2)
    while True:
        now_color = position_nemas.get((x, y))

        if now_color is None:
            return

        hostile = horizontal_direction == now_nema_vertical
        yield now_color, hostile

        x += dx
        y += dy
        now_nema_vertical = not now_nema_vertical


def is_attacking(direction: int, position: tuple[int, int], position_nemas: dict[tuple[int, int], str]) -> int:
    anchor_color = ''
    defence = None
    for i, (now_color, hostile) in enumerate(get_color_generator(position, direction, position_nemas)):
        if i == 0:
            anchor_color = now_color
            continue
        if hostile:
            if now_color == defence:
                continue
            if now_color == anchor_color:
                return i
            break
        else:
            if defence is None:
                defence = now_color
            if defence != now_color:
                break
            continue
    return 0


def get_relative_defence_center(horizontal_check: bool, position: tuple[int, int], position_nemas: dict) \
        -> tuple[Optional[int], str]:
    anchor_color = ''
    left_attack = False
    left_attacker = ''
    for i, (now_color, hostile) in enumerate(get_color_generator(position, int(horizontal_check), position_nemas)):
        if i == 0:
            anchor_color = now_color
            continue
        if hostile:
            if now_color != anchor_color:
                left_attack = i
                left_attacker = now_color
                break
        else:
            if now_color != anchor_color:
                break
    if not left_attack:
        return None, ''
    for i, (now_color, hostile), in enumerate(get_color_generator(position, int(horizontal_check) + 2, position_nemas)):
        if i == 0:
            continue
        if hostile:
            if now_color != anchor_color:
                if left_attacker == now_color:
                    return (i-left_attack) // 2, now_color
                break
        else:
            if now_color != anchor_color:
                break
    return None, ''


def calculate_score_by(game: Game, nemas: list[Nema], position: tuple[int, int]):
    width, height = 10, 10
    position_nemas = dict()

    if game.direction:
        width, height = height, width

    for nema in nemas:
        if nema.position in position_nemas:
            raise ValueError('네마의 목록이 유효하지 않습니다. 같은 자리에 2개 이상의 네마가 있습니다.')

        pos = nema.get_position(width)
        if game.direction:
            pos = tuple(reversed(pos))

        position_nemas[pos] = nema.user_id

    nema_vertical = bool(sum(position) % 2)  # False: ㅡ, True: ㅣ

    attack_positions = list()
    if nema_vertical:
        if left_attack_distance := is_attacking(3, position, position_nemas):
            attack_positions.append((position[0] + left_attack_distance // 2, position[1]))
        if right_attack_distance := is_attacking(1, position, position_nemas):
            attack_positions.append((position[0] - right_attack_distance // 2, position[1]))
    else:
        if up_attack_distance := is_attacking(0, position, position_nemas):
            attack_positions.append((position[0], position[1] - up_attack_distance // 2))
        if down_attack_distance := is_attacking(2, position, position_nemas):
            attack_positions.append((position[0], position[1] + down_attack_distance // 2))

    defence_data: list[tuple[tuple[int, int], str]] = list()
    horizontal_defence_center, defence_attacker = get_relative_defence_center(True, position, position_nemas)
    if horizontal_defence_center is not None:
        defence_data.append(((position[0] + horizontal_defence_center, position[1]), defence_attacker))
    vertical_defence_center, defence_attacker = get_relative_defence_center(False, position, position_nemas)
    if vertical_defence_center is not None:
        defence_data.append(((position[0], position[1] + vertical_defence_center), defence_attacker))

    return attack_positions, defence_data
