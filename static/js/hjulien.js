let hjulien;
let hjulienCtx;

let hjulienDirection = false;

let mouseX, mouseY;

let unit;

let floatX, floatY;

let nemas = {};

function tick() {
    floatX = Math.round((mouseX/unit - 3.5) / 2);
    floatY = Math.round((mouseY/unit - 3.5) / 2);
}

function drawHighlightNema() {
    let width = unit;
    let height = 3 * unit;
    if ((floatX + floatY) % 2 === (hjulienDirection ? 1 : 0)) {
        [width, height] = [height, width];
    }
    let x = 2 * unit * (floatX + 1.75) - width / 2;
    let y = 2 * unit * (floatY + 1.75) - height / 2;

    hjulienCtx.strokeStyle = "#f7f7f9";
    hjulienCtx.beginPath();
    hjulienCtx.moveTo(x, y);
    hjulienCtx.lineTo(x + width, y);
    hjulienCtx.lineTo(x + width, y + height);
    hjulienCtx.lineTo(x, y + height);
    hjulienCtx.lineTo(x, y);
    hjulienCtx.stroke();
}

function render() {
    drawBackground();

    if (0 <= floatX && floatX < 10 && 0 <= floatY && floatY < 10) {
        drawHighlightNema();
    }
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