import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Performance monitoring callback
const perfCallback = (metric) => {
  // Log to console in development
  if (process.env.NODE_ENV === 'development') {
    console.log(`${metric.name}:`, metric.value);
  }
  
  // Send to analytics endpoint
  if (window.gtag) {
    // Google Analytics integration
    window.gtag.event(metric.name, {
      value: Math.round(metric.value),
      event_category: 'Web Vitals',
      event_label: metric.id,
      non_interaction: true,
    });
  }
  
  // Optional: Send to your own analytics service
  // navigator.sendBeacon('/api/metrics', JSON.stringify(metric));
};

// Enable Web Vitals reporting
reportWebVitals(perfCallback);
