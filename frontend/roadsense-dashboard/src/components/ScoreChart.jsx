import React from "react";
import { Line } from "react-chartjs-2";
import { Chart as ChartJS, LineElement, PointElement, CategoryScale, LinearScale } from "chart.js";

ChartJS.register(LineElement, PointElement, CategoryScale, LinearScale);

export default function ScoreChart({ history }) {
  if (!history || history.length === 0) return <p>No score history.</p>;

  const data = {
    labels: history.map(h => h.date),
    datasets: [
      {
        label: "Score du tronçon",
        data: history.map(h => h.score),
        fill: false,
      }
    ]
  };

  return (
    <div className="bg-white p-4 shadow rounded">
      <h3 className="text-lg font-semibold mb-2">Évolution du score</h3>
      <Line data={data} />
    </div>
  );
}
