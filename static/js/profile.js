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