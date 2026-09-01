export type CircuitState = 'CLOSED' | 'OPEN' | 'HALF_OPEN';

export interface CircuitBreakerOptions {
  failureThreshold?: number; // default: 5 consecutive failures
  cooldownMs?: number; // default: 30,000ms (30s)
  requestTimeoutMs?: number; // default: 10,000ms (10s)
  maxRetries?: number; // default: 5
}

export class CircuitBreaker {
  private static instance: CircuitBreaker | null = null;

  private state: CircuitState = 'CLOSED';
  private failureCount: number = 0;
  private successCount: number = 0;
  private lastFailureTime: number = 0;
  private lastStateChange: number = Date.now();

  private readonly failureThreshold: number;
  private readonly cooldownMs: number;
  private readonly requestTimeoutMs: number;
  private readonly maxRetries: number;

  public constructor(options: CircuitBreakerOptions = {}) {
    this.failureThreshold = options.failureThreshold ?? 5;
    this.cooldownMs = options.cooldownMs ?? 30000;
    this.requestTimeoutMs = options.requestTimeoutMs ?? 10000;
    this.maxRetries = options.maxRetries ?? 5;
  }

  public static getInstance(): CircuitBreaker {
    if (!CircuitBreaker.instance) {
      CircuitBreaker.instance = new CircuitBreaker();
    }
    return CircuitBreaker.instance;
  }

  public getState(): CircuitState {
    this.checkCooldown();
    return this.state;
  }

  public getMetrics() {
    return {
      state: this.getState(),
      failureCount: this.failureCount,
      successCount: this.successCount,
      lastFailureTime: this.lastFailureTime,
      lastStateChange: this.lastStateChange,
    };
  }

  private checkCooldown(): void {
    if (this.state === 'OPEN') {
      const elapsed = Date.now() - this.lastFailureTime;
      if (elapsed >= this.cooldownMs) {
        this.state = 'HALF_OPEN';
        this.lastStateChange = Date.now();
        console.log('⚡ CircuitBreaker: Cooldown elapsed. Transitioned to HALF_OPEN (probing)');
      }
    }
  }

  private recordSuccess(): void {
    this.failureCount = 0;
    this.successCount++;
    if (this.state === 'HALF_OPEN') {
      this.state = 'CLOSED';
      this.lastStateChange = Date.now();
      console.log('✅ CircuitBreaker: Probe successful. Circuit CLOSED.');
    }
  }

  private recordFailure(err: Error): void {
    this.failureCount++;
    this.lastFailureTime = Date.now();

    if (this.state === 'HALF_OPEN' || this.failureCount >= this.failureThreshold) {
      this.state = 'OPEN';
      this.lastStateChange = Date.now();
      console.warn(`🚨 CircuitBreaker: Failure threshold reached (${this.failureCount}). Circuit OPEN.`);
    }
  }

  /**
   * Executes an async operation with 10s timeout, exponential backoff with jitter, and circuit breaker protection.
   */
  public async executeWithResilience<T>(
    operation: () => Promise<T>,
    contextName: string = 'RazorpayAPI'
  ): Promise<T> {
    if (this.getState() === 'OPEN') {
      throw new Error(`CircuitBreaker is OPEN for ${contextName}. Operations are currently suspended.`);
    }

    let lastError: any = null;

    for (let attempt = 1; attempt <= this.maxRetries; attempt++) {
      try {
        // Enforce 10s request timeout
        const result = await Promise.race([
          operation(),
          new Promise<never>((_, reject) =>
            setTimeout(() => reject(new Error(`Timeout: ${contextName} exceeded 10s limit`)), this.requestTimeoutMs)
          ),
        ]);

        this.recordSuccess();
        return result;
      } catch (err: any) {
        lastError = err;

        if (attempt === this.maxRetries) {
          break;
        }

        // Exponential backoff with jitter: 2^(attempt-1) * base + random jitter
        const baseDelayMs = Math.pow(2, attempt - 1) * 1000;
        const jitterMs = Math.floor(Math.random() * (baseDelayMs * 0.3));
        const totalDelayMs = Math.min(baseDelayMs + jitterMs, 8000);

        console.warn(
          `⚠️ ${contextName} failed on attempt ${attempt}/${this.maxRetries}: ${err.message}. Retrying in ${totalDelayMs}ms...`
        );
        await new Promise((r) => setTimeout(r, totalDelayMs));
      }
    }

    this.recordFailure(lastError);
    throw lastError;
  }

  public reset(): void {
    this.state = 'CLOSED';
    this.failureCount = 0;
    this.successCount = 0;
    this.lastFailureTime = 0;
    this.lastStateChange = Date.now();
  }
}
