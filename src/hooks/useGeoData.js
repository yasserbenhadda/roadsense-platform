import { useState, useEffect, useMemo } from "react";
import client from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function useGeoData(filters) {
  const { accessToken } = useAuth();

  const [geojson, setGeojson] = useState(null);
  const [scores, setScores] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const filtersKey = useMemo(() => JSON.stringify(filters), [filters]);

  useEffect(() => {
    let canceled = false;

    // Parse memoized filters string to an object to use in requests
    const params = filtersKey ? JSON.parse(filtersKey) : {};

    async function fetchData() {
      setLoading(true);
      setError(null);

      try {
        const [g, s] = await Promise.all([
          client.get("/geojson", {
            params,
            headers: {
              Authorization: `Bearer ${accessToken}`
            }
          }),
          client.get("/scores", {
            params,
            headers: {
              Authorization: `Bearer ${accessToken}`
            }
          }),
        ]);

        if (!canceled) {
          setGeojson(g.data);
          setScores(s.data);
        }

      } catch (err) {
        if (!canceled) setError(err);

      } finally {
        if (!canceled) setLoading(false);
      }
    }

    if (accessToken) {
      fetchData();
    }

    return () => {
      canceled = true;
    };
  }, [accessToken, filtersKey]);

  return { geojson, scores, loading, error };
}
