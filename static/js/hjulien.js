let hjulien;
let hjulienCtx;

let hjluienDirection = false;

function drawBackground() {
    let unit = hjulien.width / 25;

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
        x = (hjluienDirection ? 4 : 2) * unit + 4 * unit * i;
        hjulienCtx.fillRect(x, y, 3 * unit, unit);
    }

    x = 2 * unit;
    for (let i = 0; i < 5; i++) {
        y = (hjluienDirection ? 2 : 4) * unit + 4 * unit * i;
        hjulienCtx.fillRect(x, y, unit, 3 * unit);
    }

    y = 22 * unit;
    for (let i = 0; i < 5; i++) {
        x = (hjluienDirection ? 2 : 4) * unit + 4 * unit * i;
        hjulienCtx.fillRect(x, y, 3 * unit, unit);
    }

    x = 22 * unit;
    for (let i = 0; i < 5; i++) {
        y = (hjluienDirection ? 4 : 2) * unit + 4 * unit * i;
        hjulienCtx.fillRect(x, y, unit, 3 * unit);
    }
}

function loadHjulien() {
    hjulien = document.querySelector("#hjulien");
    hjulienCtx = hjulien.getContext("2d");

    hjulien.width = 800;
    hjulien.height = 800;

    drawBackground();
}

document.addEventListener('DOMContentLoaded', loadHjulien);