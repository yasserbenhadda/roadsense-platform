import React from "react";
import useGeoData from "../hooks/useGeoData";
import ChartTrend from "../components/ChartTrend";

export default function Stats() {
  // Use geo data hook to fetch scores; pass empty filters for full dataset
  const { scores, loading, error } = useGeoData({});

  if (loading) return <div className="p-6">Chargement des statistiques...</div>;
  if (error) return <div className="p-6">Erreur: {String(error)}</div>;

  // scores may contain an overall summary and timeseries
  const summary = scores?.summary || {};
  const timeseries = scores?.timeseries || [];

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Statistiques</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="p-4 bg-white shadow rounded">
          <div className="text-sm text-gray-500">Nombre de segments</div>
          <div className="text-2xl font-semibold">{summary.segment_count ?? "—"}</div>
        </div>

        <div className="p-4 bg-white shadow rounded">
          <div className="text-sm text-gray-500">Nombre de défauts</div>
          <div className="text-2xl font-semibold">{summary.defect_count ?? "—"}</div>
        </div>

        <div className="p-4 bg-white shadow rounded">
          <div className="text-sm text-gray-500">Segments prioritaires</div>
          <div className="text-2xl font-semibold">{summary.high_priority_count ?? "—"}</div>
        </div>
      </div>

      <div className="bg-white p-4 shadow rounded">
        <h2 className="text-lg font-medium mb-2">Tendance des défauts</h2>
        {timeseries.length ? (
          <ChartTrend timeseries={timeseries} />
        ) : (
          <p>Aucune série temporelle disponible.</p>
        )}
      </div>
    </div>
  );
}
