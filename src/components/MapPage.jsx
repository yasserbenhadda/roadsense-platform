import React, { useMemo } from "react";
import { MapContainer, TileLayer, GeoJSON, Marker, Popup } from "react-leaflet";
import MarkerClusterGroup from "react-leaflet-markercluster";
import "leaflet/dist/leaflet.css";
import "leaflet.markercluster/dist/MarkerCluster.css";
import "leaflet.markercluster/dist/MarkerCluster.Default.css";
import useGeoData from "../hooks/useGeoData";
import { styleForScore } from "../utils/symbology";

export default function MapPage({ filters }) {
  const { geojson } = useGeoData(filters);

  // Popup for polylines (segments)
  const onEachFeature = (feature, layer) => {
    const props = feature.properties || {};
    const popupHtml = `
      <div>
        <strong>ID:</strong> ${props.id || "—"}<br/>
        <strong>Score:</strong> ${props.score || "—"}<br/>
        <strong>Défauts:</strong> ${props.defect_count || 0}
      </div>
    `;
    layer.bindPopup(popupHtml);
  };

  // Extract point features for clustering (memoized for performance)
  const pointFeatures = useMemo(() => {
    return geojson?.features?.filter((f) => f.geometry.type === "Point") || [];
  }, [geojson]);

  return (
    <div className="h-full w-full">
      <MapContainer
        center={[33.54, -7.65]}
        zoom={12}
        style={{ height: "100vh", width: "100%" }}
      >
        {/* Tile Layer */}
        <TileLayer
          attribution="&copy; OSM contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Polylines colorées */}
        {geojson && (
          <GeoJSON
            data={geojson}
            style={(feature) => styleForScore(feature.properties.score)}
            onEachFeature={onEachFeature}
          />
        )}

        {/* Clustered Markers for detected defects */}
        <MarkerClusterGroup>
          {pointFeatures.map((f) => (
            <Marker
              key={f.properties?.id}
              position={[
                f.geometry.coordinates[1],
                f.geometry.coordinates[0],
              ]}
            >
              <Popup>
                <div>
                  <strong>{f.properties?.type || "Défaut"}</strong>
                  <br />
                  {f.properties?.description || "Aucune description"}
                </div>
              </Popup>
            </Marker>
          ))}
        </MarkerClusterGroup>
      </MapContainer>
    </div>
  );
}
