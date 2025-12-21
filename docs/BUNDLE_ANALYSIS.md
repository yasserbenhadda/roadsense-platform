# Bundle Analysis Report

Generated from `npm run build` output on 2025-11-29.

## Bundle Sizes (gzip)

| File | Size |
|------|------|
| main.d7a5a3a5.js | 76.81 kB |
| 187.b16b1ec7.chunk.js (React DOM) | 62.64 kB |
| 416.b137e63e.chunk.js (Leaflet + map libs) | 44.64 kB |
| 910.a9f1d3da.chunk.js (Chart.js) | 15.17 kB |
| 84.487a375e.chunk.js | 10.41 kB |
| 220.9ea64ccf.chunk.css | 6.56 kB |
| 258.d6bfd15f.chunk.css | 6.34 kB |
| Others | ~5 kB |
| **Total** | **~228 kB** |

## Key Observations

1. **React DOM chunk (62.64 kB)**: Contains React and ReactDOM. This is expected and difficult to reduce further without moving to a lighter framework. Already in a separate chunk via code-splitting.

2. **Main bundle (76.81 kB)**: Contains the app shell (App.js, routing, context). Size is reasonable for a multi-page app.

3. **Map libraries chunk (44.64 kB)**: Contains leaflet, react-leaflet, react-leaflet-markercluster. This is lazy-loaded (only fetched when user navigates to map), which is good for initial page load.

4. **Chart.js chunk (15.17 kB)**: Already lazy-loaded via dynamic import in SegmentDetail/Stats pages.

## Performance Assessment

✅ **Good practices implemented:**
- Route-level code-splitting (MapPage, SegmentDetail, Stats are lazy-loaded).
- Component-level lazy-loading (ScoreChart is lazy in SegmentDetail).
- Gzip compression enabled in nginx.conf.
- Cache headers for static assets (1y for hashed files).
- Marker clustering reduces DOM size on map.
- Web Vitals monitoring integrated.

⚠️ **Optimization opportunities (diminishing returns):**

1. **Reduce main bundle further** (~2-5 kB possible):
   - Remove unused utilities or dependencies.
   - Inline small utilities (performanceMonitor could be inlined).
   - Currently used code is necessary for routing and auth context.

2. **Defer non-critical CSS** (~1-2 KB possible):
   - The main CSS (476 B) is already small.
   - Consider inlining critical CSS for login page (already recommended in earlier audit).

3. **Tree-shake Chart.js** (~2-3 KB possible):
   - Currently importing full Chart.js; only using Line chart.
   - Ensure only necessary chart types are bundled (check react-chartjs-2 config).

4. **Vector tiles instead of GeoJSON** (~5-10 KB possible via protocol, major server change):
   - Server-side geometry simplification already recommended.
   - Vector tiles would remove client-side GeoJSON parsing overhead.

## Lighthouse Metrics (from earlier audit)

- **FCP**: 0.75 s ✅ (target < 1.5 s)
- **LCP**: 1.75 s ⚠️ (target < 2.5 s, close to limit)
- **Speed Index**: 1.0 s ✅
- **TTI**: 1.8 s ✅
- **TBT**: 20 ms ✅
- **CLS**: 0 ✅

## Recommendations (Priority Order)

1. **Implement server-side GeoJSON simplification** (High impact, backend work):
   - This will reduce the payload from API significantly.
   - Expected to reduce LCP by 200–500 ms for large datasets.

2. **Enable brotli compression on API responses** (Medium impact, ~10% bandwidth reduction):
   - Update nginx.conf or API server to use brotli for JSON responses.

3. **Inline critical CSS for login page** (Low impact, ~50-100 ms):
   - Extract and inline CSS rules needed for above-fold login form.

4. **Monitor real-world performance with Web Vitals** (Ongoing):
   - The integration is in place; ensure analytics backend captures metrics.

5. **Consider vector tiles for very large datasets** (Future optimization):
   - Only if GeoJSON simplification + server caching is insufficient.

## Conclusion

The bundle is well-optimized for a React mapping application. Current sizes are reasonable. The main performance bottleneck is likely **API response time and GeoJSON size** (server-side), not JavaScript bundle size. Focus on server-side optimizations (simplification, caching) and network delivery (compression, CDN) for the largest gains toward the <2s map load target.
