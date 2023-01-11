function getLuminance(r8b, g8b, b8b) {
  let rs = r8b / 0xff;
  let gs = g8b / 0xff;
  let bs = b8b / 0xff;

  let r = rs <= 0.03928 ? rs / 12.92 : Math.pow((rs + 0.055) / 1.055, 2.4);
  let g = gs <= 0.03928 ? gs / 12.92 : Math.pow((gs + 0.055) / 1.055, 2.4);
  let b = bs <= 0.03928 ? bs / 12.92 : Math.pow((bs + 0.055) / 1.055, 2.4);

  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function getContrastRatio(luminance1, luminance2) {
  if (luminance1 < luminance2)
    return getContrastRatio(luminance2, luminance1);

  return (luminance1 + 0.05) / (luminance2 + 0.05);
}

function linearInterpolation(v, a1, b1, a2, b2) {
  if (b1 - a1 === 0)
    return a2;

  return (b2 - a2) * (v - a1) / (b1 - a1) + a2;
}

window.addEventListener('DOMContentLoaded', () => {
  let canvas = document.querySelector('#rating-history');
  if (canvas === null) return;

  let context = canvas.getContext('2d');

  fetch(`/ratings/${USER_ID}`)
    .then(r => r.json())
    .then(data => {
      if (data.code !== 200) throw Error;

      return data.history;
    })
    .then(history => {
      let minTime = Infinity, maxTime = -Infinity;
      let maxRating = 0, minRating = Infinity;

      for (let i = 0; i < history.length; i++) {
        history[i]['time'] = new Date(history[i]['time']);
        let timeStamp = history[i]['time'].getTime();
        minTime = Math.min(minTime, timeStamp);
        maxTime = Math.max(maxTime, timeStamp);
        maxRating = Math.max(maxRating, history[i]['rating']);
        minRating = Math.min(minRating, history[i]['rating']);
      }

      // noinspection JSCheckFunctionSignatures
      minTime = new Date(minTime);
      maxTime = new Date(maxTime);

      context.beginPath();
      history.forEach(row => {
        let x = linearInterpolation(row['time'].getTime(), minTime, maxTime, 0, canvas.width);
        let y = linearInterpolation(row['rating'], minRating, maxRating, canvas.height, 0);

        context.lineTo(x, y);
        context.stroke();
        context.beginPath();
        context.arc(x, y, 3, 0, 2*Math.PI);
        context.stroke();
        context.beginPath();
        context.moveTo(x, y);
      });
      context.stroke();
    });
});