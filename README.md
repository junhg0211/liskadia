# Liskadia

> 리스카드 서버 엔진

## API

API의 구상은 [이 링크](https://sch-jeon.notion.site/Liskadia-fdc59575472843dd99b6ae900dc01a9c)에서 진행하고,
이 문서에는 코드로 구현된 API만 나열한다.

### User

| FIELD      | TYPE   | DESCRIPTION |
|------------|--------|-------------|
| id         | string | 유저 아이디      |
| _password_ | string | 비밀번호        |
| wins       | int    | 게임을 이긴 횟수   |
| games      | int    | 게임을 플레이한 횟수 |

#### GET `/users`
모든 유저 정보 불러오기

#### POST `/users/new`
새로운 계정 생성
* `id`, `password` 정보가 전달되어야 함

#### GET `/users/{user.id}`
유저 정보 불러오기

#### PATCH `/users/{user.id}`
유저 정보 변경하기
* `password` 변경할 수 있음

#### DELETE `/users/{user.id}`
유저 삭제하기

### Game

| FIELD      | TYPE     | DESCRIPTION |
|------------|----------|-------------|
| id         | int      | 게임 아이디      |
| direction  | boolean  | 네마 순환의 방향   |
| state      | int      | 게임 진행 상태    |
| created_at | datetime | 게임 생성 시각    |

#### GET `/games`
게임 목록 불러오기

#### POST `/games/new`
새로운 게임 생성

#### GET `/games/{game.id}`
게임 정보 불러오기