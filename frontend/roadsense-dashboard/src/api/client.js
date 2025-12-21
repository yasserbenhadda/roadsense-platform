import axios from "axios";

const client = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || "http://api:8000",
  timeout: 10000,
});

// Interceptor to add zoom-level and simplification parameters
client.interceptors.request.use((config) => {
  // Add simplification tolerance based on zoom level if available
  // Backend should support ?simplify=true&tolerance=X for GeoJSON endpoints
  if (config.params && !config.params.simplify) {
    config.params.simplify = true;
    config.params.tolerance = 0.001; // Adjust based on backend requirements
  }
  return config;
});

export default client;