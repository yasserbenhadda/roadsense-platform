# GeoJSON Simplification and Tile Strategy

This document describes server-side techniques to support the frontend's performance goals (map < 2s) by returning simplified geometries or vector tiles and by adding cache headers.

Goals
- Provide simplified GeoJSON based on zoom level or tolerance parameter.
- Serve tiles (vector tiles or GeoJSON tiles) for large datasets.
- Add caching and compression for tile and API endpoints.

Examples

Node.js (using turf.js)

```js
// Express example
const express = require('express');
const turf = require('@turf/turf');
const app = express();

// GET /geojson?bbox=...&zoom=12&simplify=true&tolerance=0.001
app.get('/geojson', async (req, res) => {
  const simplify = req.query.simplify === 'true';
  const tolerance = parseFloat(req.query.tolerance) || 0.001;

  // Load your features from DB or file (GeoJSON FeatureCollection)
  let features = await loadFeaturesFromDB();

  if (simplify) {
    features = {
      type: 'FeatureCollection',
      features: features.features.map(f => {
        // Simplify geometry. turf.simplify keeps properties.
        const geom = turf.simplify(f, { tolerance, highQuality: false });
        return { ...f, geometry: geom.geometry };
      })
    };
  }

  // Set caching for tiles-like requests
  res.set('Cache-Control', 'public, max-age=86400');
  res.json(features);
});

app.listen(8000);
```

Python (using shapely / flask)

```py
from flask import Flask, request, jsonify
from shapely.geometry import shape, mapping
from shapely.ops import transform
from functools import partial
import pyproj

app = Flask(__name__)

@app.route('/geojson')
def geojson():
    tolerance = float(request.args.get('tolerance', '0.001'))
    features = load_features_from_db()  # return GeoJSON FeatureCollection

    simplified = []
    for f in features['features']:
        geom = shape(f['geometry'])
        # Simplify in projected units if necessary
        s = geom.simplify(tolerance, preserve_topology=False)
        f['geometry'] = mapping(s)
        simplified.append(f)

    response = {'type': 'FeatureCollection', 'features': simplified}
    # caching
    headers = {'Cache-Control': 'public, max-age=86400'}
    return jsonify(response), 200, headers
```

Vector tiles recommendation
- For large datasets prefer serving Mapbox Vector Tiles (MVT). Use tile server solutions:
  - TileServer GL
  - tegola (Go)
  - Tippecanoe + tiles hosted on CDN
- On the server, pre-generate vector tiles or runtime-render them at tile request time.

Cache headers and compression
- Set `Cache-Control` for tile endpoints (e.g., `public, max-age=2592000` for 30d).
- Enable gzip/brotli compression at server or reverse proxy level.
- Use ETag or Last-Modified for client revalidation.

API contract expected by the frontend
- GET `/geojson` supports params: `simplify=true|false`, `tolerance=<float>`, and optional `bbox` or `zoom` to limit geometry returned.
- GET `/scores` returns summary and `timeseries` for the dashboard.
- GET `/segments/:id`, `/segments/:id/defects`, `/segments/:id/score-history`.

Notes
- Tolerance values depend on source unit (degrees vs meters). If geometries are in WGS84 (degrees), a small tolerance (0.0001–0.01) might be appropriate. For meter-based simplification, reproject to a projected CRS first.
- Simplification can change topology (split rings), test visually.

```text
Recommended server response headers for tile endpoints:
Cache-Control: public, max-age=2592000
Content-Encoding: gzip
ETag: "<hash>"
```

If you want, I can draft example server code for your backend stack (Node/Express or Python/Flask) adapted to your current API structure.