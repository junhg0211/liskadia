let hjulien;

let nemaHistoryTable;
let stateSpan;
let startForm, joinForm, leaveForm;
let participantsList;
let rankingList;

let scoreboardDiv;
let scoreboardUpdate = true;

let hjulienDirection = false;

let mouseX, mouseY;

let unit;

let floatX, floatY;

let nemas = [];
let colors = {};
let order = [];
let gameCreator;
let gameState = 0;
let nextTurn;
let scores;

let GAME_ID;

function escapeUserId(userId) {
  return userId.replaceAll('.', '-').replaceAll(' ', '-');
}

let lastNemaCountCheck;
function checkMeta() {
  let now = Date.now();
  if (lastNemaCountCheck !== null && now - lastNemaCountCheck < 1500) return;
  if (gameState === 2) return;

  fetch(`/games/${GAME_ID}/meta`)
    .then(res => res.json())
    .then(data => {
      let stateChange = false;
      if (gameState !== data['state']) {
        gameState = data['state'];
        stateChange = true;
      }

      if (order.length !== data['user_count'] || stateChange) {
        updateColors();
      }

      if (data['nema_count'] !== nemas.length) {
        updateNemas();
      }

      scores = data['scores'];
      scoreboardUpdate = true;

      let userScores = {};
      let scoredUserCounts = [];
      let userInformation = {};

      scores.forEach(score => {
        let attacker = score['user_id'];

        // calculate score
        if (Object.keys(userScores).indexOf(attacker) !== -1) {
          userScores[attacker] += 1;
        } else {
          userScores[attacker] = 1;
        }
        let pointCount = userScores[attacker];

        if (Object.keys(scoredUserCounts).length < pointCount) {
          scoredUserCounts.push(1);
        } else {
          scoredUserCounts[pointCount - 1] += 1;
        }
        let count = scoredUserCounts[pointCount - 1];
        userInformation[attacker] = [pointCount, -count];
      });

      rankingList.innerHTML = '';
      Object.entries(userInformation)
        .sort((a, b) => 100*(b[1][0] - a[1][0]) + (b[1][1] - a[1][1]))
        .map(([key, _]) => key)
        .forEach(userId => {
          let li = document.createElement('li');

          let a = document.createElement('a');
          a.innerText = userId;
          a.href = `/profile/${userId}`;
          li.appendChild(a);

          let span = document.createElement('span');
          span.className = 'user-color__' + escapeUserId(userId);
          span.innerText = ' ⬤';
          li.appendChild(span);

          rankingList.appendChild(li);
        });
    })
    .then(drawScores);

  lastNemaCountCheck = now;
}

let audioes = [
  new Audio('/static/wav/nema1.wav'),
  new Audio('/static/wav/nema2.wav'),
  new Audio('/static/wav/nema3.wav'),
  new Audio('/static/wav/nema4.wav'),
  new Audio('/static/wav/nema5.wav')
];

let notification;
function updateNemas() {
  nemaHistoryTable.children[0].innerHTML = nemaHistoryTable.rows[0].innerHTML;
  nemas.length = 0;

  let index = 0;
  fetch(`/games/${GAME_ID}/nemas`)
    .then(res => res.json())
    .then(data => data['nemas'])
    .then(nemas_ => nemas_.forEach(nema => {
      let position = nema['position'];
      let [y, x] = [Math.floor(position / 10), position % 10];
      let id = nema['user_id'];

      nemas.push([x, y, id]);

      // append on nema history
      let td;
      let tr = nemaHistoryTable.insertRow(1);

      td = document.createElement('td');
      td.innerText = (++index).toString();
      tr.appendChild(td);

      td = document.createElement('td');
      td.innerText = `X${x}Y${y}`;
      tr.appendChild(td);

      td = document.createElement('td');
      td.innerText = id;
      let span = document.createElement('span');
      span.className = 'user-color__' + escapeUserId(id);
      span.innerText = ' ⬤';
      td.appendChild(span);
      tr.appendChild(td);

      td = document.createElement('td');
      td.innerText = nema['created_at'];
      tr.appendChild(td);
    }))
    .then(updateNextTurn)
    .then(drawNemas);

  if (gameState !== 1) return;

  // noinspection JSIgnoredPromiseFromCall
  audioes[Math.floor(Math.random() * 5)].play();

  if (!document.hasFocus()) {
    notification = show_notification(`Liskadia #${GAME_ID}`, NEW_NEMA_MESSAGE);
  }
}

let meInGame = false;

function updateColors() {
  order.length = 0;
  participantsList.innerHTML = '';

  let styleSheet = document.styleSheets[document.styleSheets.length-1];
  let styleSheetRuleCount = styleSheet.rules.length;
  for (let i = 0; i < styleSheetRuleCount; i++) {
    styleSheet.deleteRule(0);
  }

  meInGame = false;
  fetch(`/games/${GAME_ID}`)
    .then(res => res.json())
    .then(data => {
      colors = {};

      data['participants'].forEach(user => {
        let color = user['color'];
        let r, g, b;
        [g, b] = [Math.floor(color / 0x100), color % 0x100];
        [r, g] = [Math.floor(g / 0x100), g % 0x100];

        colors[user['id']] = `rgb(${r}, ${g}, ${b})`;

        order.push(user['id']);

        let li, span, a;
        li = document.createElement('li');
        a = document.createElement('a');
        a.href = `/profile/${user['id']}`;
        a.innerText = user['id'];
        li.appendChild(a);
        span = document.createElement('span');
        span.className = 'user-color__' + escapeUserId(user['id']);
        span.innerText = ' ⬤';
        let convertedId = escapeUserId(user['id']);
        styleSheet.insertRule(`.user-color__${convertedId} { color: ${colors[user['id']]}; }`, 0);
        li.appendChild(span);
        participantsList.appendChild(li);

        if (!meInGame && user['id'] === LOGIN_ID) {
          meInGame = true;
        }
      });

      hjulienDirection = data['game']['direction'];

      gameCreator = data['game']['created_by'];

      gameState = data['game']['state'];
      startForm.style.display = 'none';
      joinForm.style.display = 'none';
      leaveForm.style.display = 'none';

      if (gameState === 0) {
        stateSpan.innerText = '(IDLE)';
        if (gameCreator === LOGIN_ID && Object.keys(colors).length > 1)
          startForm.style.display = 'block';
        if (LOGIN_ID) {
          if (meInGame) {
            if (gameCreator !== LOGIN_ID) {
              leaveForm.style.display = "block";
            }
          } else {
            joinForm.style.display = 'block';
          }
        }
      } else if (gameState === 1) {
        stateSpan.innerText = '';
      } else if (gameState === 2) {
        stateSpan.innerText = '(FINISHED)';
      }
    })
    .then(updateNextTurn)
    .then(drawScores)
    .then(drawNemas);
}

function updateNextTurn() {
  if (gameState !== 1) return;

  nextTurn = order[nemas.length % order.length];

  if (nextTurn === undefined) return;

  // update in nema history
  let tr = nemaHistoryTable.children[0].insertRow(1);

  tr.appendChild(document.createElement('td'));
  tr.appendChild(document.createElement('td'));
  tr.appendChild(document.createElement('td'));
  tr.appendChild(document.createElement('td'));

  tr.children[2].innerText = nextTurn;
  let span = document.createElement('span');
  span.innerText = ' ⬤';
  span.className = `user-color__${escapeUserId(nextTurn)}`;
  tr.children[2].appendChild(span);

  // update in game metadata member list bold
  if (gameState === 1) {
    for (let i = 0; i < participantsList.children.length; i++) {
      let li = participantsList.children[i];
      li.style.fontWeight = 'normal';
      if (li.innerText.indexOf(nextTurn) === 0) {
        li.style.fontWeight = 'bold';
      }
    }
  }
}

function sendNema() {
  if (!(0 <= floatX && floatX <= 9 && 0 <= floatY && floatY <= 9)) return;
  if (LOGIN_ID === null) return;
  if (gameState !== 1) return;
  if (!meInGame) return;
  if (LOGIN_ID !== nextTurn) return;

  let nemaPosition = floatY * 10 + floatX;
  fetch(`/games/${GAME_ID}/nemas/${nemaPosition}`, {method: 'POST'})
    .then(updateNemas)
    .then(() => lastNemaCountCheck = new Date() - 1500);
}

function tick() {
  floatX = Math.round((mouseX / unit - 3.5) / 2);
  floatY = Math.round((mouseY / unit - 3.5) / 2);

  if (document.hasFocus() && notification !== undefined) {
    notification.close();
    notification = undefined;
  }

  checkMeta();
}

function nemaRect(xi, yi) {
  let width = unit;
  let height = 3 * unit;
  if ((xi + yi) % 2 === (hjulienDirection ? 1 : 0)) {
    [width, height] = [height, width];
  }
  let x = 2 * unit * (xi + 1.75) - width / 2;
  let y = 2 * unit * (yi + 1.75) - height / 2;

  return [x, y, width, height];
}

let highlightNema;

function drawHighlightNema() {
  if (!(0 <= floatX && floatX < 10 && 0 <= floatY && floatY < 10)) return;
  if (gameState >= 2) {
    configureRect(highlightNema, -10, -10, 0, 0);
    return;
  }

  let [x, y, width, height] = nemaRect(floatX, floatY);

  configureRect(highlightNema, x, y, width, height);
}

let nemaGroup;

function dimColor(color, amount) {
  if (amount === undefined) amount = 0.7;
  let [r, g, b] = color.substring(4, color.length-1).split(', ');
  return `rgb(${r * 0.7874 * amount}, ${g * 0.2848 * amount}, ${b * 0.9278 * amount})`;
}

function drawNemas() {
  nemaGroup.innerHTML = '';

  nemas.forEach(nema => {
    let [xi, yi, id] = nema;
    let color = colors[id];

    let [x, y, width, height] = nemaRect(xi, yi);

    drawFillRect(nemaGroup, x, y, width, height, color, dimColor(color), 1);
  });

  /*
   * 네마를 표시하기 위해서는 `colors` 변수에 id에서 네마 색으로 매핑하는 값을 넣어야 합니다.
   * 이후, `nemas` 변수에 네마의 위치와 네마를 놓은 플레이어의 id를 길이가 3인 리스트로 넣어주면 됩니다.
   */
}

let lastNemaIndicatorBackground;
let lastNemaIndicator;
function drawLastNema() {
  if (nemas.length === 0) return;
  if (lastNemaIndicatorBackground === undefined)
    lastNemaIndicatorBackground = drawCircle(hjulien, 0, 0, unit, '#f7f7f9', 4);
  if (lastNemaIndicator === undefined)
    lastNemaIndicator = drawCircle(hjulien, 0, 0, unit, '#2c2c2c', 2);

  let [xi, yi, _] = nemas[nemas.length-1];

  let [x, y] = [2 * unit * (xi + 1.75), 2 * unit * (yi + 1.75)];

  lastNemaIndicator.setAttribute('cx', x.toString());
  lastNemaIndicator.setAttribute('cy', y.toString());
  lastNemaIndicator.setAttribute('cy', y.toString());

  lastNemaIndicatorBackground.setAttribute('cx', x.toString());
  lastNemaIndicatorBackground.setAttribute('cy', y.toString());
  lastNemaIndicatorBackground.setAttribute('cy', y.toString());
}

let scoresGroup;

function drawScores() {
  if (scores === undefined) return;
  if (Object.keys(colors).length === 0) return;

  if (scoreboardUpdate)
    scoreboardDiv.innerHTML = '';

  scoresGroup.innerHTML = '';

  let scoreboard = {};
  for (let i = 0; i < scores.length; i++) {
    let score = scores[i];
    let attacker = score['user_id'];

    if (scoreboardUpdate) {
      // process scoreboard
      if (scoreboard[attacker] === undefined) scoreboard[attacker] = 0;
      while (scoreboardDiv.children.length <= scoreboard[attacker]) {
        let row = document.createElement('div');
        row.className = "scoreboard-row";
        scoreboardDiv.appendChild(row);
      }
      let indicator = document.createElement('div');
      indicator.className = "scoreboard-point";
      indicator.style.width = '24px';
      indicator.style.height = '24px';
      indicator.style.backgroundColor = colors[attacker];
      scoreboardDiv.children[scoreboard[attacker]++].appendChild(indicator);
    }

    // draw score in hjulien
    let [sxi, syi] = [score['position'] % 10, Math.floor(score['position'] / 10)];
    let [sx, sy] = [(sxi+1.75) * 2*unit, (syi+1.75) * 2*unit];
    let [bxi, byi] = [score['by_nema_position'] % 10, Math.floor(score['by_nema_position'] / 10)];
    let [bx, by] = [(bxi+1.75) * 2*unit, (byi+1.75) * 2*unit];

    drawLine(scoresGroup, sx, sy, bx, by, dimColor(colors[attacker]), 4);
    drawLine(scoresGroup, sx, sy, bx, by, colors[attacker], 2);
    drawCircle(scoresGroup, sx, sy, unit / 2, dimColor(colors[attacker]), 7);
    drawCircle(scoresGroup, sx, sy, unit / 2, colors[attacker], 5);

    drawFillText(scoresGroup, sx, sy, (i+1).toString(), '#19191e', '#f7f7f9', 4);
  }

  scoreboardUpdate = false;
}

function render() {
  // drawNemas();

  drawHighlightNema();

  drawLastNema();
}

function drawBackground() {
  let background = newGroup();

  fillRect(background, 0, 0, hjulien.clientWidth, hjulien.clientHeight, '#2c2c2c');

  let x, y;
  let color;
  for (let i = 0; i < 9; i++) {
    y = 2 * unit * i + 4 * unit;
    for (let j = 0; j < 9; j++) {
      x = 2 * unit * j + 4 * unit;
      color = i === 4 && j === 4 ? '#fdde59' : '#f7f7f9';
      fillRect(background, x, y, unit, unit, color);
    }
  }

  y = 2 * unit;
  for (let i = 0; i < 5; i++) {
    x = (hjulienDirection ? 4 : 2) * unit + 4 * unit * i;
    fillRect(background, x, y, 3 * unit, unit, '#f7f7f9');
  }

  x = 2 * unit;
  for (let i = 0; i < 5; i++) {
    y = (hjulienDirection ? 2 : 4) * unit + 4 * unit * i;
    fillRect(background, x, y, unit, 3 * unit, '#f7f7f9');
  }

  y = 22 * unit;
  for (let i = 0; i < 5; i++) {
    x = (hjulienDirection ? 2 : 4) * unit + 4 * unit * i;
    fillRect(background, x, y, 3 * unit, unit, '#f7f7f9');
  }

  x = 22 * unit;
  for (let i = 0; i < 5; i++) {
    y = (hjulienDirection ? 4 : 2) * unit + 4 * unit * i;
    fillRect(background, x, y, unit, 3 * unit, '#f7f7f9');
  }

  for (let i = 0; i < 10; i++) {
    fillText(background, 3.5 * unit + i * 2 * unit, unit, i.toString(), '#f7f7f9');
    fillText(background, 3.5 * unit + i * 2 * unit, 24 * unit, i.toString(), '#f7f7f9');

    fillText(background, unit, 3.5 * unit + i * 2 * unit, i.toString(), '#f7f7f9');
    fillText(background, 24 * unit, 3.5 * unit + i * 2 * unit, i.toString(), '#f7f7f9');
  }

  hjulien.appendChild(background);
}

function loadHjulien() {
  hjulien = document.querySelector("#hjulien");
  hjulien.setAttribute('width', '800');
  hjulien.setAttribute('height', '800');

  GAME_ID = parseInt(document.querySelector("#game-metadata__id").textContent);

  unit = hjulien.clientWidth / 25;

  drawBackground();
  nemaGroup = newGroup(); hjulien.appendChild(nemaGroup);
  highlightNema = drawRect(hjulien, 0, 0, 0, 0, '#f7f7f980', 3);
  scoresGroup = newGroup(); hjulien.appendChild(scoresGroup);

  setInterval(() => {
    tick();
    render();
  }, 1000 / 30);

  let style = document.createElement('style');
  document.head.appendChild(style);

  nemaHistoryTable = document.querySelector('#nema-history');
  stateSpan = document.querySelector('#game-metadata__state');
  startForm = document.querySelector('#start-form');
  joinForm = document.querySelector('#join-form');
  leaveForm = document.querySelector('#leave-form');
  participantsList = document.querySelector('#participants');
  scoreboardDiv = document.querySelector('#scoreboard');
  rankingList = document.querySelector('#ranking');
}

window.addEventListener('DOMContentLoaded', loadHjulien);
document.addEventListener('mousemove', e => {
  let rect = hjulien.getBoundingClientRect();
  mouseX = e.clientX - rect.left;
  mouseY = e.clientY - rect.top;
});
document.addEventListener('click', sendNema);
