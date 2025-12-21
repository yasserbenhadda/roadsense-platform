import { BrowserRouter, Routes, Route, Suspense } from "react-router-dom";
import { lazy } from "react";
import PrivateRoute from "./router/PrivateRoute";
import { AuthProvider } from "./context/AuthContext";

import Login from "./pages/Login";
const MapPage = lazy(() => import("./pages/MapPage"));
const SegmentDetail = lazy(() => import("./pages/SegmentDetail"));

// Loading fallback component
const LoadingFallback = () => (
  <div className="flex items-center justify-center h-screen bg-gray-50">
    <div className="text-center">
      <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      <p className="mt-4 text-gray-600">Chargement...</p>
    </div>
  </div>
);

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Suspense fallback={<LoadingFallback />}>
          <Routes>

            {/* Public */}
            <Route path="/login" element={<Login />} />

            {/* Private */}
            <Route 
              path="/" 
              element={
                <PrivateRoute>
                  <MapPage />
                </PrivateRoute>
              } 
            />

            <Route 
              path="/segment/:id" 
              element={
                <PrivateRoute>
                  <SegmentDetail />
                </PrivateRoute>
              } 
            />

          </Routes>
        </Suspense>
      </BrowserRouter>
    </AuthProvider>
  );
}
