export function styleForScore(score) {
  const s = Number(score||0);
  let color = "#2ecc71"; // vert
  if (s > 70) color = "#e74c3c";      // rouge
  else if (s > 40) color = "#f1c40f"; // jaune
  return {
    color,
    weight: 4,
    opacity: 0.9,
  };
}
