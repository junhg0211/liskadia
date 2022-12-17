# Liskadia

> 리스카드 서버 엔진

## API

API의 구상은 [이 링크](https://sch-jeon.notion.site/Liskadia-fdc59575472843dd99b6ae900dc01a9c)에서 진행하고,
이 문서에는 코드로 구현된 API만 나열한다.

### 로그인 토큰

로그인 정보는 `id`와 `token` 값이다.
이때 `id`는 로그인하려는 계정의 아이디, `token`은 로그인하려는 계정에 대한 토큰이다.
`token`은 `util.encrypt`와 같이 생성된다.

로그인을 한 후에 사용할 수 있는 기능에는 *표시를 해 두었다.

클라이언트는 encrypt 방식으로 한 번 암호화하여 서버에 token을 전달하고,
서버에서는 해당 token을 한 번 더 같은 방식으로 암호화하여 데이터베이스에 저장한다.
데이터베이스에 저장된 token은 클라이언트에서 보낸 token을 encrypt 방식으로 암호화하여 일치하는지 여부로
로그인 인증을 수행한다.

### User

| FIELD      | TYPE   | DESCRIPTION    |
|------------|--------|----------------|
| id         | string | 유저 아이디         |
| _password_ | string | 비밀번호           |
| wins       | int    | 게임을 이긴 횟수      |
| games      | int    | 게임을 플레이한 횟수    |
| color      | int    | 주로 사용하는 네마의 색상 |

`user.color` 값은 6자리 HTML 16진수 색상 코드를 그대로 10진수로 변환한 것을 사용한다.

#### GET `/users`
모든 유저 정보 불러오기

#### POST `/users/new`
새로운 계정 생성
* `id`, `token` 정보가 전달되어야 함
* `color` 정보를 전달할 수 있음

### POST `/login`
세션 로그인
* `id`, `token` 정보가 전달되어야 함

#### GET `/users/{user.id}`
유저 정보 불러오기

#### PATCH `/users/{user.id}`*
유저 정보 변경하기
* `token` 변경할 수 있음

#### DELETE `/users/{user.id}`*
~~유저 삭제하기~~

### Game

| FIELD      | TYPE     | DESCRIPTION     |
|------------|----------|-----------------|
| id         | int      | 게임 아이디          |
| direction  | boolean  | 네마 순환의 방향       |
| state      | int      | 게임 진행 상태        |
| max_score  | int      | 게임 종료에 필요한 점수 수 |
| created_at | datetime | 게임 생성 시각        |
| created_by | user.id  | 게임을 생성한 유저      |

#### GET `/games`
게임 목록 불러오기

#### POST `/games/new`*
새로운 게임 생성

#### GET `/games/{game.id}`
게임 정보 불러오기

### Participant

| FIELD   | TYPE    | DESCRIPTION |
|---------|---------|-------------|
| user_id | user.id | 참가자 id      |
| game_id | game.id | 게임 id       |

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