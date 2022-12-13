let hjulien;
let hjulienCtx;

let hjulienDirection = false;

let mouseX, mouseY;

let unit;

let floatX, floatY;

let nemas = [];
let colors = {};

function tick() {
    floatX = Math.round((mouseX/unit - 3.5) / 2);
    floatY = Math.round((mouseY/unit - 3.5) / 2);
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

    if (0 <= floatX && floatX < 10 && 0 <= floatY && floatY < 10) {
        drawHighlightNema();
    }

    drawNemas();
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
            if (i === 4 && j === 4)
                hjulienCtx.fillStyle = "#fdde59";

            hjulienCtx.fillRect(x, y, unit, unit);

            if (i === 4 && j === 4)
                hjulienCtx.fillStyle = "#f7f7f9";
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

    hjulien.width = 800;
    hjulien.height = 800;

    unit = hjulien.width / 25;

    drawBackground();

    setInterval(() => {
        tick();
        render();
    }, 1000 / 30);
}

document.addEventListener('DOMContentLoaded', loadHjulien);
document.addEventListener('mousemove', e => {
    let rect = hjulien.getBoundingClientRect();
    mouseX = e.clientX - rect.left;
    mouseY = e.clientY - rect.top;
});