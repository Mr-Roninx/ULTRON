/**
 * Enterprise Prometheus Metrics Registry & Collector for ULTRON Control Plane
 * Provides standard Prometheus text format metrics for Prometheus, Grafana, Datadog.
 */

interface MetricValue {
  labels: Record<string, string>;
  value: number;
}

class PrometheusRegistry {
  private counters: Map<string, { help: string; values: MetricValue[] }> = new Map();
  private gauges: Map<string, { help: string; values: MetricValue[] }> = new Map();
  private histograms: Map<string, { help: string; buckets: number[]; observations: Array<{ labels: Record<string, string>; value: number }> }> = new Map();

  constructor() {
    this.initStandardMetrics();
  }

  private initStandardMetrics() {
    this.registerCounter('ultron_opportunities_total', 'Total number of recovery opportunities ingested');
    this.registerCounter('ultron_recovered_revenue_paise_total', 'Total cumulative revenue recovered in paise');
    this.registerCounter('ultron_interventions_dispatched_total', 'Total recovery interventions dispatched across channels');
    this.registerCounter('ultron_compliance_vetoes_total', 'Total opportunities vetoed by Action Authority');
    
    this.registerGauge('ultron_shadow_price_paise', 'Current portfolio marginal shadow price in paise');
    this.registerGauge('ultron_capacity_saturation_ratio', 'Current portfolio capacity saturation ratio (0.0 to 1.0)');
    this.registerGauge('ultron_circuit_breaker_state', 'Circuit breaker state: 0=CLOSED, 1=HALF_OPEN, 2=OPEN');
    this.registerGauge('ultron_kill_switch_state', 'Global emergency kill switch state: 0=NORMAL, 1=ENGAGED');
    
    // Enterprise Lagrangian Pacing & Anti-Blast Metrics
    this.registerGauge('ultron_lagrangian_shadow_multiplier', 'Online Lagrangian dual shadow price multiplier lambda(t)');
    this.registerGauge('ultron_budget_pacing_burn_rate', 'Current daily budget burn rate ratio vs target pacing');
    this.registerCounter('ultron_prevented_waste_paise_total', 'Cumulative financial and goodwill capital saved by preventing wasted interventions');
    this.registerGauge('ultron_bayesian_posterior_mean', 'Current Bayesian calibrated recovery probability mean');

    this.registerHistogram('ultron_recovery_latency_seconds', 'End-to-end recovery lifecycle duration in seconds', [1, 5, 15, 30, 60, 300, 900]);
    this.registerHistogram('ultron_provider_latency_seconds', 'Payment provider API request latency in seconds', [0.05, 0.1, 0.25, 0.5, 1, 2.5, 5]);
  }

  public registerCounter(name: string, help: string) {
    if (!this.counters.has(name)) {
      this.counters.set(name, { help, values: [] });
    }
  }

  public registerGauge(name: string, help: string) {
    if (!this.gauges.has(name)) {
      this.gauges.set(name, { help, values: [] });
    }
  }

  public registerHistogram(name: string, help: string, buckets: number[] = [0.1, 0.5, 1, 2.5, 5, 10]) {
    if (!this.histograms.has(name)) {
      this.histograms.set(name, { help, buckets: [...buckets].sort((a, b) => a - b), observations: [] });
    }
  }

  public incCounter(name: string, value: number = 1, labels: Record<string, string> = {}) {
    const counter = this.counters.get(name);
    if (!counter) return;

    const existing = counter.values.find(v => this.matchLabels(v.labels, labels));
    if (existing) {
      existing.value += value;
    } else {
      counter.values.push({ labels: { ...labels }, value });
    }
  }

  public setGauge(name: string, value: number, labels: Record<string, string> = {}) {
    const gauge = this.gauges.get(name);
    if (!gauge) return;

    const existing = gauge.values.find(v => this.matchLabels(v.labels, labels));
    if (existing) {
      existing.value = value;
    } else {
      gauge.values.push({ labels: { ...labels }, value });
    }
  }

  public observeHistogram(name: string, value: number, labels: Record<string, string> = {}) {
    const hist = this.histograms.get(name);
    if (!hist) return;
    hist.observations.push({ labels: { ...labels }, value });
  }

  private matchLabels(l1: Record<string, string>, l2: Record<string, string>): boolean {
    const k1 = Object.keys(l1);
    const k2 = Object.keys(l2);
    if (k1.length !== k2.length) return false;
    return k1.every(k => l1[k] === l2[k]);
  }

  private formatLabels(labels: Record<string, string>): string {
    const entries = Object.entries(labels);
    if (entries.length === 0) return '';
    const formatted = entries.map(([k, v]) => `${k}="${v.replace(/"/g, '\\"')}"`).join(',');
    return `{${formatted}}`;
  }

  /**
   * Generates Prometheus exposition format (text/plain; version=0.0.4)
   */
  public exportMetrics(): string {
    const lines: string[] = [];

    // Header metadata
    lines.push('# ====================================================================');
    lines.push('# ULTRON Autonomous Revenue Recovery Control Plane — Prometheus Export');
    lines.push('# ====================================================================');
    lines.push('');

    // Process & System Guages
    const mem = process.memoryUsage();
    lines.push('# HELP process_resident_memory_bytes Resident memory size in bytes');
    lines.push('# TYPE process_resident_memory_bytes gauge');
    lines.push(`process_resident_memory_bytes ${mem.rss}`);
    lines.push('# HELP process_heap_used_bytes Process heap memory used in bytes');
    lines.push('# TYPE process_heap_used_bytes gauge');
    lines.push(`process_heap_used_bytes ${mem.heapUsed}`);
    lines.push('# HELP process_uptime_seconds Process uptime in seconds');
    lines.push('# TYPE process_uptime_seconds gauge');
    lines.push(`process_uptime_seconds ${Math.floor(process.uptime())}`);
    lines.push('');

    // Counters
    for (const [name, counter] of this.counters.entries()) {
      lines.push(`# HELP ${name} ${counter.help}`);
      lines.push(`# TYPE ${name} counter`);
      if (counter.values.length === 0) {
        lines.push(`${name} 0`);
      } else {
        for (const val of counter.values) {
          lines.push(`${name}${this.formatLabels(val.labels)} ${val.value}`);
        }
      }
      lines.push('');
    }

    // Gauges
    for (const [name, gauge] of this.gauges.entries()) {
      lines.push(`# HELP ${name} ${gauge.help}`);
      lines.push(`# TYPE ${name} gauge`);
      if (gauge.values.length === 0) {
        lines.push(`${name} 0`);
      } else {
        for (const val of gauge.values) {
          lines.push(`${name}${this.formatLabels(val.labels)} ${val.value}`);
        }
      }
      lines.push('');
    }

    // Histograms
    for (const [name, hist] of this.histograms.entries()) {
      lines.push(`# HELP ${name} ${hist.help}`);
      lines.push(`# TYPE ${name} histogram`);
      
      const count = hist.observations.length;
      const sum = hist.observations.reduce((acc, o) => acc + o.value, 0);

      for (const bucket of hist.buckets) {
        const bucketCount = hist.observations.filter(o => o.value <= bucket).length;
        lines.push(`${name}_bucket{le="${bucket}"} ${bucketCount}`);
      }
      lines.push(`${name}_bucket{le="+Inf"} ${count}`);
      lines.push(`${name}_sum ${sum.toFixed(4)}`);
      lines.push(`${name}_count ${count}`);
      lines.push('');
    }

    return lines.join('\n');
  }
}

// Singleton global metrics registry
export const metrics = new PrometheusRegistry();
