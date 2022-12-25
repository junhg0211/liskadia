let hjulien;
let hjulienCtx;

let nemaHistoryTable;
let stateSpan;
let startForm, joinForm, leaveForm;
let participantsList;

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
    });

  lastNemaCountCheck = now;
}

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

      let td;
      let tr = document.createElement('tr');

      td = document.createElement('td');
      td.innerText = (++index).toString();
      tr.appendChild(td);

      td = document.createElement('td');
      td.innerText = `X${x}Y${y}`;
      tr.appendChild(td);

      td = document.createElement('td');
      td.innerText = id;
      tr.appendChild(td);

      td = document.createElement('td');
      td.innerText = nema['created_at'];
      tr.appendChild(td);

      nemaHistoryTable.children[0].appendChild(tr);
    }))
    .then(updateNextTurn);
}

let meInGame = false;

function updateColors() {
  order.length = 0;
  participantsList.innerHTML = '';

  meInGame = false;
  fetch(`/games/${GAME_ID}`)
    .then(res => res.json())
    .then(data => {
      data['participants'].forEach(user => {
        let color = user['color'];
        let r, g, b;
        [g, b] = [Math.floor(color / 0x100), color % 0x100];
        [r, g] = [Math.floor(g / 0x100), g % 0x100];

        colors[user['id']] = `rgb(${r}, ${g}, ${b})`;

        order.push(user['id']);

        let li = document.createElement('li');
        li.innerText = user['id'];
        let span = document.createElement('span');
        span.id = 'game-metadata__user-color__' + user['id'];
        span.innerText = ' ⬤';
        span.style.color = colors[user['id']];
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
        stateSpan.innerText = '(시작 대기중)';
        if (gameCreator === LOGIN_ID)
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
        stateSpan.innerText = '(종료됨)';
      }
    }).then(updateNextTurn);
}

function updateNextTurn() {
  if (gameState !== 1) return;

  nextTurn = order[nemas.length % order.length];

  if (nextTurn === undefined) return;

  // update in nema history
  let tr = document.createElement('tr');

  tr.appendChild(document.createElement('td'));
  tr.appendChild(document.createElement('td'));
  tr.appendChild(document.createElement('td'));
  tr.appendChild(document.createElement('td'));

  tr.children[2].innerText = nextTurn;

  nemaHistoryTable.children[0].appendChild(tr);

  // update in game metadata member list bold
  if (gameState === 1) {
    for (let i = 0; i < participantsList.children.length; i++) {
      let li = participantsList.children[i];
      li.style.fontWeight = 'normal';
      console.log(li.children[0].innerText, nextTurn);
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
  fetch(`/games/${GAME_ID}/nemas/${nemaPosition}`, {method: 'POST'}).then(updateNemas);
}

function tick() {
  floatX = Math.round((mouseX / unit - 3.5) / 2);
  floatY = Math.round((mouseY / unit - 3.5) / 2);

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

function drawHighlightNema() {
  if (!(0 <= floatX && floatX < 10 && 0 <= floatY && floatY < 10)) return;
  if (gameState >= 2) return;

  let [x, y, width, height] = nemaRect(floatX, floatY);

  hjulienCtx.strokeStyle = "#f7f7f97f";
  hjulienCtx.lineWidth = 3;
  hjulienCtx.beginPath();
  hjulienCtx.moveTo(x, y);
  hjulienCtx.lineTo(x + width, y);
  hjulienCtx.lineTo(x + width, y + height);
  hjulienCtx.lineTo(x, y + height);
  hjulienCtx.lineTo(x, y);
  hjulienCtx.stroke();
}

function drawNemas() {
  nemas.forEach(nema => {
    let [xi, yi, id] = nema;
    let color = colors[id];

    let [x, y, width, height] = nemaRect(xi, yi);

    hjulienCtx.fillStyle = color;
    hjulienCtx.fillRect(x, y, width, height);
  });

  /*
   * 네마를 표시하기 위해서는 `colors` 변수에 id에서 네마 색으로 매핑하는 값을 넣어야 합니다.
   * 이후, `nemas` 변수에 네마의 위치와 네마를 놓은 플레이어의 id를 길이가 3인 리스트로 넣어주면 됩니다.
   */
}

function drawLastNema() {
  if (nemas.length === 0) return;

  let [xi, yi, _] = nemas[nemas.length-1];

  let [x, y] = [2 * unit * (xi + 1.75), 2 * unit * (yi + 1.75)];

  hjulienCtx.strokeStyle = "black";
  hjulienCtx.lineWidth = 1;
  hjulienCtx.beginPath();
  hjulienCtx.arc(x, y, unit / 2, 0, 2 * Math.PI);
  hjulienCtx.stroke();
}

function drawScores() {
  if (scores === undefined) return;
  if (Object.keys(colors).length === 0) return;

  if (scoreboardUpdate)
    scoreboardDiv.innerHTML = '';

  let scoreboard = {};
  scores.forEach(score => {
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

    hjulienCtx.strokeStyle = colors[attacker];
    hjulienCtx.lineWidth = 5;
    hjulienCtx.beginPath();
    hjulienCtx.arc(sx, sy, unit / 2, 0, 2*Math.PI);
    hjulienCtx.stroke();

    let [bxi, byi] = [score['by_nema_position'] % 10, Math.floor(score['by_nema_position'] / 10)];
    let [bx, by] = [(bxi+1.75) * 2*unit, (byi+1.75) * 2*unit];

    hjulienCtx.lineWidth = 2;
    hjulienCtx.beginPath();
    hjulienCtx.moveTo(sx, sy);
    hjulienCtx.lineTo(bx, by);
    hjulienCtx.stroke();
  });

  scoreboardUpdate = false;
}

function render() {
  drawBackground();

  drawNemas();

  drawHighlightNema();

  drawScores();

  drawLastNema();
}

function drawBackground() {
  hjulienCtx.fillStyle = "#2c2c2c";
  hjulienCtx.fillRect(0, 0, hjulien.width, hjulien.height);

  let x, y;
  hjulienCtx.fillStyle = "#f7f7f9";
  for (let i = 0; i < 9; i++) {
    y = 2 * unit * i + 4 * unit;
    for (let j = 0; j < 9; j++) {
      x = 2 * unit * j + 4 * unit;
      if (i === 4 && j === 4) hjulienCtx.fillStyle = "#fdde59";

      hjulienCtx.fillRect(x, y, unit, unit);

      if (i === 4 && j === 4) hjulienCtx.fillStyle = "#f7f7f9";
    }
  }

  y = 2 * unit;
  for (let i = 0; i < 5; i++) {
    x = (hjulienDirection ? 4 : 2) * unit + 4 * unit * i;
    hjulienCtx.fillRect(x, y, 3 * unit, unit);
  }

  x = 2 * unit;
  for (let i = 0; i < 5; i++) {
    y = (hjulienDirection ? 2 : 4) * unit + 4 * unit * i;
    hjulienCtx.fillRect(x, y, unit, 3 * unit);
  }

  y = 22 * unit;
  for (let i = 0; i < 5; i++) {
    x = (hjulienDirection ? 2 : 4) * unit + 4 * unit * i;
    hjulienCtx.fillRect(x, y, 3 * unit, unit);
  }

  x = 22 * unit;
  for (let i = 0; i < 5; i++) {
    y = (hjulienDirection ? 4 : 2) * unit + 4 * unit * i;
    hjulienCtx.fillRect(x, y, unit, 3 * unit);
  }
}

function loadHjulien() {
  hjulien = document.querySelector("#hjulien");
  hjulienCtx = hjulien.getContext("2d");

  GAME_ID = parseInt(document.querySelector("#game-metadata__id").textContent);

  hjulien.width = 800;
  hjulien.height = 800;

  unit = hjulien.width / 25;

  drawBackground();

  setInterval(() => {
    tick();
    render();
  }, 1000 / 30);

  nemaHistoryTable = document.querySelector('#nema-history');
  stateSpan = document.querySelector('#game-metadata__state');
  startForm = document.querySelector('#start-form');
  joinForm = document.querySelector('#join-form');
  leaveForm = document.querySelector('#leave-form');
  participantsList = document.querySelector('#participants');
  scoreboardDiv = document.querySelector('#scoreboard');
}

document.addEventListener('DOMContentLoaded', loadHjulien);
document.addEventListener('mousemove', e => {
  let rect = hjulien.getBoundingClientRect();
  mouseX = e.clientX - rect.left;
  mouseY = e.clientY - rect.top;
});
document.addEventListener('click', sendNema);
