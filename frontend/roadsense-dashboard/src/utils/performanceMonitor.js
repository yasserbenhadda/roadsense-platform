/**
 * Performance Monitoring Utility
 * Measures page load times, API response times, and component rendering performance
 */

class PerformanceMonitor {
  constructor() {
    this.marks = {};
    this.metrics = [];
  }

  /**
   * Start measuring a performance metric
   */
  startMeasure(name) {
    this.marks[name] = performance.now();
  }

  /**
   * End measuring and return duration
   */
  endMeasure(name) {
    if (!this.marks[name]) {
      console.warn(`No start mark found for ${name}`);
      return null;
    }
    const duration = performance.now() - this.marks[name];
    delete this.marks[name];
    
    this.logMetric(name, duration);
    return duration;
  }

  /**
   * Log a metric
   */
  logMetric(name, value, unit = 'ms') {
    const metric = { name, value, unit, timestamp: new Date().toISOString() };
    this.metrics.push(metric);
    
    // Log in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`⏱️ ${name}: ${value.toFixed(2)}${unit}`);
    }
    
    return metric;
  }

  /**
   * Get all collected metrics
   */
  getMetrics() {
    return this.metrics;
  }

  /**
   * Clear all metrics
   */
  clearMetrics() {
    this.metrics = [];
  }

  /**
   * Export metrics as JSON
   */
  exportMetrics() {
    return JSON.stringify(this.metrics, null, 2);
  }

  /**
   * Check if page meets performance targets
   */
  checkPerformanceTargets() {
    const targets = {
      'API Response Time': 2000, // 2s
      'Component Render Time': 100, // 100ms
      'Page Load Time': 2000, // 2s
    };

    const report = {};
    for (const [metric, target] of Object.entries(targets)) {
      const values = this.metrics.filter(m => m.name.includes(metric));
      if (values.length > 0) {
        const avg = values.reduce((sum, m) => sum + m.value, 0) / values.length;
        report[metric] = {
          average: avg,
          target,
          status: avg <= target ? '✅ PASS' : '❌ FAIL'
        };
      }
    }
    return report;
  }
}

export const performanceMonitor = new PerformanceMonitor();
export default PerformanceMonitor;
