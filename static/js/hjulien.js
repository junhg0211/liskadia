let hjulien;
let hjulienCtx;

let nemaHistoryTable;
let stateSpan;
let startForm, joinForm;

let hjulienDirection = false;

let mouseX, mouseY;

let unit;

let floatX, floatY;

let nemas = [];
let colors = {};
let gameCreator;
let gameState = 0;

let nemaUpdate = true;
let colorUpdate = true;

let GAME_ID;

function updateNemas() {
  if (!nemaUpdate) return;

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
    }));

  nemaUpdate = false;
}

let meInGame = false;

function updateColors() {
  if (!colorUpdate) return;

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

        if (!meInGame && user['id'] === LOGIN_ID) {
          meInGame = true;
        }
      });

      hjulienDirection = data['game']['direction'];

      gameCreator = data['game']['created_by'];

      gameState = data['game']['state'];
      startForm.style.display = 'none';
      joinForm.style.display = 'none';

      if (gameState === 0) {
        stateSpan.innerText = '(시작 대기중)';
        if (gameCreator === LOGIN_ID)
          startForm.style.display = 'block';
        if (LOGIN_ID && !meInGame)
          joinForm.style.display = 'block';
      } else if (gameState === 1) {
        stateSpan.innerText = '';
      } else if (gameState === 2) {
        stateSpan.innerText = '(종료됨)';
      }
    });

  colorUpdate = false;
}

function sendNema(e) {
  if (!(0 <= floatX && floatX <= 9 && 0 <= floatY && floatY <= 9)) return;

  if (LOGIN_ID === null) return;

  if (gameState !== 1) return;

  if (!meInGame) return;

  let nemaPosition = floatY * 10 + floatX;
  fetch(`/games/${GAME_ID}/nemas/${nemaPosition}`, {method: 'POST'})
    .then(res => res.json())
    .then(data => {
      if (data.code === 200) {
        nemaUpdate = true;
      }
    });
}

function tick() {
  floatX = Math.round((mouseX / unit - 3.5) / 2);
  floatY = Math.round((mouseY / unit - 3.5) / 2);

  updateNemas();
  updateColors();
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

  let [x, y, width, height] = nemaRect(floatX, floatY);

  hjulienCtx.strokeStyle = "#f7f7f9";
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

function render() {
  drawBackground();

  drawNemas();

  drawHighlightNema();
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
}

document.addEventListener('DOMContentLoaded', loadHjulien);
document.addEventListener('mousemove', e => {
  let rect = hjulien.getBoundingClientRect();
  mouseX = e.clientX - rect.left;
  mouseY = e.clientY - rect.top;
});
document.addEventListener('click', sendNema);