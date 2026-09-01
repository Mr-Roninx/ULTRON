import { Redis } from 'ioredis';
import { EventEmitter } from 'node:events';

export interface CacheStatus {
  provider: 'Redis' | 'InMemoryFallback';
  connected: boolean;
  activeKeys: number;
}

export class CacheManager {
  private static instance: CacheManager | null = null;
  private redisClient: any = null;
  private redisSubscriber: any = null;
  private isRedisConnected: boolean = false;
  private fallbackStore: Map<string, { value: any; expiresAt: number }> = new Map();
  private eventBus: EventEmitter = new EventEmitter();

  private constructor() {
    const redisUrl = process.env.REDIS_URL;

    if (redisUrl) {
      try {
        const RedisClass = (Redis as any).default || Redis;
        this.redisClient = new RedisClass(redisUrl, {
          maxRetriesPerRequest: 2,
          connectTimeout: 4000,
          retryStrategy: (times: number) => (times > 3 ? null : Math.min(times * 100, 2000)),
        });

        this.redisSubscriber = new RedisClass(redisUrl, {
          maxRetriesPerRequest: 2,
          connectTimeout: 4000,
        });

        this.redisClient.on('connect', () => {
          this.isRedisConnected = true;
          console.log('⚡ CacheManager: Connected to Redis 7+ message broker');
        });

        this.redisClient.on('error', (err: any) => {
          this.isRedisConnected = false;
          console.warn('⚠️ CacheManager: Redis error, operating in resilient memory fallback mode:', err.message);
        });

        // Setup Pub/Sub subscriber
        this.redisSubscriber.subscribe('ultron:kill_switch', (err: any) => {
          if (!err) {
            console.log('📡 CacheManager: Subscribed to ultron:kill_switch pub/sub channel');
          }
        });

        this.redisSubscriber.on('message', (channel: string, message: string) => {
          if (channel === 'ultron:kill_switch') {
            const active = message === 'true';
            this.eventBus.emit('kill_switch_update', active);
          }
        });
      } catch (e: any) {
        console.warn('⚠️ CacheManager: Could not initialize Redis client, using in-memory store:', e.message);
      }
    } else {
      console.log('📦 CacheManager: REDIS_URL not configured. Operating with high-performance in-memory cache.');
    }
  }

  public static getInstance(): CacheManager {
    if (!CacheManager.instance) {
      CacheManager.instance = new CacheManager();
    }
    return CacheManager.instance;
  }

  public getStatus(): CacheStatus {
    return {
      provider: this.isRedisConnected ? 'Redis' : 'InMemoryFallback',
      connected: this.isRedisConnected,
      activeKeys: this.fallbackStore.size,
    };
  }

  public getRedisClient(): any {
    return this.isRedisConnected ? this.redisClient : null;
  }

  /**
   * Basic GET operation with TTL expiration.
   */
  public async get<T = any>(key: string): Promise<T | null> {
    if (this.isRedisConnected && this.redisClient) {
      try {
        const val = await this.redisClient.get(key);
        return val ? JSON.parse(val) : null;
      } catch (e) {
        // fallback
      }
    }

    const item = this.fallbackStore.get(key);
    if (!item) return null;
    if (Date.now() > item.expiresAt) {
      this.fallbackStore.delete(key);
      return null;
    }
    return item.value as T;
  }

  /**
   * Basic SET operation with TTL in seconds.
   */
  public async set(key: string, value: any, ttlSeconds: number = 300): Promise<void> {
    if (this.isRedisConnected && this.redisClient) {
      try {
        await this.redisClient.set(key, JSON.stringify(value), 'EX', ttlSeconds);
        return;
      } catch (e) {
        // fallback
      }
    }

    this.fallbackStore.set(key, {
      value,
      expiresAt: Date.now() + ttlSeconds * 1000,
    });
  }

  /**
   * Basic DEL operation.
   */
  public async del(key: string): Promise<void> {
    if (this.isRedisConnected && this.redisClient) {
      try {
        await this.redisClient.del(key);
      } catch (e) {
        // fallback
      }
    }
    this.fallbackStore.delete(key);
  }

  // -------------------------------------------------------------
  // High-Level Domain Caching Methods
  // -------------------------------------------------------------

  /**
   * Probability Table Caching (5-minute TTL)
   */
  public async getCachedProbabilityTable(reasonCode: string): Promise<any | null> {
    return this.get(`ultron:prob:${reasonCode}`);
  }

  public async setCachedProbabilityTable(reasonCode: string, data: any): Promise<void> {
    await this.set(`ultron:prob:${reasonCode}`, data, 300); // 5 min TTL
  }

  /**
   * Customer Trust Score Caching (Write-through invalidation)
   */
  public async getCachedCustomerTrust(customerId: string): Promise<number | null> {
    return this.get<number>(`ultron:trust:${customerId}`);
  }

  public async setCachedCustomerTrust(customerId: string, score: number): Promise<void> {
    await this.set(`ultron:trust:${customerId}`, score, 3600); // 1 hour TTL
  }

  public async invalidateCustomerTrust(customerId: string): Promise<void> {
    await this.del(`ultron:trust:${customerId}`);
  }

  /**
   * Distributed Idempotency Key Lock (SETNX with 24-hour TTL)
   * Returns true if key was acquired (first attempt), false if duplicate.
   */
  public async acquireIdempotencyKey(key: string, ttlSeconds: number = 86400): Promise<boolean> {
    const lockKey = `ultron:idemp:${key}`;
    if (this.isRedisConnected && this.redisClient) {
      try {
        const res = await this.redisClient.set(lockKey, 'locked', 'EX', ttlSeconds, 'NX');
        return res === 'OK';
      } catch (e) {
        // fallback
      }
    }

    if (this.fallbackStore.has(lockKey)) {
      const item = this.fallbackStore.get(lockKey)!;
      if (Date.now() <= item.expiresAt) {
        return false;
      }
    }

    this.fallbackStore.set(lockKey, {
      value: 'locked',
      expiresAt: Date.now() + ttlSeconds * 1000,
    });
    return true;
  }

  /**
   * Kill Switch Distributed Pub/Sub Broadcast (< 5s propagation)
   */
  public async broadcastKillSwitch(active: boolean): Promise<void> {
    if (this.isRedisConnected && this.redisClient) {
      try {
        await this.redisClient.publish('ultron:kill_switch', active ? 'true' : 'false');
      } catch (e) {
        // fallback
      }
    }
    this.eventBus.emit('kill_switch_update', active);
  }

  public onKillSwitchBroadcast(callback: (active: boolean) => void): void {
    this.eventBus.on('kill_switch_update', callback);
  }

  public async close(): Promise<void> {
    if (this.redisClient) {
      await this.redisClient.quit();
      this.redisClient = null;
    }
    if (this.redisSubscriber) {
      await this.redisSubscriber.quit();
      this.redisSubscriber = null;
    }
    this.fallbackStore.clear();
    CacheManager.instance = null;
  }
}
