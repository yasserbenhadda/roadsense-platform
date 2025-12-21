import React from "react";

export default function DefectsList({ defects }) {
  return (
    <div className="bg-white p-4 shadow rounded">
      <h3 className="text-lg font-semibold mb-3">Défauts détectés</h3>

      {defects.length === 0 && <p>Aucun défaut.</p>}

      <ul className="space-y-2">
        {defects.map(d => (
          <li key={d.id} className="border p-2 rounded">
            <strong>{d.type}</strong> <br />
            {d.description} <br />
            <span className="text-sm text-gray-600">
              Priorité: {d.priority}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
