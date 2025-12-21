import React, { useState } from "react";
import { useSearchParams } from "react-router-dom";

export default function FiltersBar({ onApply }) {
  const [searchParams, setSearchParams] = useSearchParams();

  // Default values from URL or fallback
  const [dateFrom, setDateFrom] = useState(searchParams.get("from") || "");
  const [dateTo, setDateTo] = useState(searchParams.get("to") || "");
  const [typeDefaut, setTypeDefaut] = useState(searchParams.get("type") || "");
  const [minPriority, setMinPriority] = useState(searchParams.get("pmin") || 0);
  const [maxPriority, setMaxPriority] = useState(searchParams.get("pmax") || 100);

  const applyFilters = () => {
    const filters = {
      dateFrom,
      dateTo,
      typeDefaut,
      minPriority,
      maxPriority
    };

    // Update URL parameters
    const params = {
      from: dateFrom,
      to: dateTo,
      type: typeDefaut,
      pmin: minPriority,
      pmax: maxPriority,
    };

    setSearchParams(params);

    // Send to parent
    onApply(filters);
  };

  return (
    <div className="w-full p-4 bg-white shadow flex flex-wrap gap-4 items-end">
      
      {/* Date Range */}
      <div>
        <label className="block text-sm">Date From</label>
        <input
          type="date"
          value={dateFrom}
          onChange={(e) => setDateFrom(e.target.value)}
          className="border p-2 rounded"
        />
      </div>

      <div>
        <label className="block text-sm">Date To</label>
        <input
          type="date"
          value={dateTo}
          onChange={(e) => setDateTo(e.target.value)}
          className="border p-2 rounded"
        />
      </div>

      {/* Type défaut */}
      <div>
        <label className="block text-sm">Type de défaut</label>
        <select
          value={typeDefaut}
          onChange={(e) => setTypeDefaut(e.target.value)}
          className="border p-2 rounded"
        >
          <option value="">Tous</option>
          <option value="fissure">Fissure</option>
          <option value="nid">Nid de poule</option>
          <option value="deformation">Déformation</option>
        </select>
      </div>

      {/* Priorité MIN */}
      <div>
        <label className="block text-sm">Priorité min</label>
        <input
          type="number"
          min="0"
          max="100"
          value={minPriority}
          onChange={(e) => setMinPriority(e.target.value)}
          className="border p-2 rounded w-20"
        />
      </div>

      {/* Priorité MAX */}
      <div>
        <label className="block text-sm">Priorité max</label>
        <input
          type="number"
          min="0"
          max="100"
          value={maxPriority}
          onChange={(e) => setMaxPriority(e.target.value)}
          className="border p-2 rounded w-20"
        />
      </div>

      {/* Apply button */}
      <button
        onClick={applyFilters}
        className="px-4 py-2 bg-blue-600 text-white rounded shadow hover:bg-blue-700"
      >
        Appliquer
      </button>
    </div>
  );
}
