# API Integration Guide

This document specifies the expected endpoints and data contracts between the frontend and backend.

## Base URL

```
REACT_APP_API_BASE_URL=http://api:8000  (or your backend host)
```

All requests use `Authorization: Bearer <accessToken>` header (except `/login`).

## Endpoints

### Authentication

#### POST /auth/login
Request:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

Response (200 OK):
```json
{
  "access_token": "eyJ0eXAi...",
  "token_type": "Bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "User Name"
  }
}
```

### Map & Dashboard

#### GET /geojson
Fetches GeoJSON FeatureCollection with road segments and defect points. Supports simplification for performance.

Query Parameters:
- `simplify` (boolean, default false): Enable geometry simplification.
- `tolerance` (float, default 0.001): Simplification tolerance (degrees or meters depending on projection).
- `bbox` (string, optional): Bounding box as "minLon,minLat,maxLon,maxLat" to limit results.
- `zoom` (integer, optional): Zoom level; server can use to determine simplification.
- `type` (string, optional): Filter by defect type (e.g., "fissure", "nid", "deformation").
- `from` (date, optional): Start date for filtering.
- `to` (date, optional): End date for filtering.
- `pmin`, `pmax` (integer, optional): Priority range filter (0–100).

Example Request:
```
GET /geojson?simplify=true&tolerance=0.001&type=fissure&from=2024-01-01&to=2024-12-31
Authorization: Bearer <token>
```

Response (200 OK):
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "id": "segment-123",
      "geometry": {
        "type": "LineString",
        "coordinates": [[7.5, 33.5], [7.51, 33.51], ...]
      },
      "properties": {
        "id": "segment-123",
        "name": "Route 1, Tronçon A",
        "score": 75,
        "defect_count": 3,
        "priority": 50
      }
    },
    {
      "type": "Feature",
      "id": "defect-456",
      "geometry": {
        "type": "Point",
        "coordinates": [7.5, 33.5]
      },
      "properties": {
        "id": "defect-456",
        "type": "fissure",
        "description": "Crack in pavement",
        "severity": 7,
        "segment_id": "segment-123"
      }
    }
  ]
}
```

Response Headers (recommended for caching):
```
Cache-Control: public, max-age=86400
Content-Encoding: gzip
ETag: "<hash>"
```

#### GET /scores
Fetches aggregate statistics and timeseries data for the dashboard.

Query Parameters:
- `from` (date, optional): Start date.
- `to` (date, optional): End date.
- `type` (string, optional): Filter by defect type.
- `pmin`, `pmax` (integer, optional): Priority range.

Example Request:
```
GET /scores?from=2024-01-01&to=2024-12-31
Authorization: Bearer <token>
```

Response (200 OK):
```json
{
  "summary": {
    "segment_count": 150,
    "defect_count": 342,
    "high_priority_count": 45,
    "avg_score": 68.5
  },
  "timeseries": [
    {
      "date": "2024-01-01",
      "count": 10,
      "score": 70
    },
    {
      "date": "2024-01-02",
      "count": 12,
      "score": 69
    }
  ]
}
```

### Segment Details

#### GET /segments/:id
Fetches a single segment with its geometry.

Example Request:
```
GET /segments/segment-123
Authorization: Bearer <token>
```

Response (200 OK):
```json
{
  "id": "segment-123",
  "name": "Route 1, Tronçon A",
  "length_km": 2.5,
  "score": 75,
  "priority": 50,
  "last_inspected": "2024-11-15",
  "geojson": {
    "type": "Feature",
    "geometry": {
      "type": "LineString",
      "coordinates": [[7.5, 33.5], [7.51, 33.51], ...]
    },
    "properties": {
      "id": "segment-123",
      "name": "Route 1, Tronçon A",
      "score": 75
    }
  }
}
```

#### GET /segments/:id/defects
Fetches all defects on a segment.

Example Request:
```
GET /segments/segment-123/defects
Authorization: Bearer <token>
```

Response (200 OK):
```json
[
  {
    "id": "defect-456",
    "type": "fissure",
    "description": "Longitudinal crack",
    "severity": 7,
    "location": {
      "type": "Point",
      "coordinates": [7.5, 33.5]
    },
    "detected_at": "2024-11-10"
  },
  {
    "id": "defect-457",
    "type": "nid",
    "description": "Pothole",
    "severity": 5,
    "location": {
      "type": "Point",
      "coordinates": [7.505, 33.505]
    },
    "detected_at": "2024-11-12"
  }
]
```

#### GET /segments/:id/score-history
Fetches historical score and defect count for a segment.

Example Request:
```
GET /segments/segment-123/score-history?days=30
Authorization: Bearer <token>
```

Response (200 OK):
```json
[
  {
    "date": "2024-11-01",
    "score": 70,
    "defect_count": 5
  },
  {
    "date": "2024-11-02",
    "score": 71,
    "defect_count": 5
  },
  {
    "date": "2024-11-10",
    "score": 75,
    "defect_count": 3
  }
]
```

## Frontend Usage

### useGeoData Hook
```js
const { geojson, scores, loading, error } = useGeoData({
  type: "fissure",
  from: "2024-01-01",
  to: "2024-12-31",
  pmin: 40,
  pmax: 100
});
```

Internally calls:
- `GET /geojson?simplify=true&tolerance=0.001&type=fissure&from=...&to=...&pmin=40&pmax=100`
- `GET /scores?type=fissure&from=...&to=...&pmin=40&pmax=100`

### useSegmentData Hook
```js
const { segment, defects, history, loading } = useSegmentData("segment-123");
```

Internally calls:
- `GET /segments/segment-123`
- `GET /segments/segment-123/defects`
- `GET /segments/segment-123/score-history`

## Performance Recommendations

1. **Simplification**: Return simplified geometries for `/geojson` when `simplify=true`. Use tolerance values to control detail.
2. **Caching**: Add `Cache-Control: public, max-age=86400` to tile and static endpoint responses.
3. **Compression**: Enable gzip/brotli on all API responses.
4. **Pagination**: For large defect lists, consider paginating `/segments/:id/defects`.
5. **Vector Tiles**: Consider migrating to vector tiles (Mapbox Vector Tiles or GeoJSON tiles) for very large datasets.

## Error Responses

All errors follow this format:

```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired token"
}
```

Common status codes:
- 200: OK
- 400: Bad request (invalid parameters)
- 401: Unauthorized (missing or invalid token)
- 404: Not found (segment ID doesn't exist)
- 500: Server error
