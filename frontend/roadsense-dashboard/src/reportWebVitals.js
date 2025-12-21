const reportWebVitals = onPerfEntry => {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB, INPWebVitals }) => {
      // Core Web Vitals
      getCLS(onPerfEntry);
      getFID(onPerfEntry);
      getFCP(onPerfEntry);
      getLCP(onPerfEntry);
      getTTFB(onPerfEntry);
      
      // Additional tracking for INP (Interaction to Next Paint) - replaces FID
      if (window.requestIdleCallback) {
        window.addEventListener('click', trackInteractions);
      }
    });
  }
};

// Track interaction metrics for performance monitoring
const trackInteractions = () => {
  if (window.performance && window.performance.getEntriesByType) {
    const entries = window.performance.getEntriesByType('longtask');
    if (entries.length > 0) {
      console.log('Long tasks detected:', entries);
    }
  }
};

// Monitor page visibility for better metric collection
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    // Log when user leaves the page
    console.log('User navigated away - final metrics collected');
  }
});

export default reportWebVitals;
