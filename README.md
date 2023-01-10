# Liskadia

> 리스카드 서버 엔진

### 로그인 토큰

로그인 정보는 `id`와 `password` 값이다.
이때 `id`는 로그인하려는 계정의 아이디, `password`은 로그인하려는 계정에 대한 비밀번호이다.

로그인을 한 후에 사용할 수 있는 기능에는 *표시를 해 두었다.

### User

| FIELD            | TYPE        | DESCRIPTION    |
|------------------|-------------|----------------|
| id               | varchar(30) | 유저 아이디         |
| _password_       | varchar(64) | 비밀번호           |
| wins             | int         | 게임을 이긴 횟수      |
| games            | int         | 게임을 플레이한 횟수    |
| color            | int         | 주로 사용하는 네마의 색상 |
| language         | varchar(7)  | 페이지를 표시할 언어    |
| rating           | double      | 레이팅 점수         |
| last_interaction | datetime    | 마지막으로 상호작용한 시각 |

* `user.color`: 6자리 HTML 16진수 색상 코드를 그대로 10진수로 변환한 것을 사용한다.
* `user.language`: 다음 중 하나를 사용한다.
  * `en-US` (기본값)
  * `ko-KR`
  * `ja-JP`
  * `ZA-ZS`

#### Rating
유저의 레이팅은 다음과 같이 계산한다.

* 플레이어 수 $n(h)$: 게임 $h$에 대해 그 게임을 플레이한 플레이어 수를 $n(h)$로 나타낸다.
* 플레이 수 $p$: 플레이한 게임 $h_i$에 대해 $\sum_i n(h_i)$
* 이긴 수 $w$: 플레이한 게임 중 이긴 게임 $v_i$에 대해 $\sum_i n(v_i)$
* 승률 $r$ $= \frac w p$
* 플레이 보상: $40 (1 - 0.975^p)$
* 승리 보상: $20r \ln \left( \frac w {20} + 1 \right)$
* 레이팅: 플레이 보상 + 승리 보상

#### GET `/users`
모든 유저 정보 불러오기

#### POST `/users/new`
새로운 계정 생성
* `id`, `token` 정보가 전달되어야 함
* `color` 정보를 전달할 수 있음
* `language` 정보를 전달할 수 있음

#### POST `/login`
세션 로그인
* `id`, `token` 정보가 전달되어야 함

#### GET `/users/{user.id}`
유저 정보 불러오기

#### ~~PATCH `/users/{user.id}`*~~
~~유저 정보 변경하기~~
* ~~`token` 변경할 수 있음~~

#### ~~DELETE `/users/{user.id}`*~~
~~유저 삭제하기~~

### RatingHistory

| FIELD  | TYPE     | DESCRIPTION |
|--------|----------|-------------|
| id     | user.id  | 유저 아이디      |
| rating | double   | 레이팅 점수      |
| time   | datetime | 레이팅 계산 시점   |

### Game

| FIELD      | TYPE         | DESCRIPTION     |
|------------|--------------|-----------------|
| id         | int          | 게임 아이디          |
| direction  | boolean      | 네마 순환의 방향       |
| state      | int          | 게임 진행 상태        |
| max_score  | unsigned int | 게임 종료에 필요한 점수 수 |
| created_at | datetime     | 게임 생성 시각        |
| created_by | user.id      | 게임을 생성한 유저      |

#### GET `/games`
게임 목록 불러오기

#### POST `/games/new`*
새로운 게임 생성

#### GET `/games/{game.id}`
게임 정보 불러오기

#### GET `/games/{game.id}/meta`
게임의 메타적인 정보를 불러온다.

* 네마의 개수
* `game.state`
* 게임에 참가중인 플레이어의 수
* 득점이 발생한 네마의 중간 위치 (scores 객체)

### Participant

| FIELD     | TYPE     | DESCRIPTION |
|-----------|----------|-------------|
| user_id   | user.id  | 참가자 id      |
| game_id   | game.id  | 게임 id       |
| joined_at | datetime | 참가한 시각      |
| place     | int      | 게임 종료 시 순위  |

#### POST `/games/{game.id}/join`*
게임에 참가

#### POST `/games/{game.id}/leave`*
게임에서 퇴장

#### POST `/games/{game.id}/start`*
게임 시작하기

#### GET `/users/{user.id}/games`
유저가 플레이어로 등록되어있는 게임 목록 불러오기

### Nema

| FIELD      | TYPE     | DESCRIPTION |
|------------|----------|-------------|
| user_id    | user.id  | 참가자 id      |
| game_id    | game.id  | 게임 id       |
| position   | int      | 네마의 위치      |
| created_at | datetime | 네마가 위치된 시각  |

휼리엔에서 가장 왼쪽 위에 보이는 네마의 좌표를 (0, 0)이라고 하고, 첫 번째 수를 x값, 두 번째 수를 y값이라고 한다.
오른쪽으로 갈 수록 x값이 1씩 증가하고, 아래로 갈수록 y의 값이 1씩 증가한다.
따라서 가로가 10, 세로가 10인 휼리엔에서 가장 오른쪽 아래에 있는 네마의 좌표는 (9, 9)이다.

너비(가로)가 w인 휼리엔에서 `nema.position`의 값이 (x, y)좌표를 나타낼 때, `nema.position = w*x + y`이다.

#### POST `/games/{game.id}/nemas/{nema.position}`*
게임에 네마 놓기

#### GET `/games/{game.id}/nemas`
게임의 네마 정보 불러오기

### Score

| FIELD            | TYPE    | DESCRIPTION        |
|------------------|---------|--------------------|
| game_id          | game.id | 게임 id              |
| position         | int     | 네마의 위치             |
| user_id          | user.id | 네마로 점수를 획득한 유저의 id |
| by_nema_position | int     | 점수를 획득하게 한 네마의 위치  |
