import React from "react";
import { Line } from "react-chartjs-2";

export default function ChartTrend({ timeseries }) {
  const data = {
    labels: timeseries.map(t => t.date),
    datasets: [
      {
        label: "Nombre de défauts",
        data: timeseries.map(t => t.count),
        fill: false,
        tension: 0.3,
      }
    ],
  };
  return <div className="p-4"><Line data={data} /></div>;
}
