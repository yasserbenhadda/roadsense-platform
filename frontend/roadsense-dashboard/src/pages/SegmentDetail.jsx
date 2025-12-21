import React, { Suspense, lazy } from "react";
import { useParams } from "react-router-dom";
import { MapContainer, TileLayer, GeoJSON } from "react-leaflet";
import "leaflet/dist/leaflet.css";

import useSegmentData from "../hooks/useSegmentData";
import DefectsList from "../components/DefectsList";
import axios from "axios";

// Lazy import after all static imports to satisfy ESLint import/first rule
const ScoreChart = lazy(() => import("../components/ScoreChart"));

export default function SegmentDetail() {
  const { id } = useParams();
  const { segment, defects, history, loading } = useSegmentData(id);

  if (loading) return <p className="p-5">Loading...</p>;
  if (!segment) return <p className="p-5">Segment not found.</p>;

  const geojson = segment.geojson; // API returns {"type":"Feature"}

  // Actions
  const markAsRepaired = async () => {
    await axios.put(`/api/segments/${id}/repair`);
    alert("Tronçon marqué comme réparé");
  };

  const addNote = async () => {
    const note = prompt("Votre note:");
    if (!note) return;

    await axios.post(`/api/segments/${id}/note`, { note });
    alert("Note ajoutée");
  };

  return (
    <div className="p-4 space-y-6">

      <h1 className="text-2xl font-bold">
        Détails du Tronçon #{id}
      </h1>

      {/* Map zoomed on this segment */}
      <div className="h-64 w-full rounded overflow-hidden shadow">
        <MapContainer
          bounds={geojson.geometry.coordinates}
          style={{ height: "100%", width: "100%" }}
          scrollWheelZoom={true}
        >
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

          <GeoJSON
            data={geojson}
            style={{ color: "red", weight: 5 }}
          />
        </MapContainer>
      </div>

      {/* Charts */}
      <Suspense fallback={<div className="p-4">Chargement du graphique...</div>}>
        <ScoreChart history={history} />
      </Suspense>

      {/* Defects */}
      <DefectsList defects={defects} />

      {/* Actions */}
      <div className="flex gap-4">
        <button
          onClick={markAsRepaired}
          className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
        >
          Marquer comme réparé
        </button>

        <button
          onClick={addNote}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Ajouter une note
        </button>
      </div>
    </div>
  );
}
