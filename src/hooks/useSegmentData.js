import { useEffect, useState } from "react";
import client from "../api/client";          // use your axios instance
import { useAuth } from "../context/AuthContext";

export default function useSegmentData(id) {
  const { accessToken } = useAuth();

  const [segment, setSegment] = useState(null);
  const [defects, setDefects] = useState([]);
  const [history, setHistory] = useState([]); 
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!accessToken) return; // avoid requesting before login

    const fetchAll = async () => {
      setLoading(true);

      try {
        const seg = await client.get(`/segments/${id}`, {
          headers: { Authorization: `Bearer ${accessToken}` }
        });

        const def = await client.get(`/segments/${id}/defects`, {
          headers: { Authorization: `Bearer ${accessToken}` }
        });

        const hist = await client.get(`/segments/${id}/score-history`, {
          headers: { Authorization: `Bearer ${accessToken}` }
        });

        setSegment(seg.data);
        setDefects(def.data);
        setHistory(hist.data);

      } catch (e) {
        console.error("Error loading detail:", e);

      } finally {
        setLoading(false);
      }
    };

    fetchAll();
  }, [id, accessToken]);

  return { segment, defects, history, loading };
}
