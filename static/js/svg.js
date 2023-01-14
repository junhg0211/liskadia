let URL = "http://www.w3.org/2000/svg"

function fillRect(at, x, y, width, height, color) {
  let rect = document.createElementNS(URL, 'rect');
  configureRect(rect, x, y, width, height);
  rect.setAttribute('fill', color);
  at.appendChild(rect);
  return rect;
}

function drawRect(at, x, y, width, height, color, stroke) {
  let rect = document.createElementNS(URL, 'rect');
  configureRect(rect, x, y, width, height);
  rect.setAttribute('fill', 'none');
  rect.setAttribute('stroke', color);
  rect.setAttribute('stroke-width', stroke.toString());
  at.appendChild(rect);
  return rect;
}

function drawFillRect(at, x, y, width, height, color, strokeColor, stroke) {
  let rect = document.createElementNS(URL, 'rect');
  configureRect(rect, x, y, width, height);
  rect.setAttribute('fill', color);
  rect.setAttribute('stroke', strokeColor);
  rect.setAttribute('stroke-width', stroke.toString());
  at.appendChild(rect);
  return rect;
}

function configureRect(what, x, y, width, height) {
  what.setAttribute('x', x.toString());
  what.setAttribute('y', y.toString());
  what.setAttribute('width', width.toString());
  what.setAttribute('height', height.toString());
  return what;
}

function fillText(at, x, y, string, color) {
  let text = document.createElementNS(URL, 'text');
  text.textContent = string;
  text.setAttribute('x', x.toString());
  text.setAttribute('y', y.toString());
  text.setAttribute('fill', color);
  text.setAttribute('text-anchor', 'middle');
  text.setAttribute('dominant-baseline', 'middle');
  at.appendChild(text);
  return text;
}

function drawFillText(at, x, y, string, color, strokeColor, stroke) {
  let text = document.createElementNS(URL, 'text');
  text.textContent = string;
  text.setAttribute('x', x.toString());
  text.setAttribute('y', y.toString());
  text.setAttribute('fill', color);
  text.setAttribute('stroke', strokeColor);
  text.setAttribute('stroke-width', stroke.toString());
  text.setAttribute('stroke-alignment', 'outer');
  text.setAttribute('paint-order', 'stroke');
  text.setAttribute('text-anchor', 'middle');
  text.setAttribute('dominant-baseline', 'middle');
  at.appendChild(text);
  return text;
}

function drawCircle(at, x, y, r, color, stroke) {
  let circle = document.createElementNS(URL, 'circle');
  circle.setAttribute('cx', x.toString());
  circle.setAttribute('cy', y.toString());
  circle.setAttribute('r', r.toString());
  circle.setAttribute('fill', 'none');
  circle.setAttribute('stroke', color);
  circle.setAttribute('stroke-width', stroke.toString());
  at.appendChild(circle);
  return circle;
}

function drawLine(at, x1, y1, x2, y2, color, stroke, dashArray) {
  let line = document.createElementNS(URL, 'line');
  line.setAttribute('x1', x1.toString());
  line.setAttribute('y1', y1.toString());
  line.setAttribute('x2', x2.toString());
  line.setAttribute('y2', y2.toString());
  line.setAttribute('stroke', color);
  line.setAttribute('stroke-width', stroke.toString());
  line.setAttribute('stroke-linecap', 'round');
  if (dashArray) line.setAttribute('stroke-dasharray', dashArray);
  at.appendChild(line);
  return line;
}

function drawPath(at, pathString, color, stroke) {
  let path = document.createElementNS(URL, 'path');
  path.setAttribute('d', pathString);
  path.setAttribute('stroke', color);
  path.setAttribute('stroke-width', stroke.toString());
  path.setAttribute('fill', 'none');
  at.appendChild(path);
  return path;
}

function newGroup() {
  return document.createElementNS(URL, 'g');
}
